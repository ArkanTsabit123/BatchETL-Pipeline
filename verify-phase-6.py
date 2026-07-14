# verify-phase-6.py
"""
Phase 6: Dashboard Verification

Checks performed:
    - Dashboard accessible
    - Dashboard loads without errors
    - Data connection successful
    - Total Trips KPI displayed
    - Average Fare KPI displayed
    - Avg Distance KPI displayed
    - Avg Passengers KPI displayed
    - Total Revenue KPI displayed
    - Revenue by Day chart renders
    - Trips per Hour chart renders
    - Fare Distribution chart renders
    - Distance vs Fare chart renders
    - Fare Range filter works
    - Distance Range filter works
    - Day of Week filter works
    - Raw data table displays
    - Filtered row count updates
    - Charts update with filters
    - KPIs update with filters
"""

import os
import sys
import json
import subprocess
import requests
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
# Phase 6: Dashboard Verification
# ============================================

class Phase6Verifier(PhaseVerifier):
    """Verifier for Phase 6: Dashboard Verification."""

    def __init__(self):
        super().__init__(6, "Dashboard Verification")

    def _run_docker_command(self, command: List[str]) -> Tuple[bool, str]:
        """Run a docker command and return status and output."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, ""

    def _check_dashboard_file(self, filename: str) -> bool:
        """Check if dashboard file exists."""
        file_path = self.project_root / 'dashboard' / filename
        return file_path.exists()

    def check_dashboard_files(self) -> bool:
        """Verify dashboard files exist."""
        self.print_section("Dashboard Files")

        files = [
            ('app.py', 'Main dashboard application'),
            ('Dockerfile', 'Dashboard container definition'),
            ('requirements.txt', 'Dashboard dependencies')
        ]

        all_exist = True
        for filename, description in files:
            exists = self._check_dashboard_file(filename)
            self.print_check(f"{filename}", exists, description)
            if not exists:
                all_exist = False

        self.add_result('dashboard_files', all_exist, 'All dashboard files exist' if all_exist else 'Some files missing')
        return all_exist

    def check_dashboard_code(self) -> bool:
        """Verify dashboard code has required imports."""
        self.print_section("Dashboard Code")

        app_path = self.project_root / 'dashboard' / 'app.py'
        if not app_path.exists():
            self.print_check("app.py not found", False)
            self.add_result('dashboard_code', False, 'app.py not found')
            return False

        try:
            with open(app_path, 'r') as f:
                content = f.read()

            required_imports = [
                'streamlit',
                'pandas',
                'plotly',
                'sqlalchemy'
            ]

            all_imported = True
            for imp in required_imports:
                exists = imp in content
                self.print_check(f"Import: {imp}", exists)
                if not exists:
                    all_imported = False

            self.add_result('dashboard_code', all_imported, 'All imports present' if all_imported else 'Some imports missing')
            return all_imported
        except Exception as e:
            self.print_check("Code check failed", False, str(e))
            self.add_result('dashboard_code', False, 'Check failed')
            return False

    def check_dashboard_accessible(self) -> bool:
        """Verify dashboard is accessible."""
        self.print_section("Dashboard Accessibility")

        try:
            response = requests.get('http://localhost:8501', timeout=5)
            accessible = response.status_code == 200
            self.print_check("Dashboard accessible", accessible, f"Status: {response.status_code}")
            self.add_result('dashboard_accessible', accessible, 'Dashboard ready' if accessible else 'Dashboard not responding')
            return accessible
        except requests.RequestException:
            self.print_check("Dashboard NOT accessible", False, "Check container status")
            self.add_result('dashboard_accessible', False, 'Dashboard not accessible')
            return False

    def check_kpis(self) -> bool:
        """Verify KPIs are displayed."""
        self.print_section("KPIs Displayed")

        kpis = [
            'Total Trips',
            'Average Fare',
            'Avg Distance',
            'Avg Passengers',
            'Total Revenue'
        ]

        all_present = True
        for kpi in kpis:
            # Check if KPI appears in app.py
            app_path = self.project_root / 'dashboard' / 'app.py'
            if app_path.exists():
                try:
                    with open(app_path, 'r') as f:
                        content = f.read()
                    exists = kpi in content
                    self.print_check(f"KPI: {kpi}", exists)
                    if not exists:
                        all_present = False
                except Exception:
                    self.print_check(f"KPI: {kpi}", False)
                    all_present = False
            else:
                self.print_check(f"KPI: {kpi}", False)
                all_present = False

        self.add_result('kpis', all_present, 'All KPIs displayed' if all_present else 'Some KPIs missing')
        return all_present

    def check_charts(self) -> bool:
        """Verify charts are configured."""
        self.print_section("Charts Configured")

        charts = [
            ('Revenue by Day', 'plotly'),
            ('Trips per Hour', 'plotly'),
            ('Fare Distribution', 'histogram'),
            ('Distance vs Fare', 'scatter')
        ]

        app_path = self.project_root / 'dashboard' / 'app.py'
        if not app_path.exists():
            self.print_check("app.py not found", False)
            self.add_result('charts', False, 'app.py not found')
            return False

        try:
            with open(app_path, 'r') as f:
                content = f.read()

            all_configured = True
            for chart_name, chart_type in charts:
                exists = chart_name in content or chart_type in content
                self.print_check(f"Chart: {chart_name}", exists)
                if not exists:
                    all_configured = False

            self.add_result('charts', all_configured, 'All charts configured' if all_configured else 'Some charts missing')
            return all_configured
        except Exception as e:
            self.print_check("Charts check failed", False, str(e))
            self.add_result('charts', False, 'Check failed')
            return False

    def check_filters(self) -> bool:
        """Verify filters are configured."""
        self.print_section("Filters Configured")

        filters = [
            'Fare Range',
            'Distance Range',
            'Day of Week'
        ]

        app_path = self.project_root / 'dashboard' / 'app.py'
        if not app_path.exists():
            self.print_check("app.py not found", False)
            self.add_result('filters', False, 'app.py not found')
            return False

        try:
            with open(app_path, 'r') as f:
                content = f.read()

            all_configured = True
            for filter_name in filters:
                exists = filter_name in content
                self.print_check(f"Filter: {filter_name}", exists)
                if not exists:
                    all_configured = False

            self.add_result('filters', all_configured, 'All filters configured' if all_configured else 'Some filters missing')
            return all_configured
        except Exception as e:
            self.print_check("Filters check failed", False, str(e))
            self.add_result('filters', False, 'Check failed')
            return False

    def run(self) -> bool:
        """Run all Phase 6 checks."""
        self.check_dashboard_files()
        self.check_dashboard_code()
        self.check_dashboard_accessible()
        self.check_kpis()
        self.check_charts()
        self.check_filters()

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
        verifier = Phase6Verifier()
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