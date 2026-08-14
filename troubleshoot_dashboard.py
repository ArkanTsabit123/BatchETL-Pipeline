# troubleshoot_dashboard.py

"""
BatchETL Pipeline - Dashboard Troubleshooting

Checks dashboard container, accessibility, files, imports, connection,
content validation (KPIs, charts, filters), load time, and error logs.
"""

import sys
import time
from pathlib import Path

from troubleshoot_utils import (
    Colors, print_header, print_check, print_warning,
    get_docker_container_status, check_url, check_file_exists,
    print_summary, get_container_logs
)
from troubleshoot_config import (
    CONTAINERS, PORTS, TIMEOUTS, DASHBOARD_FILES, REQUIRED_IMPORTS,
    DASHBOARD_KPIS, DASHBOARD_CHARTS, DASHBOARD_FILTERS, THRESHOLDS
)


def check_dashboard_container() -> bool:
    """Check if Streamlit container is running."""
    print_header("DASHBOARD CONTAINER")

    container_name = CONTAINERS['streamlit']
    is_running, status = get_docker_container_status(container_name)

    if is_running:
        print_check("Streamlit container is running", True, status)
        return True
    else:
        exists = get_docker_container_exists(container_name)

        if exists:
            print_check("Streamlit container is STOPPED", False, "Container exists but not running")
            print(f"     {Colors.YELLOW}-> Run: docker-compose start {container_name}{Colors.END}")
        else:
            print_check("Streamlit container does NOT exist", False)
            print(f"     {Colors.YELLOW}-> Run: docker-compose up -d streamlit{Colors.END}")
        return False


def check_dashboard_accessible() -> bool:
    """Check if dashboard is accessible."""
    print_header("DASHBOARD ACCESSIBILITY")

    is_ok, status, _ = check_url(f'http://localhost:{PORTS["streamlit"]}', TIMEOUTS['http'])

    if is_ok:
        print_check(f"Dashboard accessible (port {PORTS['streamlit']})", True, f"Status: {status}")
        return True
    else:
        print_check(f"Dashboard NOT accessible (port {PORTS['streamlit']})", False, f"Status: {status}")
        print(f"     {Colors.YELLOW}-> Check if container is running{Colors.END}")
        return False


def check_dashboard_files() -> bool:
    """Check if dashboard files exist."""
    print_header("DASHBOARD FILES")

    all_exist = True
    for file_path in DASHBOARD_FILES:
        exists, info = check_file_exists(file_path)
        if exists:
            print_check(f"{file_path}", True, f"{info['size_kb']:.1f} KB")
        else:
            print_check(f"{file_path}", False, "Not found")
            all_exist = False

    return all_exist


def check_dashboard_imports() -> bool:
    """Check if dashboard has required imports."""
    print_header("DASHBOARD IMPORTS")

    app_path = Path.cwd() / 'dashboard' / 'app.py'

    if not app_path.exists():
        print_check("app.py NOT found", False)
        return False

    try:
        with open(app_path, 'r') as f:
            content = f.read()

        all_present = True
        for imp in REQUIRED_IMPORTS:
            exists = imp in content
            print_check(f"Import: {imp}", exists)
            if not exists:
                all_present = False

        return all_present
    except Exception as e:
        print_check("Could not read app.py", False, str(e))
        return False


def check_dashboard_connection() -> bool:
    """Check if dashboard has connection string."""
    print_header("DATABASE CONNECTION")

    app_path = Path.cwd() / 'dashboard' / 'app.py'

    if not app_path.exists():
        print_check("app.py NOT found", False)
        return False

    try:
        with open(app_path, 'r') as f:
            content = f.read()

        has_connection = 'postgresql' in content and 'warehouse' in content
        print_check("Database connection string configured", has_connection)

        if has_connection:
            has_admin = 'admin' in content
            has_port = '5432' in content
            print_check("Username: admin", has_admin)
            print_check("Port: 5432", has_port)

        return has_connection
    except Exception as e:
        print_check("Could not read app.py", False, str(e))
        return False


