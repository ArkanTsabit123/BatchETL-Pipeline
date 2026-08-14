# troubleshoot_docker.py

"""
BatchETL Pipeline - Docker Troubleshooting

Checks Docker daemon, containers, volumes, network, disk space, and resource usage.
"""

import sys
from pathlib import Path

from troubleshoot_utils import (
    Colors, print_header, print_check, print_warning,
    run_command, run_docker_command, get_docker_container_status,
    get_docker_container_exists, get_container_logs,
    check_disk_space, format_bytes, print_summary
)
from troubleshoot_config import (
    CONTAINERS, REQUIRED_CONTAINERS, OPTIONAL_CONTAINERS,
    TIMEOUTS, FILES, THRESHOLDS
)


def check_docker_daemon() -> bool:
    """Check if Docker daemon is running."""
    print_header("DOCKER DAEMON")

    success, output = run_command(['docker', '--version'], TIMEOUTS['command'])

    if success:
        print_check("Docker daemon is running", True, output)
        return True
    else:
        print_check("Docker daemon is NOT running", False)
        print(f"     {Colors.YELLOW}-> Start Docker Desktop{Colors.END}")
        return False


def check_compose_file() -> bool:
    """Check if docker-compose.yml exists."""
    print_header("DOCKER COMPOSE FILE")

    compose_path = Path.cwd() / FILES['compose']

    if compose_path.exists():
        size_kb = compose_path.stat().st_size / 1024
        print_check("docker-compose.yml exists", True, f"{size_kb:.1f} KB")
        return True
    else:
        print_check("docker-compose.yml NOT found", False)
        print(f"     {Colors.YELLOW}-> Create docker-compose.yml in the project root{Colors.END}")
        return False


def check_containers() -> bool:
    """Check if required containers are running."""
    print_header("CONTAINER STATUS")

    all_running = True

    for container_key in REQUIRED_CONTAINERS:
        container_name = CONTAINERS[container_key]
        is_running, status = get_docker_container_status(container_name)

        if is_running:
            print_check(f"{container_key.capitalize()} ({container_name}) is running", True, status)
        else:
            exists = get_docker_container_exists(container_name)

            if exists:
                print_check(f"{container_key.capitalize()} ({container_name}) is STOPPED", False,
                           "Container exists but not running")
                print(f"     {Colors.YELLOW}-> Run: docker-compose start {container_name}{Colors.END}")
            else:
                print_check(f"{container_key.capitalize()} ({container_name}) does NOT exist", False,
                           "Container not found")
                print(f"     {Colors.YELLOW}-> Run: docker-compose up -d{Colors.END}")
            all_running = False

    for container_key in OPTIONAL_CONTAINERS:
        container_name = CONTAINERS[container_key]
        is_running, status = get_docker_container_status(container_name)

        if is_running:
            print_check(f"{container_key.capitalize()} ({container_name}) is running", True, status)
        else:
            print_warning(f"{container_key.capitalize()} ({container_name}) is not running",
                         "Optional: Run docker-compose up -d for full pipeline")

    return all_running


def check_container_logs() -> None:
    """Display last 10 lines of container logs."""
    print_header("CONTAINER LOGS (Last 10 lines)")

    containers_to_check = REQUIRED_CONTAINERS + OPTIONAL_CONTAINERS
    has_errors = False

    for container_key in containers_to_check:
        container_name = CONTAINERS[container_key]
        is_running, _ = get_docker_container_status(container_name)

        if not is_running:
            print(f"\n{Colors.BOLD}{container_name}:{Colors.END}")
            print(f"  {Colors.YELLOW}Container not running{Colors.END}")
            continue

        success, output = get_container_logs(container_name, 20)

        print(f"\n{Colors.BOLD}{container_name}:{Colors.END}")
        if success and output:
            error_lines = [line for line in output.split('\n')[:20] if line.strip() and 'error' in line.lower()]
            warning_lines = [line for line in output.split('\n')[:20] if line.strip() and 'warning' in line.lower()]
            info_lines = [line for line in output.split('\n')[:20] if line.strip() and 'error' not in line.lower() and 'warning' not in line.lower()]

            if error_lines:
                has_errors = True
                for line in error_lines[:5]:
                    print(f"  {Colors.RED}{line}{Colors.END}")
                if len(error_lines) > 5:
                    print(f"  {Colors.RED}... and {len(error_lines) - 5} more errors{Colors.END}")

            for line in warning_lines[:3]:
                print(f"  {Colors.YELLOW}{line}{Colors.END}")

            if not error_lines and not warning_lines and info_lines:
                for line in info_lines[:3]:
                    print(f"  {line}")
                if len(info_lines) > 3:
                    print(f"  ... and {len(info_lines) - 3} more lines")
        else:
            print(f"  {Colors.YELLOW}No logs available{Colors.END}")

    if has_errors:
        print_warning("Errors found in container logs. Check the logs above.")


