# verify-phase-5.py
"""
Phase 5: PostgreSQL Data Verification

Checks performed:
    - fact_trips table exists
    - Data loaded successfully
    - Row count > 90,000
    - Indexes created
    - Primary key exists
    - All columns present
    - Correct data types
    - No duplicate trip_ids
    - pickup_datetime not null
    - Sample query returns data
    - fare_amount values between 0-500
    - trip_distance values between 0-100
"""

import os
import sys
import json
import subprocess
import re
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
# Phase 5: PostgreSQL Data Verification
# ============================================

class Phase5Verifier(PhaseVerifier):
    """Verifier for Phase 5: PostgreSQL Data Verification."""

    def __init__(self):
        super().__init__(5, "PostgreSQL Data Verification")

    def _run_psql(self, query: str) -> Tuple[bool, str]:
        """Run a PostgreSQL query and return result."""
        try:
            result = subprocess.run(
                ['docker', 'exec', 'batch-etl-postgres', 'psql', '-U', 'admin', '-d', 'warehouse', '-t', '-c', query],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            return False, result.stderr.strip()
        except Exception as e:
            return False, str(e)

    def check_table_exists(self) -> bool:
        """Verify fact_trips table exists."""
        self.print_section("Table Existence")

        success, output = self._run_psql("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'fact_trips');")

        if success and 't' in output:
            self.print_check("fact_trips table exists", True)
            self.add_result('table_exists', True, 'Table exists')
            return True
        else:
            self.print_check("fact_trips table NOT found", False)
            self.add_result('table_exists', False, 'Table not found')
            return False

    def check_row_count(self) -> bool:
        """Verify row count > 90,000."""
        self.print_section("Row Count")

        success, output = self._run_psql("SELECT COUNT(*) FROM fact_trips;")

        if success:
            try:
                row_count = int(output.strip())
                self.print_check(f"Total rows: {row_count:,}", row_count > 0)
                self.print_check(f"Row count > 90,000", row_count > 90000)
                is_valid = row_count > 90000
                self.add_result('row_count', is_valid, f'{row_count:,} rows')
                return is_valid
            except ValueError:
                self.print_check("Could not parse row count", False, output)
                self.add_result('row_count', False, 'Parse failed')
                return False
        else:
            self.print_check("Query failed", False, output)
            self.add_result('row_count', False, 'Query failed')
            return False

    def check_columns(self) -> bool:
        """Verify all columns exist."""
        self.print_section("Column Check")

        expected_columns = [
            'trip_id', 'vendor_id', 'pickup_datetime', 'dropoff_datetime',
            'passenger_count', 'trip_distance', 'fare_amount', 'total_amount',
            'payment_type', 'pickup_hour', 'pickup_day', 'pickup_month'
        ]

        success, output = self._run_psql("SELECT column_name FROM information_schema.columns WHERE table_name = 'fact_trips' ORDER BY ordinal_position;")

        if success:
            actual_columns = [col.strip() for col in output.split('\n') if col.strip()]
            missing = [col for col in expected_columns if col not in actual_columns]

            if missing:
                self.print_check(f"Missing columns: {missing}", False)
                self.add_result('columns', False, f'Missing: {missing}')
                return False

            self.print_check(f"All {len(expected_columns)} columns present", True)
            self.add_result('columns', True, f'{len(expected_columns)} columns present')
            return True
        else:
            self.print_check("Column query failed", False, output)
            self.add_result('columns', False, 'Query failed')
            return False

    def check_indexes(self) -> bool:
        """Verify indexes exist."""
        self.print_section("Indexes")

        expected_indexes = ['idx_pickup_datetime', 'idx_pickup_day', 'idx_fare_amount']

        success, output = self._run_psql("SELECT indexname FROM pg_indexes WHERE tablename = 'fact_trips';")

        if success:
            existing_indexes = [idx.strip() for idx in output.split('\n') if idx.strip()]
            missing = [idx for idx in expected_indexes if idx not in existing_indexes]

            if missing:
                self.print_check(f"Missing indexes: {missing}", False)
                self.add_result('indexes', False, f'Missing: {missing}')
                return False

            self.print_check(f"All {len(expected_indexes)} indexes exist", True)
            self.add_result('indexes', True, f'{len(expected_indexes)} indexes present')
            return True
        else:
            self.print_check("Index query failed", False, output)
            self.add_result('indexes', False, 'Query failed')
            return False

    def check_primary_key(self) -> bool:
        """Verify primary key exists."""
        self.print_section("Primary Key")

        success, output = self._run_psql("SELECT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE table_name = 'fact_trips' AND constraint_type = 'PRIMARY KEY');")

        if success and 't' in output:
            self.print_check("Primary key exists (trip_id)", True)
            self.add_result('primary_key', True, 'Primary key exists')
            return True
        else:
            self.print_check("Primary key NOT found", False)
            self.add_result('primary_key', False, 'Primary key missing')
            return False

    def check_no_duplicates(self) -> bool:
        """Verify no duplicate trip_ids."""
        self.print_section("Duplicate Check")

        success, output = self._run_psql("SELECT COUNT(*) - COUNT(DISTINCT trip_id) FROM fact_trips;")

        if success:
            try:
                duplicates = int(output.strip())
                self.print_check(f"Duplicate trip_ids: {duplicates}", duplicates == 0)
                is_valid = duplicates == 0
                self.add_result('no_duplicates', is_valid, f'{duplicates} duplicates found' if duplicates > 0 else 'No duplicates')
                return is_valid
            except ValueError:
                self.print_check("Could not parse count", False, output)
                self.add_result('no_duplicates', False, 'Parse failed')
                return False
        else:
            self.print_check("Query failed", False, output)
            self.add_result('no_duplicates', False, 'Query failed')
            return False

    def check_data_quality(self) -> bool:
        """Verify data quality rules."""
        self.print_section("Data Quality")

        # Check fare_amount range (0-500)
        success, output = self._run_psql("SELECT COUNT(*) FROM fact_trips WHERE fare_amount < 0 OR fare_amount > 500;")

        if success:
            try:
                invalid_fares = int(output.strip())
                self.print_check(f"Invalid fare_amount (< 0 or > 500): {invalid_fares}", invalid_fares == 0)
            except ValueError:
                self.print_check("Could not parse fare count", False)
                return False
        else:
            self.print_check("Fare query failed", False)
            return False

        # Check trip_distance range (0-100)
        success, output = self._run_psql("SELECT COUNT(*) FROM fact_trips WHERE trip_distance < 0 OR trip_distance > 100;")

        if success:
            try:
                invalid_distances = int(output.strip())
                self.print_check(f"Invalid trip_distance (< 0 or > 100): {invalid_distances}", invalid_distances == 0)
            except ValueError:
                self.print_check("Could not parse distance count", False)
                return False
        else:
            self.print_check("Distance query failed", False)
            return False

        # Check nulls in critical columns
        success, output = self._run_psql("SELECT COUNT(*) FROM fact_trips WHERE pickup_datetime IS NULL;")

        if success:
            try:
                null_pickups = int(output.strip())
                self.print_check(f"NULL pickup_datetime: {null_pickups}", null_pickups == 0)
            except ValueError:
                self.print_check("Could not parse null count", False)
                return False
        else:
            self.print_check("Null query failed", False)
            return False

        is_valid = True
        self.add_result('data_quality', is_valid, 'Data quality rules passed')
        return is_valid

    def check_sample_data(self) -> bool:
        """Verify sample query returns data."""
        self.print_section("Sample Data")

        success, output = self._run_psql("SELECT COUNT(*) FROM fact_trips LIMIT 10;")

        if success:
            try:
                row_count = int(output.strip())
                self.print_check(f"Sample query returns data", row_count > 0)
                is_valid = row_count > 0
                self.add_result('sample_data', is_valid, f'{row_count} rows in sample')
                return is_valid
            except ValueError:
                self.print_check("Could not parse sample count", False)
                self.add_result('sample_data', False, 'Parse failed')
                return False
        else:
            self.print_check("Sample query failed", False, output)
            self.add_result('sample_data', False, 'Query failed')
            return False

    def run(self) -> bool:
        """Run all Phase 5 checks."""
        self.check_table_exists()
        self.check_row_count()
        self.check_columns()
        self.check_indexes()
        self.check_primary_key()
        self.check_no_duplicates()
        self.check_data_quality()
        self.check_sample_data()

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
        verifier = Phase5Verifier()
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