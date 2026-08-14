# troubleshoot_network.py

"""
BatchETL Pipeline - Network Troubleshooting

Checks ports, DNS resolution, Docker network, container connectivity,
internet connectivity, and network latency.
"""

import sys
import socket
import time

from troubleshoot_utils import (
    Colors, print_header, print_check, print_warning,
    run_command, run_docker_command, check_port_open,
    check_url, print_summary
)
from troubleshoot_config import (
    PORTS, PORT_DESCRIPTIONS, TIMEOUTS, DB_CONFIG,
    EXTERNAL_URLS, THRESHOLDS, CONTAINERS
)


def check_ports() -> bool:
    """Check required ports."""
    print_header("PORT CHECK")

    all_open = True
    for port, service in PORT_DESCRIPTIONS.items():
        is_open = check_port_open('localhost', port, TIMEOUTS['port_check'])
        if is_open:
            print_check(f"{service} (port {port})", True, "Open")
        else:
            print_check(f"{service} (port {port})", False, "Closed or in use")
            all_open = False

    return all_open


def check_dns() -> bool:
    """Check DNS resolution."""
    print_header("DNS RESOLUTION")

    hosts = ['localhost']
    all_resolved = True

    for host in hosts:
        try:
            ip = socket.gethostbyname(host)
            print_check(f"{host} resolves to {ip}", True)
        except socket.gaierror:
            print_check(f"{host} could NOT be resolved", False)
            all_resolved = False

    print(f"\n  {Colors.CYAN}Note: Container names (postgres, airflow, streamlit) are only resolvable inside Docker network{Colors.END}")

    return all_resolved


def check_external_dns() -> bool:
    """Check external DNS resolution."""
    print_header("EXTERNAL DNS RESOLUTION")

    external_hosts = ['google.com', 'github.com', 'pypi.org']

    all_resolved = True
    for host in external_hosts:
        try:
            ip = socket.gethostbyname(host)
            print_check(f"{host} resolves to {ip}", True)
        except socket.gaierror:
            print_check(f"{host} could NOT be resolved", False)
            all_resolved = False

    return all_resolved


def check_docker_network() -> bool:
    """Check Docker network connectivity."""
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
            print(f"     {Colors.YELLOW}-> Network will be created when containers start{Colors.END}")
            return False
    else:
        print_check("Could not list networks", False)
        return False


def check_container_connectivity() -> bool:
    """Check connectivity between containers."""
    print_header("CONTAINER CONNECTIVITY")

    pg_accessible = check_port_open('localhost', PORTS['postgres'], TIMEOUTS['port_check'])
    if pg_accessible:
        print_check("PostgreSQL is accessible from host (port 5432)", True)
    else:
        print_check("PostgreSQL is NOT accessible from host", False)

    af_accessible = check_port_open('localhost', PORTS['airflow'], TIMEOUTS['port_check'])
    if af_accessible:
        print_check("Airflow is accessible from host (port 8080)", True)
    else:
        print_check("Airflow is NOT accessible from host", False)

    st_accessible = check_port_open('localhost', PORTS['streamlit'], TIMEOUTS['port_check'])
    if st_accessible:
        print_check("Streamlit is accessible from host (port 8501)", True)
    else:
        print_check("Streamlit is NOT accessible from host", False)

    print(f"\n  {Colors.CYAN}Testing container-to-container connectivity...{Colors.END}")

    try:
        test_query = f"SELECT 1 FROM pg_database WHERE datname = '{DB_CONFIG['database']}';"
        success, output = run_command([
            'docker', 'exec', CONTAINERS['airflow'],
            'python', '-c',
            f"from sqlalchemy import create_engine; "
            f"engine = create_engine('postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@postgres:{DB_CONFIG['port']}/{DB_CONFIG['database']}'); "
            f"conn = engine.connect(); "
            f"result = conn.execute('{test_query}'); "
            f"print('Connected'); "
            f"conn.close()"
        ], TIMEOUTS['command'])

        if success and 'Connected' in output:
            print_check("Airflow -> PostgreSQL connection test", True)
            return True
        else:
            print_check("Airflow -> PostgreSQL connection test", False, "Connection failed")
            print(f"     {Colors.YELLOW}-> Check PostgreSQL credentials and container status{Colors.END}")
            return False
    except Exception as e:
        print_check("Airflow -> PostgreSQL connection test", False, str(e))
        return False


def check_internet_connectivity() -> bool:
    """Check internet connectivity."""
    print_header("INTERNET CONNECTIVITY")

    all_accessible = True
    for name, url in EXTERNAL_URLS:
        is_ok, status, _ = check_url(url, TIMEOUTS['http'])
        if is_ok:
            print_check(f"{name} accessible", True, f"Status: {status}")
        else:
            print_check(f"{name} accessible", False, f"Status: {status}")
            all_accessible = False

    return all_accessible


def check_network_latency() -> bool:
    """Check network latency to external services."""
    print_header("NETWORK LATENCY")

    test_urls = [
        ('GitHub', 'https://github.com'),
        ('PyPI', 'https://pypi.org'),
        ('Google', 'https://google.com'),
    ]

    max_time = THRESHOLDS['response_time']['max_ms'] / 1000
    all_good = True

    for name, url in test_urls:
        start_time = time.time()
        is_ok, _, _ = check_url(url, TIMEOUTS['http'])
        elapsed = time.time() - start_time

        if is_ok:
            status_text = f"{elapsed:.3f}s"
            is_fast = elapsed < max_time
            print_check(f"{name}: {status_text}", is_fast)
            if not is_fast:
                print_warning(f"Latency {elapsed:.3f}s exceeds recommended {max_time:.3f}s")
                all_good = False
        else:
            print_check(f"{name}: FAILED", False)
            all_good = False

    return all_good


def main() -> None:
    """Main entry point."""
    print_header("BATCHETL PIPELINE - NETWORK TROUBLESHOOTING")

    results = {
        'ports': check_ports(),
        'dns': check_dns(),
        'external_dns': check_external_dns(),
        'docker_network': check_docker_network(),
        'connectivity': check_container_connectivity(),
        'internet': check_internet_connectivity(),
        'latency': check_network_latency(),
    }

    print_summary(results, "NETWORK TROUBLESHOOTING SUMMARY")


if __name__ == "__main__":
    main()