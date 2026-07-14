# troubleshoot_network.py
"""
BatchETL Pipeline - Network Troubleshooting

Checks:
    - Port availability (8080, 5432, 8501)
    - DNS resolution
    - Docker network connectivity
    - Container to container connectivity
"""

import subprocess
import sys
import socket
import requests
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


def check_port(port: int, host: str = 'localhost') -> Tuple[bool, str]:
    """Check if a port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            return True, f"Port {port} is open"
        else:
            return False, f"Port {port} is closed"
    except Exception as e:
        return False, str(e)


def check_ports() -> bool:
    """Check required ports."""
    print_header("PORT CHECK")

    ports = [
        (8080, 'Airflow UI'),
        (5432, 'PostgreSQL'),
        (8501, 'Streamlit Dashboard'),
    ]

    all_open = True
    for port, service in ports:
        open_status, message = check_port(port)
        print_check(f"{service} (port {port})", open_status, message)
        if not open_status:
            all_open = False

    return all_open


def check_dns() -> bool:
    """Check DNS resolution."""
    print_header("DNS RESOLUTION")

    hosts = [
        'localhost',
        'postgres',
        'airflow',
        'streamlit',
    ]

    all_resolved = True
    for host in hosts:
        try:
            ip = socket.gethostbyname(host)
            print_check(f"{host} resolves to {ip}", True)
        except socket.gaierror:
            print_check(f"{host} could NOT be resolved", False)
            if host in ['postgres', 'airflow', 'streamlit']:
                print(f"     {Colors.YELLOW}-> This is expected if not using Docker network{Colors.END}")
            all_resolved = False

    return all_resolved


def check_docker_network() -> bool:
    """Check Docker network connectivity."""
    print_header("DOCKER NETWORK")

    success, output = run_command([
        'docker', 'network', 'inspect', 'batch-etl-network'
    ])

    if success:
        print_check("batch-etl-network exists", True)

        # Check if containers are connected
        containers = ['batch-etl-postgres', 'batch-etl-airflow', 'batch-etl-streamlit']
        for container in containers:
            connected = container in output
            print_check(f"{container} connected", connected)

        return True
    else:
        print_check("batch-etl-network NOT found", False)
        print(f"     {Colors.YELLOW}-> Network will be created when containers start{Colors.END}")
        return False


def check_container_connectivity() -> bool:
    """Check connectivity between containers."""
    print_header("CONTAINER CONNECTIVITY")

    # Try to ping postgres from airflow container
    success, output = run_command([
        'docker', 'exec', 'batch-etl-airflow',
        'ping', '-c', '1', 'postgres'
    ])

    if success:
        print_check("Airflow -> PostgreSQL connectivity", True)
    else:
        print_check("Airflow -> PostgreSQL connectivity", False, "Ping failed")
        print(f"     {Colors.YELLOW}-> Check if containers are on the same network{Colors.END}")

    # Try to connect to postgres from airflow
    success, output = run_command([
        'docker', 'exec', 'batch-etl-airflow',
        'python', '-c',
        "from sqlalchemy import create_engine; engine = create_engine('postgresql+psycopg2://admin:admin@postgres:5432/warehouse'); conn = engine.connect(); print('Connected'); conn.close()"
    ])

    if success and 'Connected' in output:
        print_check("Airflow -> PostgreSQL connection test", True)
    else:
        print_check("Airflow -> PostgreSQL connection test", False, "Connection failed")
        print(f"     {Colors.YELLOW}-> Check PostgreSQL credentials and container status{Colors.END}")

    return True


def main() -> None:
    """Main entry point."""
    print_header("BATCHETL PIPELINE - NETWORK TROUBLESHOOTING")

    results = {
        'ports': check_ports(),
        'dns': check_dns(),
        'docker_network': check_docker_network(),
        'connectivity': check_container_connectivity(),
    }

    print_header("NETWORK TROUBLESHOOTING SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n  Total Checks: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {total - passed}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All Network checks passed!{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some Network checks failed.{Colors.END}")
        print(f"{Colors.YELLOW}Please fix the issues above before proceeding.{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()