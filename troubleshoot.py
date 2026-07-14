# troubleshoot.py
"""
BatchETL Pipeline - Troubleshooting Main Entry Point

This script provides a menu to run specific troubleshooting modules
or run all checks at once.

Usage:
    python troubleshoot.py          # Show menu
    python troubleshoot.py --all    # Run all checks
    python troubleshoot.py --docker # Run Docker checks only
    python troubleshoot.py --airflow # Run Airflow checks only
    python troubleshoot.py --postgres # Run PostgreSQL checks only
    python troubleshoot.py --dashboard # Run Dashboard checks only
    python troubleshoot.py --network # Run Network checks only
"""

import sys
import subprocess
import os
from pathlib import Path
from typing import List, Dict, Optional


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


def print_menu() -> None:
    """Display troubleshooting menu."""
    print_header("BATCHETL PIPELINE - TROUBLESHOOTING MENU")

    print("Select a troubleshooting module:\n")
    print(f"  {Colors.BOLD}1.{Colors.END} Docker & Containers      - Check Docker daemon and container status")
    print(f"  {Colors.BOLD}2.{Colors.END} Airflow                 - Check Airflow DAG, UI, and scheduler")
    print(f"  {Colors.BOLD}3.{Colors.END} PostgreSQL             - Check database connection, tables, and data")
    print(f"  {Colors.BOLD}4.{Colors.END} Dashboard              - Check Streamlit dashboard and connectivity")
    print(f"  {Colors.BOLD}5.{Colors.END} Network & Ports        - Check ports and network connectivity")
    print(f"  {Colors.BOLD}6.{Colors.END} Run All Checks         - Run all troubleshooting modules")
    print(f"  {Colors.BOLD}0.{Colors.END} Exit                   - Exit troubleshooting")
    print()


def run_module(module: str) -> None:
    """Run a specific troubleshooting module."""
    script_map = {
        'docker': 'troubleshoot_docker.py',
        'airflow': 'troubleshoot_airflow.py',
        'postgres': 'troubleshoot_postgres.py',
        'dashboard': 'troubleshoot_dashboard.py',
        'network': 'troubleshoot_network.py',
    }

    if module not in script_map:
        print(f"{Colors.RED}Unknown module: {module}{Colors.END}")
        return

    script = script_map[module]
    script_path = Path(__file__).parent / script

    if not script_path.exists():
        print(f"{Colors.RED}Script not found: {script}{Colors.END}")
        print(f"{Colors.YELLOW}Please ensure all troubleshooting scripts are in the same directory.{Colors.END}")
        return

    try:
        result = subprocess.run([sys.executable, str(script_path)], capture_output=False)
        if result.returncode != 0:
            print(f"{Colors.YELLOW}Module {module} completed with warnings or errors.{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}Error running module {module}: {str(e)}{Colors.END}")


def run_all() -> None:
    """Run all troubleshooting modules sequentially."""
    print_header("RUNNING ALL TROUBLESHOOTING CHECKS")

    modules = ['docker', 'airflow', 'postgres', 'dashboard', 'network']
    failed = []

    for module in modules:
        print(f"\n{Colors.CYAN}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}Running: {module.upper()}{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")

        script = f'troubleshoot_{module}.py'
        script_path = Path(__file__).parent / script

        if not script_path.exists():
            print(f"{Colors.RED}Script not found: {script}{Colors.END}")
            failed.append(module)
            continue

        try:
            result = subprocess.run([sys.executable, str(script_path)], capture_output=False)
            if result.returncode != 0:
                failed.append(module)
        except Exception as e:
            print(f"{Colors.RED}Error: {str(e)}{Colors.END}")
            failed.append(module)

    print_header("TROUBLESHOOTING SUMMARY")

    if failed:
        print(f"{Colors.YELLOW}Modules with issues: {', '.join(failed)}{Colors.END}")
        print(f"{Colors.YELLOW}Please check the logs above for details.{Colors.END}")
        sys.exit(1)
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}All checks passed! No issues detected.{Colors.END}")
        sys.exit(0)


def main() -> None:
    """Main entry point."""
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg == '--all' or arg == '-a':
            run_all()
            return
        elif arg == '--docker' or arg == '-d':
            run_module('docker')
            return
        elif arg == '--airflow' or arg == '-a':
            run_module('airflow')
            return
        elif arg == '--postgres' or arg == '-p':
            run_module('postgres')
            return
        elif arg == '--dashboard' or arg == '-db':
            run_module('dashboard')
            return
        elif arg == '--network' or arg == '-n':
            run_module('network')
            return
        elif arg == '--help' or arg == '-h':
            print("Usage: python troubleshoot.py [OPTION]")
            print("\nOptions:")
            print("  --all, -a      Run all troubleshooting checks")
            print("  --docker, -d   Run Docker checks only")
            print("  --airflow, -a  Run Airflow checks only")
            print("  --postgres, -p Run PostgreSQL checks only")
            print("  --dashboard, -db Run Dashboard checks only")
            print("  --network, -n  Run Network checks only")
            print("  --help, -h     Show this help message")
            print("\nWithout options, shows interactive menu.")
            return

    # Interactive menu
    while True:
        print_menu()
        choice = input(f"{Colors.BOLD}Enter your choice (0-6): {Colors.END}").strip()

        if choice == '0':
            print(f"\n{Colors.CYAN}Exiting troubleshooting. Goodbye!{Colors.END}")
            sys.exit(0)
        elif choice == '1':
            run_module('docker')
        elif choice == '2':
            run_module('airflow')
        elif choice == '3':
            run_module('postgres')
        elif choice == '4':
            run_module('dashboard')
        elif choice == '5':
            run_module('network')
        elif choice == '6':
            run_all()
        else:
            print(f"{Colors.RED}Invalid choice. Please enter 0-6.{Colors.END}")


if __name__ == "__main__":
    main()