def check_volumes() -> bool:
    """Check if required Docker volumes exist."""
    print_header("DOCKER VOLUMES")

    success, output = run_docker_command([
        'volume', 'ls', '--format', '{{.Name}}'
    ], TIMEOUTS['command'])

    if success:
        volumes = output.split('\n') if output else []
        has_volume = any('postgres_data' in v or 'batch-etl_postgres_data' in v for v in volumes)

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

    success, output = run_docker_command([
        'network', 'ls', '--format', '{{.Name}}'
    ], TIMEOUTS['command'])

    if success:
        networks = output.split('\n') if output else []
        print(f"  {Colors.CYAN}Networks found: {', '.join(networks) if networks else 'None'}{Colors.END}")

        has_network = any('batch-etl-network' in n for n in networks)

        if has_network:
            print_check("batch-etl-network exists", True)
            return True
        else:
            print_check("batch-etl-network NOT found", False)
            print(f"     {Colors.YELLOW}-> Run: docker-compose up -d to create network{Colors.END}")
            return False
    else:
        print_check("Could not list networks", False, output)
        return False


def check_disk_space_usage() -> bool:
    """Check disk space availability."""
    print_header("DISK SPACE")

    success, info = check_disk_space('.')

    if success:
        free_gb = info['free_gb']
        total_gb = info['total_gb']
        min_required = THRESHOLDS['disk_space']['min_gb']
        warning_level = THRESHOLDS['disk_space']['warning_gb']

        print_check(f"Total disk space: {format_bytes(info['total_gb'] * 1024 ** 3)}", True)

        if free_gb < min_required:
            print_check(f"Free space {free_gb:.1f} GB >= {min_required} GB required", False)
            print(f"     {Colors.RED}-> Critical: Low disk space! Free up at least {min_required} GB{Colors.END}")
            return False
        elif free_gb < warning_level:
            print_warning(f"Free space {free_gb:.1f} GB < {warning_level} GB warning threshold")
            return True
        else:
            print_check(f"Free space {free_gb:.1f} GB available", True)
            return True
    else:
        print_check("Could not check disk space", False)
        return False


def check_container_resources() -> None:
    """Check container resource usage."""
    print_header("CONTAINER RESOURCES")

    containers_to_check = REQUIRED_CONTAINERS + OPTIONAL_CONTAINERS

    for container_key in containers_to_check:
        container_name = CONTAINERS[container_key]
        is_running, _ = get_docker_container_status(container_name)

        if not is_running:
            print(f"\n{Colors.BOLD}{container_name}:{Colors.END}")
            print(f"  {Colors.YELLOW}Container not running{Colors.END}")
            continue

        success, output = run_docker_command([
            'stats', '--no-stream', '--format',
            '{{.Name}} | CPU: {{.CPUPerc}} | MEM: {{.MemUsage}} | NET: {{.NetIO}}',
            container_name
        ], TIMEOUTS['command'])

        if success and output:
            print(f"\n{Colors.BOLD}{container_name}:{Colors.END}")
            print(f"  {output}")
        else:
            print(f"\n{Colors.BOLD}{container_name}:{Colors.END}")
            print(f"  {Colors.YELLOW}Could not get resource usage{Colors.END}")


def main() -> None:
    """Main entry point."""
    print_header("BATCHETL PIPELINE - DOCKER TROUBLESHOOTING")

    results = {
        'compose_file': check_compose_file(),
        'docker_daemon': check_docker_daemon(),
        'containers': check_containers(),
        'volumes': check_volumes(),
        'network': check_network(),
        'disk_space': check_disk_space_usage(),
    }

    if results['docker_daemon']:
        check_container_logs()
        check_container_resources()

    print_summary(results, "DOCKER TROUBLESHOOTING SUMMARY")


if __name__ == "__main__":
    main()