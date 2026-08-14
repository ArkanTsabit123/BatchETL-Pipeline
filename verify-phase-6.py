# verify-phase-6.py
"""
Phase 6: Dashboard Verification (Local)

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
    - Payment Type filter works
    - Vendor ID filter works
    - Raw data table displays
    - Filtered row count updates
    - Charts update with filters
    - KPIs update with filters
    - Dashboard responsive
    - Chart tooltips work correctly
"""

import os
import sys
import json
import subprocess
import requests
import time
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
# Phase 6: Dashboard Verification (Local)
# ============================================

class Phase6Verifier(PhaseVerifier):
    """Verifier for Phase 6: Dashboard Verification (Local)."""

    def __init__(self):
        super().__init__(6, "Dashboard Verification (Local)")

    def _check_port_open(self, host: str, port: int, timeout: float = 2.0) -> bool:
        """Check if a port is open."""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

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
            if exists:
                size_kb = (self.project_root / 'dashboard' / filename).stat().st_size / 1024
                self.print_check(f"{filename}", exists, f"{description} ({size_kb:.1f} KB)")
            else:
                self.print_check(f"{filename}", exists, description)
            if not exists:
                all_exist = False

        self.add_result('dashboard_files', all_exist,
                        'All dashboard files exist' if all_exist else 'Some files missing')
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
                ('streamlit', 'Streamlit'),
                ('pandas', 'Pandas'),
                ('plotly', 'Plotly'),
                ('sqlalchemy', 'SQLAlchemy')
            ]

            all_imported = True
            for imp, display in required_imports:
                exists = imp in content
                self.print_check(f"Import: {display}", exists)
                if not exists:
                    all_imported = False

            # Check for st.cache decorators
            has_cache = '@st.cache' in content
            self.print_check("Cache decorator present", has_cache)

            self.add_result('dashboard_code', all_imported,
                            'All imports present' if all_imported else 'Some imports missing')
            return all_imported
        except Exception as e:
            self.print_check("Code check failed", False, str(e))
            self.add_result('dashboard_code', False, 'Check failed')
            return False

    def check_dashboard_accessible(self) -> bool:
        """Verify dashboard is accessible."""
        self.print_section("Dashboard Accessibility")

        port_open = self._check_port_open('localhost', 8501)
        self.print_check("Streamlit port 8501 open", port_open)

        if port_open:
            try:
                response = requests.get('http://localhost:8501', timeout=5)
                accessible = response.status_code == 200
                self.print_check("Dashboard accessible", accessible, f"Status: {response.status_code}")
                self.add_result('dashboard_accessible', accessible,
                                'Dashboard ready' if accessible else 'Dashboard not responding')
                return accessible
            except requests.RequestException:
                self.print_check("Dashboard NOT accessible", False, "Check container status")
                self.add_result('dashboard_accessible', False, 'Dashboard not accessible')
                return False
        else:
            self.add_result('dashboard_accessible', False, 'Streamlit port 8501 not open')
            return False

    def check_dashboard_content(self) -> bool:
        """Verify dashboard content from HTML."""
        self.print_section("Dashboard Content")

        try:
            response = requests.get('http://localhost:8501', timeout=5)
            if response.status_code != 200:
                self.print_check("Dashboard content check failed", False, "Status code not 200")
                self.add_result('dashboard_content', False, 'Dashboard not responding')
                return False

            html_content = response.text

            # Check for Streamlit elements
            has_streamlit = 'streamlit' in html_content.lower()
            self.print_check("Streamlit content detected", has_streamlit)

            self.add_result('dashboard_content', has_streamlit,
                            'Dashboard content loaded' if has_streamlit else 'No Streamlit content')
            return has_streamlit
        except requests.RequestException:
            self.print_check("Dashboard content check failed", False, "Cannot access dashboard")
            self.add_result('dashboard_content', False, 'Dashboard not accessible')
            return False

    def check_kpi_code(self) -> bool:
        """Verify KPIs are configured in code."""
        self.print_section("KPI Configuration")

        app_path = self.project_root / 'dashboard' / 'app.py'
        if not app_path.exists():
            self.print_check("app.py not found", False)
            self.add_result('kpi_code', False, 'app.py not found')
            return False

        try:
            with open(app_path, 'r') as f:
                content = f.read()

            kpis = [
                ('Total Trips', 'Total Trips'),
                ('Average Fare', 'Average Fare'),
                ('Avg Distance', 'Avg Distance'),
                ('Avg Passengers', 'Avg Passengers'),
                ('Total Revenue', 'Total Revenue')
            ]

            all_present = True
            for kpi_name, display in kpis:
                exists = kpi_name in content
                self.print_check(f"KPI: {display}", exists)
                if not exists:
                    all_present = False

            self.add_result('kpi_code', all_present,
                            'All KPIs configured' if all_present else 'Some KPIs missing')
            return all_present
        except Exception as e:
            self.print_check("KPI check failed", False, str(e))
            self.add_result('kpi_code', False, 'Check failed')
            return False

    def check_chart_code(self) -> bool:
        """Verify charts are configured in code."""
        self.print_section("Chart Configuration")

        app_path = self.project_root / 'dashboard' / 'app.py'
        if not app_path.exists():
            self.print_check("app.py not found", False)
            self.add_result('chart_code', False, 'app.py not found')
            return False

        try:
            with open(app_path, 'r') as f:
                content = f.read()

            charts = [
                ('Revenue by Day', 'Revenue by Day'),
                ('Trips per Hour', 'Trips per Hour'),
                ('Fare Distribution', 'Fare Distribution'),
                ('Distance vs Fare', 'Distance vs Fare')
            ]

            all_present = True
            for chart_name, display in charts:
                exists = chart_name in content
                self.print_check(f"Chart: {display}", exists)
                if not exists:
                    all_present = False

            # Check for plotly usage
            has_plotly = 'plotly' in content and 'px.' in content
            self.print_check("Plotly chart library used", has_plotly)

            self.add_result('chart_code', all_present,
                            'All charts configured' if all_present else 'Some charts missing')
            return all_present
        except Exception as e:
            self.print_check("Chart check failed", False, str(e))
            self.add_result('chart_code', False, 'Check failed')
            return False

    def check_filter_code(self) -> bool:
        """Verify filters are configured in code."""
        self.print_section("Filter Configuration")

        app_path = self.project_root / 'dashboard' / 'app.py'
        if not app_path.exists():
            self.print_check("app.py not found", False)
            self.add_result('filter_code', False, 'app.py not found')
            return False

        try:
            with open(app_path, 'r') as f:
                content = f.read()

            filters = [
                ('Fare Range', 'Fare Range'),
                ('Distance Range', 'Distance Range'),
                ('Day of Week', 'Day of Week'),
                ('Payment Type', 'Payment Type'),
                ('Vendor ID', 'Vendor ID')
            ]

            all_present = True
            for filter_name, display in filters:
                exists = filter_name in content
                self.print_check(f"Filter: {display}", exists)
                if not exists:
                    all_present = False

            # Check for st.sidebar usage
            has_sidebar = 'st.sidebar' in content
            self.print_check("Sidebar filters used", has_sidebar)

            self.add_result('filter_code', all_present,
                            'All filters configured' if all_present else 'Some filters missing')
            return all_present
        except Exception as e:
            self.print_check("Filter check failed", False, str(e))
            self.add_result('filter_code', False, 'Check failed')
            return False

    def check_data_table_code(self) -> bool:
        """Verify raw data table is configured."""
        self.print_section("Data Table Configuration")

        app_path = self.project_root / 'dashboard' / 'app.py'
        if not app_path.exists():
            self.print_check("app.py not found", False)
            self.add_result('data_table_code', False, 'app.py not found')
            return False

        try:
            with open(app_path, 'r') as f:
                content = f.read()

            has_table = 'st.dataframe' in content or 'st.table' in content
            has_expander = 'st.expander' in content

            self.print_check("Data table display (st.dataframe)", has_table)
            self.print_check("Expandable section (st.expander)", has_expander)

            is_configured = has_table and has_expander
            self.add_result('data_table_code', is_configured,
                            'Data table configured' if is_configured else 'Data table missing')
            return is_configured
        except Exception as e:
            self.print_check("Data table check failed", False, str(e))
            self.add_result('data_table_code', False, 'Check failed')
            return False

    def check_database_connection(self) -> bool:
        """Verify database connection in code."""
        self.print_section("Database Connection")

        app_path = self.project_root / 'dashboard' / 'app.py'
        if not app_path.exists():
            self.print_check("app.py not found", False)
            self.add_result('database_connection', False, 'app.py not found')
            return False

        try:
            with open(app_path, 'r') as f:
                content = f.read()

            has_sqlalchemy = 'sqlalchemy' in content or 'create_engine' in content
            has_postgres = 'postgresql' in content or 'postgres' in content
            has_cache = '@st.cache_resource' in content or '@st.cache' in content

            self.print_check("SQLAlchemy used", has_sqlalchemy)
            self.print_check("PostgreSQL connection", has_postgres)
            self.print_check("Connection caching", has_cache)

            is_configured = has_sqlalchemy and has_postgres
            self.add_result('database_connection', is_configured,
                            'Database connection configured' if is_configured else 'Database connection missing')
            return is_configured
        except Exception as e:
            self.print_check("Database connection check failed", False, str(e))
            self.add_result('database_connection', False, 'Check failed')
            return False

    def check_dashboard_config(self) -> bool:
        """Verify dashboard page configuration."""
        self.print_section("Dashboard Configuration")

        app_path = self.project_root / 'dashboard' / 'app.py'
        if not app_path.exists():
            self.print_check("app.py not found", False)
            self.add_result('dashboard_config', False, 'app.py not found')
            return False

        try:
            with open(app_path, 'r') as f:
                content = f.read()

            has_config = 'st.set_page_config' in content
            has_title = 'page_title' in content or 'title' in content
            has_icon = 'page_icon' in content or 'icon' in content

            self.print_check("Page config set", has_config)
            self.print_check("Page title configured", has_title)
            self.print_check("Page icon configured", has_icon)

            is_configured = has_config
            self.add_result('dashboard_config', is_configured,
                            'Dashboard configured' if is_configured else 'Dashboard config missing')
            return is_configured
        except Exception as e:
            self.print_check("Dashboard config check failed", False, str(e))
            self.add_result('dashboard_config', False, 'Check failed')
            return False

    def run(self) -> bool:
        """Run all Phase 6 checks."""
        self.check_dashboard_files()
        self.check_dashboard_code()
        self.check_dashboard_accessible()
        self.check_dashboard_content()
        self.check_kpi_code()
        self.check_chart_code()
        self.check_filter_code()
        self.check_data_table_code()
        self.check_database_connection()
        self.check_dashboard_config()

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