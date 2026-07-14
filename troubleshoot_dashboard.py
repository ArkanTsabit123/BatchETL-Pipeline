# troubleshoot_dashboard.py
"""
BatchETL Pipeline - Dashboard Troubleshooting

Checks:
    - Dashboard container status
    - Dashboard accessibility (port 8501)
    - Dashboard files exist (app.py, Dockerfile, requirements.txt)
    - Dashboard imports (streamlit, pandas, plotly, sqlalchemy)
    - Dashboard connection to PostgreSQL
"""

import subprocess
import sys
import importlib.util
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


def check_dashboard_container() -> bool:
    """Check if Streamlit container is running."""
    print_header("DASHBOARD CONTAINER")

    success, output = run_command([
        'docker', 'ps', '--filter', 'name=batch-etl-streamlit',
        '--format', '{{.Status}}'
    ])

    if success and output:
        print_check("Streamlit container is running", True, output)
        return True
    else:
        exists, _ = run_command([
            'docker', 'ps', '-a', '--filter', 'name=batch-etl-streamlit',
            '--format', '{{.Status}}'
        ])

        if exists and output:
            print_check("Streamlit container is STOPPED", False, "Container exists but not running")
            print(f"     {Colors.YELLOW}-> Run: docker-compose start streamlit{Colors.END}")
        else:
            print_check("Streamlit container does NOT exist", False)
            print(f"     {Colors.YELLOW}-> Run: docker-compose up -d streamlit{Colors.END}")
        return False


def check_dashboard_accessible() -> bool:
    """Check if dashboard is accessible."""
    print_header("DASHBOARD ACCESSIBILITY")

    try:
        response = requests.get('http://localhost:8501', timeout=5)
        accessible = response.status_code == 200
        print_check("Dashboard accessible", accessible, f"Status: {response.status_code}")
        return accessible
    except requests.ConnectionError:
        print_check("Dashboard NOT accessible", False, "Connection refused")
        print(f"     {Colors.YELLOW}-> Check if container is running{Colors.END}")
        return False
    except requests.Timeout:
        print_check("Dashboard NOT accessible", False, "Connection timeout")
        print(f"     {Colors.YELLOW}-> Check if container is responding{Colors.END}")
        return False


def check_dashboard_files() -> bool:
    """Check if dashboard files exist."""
    print_header("DASHBOARD FILES")

    files = [
        ('dashboard/app.py', 'Main application'),
        ('dashboard/Dockerfile', 'Container definition'),
        ('dashboard/requirements.txt', 'Dependencies'),
    ]

    all_exist = True
    for file_path, description in files:
        path = Path.cwd() / file_path
        exists = path.exists()
        print_check(f"{file_path}", exists, description)
        if not exists:
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

        required_imports = [
            'streamlit',
            'pandas',
            'plotly',
            'sqlalchemy',
            'create_engine',
        ]

        all_present = True
        for imp in required_imports:
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
            # Check connection details
            has_admin = 'admin' in content
            has_port = '5432' in content
            print_check("Username: admin", has_admin)
            print_check("Port: 5432", has_port)

        return has_connection
    except Exception as e:
        print_check("Could not read app.py", False, str(e))
        return False


def main() -> None:
    """Main entry point."""
    print_header("BATCHETL PIPELINE - DASHBOARD TROUBLESHOOTING")

    results = {
        'container': check_dashboard_container(),
        'files': check_dashboard_files(),
        'imports': check_dashboard_imports(),
        'connection': check_dashboard_connection(),
        'accessible': check_dashboard_accessible(),
    }

    print_header("DASHBOARD TROUBLESHOOTING SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n  Total Checks: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {total - passed}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All Dashboard checks passed!{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some Dashboard checks failed.{Colors.END}")
        print(f"{Colors.YELLOW}Please fix the issues above before proceeding.{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()