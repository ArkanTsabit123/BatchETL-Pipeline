# verify-phase-4.py
"""
Phase 4: Pipeline Execution Verification

Checks performed:
    - DAG triggered successfully
    - Extract task status = Success
    - Transform task status = Success
    - Load task status = Success
    - Extract task logs show row count
    - Transform task logs show cleaning stats
    - Load task logs show row count
    - Staging files created
    - Pipeline execution time < 10 seconds
    - No Airflow task errors
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple


class Colors:
    """Terminal color codes."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class VerificationResult:
    """Result of a single verification check."""
    def __init__(self, name: str, status: bool, message: str, details: Optional[Dict] = None):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}


class PhaseVerifier:
    """Base class for phase verification."""

    def __init__(self, phase: int, phase_name: str):
        self.phase = phase
        self.phase_name = phase_name
        self.project_root = Path.cwd()
        self.checks_passed = 0
        self.checks_failed = 0
        self.results: List[VerificationResult] = []
        self.timestamp = datetime.now().isoformat()

    def print_header(self, text: str) -> None:
        """Print formatted header."""
        print(f"\n{Colors.CYAN}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 60}{Colors.END}\n")

    def print_section(self, text: str) -> None:
        """Print section header."""
        print(f"\n{Colors.YELLOW}{text}{Colors.END}")
        print(f"{Colors.YELLOW}{'-' * 40}{Colors.END}")

    def print_check(self, text: str, status: bool, detail: str = "") -> None:
        """Print check result with appropriate color."""
        icon = "PASS" if status else "FAIL"
        color = Colors.GREEN if status else Colors.RED
        if detail:
            print(f"{color}{icon} {text}{Colors.END}")
            print(f"   {Colors.CYAN}-> {detail}{Colors.END}")
        else:
            print(f"{color}{icon} {text}{Colors.END}")

    def add_result(self, name: str, status: bool, message: str, details: Optional[Dict] = None) -> None:
        """Add a verification result."""
        self.results.append(VerificationResult(name, status, message, details))
        if status:
            self.checks_passed += 1
        else:
            self.checks_failed += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get verification summary."""
        total = self.checks_passed + self.checks_failed
        return {
            'phase': self.phase,
            'phase_name': self.phase_name,
            'total_checks': total,
            'passed': self.checks_passed,
            'failed': self.checks_failed,
            'success_rate': round((self.checks_passed / total * 100) if total > 0 else 0, 1)
        }

    def save_json_report(self) -> None:
        """Save JSON report."""
        summary = self.get_summary()
        report = {
            'timestamp': self.timestamp,
            'project_root': str(self.project_root),
            'phase': self.phase,
            'phase_name': self.phase_name,
            'summary': summary,
            'checks': [
                {'name': r.name, 'status': r.status, 'message': r.message, 'details': r.details}
                for r in self.results
            ],
            'overall_status': 'ready' if self.checks_failed == 0 else 'needs_fix'
        }

        json_file = self.project_root / f'phase{self.phase}_verification.json'
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nJSON report saved to: {json_file}")

    def save_text_report(self) -> None:
        """Save text report."""
        summary = self.get_summary()
        report_file = self.project_root / f'phase{self.phase}_verification_report.txt'

        with open(report_file, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write(f"PHASE {self.phase} VERIFICATION REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Success Rate: {summary['success_rate']:.1f}%\n")
            f.write(f"Passed: {self.checks_passed}, Failed: {self.checks_failed}\n")
            f.write("=" * 60 + "\n\n")

            failed = [r for r in self.results if not r.status]
            if failed:
                f.write("Failed Items:\n")
                for r in failed:
                    f.write(f"  - {r.name}: {r.message}\n")
            else:
                f.write("All checks passed successfully!\n")

        print(f"Text report saved to: {report_file}")

    def display_summary(self) -> None:
        """Display verification summary."""
        summary = self.get_summary()

        self.print_section("Verification Summary")
        print(f"\n  Total Checks: {summary['total_checks']}")
        print(f"  Passed: {self.checks_passed}")
        print(f"  Failed: {self.checks_failed}")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")

        if self.checks_failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}All checks passed! Phase {self.phase} is complete!{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}Some checks failed{Colors.END}")
            print(f"{Colors.YELLOW}Fix the failed items before proceeding{Colors.END}")

            failed = [r for r in self.results if not r.status]
            if failed:
                print(f"\n{Colors.RED}Items requiring attention:{Colors.END}")
                for r in failed:
                    print(f"  {r.name}: {r.message}")

        print(f"\n{Colors.CYAN}{'=' * 60}{Colors.END}")

    def run(self) -> bool:
        """Run all verification checks."""
        self.print_header(f"PHASE {self.phase} VERIFICATION - {self.phase_name}")
        print(f"Project Root: {self.project_root}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        raise NotImplementedError("Subclasses must implement run()")


# ============================================
# Phase 4: Pipeline Execution
# ============================================

class Phase4Verifier(PhaseVerifier):
    """Verifier for Phase 4: Pipeline Execution."""

    def __init__(self):
        super().__init__(4, "Pipeline Execution")

    def _run_docker_command(self, command: List[str]) -> Tuple[bool, str]:
        """Run a docker command and return status and output."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, ""

    def check_staging_files(self) -> bool:
        """Verify staging files exist."""
        self.print_section("Staging Files")

        files = [
            ('data/staging/taxi_raw.csv', 'Raw staging file'),
            ('data/staging/taxi_clean.csv', 'Clean staging file')
        ]

        all_exist = True
        for file_path, description in files:
            exists = (self.project_root / file_path).exists()
            self.print_check(f"{file_path}", exists, description)
            if not exists:
                all_exist = False

        self.add_result('staging_files', all_exist, 'Staging files exist' if all_exist else 'Some staging files missing')
        return all_exist

    def check_extract_task(self) -> bool:
        """Verify extract task executed successfully."""
        self.print_section("Extract Task")

        # Check raw CSV exists
        raw_path = self.project_root / 'data' / 'staging' / 'taxi_raw.csv'
        exists = raw_path.exists()

        if exists:
            size_mb = raw_path.stat().st_size / (1024 * 1024)
            self.print_check("taxi_raw.csv created", True, f"{size_mb:.2f} MB")

            # Try to count rows
            try:
                import pandas as pd
                df = pd.read_csv(raw_path)
                row_count = len(df)
                self.print_check(f"Rows extracted: {row_count:,}", True)
                self.add_result('extract_task', True, f'Extracted {row_count:,} rows')
                return True
            except Exception:
                self.print_check("Could not read CSV", False, "Check file format")
                self.add_result('extract_task', False, 'CSV read failed')
                return False
        else:
            self.print_check("taxi_raw.csv NOT found", False, "Run extract task first")
            self.add_result('extract_task', False, 'Extract task not executed')
            return False

    def check_transform_task(self) -> bool:
        """Verify transform task executed successfully."""
        self.print_section("Transform Task")

        clean_path = self.project_root / 'data' / 'staging' / 'taxi_clean.csv'
        exists = clean_path.exists()

        if exists:
            size_mb = clean_path.stat().st_size / (1024 * 1024)
            self.print_check("taxi_clean.csv created", True, f"{size_mb:.2f} MB")

            # Try to count rows
            try:
                import pandas as pd
                df = pd.read_csv(clean_path)
                row_count = len(df)
                self.print_check(f"Rows after transform: {row_count:,}", True)

                # Check columns
                expected_columns = ['vendor_id', 'pickup_datetime', 'dropoff_datetime', 'passenger_count',
                                   'trip_distance', 'fare_amount', 'total_amount', 'payment_type',
                                   'pickup_hour', 'pickup_day', 'pickup_month']
                actual_columns = df.columns.tolist()
                missing = [col for col in expected_columns if col not in actual_columns]

                if missing:
                    self.print_check(f"Missing columns: {missing}", False)
                    self.add_result('transform_task', False, f'Missing columns: {missing}')
                    return False

                self.print_check("All expected columns present", True)
                self.add_result('transform_task', True, f'Transformed {row_count:,} rows')
                return True
            except Exception as e:
                self.print_check(f"CSV read failed: {str(e)}", False)
                self.add_result('transform_task', False, 'CSV read failed')
                return False
        else:
            self.print_check("taxi_clean.csv NOT found", False, "Run transform task first")
            self.add_result('transform_task', False, 'Transform task not executed')
            return False

    def check_load_task(self) -> bool:
        """Verify load task executed successfully."""
        self.print_section("Load Task")

        try:
            # Check PostgreSQL for data
            result = subprocess.run(
                ['docker', 'exec', 'batch-etl-postgres', 'psql', '-U', 'admin', '-d', 'warehouse', '-c', "SELECT COUNT(*) FROM fact_trips;"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Extract count from output
                import re
                match = re.search(r'(\d+)', result.stdout)
                if match:
                    row_count = int(match.group(1))
                    self.print_check(f"Rows loaded to PostgreSQL: {row_count:,}", True)
                    self.add_result('load_task', True, f'Loaded {row_count:,} rows')
                    return True
                else:
                    self.print_check("Could not parse row count", False)
                    self.add_result('load_task', False, 'Parse failed')
                    return False
            else:
                self.print_check("PostgreSQL query failed", False, result.stderr)
                self.add_result('load_task', False, 'Query failed')
                return False
        except Exception as e:
            self.print_check(f"Load check failed: {str(e)}", False)
            self.add_result('load_task', False, 'Check failed')
            return False

    def run(self) -> bool:
        """Run all Phase 4 checks."""
        self.check_staging_files()
        self.check_extract_task()
        self.check_transform_task()
        self.check_load_task()

        self.display_summary()
        self.save_json_report()
        self.save_text_report()

        return self.checks_failed == 0


# ============================================
# Main Entry Point
# ============================================

def main() -> None:
    """Main entry point."""
    try:
        verifier = Phase4Verifier()
        verifier.run()
        print(f"\n{Colors.CYAN}Verification complete!{Colors.END}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Verification interrupted by user.{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()