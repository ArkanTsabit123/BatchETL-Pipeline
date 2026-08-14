# troubleshoot_utils.py

"""
BatchETL Pipeline - Troubleshooting Utilities

Shared utility functions for all troubleshooting scripts.
"""

import subprocess
import sys
import socket
import requests
import shutil
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Optional, Dict, Any


class Colors:
    """Terminal color codes."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str, char: str = '=') -> None:
    """Print formatted header."""
    print(f"\n{Colors.CYAN}{char * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.CYAN}{char * 60}{Colors.END}\n")


def print_check(text: str, status: bool, detail: str = "") -> None:
    """Print check result with appropriate color."""
    icon = "PASS" if status else "FAIL"
    color = Colors.GREEN if status else Colors.RED
    if detail:
        print(f"  {color}{icon} {text}{Colors.END}")
        print(f"     {Colors.CYAN}-> {detail}{Colors.END}")
    else:
        print(f"  {color}{icon} {text}{Colors.END}")


def print_warning(text: str, detail: str = "") -> None:
    """Print warning message."""
    print(f"  {Colors.YELLOW}WARN {text}{Colors.END}")
    if detail:
        print(f"     {Colors.CYAN}-> {detail}{Colors.END}")


def print_success(text: str, detail: str = "") -> None:
    """Print success message."""
    print(f"  {Colors.GREEN}PASS {text}{Colors.END}")
    if detail:
        print(f"     {Colors.CYAN}-> {detail}{Colors.END}")


def print_error(text: str, detail: str = "") -> None:
    """Print error message."""
    print(f"  {Colors.RED}FAIL {text}{Colors.END}")
    if detail:
        print(f"     {Colors.CYAN}-> {detail}{Colors.END}")


def run_command(command: List[str], timeout: int = 30) -> Tuple[bool, str]:
    """Run a shell command and return status and output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return False, f"Command not found: {command[0]}"
    except Exception as e:
        return False, str(e)


def run_docker_command(command: List[str], timeout: int = 30) -> Tuple[bool, str]:
    """Run a docker command."""
    return run_command(['docker'] + command, timeout)


def run_psql(query: str, container: str = 'batch-etl-postgres',
             user: str = 'admin', db: str = 'warehouse',
             timeout: int = 30) -> Tuple[bool, str]:
    """Run a PostgreSQL query via docker exec."""
    return run_command([
        'docker', 'exec', container,
        'psql', '-U', user, '-d', db,
        '-t', '-c', query
    ], timeout)


def run_airflow_command(command: List[str], container: str = 'batch-etl-airflow',
                        timeout: int = 30) -> Tuple[bool, str]:
    """Run an Airflow command inside the container."""
    return run_command([
        'docker', 'exec', container,
        'airflow'
    ] + command, timeout)


def check_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_url(url: str, timeout: int = 10) -> Tuple[bool, int, str]:
    """Check if a URL is accessible."""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200, response.status_code, response.text[:200]
    except requests.ConnectionError:
        return False, 0, "Connection refused"
    except requests.Timeout:
        return False, 0, "Connection timeout"
    except Exception as e:
        return False, 0, str(e)


def check_file_exists(file_path: str) -> Tuple[bool, Dict[str, Any]]:
    """Check if a file exists and return metadata."""
    path = Path(file_path)
    if path.exists():
        return True, {
            'size_kb': path.stat().st_size / 1024,
            'path': str(path),
            'modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat()
        }
    return False, {}


def get_docker_container_status(container_name: str) -> Tuple[bool, str]:
    """Get Docker container status."""
    success, output = run_docker_command([
        'ps', '--filter', f'name={container_name}',
        '--format', '{{.Status}}'
    ])
    if success and output:
        return True, output
    return False, "not running"


def get_docker_container_exists(container_name: str) -> bool:
    """Check if Docker container exists."""
    success, output = run_docker_command([
        'ps', '-a', '--filter', f'name={container_name}',
        '--format', '{{.Status}}'
    ])
    return success and bool(output)


def get_container_logs(container_name: str, lines: int = 20) -> Tuple[bool, str]:
    """Get container logs."""
    return run_docker_command(['logs', '--tail', str(lines), container_name])


def check_file_permissions(file_path: str) -> bool:
    """Check if file is readable and writable."""
    path = Path(file_path)
    if not path.exists():
        return False
    return os.access(str(path), os.R_OK) and os.access(str(path), os.W_OK)


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def get_timestamp() -> str:
    """Get current timestamp as string."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def validate_json_output(output: str) -> Tuple[bool, Any]:
    """Validate and parse JSON output."""
    try:
        data = json.loads(output)
        return True, data
    except json.JSONDecodeError:
        return False, None


def check_disk_space(path: str = '.') -> Tuple[bool, Dict[str, Any]]:
    """Check disk space available at path."""
    try:
        usage = shutil.disk_usage(path)
        free_gb = usage.free / (1024 ** 3)
        total_gb = usage.total / (1024 ** 3)
        used_gb = usage.used / (1024 ** 3)
        return True, {
            'free_gb': free_gb,
            'total_gb': total_gb,
            'used_gb': used_gb,
            'percent_used': round((usage.used / usage.total) * 100, 1)
        }
    except Exception:
        return False, {}


def print_summary(results: Dict[str, bool], title: str = "SUMMARY") -> None:
    """Print a summary of results."""
    print_header(title)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n  Total Checks: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {total - passed}")
    print(f"  Success Rate: {round((passed / total * 100) if total > 0 else 0, 1)}%")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All checks passed.{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some checks failed.{Colors.END}")
        print(f"{Colors.YELLOW}Fix the issues above before proceeding.{Colors.END}")
        sys.exit(1)