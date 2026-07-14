# troubleshoot_docker.py
"""
BatchETL Pipeline - Docker Troubleshooting

Checks:
    - Docker daemon status
    - Required containers status
    - Container logs (last 10 lines)
    - Docker volumes
    - Docker network
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple, List, Dict, Optional


class Colors:
    """Terminal color codes."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str) -> None:
    """Print formatted header."""
    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}\n")


def print_check(text: str, status: bool, detail: str = "") -> None:
    """Print check result."""
    icon = "✓" if status else "✗"
    color = Colors.GREEN if status else Colors.RED
    if detail:
        print(f"  {color}{icon} {text}{Colors.END}")
        print(f"     {Colors.CYAN}-> {detail}{Colors.END}")
    else:
        print(f"  {color}{icon} {text}{Colors.END}")


def run_command(command: List[str]) -> Tuple[bool, str]:
    """Run a shell command and return status and output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return False, str(e)


def check_docker_daemon() -> bool:
    """Check if Docker daemon is running."""
    print_header("DOCKER DAEMON")

    success, output = run_command(['docker', '--version'])

    if success:
        print_check("Docker daemon is running", True, output)
        return True
    else:
        print_check("Docker daemon is NOT running", False)
        print(f"     {Colors.YELLOW}-> Please start Docker Desktop{Colors.END}")
        return False


def check_containers() -> bool:
    """Check if required containers are running."""
    print_header("CONTAINER STATUS")

    required_containers = [
        ('batch-etl-postgres', 'PostgreSQL'),
        ('batch-etl-airflow', 'Airflow'),
        ('batch-etl-streamlit', 'Streamlit')
    ]

    all_running = True
    container_status = {}

    for container_name, display_name in required_containers:
        success, output = run_command([
            'docker', 'ps', '--filter', f'name={container_name}',
            '--format', '{{.Status}}'
        ])

        if success and output:
            print_check(f"{display_name} ({container_name}) is running", True, output)
            container_status[container_name] = 'running'
        else:
            # Check if container exists but is stopped
            exists, _ = run_command([
                'docker', 'ps', '-a', '--filter', f'name={container_name}',
                '--format', '{{.Status}}'
            ])

            if exists and output:
                print_check(f"{display_name} ({container_name}) is STOPPED", False, "Container exists but not running")
                print(f"     {Colors.YELLOW}-> Run: docker-compose start {container_name}{Colors.END}")
                all_running = False
                container_status[container_name] = 'stopped'
            else:
                print_check(f"{display_name} ({container_name}) does not exist", False, "Container not found")
                print(f"     {Colors.YELLOW}-> Run: docker-compose up -d{Colors.END}")
                all_running = False
                container_status[container_name] = 'missing'

    return all_running


def check_container_logs() -> None:
    """Display last 10 lines of container logs."""
    print_header("CONTAINER LOGS (Last 10 lines)")

    containers = ['batch-etl-postgres', 'batch-etl-airflow', 'batch-etl-streamlit']

    for container in containers:
        success, output = run_command([
            'docker', 'logs', '--tail', '10', container
        ])

        print(f"\n{Colors.BOLD}{container}:{Colors.END}")
        if success and output:
            for line in output.split('\n')[:10]:
                if 'error' in line.lower() or 'fail' in line.lower():
                    print(f"  {Colors.RED}{line}{Colors.END}")
                elif 'warning' in line.lower():
                    print(f"  {Colors.YELLOW}{line}{Colors.END}")
                else:
                    print(f"  {line}")
        else:
            print(f"  {Colors.YELLOW}No logs available or container not running{Colors.END}")


def check_volumes() -> bool:
    """Check if required Docker volumes exist."""
    print_header("DOCKER VOLUMES")

    success, output = run_command([
        'docker', 'volume', 'ls', '--format', '{{.Name}}'
    ])

    if success:
        volumes = output.split('\n') if output else []
        has_volume = 'postgres_data' in str(volumes) or 'batch-etl_postgres_data' in str(volumes)

        if has_volume:
            print_check("PostgreSQL volume exists", True)
            return True
        else:
            print_check("PostgreSQL volume NOT found", False)
            print(f"     {Colors.YELLOW}-> Volume will be created when containers start{Colors.END}")
            return False
    else:
        print_check("Could not list volumes", False, output)
        return False


def check_network() -> bool:
    """Check if Docker network exists."""
    print_header("DOCKER NETWORK")

    success, output = run_command([
        'docker', 'network', 'ls', '--format', '{{.Name}}'
    ])

    if success:
        networks = output.split('\n') if output else []
        has_network = 'batch-etl-network' in str(networks)

        if has_network:
            print_check("batch-etl-network exists", True)
            return True
        else:
            print_check("batch-etl-network NOT found", False)
            print(f"     {Colors.YELLOW}-> Network will be created when containers start{Colors.END}")
            return False
    else:
        print_check("Could not list networks", False, output)
        return False


def check_compose_file() -> bool:
    """Check if docker-compose.yml exists."""
    print_header("DOCKER COMPOSE FILE")

    compose_path = Path.cwd() / 'docker-compose.yml'

    if compose_path.exists():
        size_kb = compose_path.stat().st_size / 1024
        print_check("docker-compose.yml exists", True, f"{size_kb:.1f} KB")
        return True
    else:
        print_check("docker-compose.yml NOT found", False)
        print(f"     {Colors.YELLOW}-> Please create docker-compose.yml in the project root{Colors.END}")
        return False


def main() -> None:
    """Main entry point."""
    print_header("BATCHETL PIPELINE - DOCKER TROUBLESHOOTING")

    results = {
        'compose_file': check_compose_file(),
        'docker_daemon': check_docker_daemon(),
        'containers': check_containers(),
        'volumes': check_volumes(),
        'network': check_network(),
    }

    if results['docker_daemon'] and results['containers']:
        check_container_logs()

    print_header("DOCKER TROUBLESHOOTING SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n  Total Checks: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {total - passed}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All Docker checks passed!{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some Docker checks failed.{Colors.END}")
        print(f"{Colors.YELLOW}Please fix the issues above before proceeding.{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()