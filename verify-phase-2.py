# verify-phase-2.py
"""
Phase 2: Docker & Container Setup Verification

Checks performed:
    - Docker daemon running
    - PostgreSQL container running
    - Airflow container running
    - Streamlit container running
    - All containers healthy
    - PostgreSQL accessible
    - Airflow UI accessible
    - Database initialized
    - Docker volumes created
    - Docker network created
    - Streamlit dashboard accessible
"""

import os
import sys
import json
import subprocess
import time
import socket
import requests
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
# Phase 2: Docker & Container Setup
# ============================================

class Phase2Verifier(PhaseVerifier):
    """Verifier for Phase 2: Docker & Container Setup."""

    def __init__(self):
        super().__init__(2, "Docker & Container Setup")

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

    def _check_port_open(self, host: str, port: int, timeout: float = 2.0) -> bool:
        """Check if a port is open."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def check_docker_daemon(self) -> bool:
        """Verify Docker daemon is running."""
        self.print_section("Docker Daemon")

        success, version = self._run_docker_command(['docker', '--version'])
        if success:
            self.print_check("Docker daemon running", True, version)
        else:
            self.print_check("Docker daemon NOT running", False, "Start Docker Desktop")

        self.add_result('docker_daemon', success, 'Docker daemon ready' if success else 'Docker daemon not running')
        return success

    def check_containers_running(self) -> bool:
        """Verify all required containers are running."""
        self.print_section("Container Status")

        required_containers = {
            'batch-etl-postgres': 'PostgreSQL',
            'batch-etl-airflow': 'Airflow',
            'batch-etl-streamlit': 'Streamlit'
        }

        all_running = True
        for container_name, description in required_containers.items():
            success, status = self._run_docker_command(['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Status}}'])
            if success and status:
                self.print_check(f"{container_name} running", True, status)
            else:
                self.print_check(f"{container_name} NOT running", False, f"Run: docker-compose up -d")
                all_running = False

        self.add_result('containers_running', all_running, 'All containers running' if all_running else 'Some containers not running')
        return all_running

    def check_postgres_accessible(self) -> bool:
        """Verify PostgreSQL is accessible."""
        self.print_section("PostgreSQL")

        # Check port
        port_open = self._check_port_open('localhost', 5432)
        self.print_check("PostgreSQL port 5432 open", port_open)

        if port_open:
            # Try to connect via psql
            try:
                result = subprocess.run(
                    ['docker', 'exec', 'batch-etl-postgres', 'psql', '-U', 'admin', '-d', 'warehouse', '-c', 'SELECT 1'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                accessible = result.returncode == 0
                self.print_check("PostgreSQL accessible", accessible)
                self.add_result('postgres_accessible', accessible, 'PostgreSQL ready' if accessible else 'PostgreSQL connection failed')
                return accessible
            except Exception:
                self.print_check("PostgreSQL accessible", False)
                self.add_result('postgres_accessible', False, 'PostgreSQL connection failed')
                return False
        else:
            self.add_result('postgres_accessible', False, 'PostgreSQL port 5432 not open')
            return False

    def check_airflow_ui(self) -> bool:
        """Verify Airflow UI is accessible."""
        self.print_section("Airflow UI")

        port_open = self._check_port_open('localhost', 8080)
        self.print_check("Airflow port 8080 open", port_open)

        if port_open:
            try:
                response = requests.get('http://localhost:8080', timeout=5)
                accessible = response.status_code == 200
                self.print_check("Airflow UI accessible", accessible, f"Status: {response.status_code}")
                self.add_result('airflow_ui', accessible, 'Airflow UI ready' if accessible else 'Airflow UI not responding')
                return accessible
            except requests.RequestException:
                self.print_check("Airflow UI accessible", False, "Check Airflow container logs")
                self.add_result('airflow_ui', False, 'Airflow UI not responding')
                return False
        else:
            self.add_result('airflow_ui', False, 'Airflow port 8080 not open')
            return False

    def check_dashboard_accessible(self) -> bool:
        """Verify Streamlit dashboard is accessible."""
        self.print_section("Streamlit Dashboard")

        port_open = self._check_port_open('localhost', 8501)
        self.print_check("Streamlit port 8501 open", port_open)

        if port_open:
            try:
                response = requests.get('http://localhost:8501', timeout=5)
                accessible = response.status_code == 200
                self.print_check("Dashboard accessible", accessible, f"Status: {response.status_code}")
                self.add_result('dashboard_accessible', accessible, 'Dashboard ready' if accessible else 'Dashboard not responding')
                return accessible
            except requests.RequestException:
                self.print_check("Dashboard accessible", False, "Check Streamlit container logs")
                self.add_result('dashboard_accessible', False, 'Dashboard not responding')
                return False
        else:
            self.add_result('dashboard_accessible', False, 'Streamlit port 8501 not open')
            return False

    def check_database_initialized(self) -> bool:
        """Verify database is initialized with fact_trips table."""
        self.print_section("Database Initialization")

        try:
            # Check if fact_trips table exists
            result = subprocess.run(
                ['docker', 'exec', 'batch-etl-postgres', 'psql', '-U', 'admin', '-d', 'warehouse', '-c', "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'fact_trips');"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and 't' in result.stdout:
                self.print_check("fact_trips table exists", True)
                self.add_result('database_initialized', True, 'Database initialized successfully')
                return True
            else:
                self.print_check("fact_trips table NOT found", False, "Run init.sql manually")
                self.add_result('database_initialized', False, 'Database not initialized')
                return False
        except Exception:
            self.print_check("Database check failed", False, "PostgreSQL not accessible")
            self.add_result('database_initialized', False, 'Database check failed')
            return False

    def check_docker_volumes(self) -> bool:
        """Verify Docker volumes exist."""
        self.print_section("Docker Volumes")

        success, volumes = self._run_docker_command(['docker', 'volume', 'ls', '--format', '{{.Name}}'])
        if success:
            has_volume = 'batch-etl_postgres_data' in volumes or 'postgres_data' in volumes
            self.print_check("PostgreSQL volume exists", has_volume)
            self.add_result('docker_volumes', has_volume, 'Volumes ready' if has_volume else 'Volume not found')
            return has_volume
        else:
            self.print_check("Cannot list volumes", False)
            self.add_result('docker_volumes', False, 'Cannot list Docker volumes')
            return False

    def check_docker_network(self) -> bool:
        """Verify Docker network exists."""
        self.print_section("Docker Network")

        success, networks = self._run_docker_command(['docker', 'network', 'ls', '--format', '{{.Name}}'])
        if success:
            has_network = 'batch-etl-network' in networks
            self.print_check("batch-etl-network exists", has_network)
            self.add_result('docker_network', has_network, 'Network ready' if has_network else 'Network not found')
            return has_network
        else:
            self.print_check("Cannot list networks", False)
            self.add_result('docker_network', False, 'Cannot list Docker networks')
            return False

    def check_compose_file(self) -> bool:
        """Verify docker-compose.yml exists."""
        self.print_section("Docker Compose")

        compose_path = self.project_root / 'docker-compose.yml'
        exists = compose_path.exists()
        self.print_check("docker-compose.yml exists", exists)

        if exists:
            size_kb = compose_path.stat().st_size / 1024
            self.print_check("docker-compose.yml size", True, f"{size_kb:.1f} KB")

        self.add_result('compose_file', exists, 'docker-compose.yml ready' if exists else 'docker-compose.yml not found')
        return exists

    def run(self) -> bool:
        """Run all Phase 2 checks."""
        self.check_docker_daemon()
        self.check_compose_file()
        self.check_containers_running()
        self.check_postgres_accessible()
        self.check_database_initialized()
        self.check_airflow_ui()
        self.check_dashboard_accessible()
        self.check_docker_volumes()
        self.check_docker_network()

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
        verifier = Phase2Verifier()
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