# troubleshoot_airflow.py

"""
BatchETL Pipeline - Airflow Troubleshooting

Checks Airflow container, UI, DAG file, tasks, scheduler, and webserver.
"""

import sys
import ast
from pathlib import Path

from troubleshoot_utils import (
    Colors, print_header, print_check, print_warning,
    run_airflow_command, get_docker_container_status,
    check_url, print_summary
)
from troubleshoot_config import (
    CONTAINERS, DAG_CONFIG, DAG_TASKS, TIMEOUTS
)


def check_airflow_container() -> bool:
    """Check if Airflow container is running."""
    print_header("AIRFLOW CONTAINER")

    container_name = CONTAINERS['airflow']
    is_running, status = get_docker_container_status(container_name)

    if is_running:
        print_check("Airflow container is running", True, status)
        return True
    else:
        exists = get_docker_container_exists(container_name)

        if exists:
            print_check("Airflow container is STOPPED", False, "Container exists but not running")
            print(f"     {Colors.YELLOW}-> Run: docker-compose start {container_name}{Colors.END}")
        else:
            print_check("Airflow container does NOT exist", False)
            print(f"     {Colors.YELLOW}-> Run: docker-compose up -d airflow{Colors.END}")
        return False


def check_airflow_ui() -> bool:
    """Check if Airflow UI is accessible."""
    print_header("AIRFLOW UI")

    is_ok, status, _ = check_url('http://localhost:8080', TIMEOUTS['http'])

    if is_ok:
        print_check("Airflow UI accessible", True, f"Status: {status}")
        return True
    else:
        print_check("Airflow UI NOT accessible", False, f"Status: {status}")
        print(f"     {Colors.YELLOW}-> Check if Airflow container is running{Colors.END}")
        return False


def check_dag_file() -> bool:
    """Check DAG file syntax and existence."""
    print_header("DAG FILE")

    dag_path = Path.cwd() / DAG_CONFIG['dag_file']

    if not dag_path.exists():
        print_check("DAG file NOT found", False, f"{DAG_CONFIG['dag_file']} missing")
        print(f"     {Colors.YELLOW}-> Create {DAG_CONFIG['dag_file']}{Colors.END}")
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

    dag_path = Path.cwd() / DAG_CONFIG['dag_file']

    if not dag_path.exists():
        print_check("DAG file NOT found", False)
        return False

    try:
        with open(dag_path, 'r') as f:
            content = f.read()

        checks = {
            f"DAG ID ({DAG_CONFIG['dag_id']})": DAG_CONFIG['dag_id'] in content,
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
    except Exception:
        print_check("Could not read DAG file", False)
        return False


def check_dag_in_ui() -> bool:
    """Check if DAG appears in Airflow UI."""
    print_header("DAG IN UI")

    try:
        success, output = run_airflow_command([
            'dags', 'list'
        ], CONTAINERS['airflow'], TIMEOUTS['command'])

        if success and DAG_CONFIG['dag_id'] in output:
            print_check(f"DAG '{DAG_CONFIG['dag_id']}' found in Airflow", True)
            return True
        else:
            print_check(f"DAG '{DAG_CONFIG['dag_id']}' NOT found in Airflow", False)
            print(f"     {Colors.YELLOW}-> Check if DAG file is in the correct folder{Colors.END}")
            return False
    except Exception as e:
        print_check("Could not fetch DAG list", False, str(e))
        return False


def check_task_status() -> bool:
    """Check status of DAG tasks."""
    print_header("TASK STATUS")

    all_success = True

    for task in DAG_TASKS:
        try:
            success, output = run_airflow_command([
                'tasks', 'state', DAG_CONFIG['dag_id'], task,
                '--execution-date', 'latest'
            ], CONTAINERS['airflow'], TIMEOUTS['command'])

            if success:
                status = output.strip() if output else 'unknown'
                is_success = 'success' in status.lower() or 'none' in status.lower()
                print_check(f"Task: {task}", is_success, f"Status: {status}")
                if not is_success and 'none' not in status.lower():
                    all_success = False
            else:
                print_check(f"Task: {task}", False, "Could not check status")
                all_success = False
        except Exception as e:
            print_check(f"Task: {task}", False, str(e))
            all_success = False

    if not all_success:
        print_warning("Some tasks are not successful. Check Airflow UI for details.")

    return all_success


def check_scheduler_status() -> bool:
    """Check if Airflow scheduler is running."""
    print_header("SCHEDULER STATUS")

    try:
        success, _ = run_airflow_command([
            'scheduler', '--status'
        ], CONTAINERS['airflow'], TIMEOUTS['command'])

        if success:
            print_check("Airflow scheduler is running", True)
            return True
        else:
            print_check("Airflow scheduler is NOT running", False)
            print(f"     {Colors.YELLOW}-> Run: docker exec {CONTAINERS['airflow']} airflow scheduler &{Colors.END}")
            return False
    except Exception as e:
        print_check("Could not check scheduler status", False, str(e))
        return False


def check_webserver_status() -> bool:
    """Check if Airflow webserver is running."""
    print_header("WEBSERVER STATUS")

    try:
        is_ok, status, _ = check_url('http://localhost:8080/health', TIMEOUTS['http'])

        if is_ok:
            print_check("Airflow webserver is running", True, f"Status: {status}")
            return True
        else:
            print_check("Airflow webserver is NOT running", False)
            print(f"     {Colors.YELLOW}-> Run: docker exec {CONTAINERS['airflow']} airflow webserver{Colors.END}")
            return False
    except Exception as e:
        print_check("Could not check webserver status", False, str(e))
        return False


def main() -> None:
    """Main entry point."""
    print_header("BATCHETL PIPELINE - AIRFLOW TROUBLESHOOTING")

    results = {
        'container': check_airflow_container(),
        'ui': check_airflow_ui(),
        'dag_file': check_dag_file(),
        'dag_content': check_dag_content(),
    }

    if results['container']:
        results['dag_in_ui'] = check_dag_in_ui()
        results['task_status'] = check_task_status()
        results['scheduler'] = check_scheduler_status()
        results['webserver'] = check_webserver_status()

    print_summary(results, "AIRFLOW TROUBLESHOOTING SUMMARY")


if __name__ == "__main__":
    main()