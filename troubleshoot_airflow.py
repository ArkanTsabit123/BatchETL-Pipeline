# troubleshoot_airflow.py
"""
BatchETL Pipeline - Airflow Troubleshooting

Checks:
    - Airflow container status
    - Airflow UI accessibility
    - DAG file syntax
    - DAG list in UI (with session auth)
    - DAG status
"""

import subprocess
import sys
import ast
import requests
import re
from pathlib import Path
from typing import Tuple, List, Dict


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
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, ""


def check_airflow_container() -> bool:
    """Check if Airflow container is running."""
    print_header("AIRFLOW CONTAINER")

    success, output = run_command([
        'docker', 'ps', '--filter', 'name=batch-etl-airflow',
        '--format', '{{.Status}}'
    ])

    if success and output:
        print_check("Airflow container is running", True, output)
        return True
    else:
        exists, stopped_output = run_command([
            'docker', 'ps', '-a', '--filter', 'name=batch-etl-airflow',
            '--format', '{{.Status}}'
        ])

        if exists and stopped_output:
            print_check("Airflow container is STOPPED", False, "Container exists but not running")
            print(f"     {Colors.YELLOW}-> Run: docker-compose start airflow{Colors.END}")
        else:
            print_check("Airflow container does NOT exist", False)
            print(f"     {Colors.YELLOW}-> Run: docker-compose up -d airflow{Colors.END}")
        return False


def check_airflow_ui() -> bool:
    """Check if Airflow UI is accessible."""
    print_header("AIRFLOW UI")

    try:
        response = requests.get('http://localhost:8080', timeout=5)
        accessible = response.status_code == 200
        print_check("Airflow UI accessible", accessible, f"Status: {response.status_code}")
        return accessible
    except requests.ConnectionError:
        print_check("Airflow UI NOT accessible", False, "Connection refused")
        print(f"     {Colors.YELLOW}-> Check if Airflow container is running{Colors.END}")
        return False
    except requests.Timeout:
        print_check("Airflow UI NOT accessible", False, "Connection timeout")
        print(f"     {Colors.YELLOW}-> Check if Airflow container is responding{Colors.END}")
        return False


def check_dag_file() -> bool:
    """Check DAG file syntax and existence."""
    print_header("DAG FILE")

    dag_path = Path.cwd() / 'dags' / 'etl_pipeline.py'

    if not dag_path.exists():
        print_check("DAG file NOT found", False, "dags/etl_pipeline.py missing")
        print(f"     {Colors.YELLOW}-> Create dags/etl_pipeline.py{Colors.END}")
        return False

    print_check("DAG file exists", True)

    try:
        with open(dag_path, 'r') as f:
            content = f.read()
        ast.parse(content)
        print_check("DAG file syntax valid", True)
        return True
    except SyntaxError as e:
        print_check("DAG file syntax INVALID", False, f"Line {e.lineno}: {e.msg}")
        return False


def check_dag_content() -> bool:
    """Check DAG content for required components."""
    print_header("DAG CONTENT")

    dag_path = Path.cwd() / 'dags' / 'etl_pipeline.py'

    if not dag_path.exists():
        print_check("DAG file NOT found", False)
        return False

    try:
        with open(dag_path, 'r') as f:
            content = f.read()

        checks = {
            'DAG ID (etl_pipeline)': 'etl_pipeline' in content or "dag_id='etl_pipeline'" in content,
            'Schedule (@daily)': '@daily' in content or "schedule_interval" in content,
            'Extract task': 'extract_data' in content,
            'Transform task': 'transform_data' in content,
            'Load task': 'load_data' in content,
            'Dependencies (>>)': '>>' in content,
            'Tags': 'tags=' in content,
        }

        all_passed = True
        for name, passed in checks.items():
            print_check(name, passed)
            if not passed:
                all_passed = False

        return all_passed
    except Exception as e:
        print_check("Could not read DAG file", False, str(e))
        return False


def check_dag_in_ui() -> bool:
    """Check if DAG appears in Airflow UI with session authentication."""
    print_header("DAG IN UI")

    try:
        # Create session
        session = requests.Session()
        
        # Get login page to get CSRF token
        login_page = session.get('http://localhost:8080/login')
        csrf_token = None
        
        # Extract CSRF token
        csrf_match = re.search(r'name="csrf_token".*?value="(.*?)"', login_page.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
        
        # Login data
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        if csrf_token:
            login_data['csrf_token'] = csrf_token
        
        # Perform login
        login_response = session.post('http://localhost:8080/login', data=login_data)
        
        # Check if login successful
        if login_response.status_code == 200 or 'home' in login_response.url:
            # Now fetch DAGs with authenticated session
            response = session.get('http://localhost:8080/api/v1/dags', timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                dags = [dag['dag_id'] for dag in data.get('dags', [])]
                if 'etl_pipeline' in dags:
                    print_check("DAG 'etl_pipeline' found in UI", True)
                    return True
                else:
                    print_check("DAG 'etl_pipeline' NOT found in UI", False)
                    print(f"     {Colors.YELLOW}-> Available DAGs: {', '.join(dags[:5]) if dags else 'None'}{Colors.END}")
                    print(f"     {Colors.YELLOW}-> Check if DAG file is in the correct folder{Colors.END}")
                    return False
            else:
                print_check("Could not fetch DAG list", False, f"Status: {response.status_code}")
                print(f"     {Colors.YELLOW}-> Try logging in manually at http://localhost:8080{Colors.END}")
                return False
        else:
            print_check("Login to Airflow failed", False, "Check credentials or CSRF token")
            print(f"     {Colors.YELLOW}-> Try logging in manually at http://localhost:8080{Colors.END}")
            return False
            
    except requests.ConnectionError:
        print_check("Could not fetch DAG list", False, "Airflow UI not accessible")
        return False
    except Exception as e:
        print_check("Could not fetch DAG list", False, str(e))
        return False


def main() -> None:
    """Main entry point."""
    print_header("BATCHETL PIPELINE - AIRFLOW TROUBLESHOOTING")

    container_ok = check_airflow_container()
    ui_ok = check_airflow_ui()
    dag_file_ok = check_dag_file()
    dag_content_ok = check_dag_content()

    results = {
        'container': container_ok,
        'ui': ui_ok,
        'dag_file': dag_file_ok,
        'dag_content': dag_content_ok,
    }

    if container_ok and ui_ok:
        results['dag_in_ui'] = check_dag_in_ui()

    print_header("AIRFLOW TROUBLESHOOTING SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n  Total Checks: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {total - passed}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All Airflow checks passed!{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some Airflow checks failed.{Colors.END}")
        print(f"{Colors.YELLOW}Please fix the issues above before proceeding.{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()