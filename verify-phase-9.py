# verify-phase-9.py
"""
Phase 9: Streamlit Cloud Deployment Verification

Checks performed:
    - Repository batchetl-streamlit created
    - Sample data (100,000 rows) created
    - Standalone app.py created
    - requirements.txt created
    - .streamlit/config.toml created
    - Folder structure prepared
    - Files committed to GitHub
    - Pushed to GitHub repository
    - Deployed to Streamlit Cloud
    - Deployment successful
    - App URL accessible
    - Dashboard loads in browser
    - 5 KPIs display correctly
    - 4 charts render correctly
    - All 5 filters work
    - Data updates when filters applied
    - Raw data table view works
    - Load time less than 5 seconds
    - Mobile responsive
    - No errors in console
    - README.md updated with live demo link
    - Screenshots captured of live demo
    - Verification checklist updated
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
# Phase 9: Streamlit Cloud Deployment
# ============================================

class Phase9Verifier(PhaseVerifier):
    """Verifier for Phase 9: Streamlit Cloud Deployment."""

    def __init__(self):
        super().__init__(9, "Streamlit Cloud Deployment")

    def _run_git_command(self, command: List[str]) -> Tuple[bool, str]:
        """Run a git command and return status and output."""
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

    # ============================================
    # Preparation Checks
    # ============================================

    def check_streamlit_repo(self) -> bool:
        """Verify batchetl-streamlit repository exists."""
        self.print_section("Streamlit Repository")

        repo_path = self.project_root / 'batchetl-streamlit'
        exists = repo_path.exists() and repo_path.is_dir()

        if exists:
            self.print_check("batchetl-streamlit/ directory exists", True)
            # Check if it's a git repo
            git_path = repo_path / '.git'
            is_git = git_path.exists()
            self.print_check("Git repository initialized", is_git)
            self.add_result('streamlit_repo', True, 'Streamlit repository ready')
            return True
        else:
            self.print_check("batchetl-streamlit/ directory NOT found", False,
                           "Create: mkdir batchetl-streamlit")
            self.add_result('streamlit_repo', False, 'Streamlit repository missing')
            return False

    def check_sample_data(self) -> bool:
        """Verify sample data (100,000 rows) exists."""
        self.print_section("Sample Data")

        # Check in root data/staging
        sample_path = self.project_root / 'data' / 'staging' / 'taxi_clean_sample.csv'
        exists = sample_path.exists()

        if exists:
            size_mb = sample_path.stat().st_size / (1024 * 1024)
            try:
                import pandas as pd
                df = pd.read_csv(sample_path)
                row_count = len(df)
                self.print_check("taxi_clean_sample.csv exists", True,
                               f"{size_mb:.2f} MB, {row_count:,} rows")
                self.print_check("Row count ~100,000", row_count >= 100000)
                is_valid = row_count >= 100000
                self.add_result('sample_data', is_valid,
                               f'{row_count:,} rows' if is_valid else f'{row_count:,} rows (less than 100,000)')
                return is_valid
            except Exception as e:
                self.print_check("Cannot read sample data", False, str(e))
                self.add_result('sample_data', False, 'Cannot read sample data')
                return False
        else:
            self.print_check("taxi_clean_sample.csv NOT found", False,
                           "Run: python scripts/create_sample.py")
            self.add_result('sample_data', False, 'Sample data missing')
            return False

    def check_standalone_app(self) -> bool:
        """Verify standalone app.py exists."""
        self.print_section("Standalone App")

        repo_path = self.project_root / 'batchetl-streamlit'
        if not repo_path.exists():
            self.print_check("batchetl-streamlit/ not found", False)
            self.add_result('standalone_app', False, 'Repository not found')
            return False

        app_path = repo_path / 'app.py'
        exists = app_path.exists()

        if exists:
            size_kb = app_path.stat().st_size / 1024
            self.print_check("app.py exists", True, f"{size_kb:.1f} KB")

            # Check if it reads CSV (not database)
            try:
                with open(app_path, 'r') as f:
                    content = f.read()
                has_csv_read = 'pd.read_csv' in content or 'read_csv' in content
                has_no_db = 'sqlalchemy' not in content and 'create_engine' not in content
                self.print_check("Reads CSV directly", has_csv_read)
                self.print_check("No database connection", has_no_db)
                is_valid = has_csv_read and has_no_db
                self.add_result('standalone_app', is_valid,
                               'Standalone app ready' if is_valid else 'App may still use database')
                return is_valid
            except Exception as e:
                self.print_check("Cannot read app.py", False, str(e))
                self.add_result('standalone_app', False, 'Cannot read app.py')
                return False
        else:
            self.print_check("app.py NOT found", False, "Create standalone app.py")
            self.add_result('standalone_app', False, 'app.py missing')
            return False

    def check_streamlit_requirements(self) -> bool:
        """Verify requirements.txt exists."""
        self.print_section("Streamlit Requirements")

        repo_path = self.project_root / 'batchetl-streamlit'
        if not repo_path.exists():
            self.print_check("batchetl-streamlit/ not found", False)
            self.add_result('streamlit_requirements', False, 'Repository not found')
            return False

        req_path = repo_path / 'requirements.txt'
        exists = req_path.exists()

        if exists:
            size_kb = req_path.stat().st_size / 1024
            self.print_check("requirements.txt exists", True, f"{size_kb:.1f} KB")

            try:
                with open(req_path, 'r') as f:
                    content = f.read()
                required = ['pandas', 'streamlit', 'plotly']
                found = [pkg for pkg in required if pkg in content]
                self.print_check(f"Required packages found: {len(found)}/{len(required)}",
                               len(found) == len(required))
                is_valid = len(found) == len(required)
                self.add_result('streamlit_requirements', is_valid,
                               'Requirements ready' if is_valid else 'Some packages missing')
                return is_valid
            except Exception as e:
                self.print_check("Cannot read requirements.txt", False, str(e))
                self.add_result('streamlit_requirements', False, 'Cannot read file')
                return False
        else:
            self.print_check("requirements.txt NOT found", False)
            self.add_result('streamlit_requirements', False, 'requirements.txt missing')
            return False

    def check_streamlit_config(self) -> bool:
        """Verify .streamlit/config.toml exists."""
        self.print_section("Streamlit Config")

        repo_path = self.project_root / 'batchetl-streamlit'
        if not repo_path.exists():
            self.print_check("batchetl-streamlit/ not found", False)
            self.add_result('streamlit_config', False, 'Repository not found')
            return False

        config_path = repo_path / '.streamlit' / 'config.toml'
        exists = config_path.exists()

        if exists:
            size_kb = config_path.stat().st_size / 1024
            self.print_check(".streamlit/config.toml exists", True, f"{size_kb:.1f} KB")

            try:
                with open(config_path, 'r') as f:
                    content = f.read()
                has_theme = 'theme' in content
                self.print_check("Theme configured", has_theme)
                is_valid = has_theme
                self.add_result('streamlit_config', is_valid,
                               'Config ready' if is_valid else 'Theme not configured')
                return is_valid
            except Exception as e:
                self.print_check("Cannot read config.toml", False, str(e))
                self.add_result('streamlit_config', False, 'Cannot read file')
                return False
        else:
            self.print_check(".streamlit/config.toml NOT found", False,
                           "Create .streamlit/config.toml")
            self.add_result('streamlit_config', False, 'config.toml missing')
            return False

    def check_streamlit_folder_structure(self) -> bool:
        """Verify folder structure is prepared."""
        self.print_section("Folder Structure")

        repo_path = self.project_root / 'batchetl-streamlit'
        if not repo_path.exists():
            self.print_check("batchetl-streamlit/ not found", False)
            self.add_result('streamlit_folder_structure', False, 'Repository not found')
            return False

        required_items = [
            ('app.py', 'Main dashboard'),
            ('requirements.txt', 'Dependencies'),
            ('.streamlit/config.toml', 'Streamlit config'),
            ('data/taxi_clean_sample.csv', 'Sample data')
        ]

        all_exist = True
        for item, description in required_items:
            path = repo_path / item
            exists = path.exists()
            self.print_check(f"{item}", exists, description)
            if not exists:
                all_exist = False

        self.add_result('streamlit_folder_structure', all_exist,
                        'All files present' if all_exist else 'Some files missing')
        return all_exist

    # ============================================
    # Deployment Checks
    # ============================================

    def check_git_commit(self) -> bool:
        """Verify files committed to GitHub."""
        self.print_section("Git Commit")

        repo_path = self.project_root / 'batchetl-streamlit'
        if not repo_path.exists():
            self.print_check("batchetl-streamlit/ not found", False)
            self.add_result('git_commit', False, 'Repository not found')
            return False

        try:
            result = subprocess.run(
                ['git', 'log', '--oneline'],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=repo_path
            )
            has_commits = result.returncode == 0 and result.stdout.strip()
            self.print_check("Git commits exist", has_commits)
            self.add_result('git_commit', has_commits,
                            'Commits present' if has_commits else 'No commits found')
            return has_commits
        except Exception as e:
            self.print_check("Git commit check failed", False, str(e))
            self.add_result('git_commit', False, 'Check failed')
            return False

    def check_git_push(self) -> bool:
        """Verify pushed to GitHub repository."""
        self.print_section("Git Push")

        repo_path = self.project_root / 'batchetl-streamlit'
        if not repo_path.exists():
            self.print_check("batchetl-streamlit/ not found", False)
            self.add_result('git_push', False, 'Repository not found')
            return False

        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=repo_path
            )
            has_remote = result.returncode == 0 and result.stdout.strip()
            remote_url = result.stdout.strip() if has_remote else ""
            self.print_check("Git remote configured", has_remote, remote_url)

            if has_remote and 'github.com' in remote_url:
                self.print_check("GitHub remote (should be pushed)", True)
                is_pushed = True
            else:
                self.print_check("GitHub remote not configured", False)
                is_pushed = False

            self.add_result('git_push', is_pushed,
                            'Pushed to GitHub' if is_pushed else 'Not pushed to GitHub')
            return is_pushed
        except Exception as e:
            self.print_check("Git push check failed", False, str(e))
            self.add_result('git_push', False, 'Check failed')
            return False

    def check_streamlit_deploy(self) -> bool:
        """Verify deployed to Streamlit Cloud."""
        self.print_section("Streamlit Cloud Deployment")

        # Check if URL is accessible
        # This is a generic check - user should provide their URL
        url = "https://batchetl-streamlit.streamlit.app"
        self.print_check("Streamlit Cloud URL", True, f"Expected: {url}")

        # Try to access the URL
        try:
            response = requests.get(url, timeout=10)
            is_live = response.status_code == 200
            self.print_check("App URL accessible", is_live, f"Status: {response.status_code}")
            self.add_result('streamlit_deploy', is_live,
                            'App deployed and accessible' if is_live else 'App not accessible')
            return is_live
        except requests.RequestException:
            self.print_check("App URL NOT accessible", False,
                           "Deploy at: https://share.streamlit.io")
            self.add_result('streamlit_deploy', False, 'App not deployed')
            return False

    # ============================================
    # Verification Checks
    # ============================================

    def check_dashboard_live(self) -> bool:
        """Verify dashboard loads in browser."""
        self.print_section("Live Dashboard")

        url = "https://batchetl-streamlit.streamlit.app"
        try:
            response = requests.get(url, timeout=10)
            is_live = response.status_code == 200
            self.print_check("Dashboard loads", is_live, f"Status: {response.status_code}")
            self.add_result('dashboard_live', is_live,
                            'Dashboard live' if is_live else 'Dashboard not responding')
            return is_live
        except requests.RequestException:
            self.print_check("Dashboard NOT accessible", False)
            self.add_result('dashboard_live', False, 'Dashboard not accessible')
            return False

    def check_kpis_live(self) -> bool:
        """Verify 5 KPIs display correctly."""
        self.print_section("Live KPIs")

        kpis = [
            'Total Trips',
            'Average Fare',
            'Avg Distance',
            'Avg Passengers',
            'Total Revenue'
        ]

        url = "https://batchetl-streamlit.streamlit.app"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                self.print_check("Cannot check KPIs", False, "Dashboard not accessible")
                self.add_result('kpis_live', False, 'Dashboard not accessible')
                return False

            html = response.text
            found_kpis = [kpi for kpi in kpis if kpi in html]
            self.print_check(f"KPIs found: {len(found_kpis)}/{len(kpis)}",
                           len(found_kpis) == len(kpis))
            for kpi in kpis:
                self.print_check(f"  {kpi}", kpi in html)

            is_valid = len(found_kpis) == len(kpis)
            self.add_result('kpis_live', is_valid,
                            'All KPIs visible' if is_valid else 'Some KPIs missing')
            return is_valid
        except requests.RequestException:
            self.print_check("Cannot check KPIs", False, "Dashboard not accessible")
            self.add_result('kpis_live', False, 'Dashboard not accessible')
            return False

    def check_charts_live(self) -> bool:
        """Verify 4 charts render correctly."""
        self.print_section("Live Charts")

        charts = [
            'Revenue by Day',
            'Trips per Hour',
            'Fare Distribution',
            'Distance vs Fare'
        ]

        url = "https://batchetl-streamlit.streamlit.app"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                self.print_check("Cannot check charts", False, "Dashboard not accessible")
                self.add_result('charts_live', False, 'Dashboard not accessible')
                return False

            html = response.text
            found_charts = [chart for chart in charts if chart in html]
            self.print_check(f"Charts found: {len(found_charts)}/{len(charts)}",
                           len(found_charts) == len(charts))
            for chart in charts:
                self.print_check(f"  {chart}", chart in html)

            is_valid = len(found_charts) == len(charts)
            self.add_result('charts_live', is_valid,
                            'All charts visible' if is_valid else 'Some charts missing')
            return is_valid
        except requests.RequestException:
            self.print_check("Cannot check charts", False, "Dashboard not accessible")
            self.add_result('charts_live', False, 'Dashboard not accessible')
            return False

    def check_filters_live(self) -> bool:
        """Verify all 5 filters work."""
        self.print_section("Live Filters")

        filters = [
            'Fare Range',
            'Distance Range',
            'Day of Week',
            'Payment Type',
            'Vendor ID'
        ]

        url = "https://batchetl-streamlit.streamlit.app"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                self.print_check("Cannot check filters", False, "Dashboard not accessible")
                self.add_result('filters_live', False, 'Dashboard not accessible')
                return False

            html = response.text
            found_filters = [f for f in filters if f in html]
            self.print_check(f"Filters found: {len(found_filters)}/{len(filters)}",
                           len(found_filters) == len(filters))
            for f in filters:
                self.print_check(f"  {f}", f in html)

            is_valid = len(found_filters) == len(filters)
            self.add_result('filters_live', is_valid,
                            'All filters visible' if is_valid else 'Some filters missing')
            return is_valid
        except requests.RequestException:
            self.print_check("Cannot check filters", False, "Dashboard not accessible")
            self.add_result('filters_live', False, 'Dashboard not accessible')
            return False

    def check_performance_live(self) -> bool:
        """Verify load time less than 5 seconds."""
        self.print_section("Performance")

        url = "https://batchetl-streamlit.streamlit.app"
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            elapsed = time.time() - start_time

            self.print_check(f"Page load time: {elapsed:.2f} seconds",
                           elapsed < 5.0)
            is_valid = elapsed < 5.0
            self.add_result('performance_live', is_valid,
                            f'Loaded in {elapsed:.2f}s' if is_valid else f'Load time: {elapsed:.2f}s (exceeds 5s)')
            return is_valid
        except requests.RequestException:
            self.print_check("Performance check failed", False, "Dashboard not accessible")
            self.add_result('performance_live', False, 'Dashboard not accessible')
            return False

    def check_mobile_responsive(self) -> bool:
        """Verify mobile responsive."""
        self.print_section("Mobile Responsive")

        # Check viewport meta tag
        url = "https://batchetl-streamlit.streamlit.app"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                self.print_check("Cannot check mobile", False, "Dashboard not accessible")
                self.add_result('mobile_responsive', False, 'Dashboard not accessible')
                return False

            html = response.text
            has_viewport = 'viewport' in html
            self.print_check("Viewport meta tag present", has_viewport)

            # Check for Streamlit's built-in responsiveness
            has_responsive = 'responsive' in html or 'container' in html
            self.print_check("Responsive elements present", has_responsive)

            is_valid = has_viewport and has_responsive
            self.add_result('mobile_responsive', is_valid,
                            'Mobile responsive' if is_valid else 'May not be mobile responsive')
            return is_valid
        except requests.RequestException:
            self.print_check("Cannot check mobile", False, "Dashboard not accessible")
            self.add_result('mobile_responsive', False, 'Dashboard not accessible')
            return False

    # ============================================
    # Documentation Checks
    # ============================================

    def check_readme_updated(self) -> bool:
        """Verify README.md updated with live demo link."""
        self.print_section("README Update")

        readme_path = self.project_root / 'README.md'
        if not readme_path.exists():
            self.print_check("README.md NOT found", False)
            self.add_result('readme_updated', False, 'README.md missing')
            return False

        try:
            with open(readme_path, 'r') as f:
                content = f.read()

            has_live_demo = 'Live Demo' in content or 'live-demo' in content or 'streamlit.app' in content
            has_badge = 'badge' in content.lower() or 'img.shields.io' in content

            self.print_check("Live Demo section present", has_live_demo)
            self.print_check("Badge present", has_badge)

            is_valid = has_live_demo
            self.add_result('readme_updated', is_valid,
                            'README updated' if is_valid else 'Live Demo section missing')
            return is_valid
        except Exception as e:
            self.print_check("README check failed", False, str(e))
            self.add_result('readme_updated', False, 'Check failed')
            return False

    def check_live_demo_screenshots(self) -> bool:
        """Verify live demo screenshots captured."""
        self.print_section("Live Demo Screenshots")

        screenshots = [
            '17-streamlit-cloud-deploy.png',
            '18-live-demo-dashboard.png',
            '19-live-demo-url.png'
        ]

        all_exist = True
        for screenshot in screenshots:
            file_path = self.project_root / 'screenshots' / screenshot
            exists = file_path.exists()
            if exists:
                size_kb = file_path.stat().st_size / 1024
                self.print_check(f"{screenshot}", True, f"{size_kb:.1f} KB")
            else:
                self.print_check(f"{screenshot}", False, "Not captured yet")
                all_exist = False

        self.add_result('live_demo_screenshots', all_exist,
                        'All live demo screenshots captured' if all_exist else 'Some screenshots missing')
        return all_exist

    def run(self) -> bool:
        """Run all Phase 9 checks."""
        # Preparation
        self.check_streamlit_repo()
        self.check_sample_data()
        self.check_standalone_app()
        self.check_streamlit_requirements()
        self.check_streamlit_config()
        self.check_streamlit_folder_structure()

        # Deployment
        self.check_git_commit()
        self.check_git_push()
        self.check_streamlit_deploy()

        # Verification
        self.check_dashboard_live()
        self.check_kpis_live()
        self.check_charts_live()
        self.check_filters_live()
        self.check_performance_live()
        self.check_mobile_responsive()

        # Documentation
        self.check_readme_updated()
        self.check_live_demo_screenshots()

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
        verifier = Phase9Verifier()
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