def check_dashboard_content() -> bool:
    """Check dashboard content for key elements."""
    print_header("DASHBOARD CONTENT VALIDATION")

    is_ok, status, html = check_url(f'http://localhost:{PORTS["streamlit"]}', TIMEOUTS['http'])

    if not is_ok:
        print_check("Dashboard NOT accessible", False)
        return False

    print_check("Dashboard content loaded", True)

    print(f"\n  {Colors.BOLD}KPIs:{Colors.END}")
    kpi_found = 0
    for kpi in DASHBOARD_KPIS:
        exists = kpi in html
        print_check(f"  {kpi}", exists)
        if exists:
            kpi_found += 1

    print(f"\n  {Colors.BOLD}Charts:{Colors.END}")
    chart_found = 0
    for chart in DASHBOARD_CHARTS:
        exists = chart in html
        print_check(f"  {chart}", exists)
        if exists:
            chart_found += 1

    print(f"\n  {Colors.BOLD}Filters:{Colors.END}")
    filter_found = 0
    for filter_name in DASHBOARD_FILTERS:
        exists = filter_name in html
        print_check(f"  {filter_name}", exists)
        if exists:
            filter_found += 1

    total_kpis = len(DASHBOARD_KPIS)
    total_charts = len(DASHBOARD_CHARTS)
    total_filters = len(DASHBOARD_FILTERS)

    kpi_status = kpi_found == total_kpis
    chart_status = chart_found == total_charts
    filter_status = filter_found == total_filters

    print(f"\n  {Colors.BOLD}Summary:{Colors.END}")
    print_check(f"  KPIs: {kpi_found}/{total_kpis}", kpi_status)
    print_check(f"  Charts: {chart_found}/{total_charts}", chart_status)
    print_check(f"  Filters: {filter_found}/{total_filters}", filter_status)

    return kpi_status and chart_status and filter_status


def check_load_time() -> bool:
    """Check dashboard load time."""
    print_header("LOAD TIME")

    max_time = THRESHOLDS['response_time']['max_ms'] / 1000

    start_time = time.time()
    is_ok, _, _ = check_url(f'http://localhost:{PORTS["streamlit"]}', TIMEOUTS['http'])
    elapsed = time.time() - start_time

    if is_ok:
        is_fast = elapsed < max_time
        print_check(f"Dashboard load time: {elapsed:.3f}s", is_fast)
        if not is_fast:
            print_warning(f"Load time {elapsed:.3f}s exceeds recommended {max_time:.3f}s")
        return is_fast
    else:
        print_check("Dashboard load time: FAILED", False, "Dashboard not accessible")
        return False


def check_dashboard_errors() -> bool:
    """Check for errors in dashboard logs."""
    print_header("DASHBOARD ERRORS")

    container_name = CONTAINERS['streamlit']
    success, output = get_container_logs(container_name, 50)

    if not success:
        print_check("Could not fetch dashboard logs", False)
        return False

    error_keywords = ['error', 'exception', 'failed', 'traceback', 'st.error']
    found_errors = []

    for line in output.split('\n'):
        line_lower = line.lower()
        if any(kw in line_lower for kw in error_keywords):
            found_errors.append(line.strip())

    if found_errors:
        print_check(f"Found {len(found_errors)} error(s) in logs", False)
        for error in found_errors[:5]:
            print(f"  {Colors.RED}-> {error[:100]}{Colors.END}")
        if len(found_errors) > 5:
            print(f"  {Colors.RED}... and {len(found_errors) - 5} more errors{Colors.END}")
        return False
    else:
        print_check("No errors found in dashboard logs", True)
        return True


def main() -> None:
    """Main entry point."""
    print_header("BATCHETL PIPELINE - DASHBOARD TROUBLESHOOTING")

    results = {
        'container': check_dashboard_container(),
        'files': check_dashboard_files(),
        'imports': check_dashboard_imports(),
        'connection': check_dashboard_connection(),
        'accessible': check_dashboard_accessible(),
        'content': check_dashboard_content(),
        'load_time': check_load_time(),
        'errors': check_dashboard_errors(),
    }

    print_summary(results, "DASHBOARD TROUBLESHOOTING SUMMARY")


if __name__ == "__main__":
    main()