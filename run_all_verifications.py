# run_all_verifications.py
"""
Run All Verifications - BatchETL Pipeline

This script runs all 8 phase verification scripts sequentially
and displays a summary of results.
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


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
    """Print check result with appropriate color."""
    icon = "PASS" if status else "FAIL"
    color = Colors.GREEN if status else Colors.RED
    if detail:
        print(f"{color}{icon} {text}{Colors.END}")
        print(f"   {Colors.CYAN}-> {detail}{Colors.END}")
    else:
        print(f"{color}{icon} {text}{Colors.END}")


def get_phase_info(phase: int) -> Tuple[str, str]:
    """Get phase name and description."""
    phases = {
        1: ("Setup & Environment", "Folder structure, venv, dependencies"),
        2: ("Docker & Container Setup", "PostgreSQL, Airflow, Streamlit containers"),
        3: ("Airflow DAG Creation", "DAG syntax, tasks, dependencies"),
        4: ("Pipeline Execution", "Extract, Transform, Load tasks"),
        5: ("PostgreSQL Data Verification", "Schema, indexes, data quality"),
        6: ("Dashboard Verification", "KPIs, charts, filters"),
        7: ("Screenshots Documentation", "16 screenshots + 2 diagrams"),
        8: ("Documentation & Deployment", "README, LICENSE, Git, GitHub")
    }
    return phases.get(phase, (f"Phase {phase}", ""))


def run_verification(phase: int) -> bool:
    """Run a single phase verification script."""
    script = f"verify-phase-{phase}.py"
    phase_name, description = get_phase_info(phase)

    if not os.path.exists(script):
        print_check(f"{script} not found", False, "File missing")
        return False

    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}Phase {phase}: {phase_name}{Colors.END}")
    print(f"{Colors.CYAN}Description: {description}{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}\n")

    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=False,
            timeout=120
        )
        success = result.returncode == 0
    except subprocess.TimeoutExpired:
        print_check(f"Phase {phase} TIMEOUT", False, "Exceeded 120 seconds")
        return False
    except Exception as e:
        print_check(f"Phase {phase} ERROR", False, str(e))
        return False

    if success:
        print_check(f"Phase {phase} PASSED", True)
    else:
        print_check(f"Phase {phase} FAILED", False)

    return success


def check_verification_files() -> List[int]:
    """Check which verification files exist."""
    existing = []
    for phase in range(1, 9):
        script = f"verify-phase-{phase}.py"
        if os.path.exists(script):
            existing.append(phase)
    return existing


def main() -> None:
    """Main execution function."""
    print_header("BATCHETL PIPELINE - ALL VERIFICATIONS")

    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project: {os.getcwd()}\n")

    # Check which files exist
    existing = check_verification_files()
    print(f"Found {len(existing)} verification files: Phase {', '.join(map(str, existing))}\n")

    if not existing:
        print_check("No verification files found", False, "Run verify-phase-1.py first")
        sys.exit(1)

    results: Dict[str, bool] = {}
    phase_names: Dict[str, str] = {}

    for phase in existing:
        phase_name, _ = get_phase_info(phase)
        results[f"Phase {phase}"] = run_verification(phase)
        phase_names[f"Phase {phase}"] = phase_name

    # Summary
    print_header("VERIFICATION SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"{Colors.BOLD}Summary by Phase:{Colors.END}\n")

    for phase, status in results.items():
        icon = "✓" if status else "✗"
        color = Colors.GREEN if status else Colors.RED
        name = phase_names.get(phase, "")
        print(f"  {color}{icon} {phase}: {name}{Colors.END}")

    print(f"\n{Colors.BOLD}{'=' * 40}{Colors.END}")
    print(f"{Colors.BOLD}Total: {passed}/{total} passed{Colors.END}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All verifications passed! Project is ready!{Colors.END}")
        sys.exit(0)

    print(f"\n{Colors.YELLOW}{Colors.BOLD}Some verifications failed.{Colors.END}")
    print(f"{Colors.YELLOW}Fix the failed items before proceeding{Colors.END}")

    # Show which phases failed
    failed_phases = [p for p, s in results.items() if not s]
    if failed_phases:
        print(f"\n{Colors.RED}Failed phases: {', '.join(failed_phases)}{Colors.END}")

    sys.exit(1)


if __name__ == "__main__":
    main()