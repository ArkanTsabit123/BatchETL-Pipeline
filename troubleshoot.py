# troubleshoot.py

"""
BatchETL Pipeline - Troubleshooting Main Entry Point

Usage:
    python troubleshoot.py              # Show menu
    python troubleshoot.py --all        # Run all checks
    python troubleshoot.py --docker     # Run Docker checks only
    python troubleshoot.py --airflow    # Run Airflow checks only
    python troubleshoot.py --postgres   # Run PostgreSQL checks only
    python troubleshoot.py --dashboard  # Run Dashboard checks only
    python troubleshoot.py --network    # Run Network checks only
"""

import sys
import subprocess
from pathlib import Path

from troubleshoot_utils import Colors, print_header, print_error, print_success
from troubleshoot_config import VERIFICATION_SCRIPTS


def print_menu() -> None:
    """Display troubleshooting menu."""
    print_header("BATCHETL PIPELINE - TROUBLESHOOTING MENU")

    print("Select a troubleshooting module:\n")
    print(f"  {Colors.BOLD}1.{Colors.END} Docker and Containers")
    print(f"  {Colors.BOLD}2.{Colors.END} Airflow")
    print(f"  {Colors.BOLD}3.{Colors.END} PostgreSQL")
    print(f"  {Colors.BOLD}4.{Colors.END} Dashboard")
    print(f"  {Colors.BOLD}5.{Colors.END} Network and Ports")
    print(f"  {Colors.BOLD}6.{Colors.END} Run All Troubleshooting")
    print(f"  {Colors.BOLD}7.{Colors.END} Run All Verifications")
    print(f"  {Colors.BOLD}8.{Colors.END} Show System Information")
    print(f"  {Colors.BOLD}0.{Colors.END} Exit")
    print()


def print_system_info() -> None:
    """Display system information."""
    print_header("SYSTEM INFORMATION")

    import platform

    print(f"  {Colors.BOLD}OS:{Colors.END} {platform.system()} {platform.release()}")
    print(f"  {Colors.BOLD}Python:{Colors.END} {platform.python_version()}")
    print(f"  {Colors.BOLD}Working Directory:{Colors.END} {Path.cwd()}")

    from troubleshoot_utils import run_command, get_docker_container_status
    from troubleshoot_config import CONTAINERS

    success, version = run_command(['docker', '--version'])
    print(f"  {Colors.BOLD}Docker:{Colors.END} {version if success else 'Not installed'}")

    for name, container in CONTAINERS.items():
        is_running, status = get_docker_container_status(container)
        icon = "PASS" if is_running else "FAIL"
        color = Colors.GREEN if is_running else Colors.RED
        print(f"  {color}{Colors.BOLD}{container}:{Colors.END} {status}")


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
        print_error(f"Unknown module: {module}")
        return

    script = script_map[module]
    script_path = Path(__file__).parent / script

    if not script_path.exists():
        print_error(f"Script not found: {script}")
        print(f"     {Colors.YELLOW}-> Ensure all scripts are in the same directory.{Colors.END}")
        return

    try:
        result = subprocess.run([sys.executable, str(script_path)], capture_output=False)
        if result.returncode != 0:
            print_warning(f"Module {module} completed with warnings or errors.")
    except Exception as e:
        print_error(f"Error running module {module}: {str(e)}")


def run_all_troubleshooting() -> None:
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
            print_error(f"Script not found: {script}")
            failed.append(module)
            continue

        try:
            result = subprocess.run([sys.executable, str(script_path)], capture_output=False)
            if result.returncode != 0:
                failed.append(module)
        except Exception as e:
            print_error(f"Error: {str(e)}")
            failed.append(module)

    print_header("TROUBLESHOOTING SUMMARY")

    if failed:
        print(f"{Colors.YELLOW}Modules with issues: {', '.join(failed)}{Colors.END}")
        print(f"{Colors.YELLOW}Check the logs above for details.{Colors.END}")
        sys.exit(1)
    else:
        print_success("All troubleshooting checks passed.")
        sys.exit(0)


def run_all_verifications() -> None:
    """Run all verification scripts."""
    print_header("RUNNING ALL VERIFICATION SCRIPTS")

    failed = []

    for script in VERIFICATION_SCRIPTS:
        script_path = Path(__file__).parent / script
        if not script_path.exists():
            print_warning(f"Script not found: {script}")
            continue

        print(f"\n{Colors.BOLD}Running: {script}{Colors.END}")
        try:
            result = subprocess.run([sys.executable, str(script_path)], capture_output=False)
            if result.returncode != 0:
                failed.append(script)
        except Exception as e:
            print_error(f"Error running {script}: {str(e)}")
            failed.append(script)

    print_header("VERIFICATION SUMMARY")

    if failed:
        print(f"{Colors.YELLOW}Failed scripts: {', '.join(failed)}{Colors.END}")
        sys.exit(1)
    else:
        print_success("All verification scripts passed.")
        sys.exit(0)


def show_help() -> None:
    """Show help message."""
    print("""
BatchETL Pipeline - Troubleshooting

Usage:
    python troubleshoot.py              # Show interactive menu
    python troubleshoot.py [OPTION]     # Run specific checks

Options:
    --all, -a       Run all troubleshooting checks
    --verification, -v Run all verification checks
    --docker, -d    Run Docker checks only
    --airflow, -af  Run Airflow checks only
    --postgres, -p  Run PostgreSQL checks only
    --dashboard, -db Run Dashboard checks only
    --network, -n   Run Network checks only
    --info, -i      Show system information
    --help, -h      Show this help message
    """)


def main() -> None:
    """Main entry point."""
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg in ['--all', '-a']:
            run_all_troubleshooting()
        elif arg in ['--verification', '-v']:
            run_all_verifications()
        elif arg in ['--docker', '-d']:
            run_module('docker')
        elif arg in ['--airflow', '-af']:
            run_module('airflow')
        elif arg in ['--postgres', '-p']:
            run_module('postgres')
        elif arg in ['--dashboard', '-db']:
            run_module('dashboard')
        elif arg in ['--network', '-n']:
            run_module('network')
        elif arg in ['--info', '-i']:
            print_system_info()
        elif arg in ['--help', '-h']:
            show_help()
        else:
            print_error(f"Unknown option: {arg}")
            show_help()
            sys.exit(1)
        return

    while True:
        print_menu()
        choice = input(f"{Colors.BOLD}Enter your choice (0-8): {Colors.END}").strip()

        if choice == '0':
            print(f"\n{Colors.CYAN}Exiting troubleshooting.{Colors.END}")
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
            run_all_troubleshooting()
        elif choice == '7':
            run_all_verifications()
        elif choice == '8':
            print_system_info()
        else:
            print_error(f"Invalid choice: {choice}. Please enter 0-8.")


if __name__ == "__main__":
    main()