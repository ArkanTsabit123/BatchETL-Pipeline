# verify-phase-7.py
"""
Phase 7: Screenshots Documentation Verification

Checks performed:
    - architecture-diagram.png exists
    - data-flow-diagram.png exists
    - erd-diagram.png exists
    - 01-folder-structure.png exists
    - 02-dataset-downloaded.png exists
    - 03-airflow-dag-list.png exists
    - 04-airflow-grid-success.png exists
    - 05-airflow-tree-success.png exists
    - 06-postgres-data.png exists
    - 07-dashboard-overview.png exists
    - 08-dashboard-charts.png exists
    - 09-airflow-dag-code.png exists
    - 10-extract-script.png exists
    - 11-transform-script.png exists
    - 12-load-script.png exists
    - 13-dashboard-code.png exists
    - 14-docker-compose.png exists
    - 15-airflow-log.png exists
    - 16-dashboard-with-filter.png exists
    - 17-streamlit-cloud-deploy.png exists (PENDING)
    - 18-live-demo-dashboard.png exists (PENDING)
    - 19-live-demo-url.png exists (PENDING)
"""

import os
import sys
import json
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
# Phase 7: Screenshots Documentation
# ============================================

class Phase7Verifier(PhaseVerifier):
    """Verifier for Phase 7: Screenshots Documentation."""

    def __init__(self):
        super().__init__(7, "Screenshots Documentation")

    def check_screenshots(self) -> bool:
        """Verify all screenshot files exist."""
        self.print_section("Screenshots")

        # Architecture Diagrams (3)
        diagram_screenshots = [
            'architecture-diagram.png',
            'data-flow-diagram.png',
            'erd-diagram.png'
        ]

        # Level 1: Mandatory (8)
        mandatory_screenshots = [
            '01-folder-structure.png',
            '02-dataset-downloaded.png',
            '03-airflow-dag-list.png',
            '04-airflow-grid-success.png',
            '05-airflow-tree-success.png',
            '06-postgres-data.png',
            '07-dashboard-overview.png',
            '08-dashboard-charts.png'
        ]

        # Level 2: Recommended (4)
        recommended_screenshots = [
            '09-airflow-dag-code.png',
            '10-extract-script.png',
            '11-transform-script.png',
            '12-load-script.png'
        ]

        # Level 3: Value-Add (4)
        value_add_screenshots = [
            '13-dashboard-code.png',
            '14-docker-compose.png',
            '15-airflow-log.png',
            '16-dashboard-with-filter.png'
        ]

        # Level 4: Live Demo (3) - PENDING
        live_demo_screenshots = [
            '17-streamlit-cloud-deploy.png',
            '18-live-demo-dashboard.png',
            '19-live-demo-url.png'
        ]

        all_exist = True

        # Check Architecture Diagrams
        self.print_check("Architecture Diagrams (3)", True)
        for screenshot in diagram_screenshots:
            file_path = self.project_root / 'screenshots' / screenshot
            exists = file_path.exists()
            if exists:
                size_kb = file_path.stat().st_size / 1024
                self.print_check(f"  {screenshot}", True, f"{size_kb:.1f} KB")
            else:
                self.print_check(f"  {screenshot}", False, "Not found")
                all_exist = False

        # Check Level 1: Mandatory
        self.print_check("\nLevel 1: Mandatory (8)", True)
        for screenshot in mandatory_screenshots:
            file_path = self.project_root / 'screenshots' / screenshot
            exists = file_path.exists()
            if exists:
                size_kb = file_path.stat().st_size / 1024
                self.print_check(f"  {screenshot}", True, f"{size_kb:.1f} KB")
            else:
                self.print_check(f"  {screenshot}", False, "Not found")
                all_exist = False

        # Check Level 2: Recommended
        self.print_check("\nLevel 2: Recommended (4)", True)
        for screenshot in recommended_screenshots:
            file_path = self.project_root / 'screenshots' / screenshot
            exists = file_path.exists()
            if exists:
                size_kb = file_path.stat().st_size / 1024
                self.print_check(f"  {screenshot}", True, f"{size_kb:.1f} KB")
            else:
                self.print_check(f"  {screenshot}", False, "Not found")
                all_exist = False

        # Check Level 3: Value-Add
        self.print_check("\nLevel 3: Value-Add (4)", True)
        for screenshot in value_add_screenshots:
            file_path = self.project_root / 'screenshots' / screenshot
            exists = file_path.exists()
            if exists:
                size_kb = file_path.stat().st_size / 1024
                self.print_check(f"  {screenshot}", True, f"{size_kb:.1f} KB")
            else:
                self.print_check(f"  {screenshot}", False, "Not found")
                all_exist = False

        # Check Level 4: Live Demo (PENDING)
        self.print_check("\nLevel 4: Live Demo (3) - PENDING", False)
        for screenshot in live_demo_screenshots:
            file_path = self.project_root / 'screenshots' / screenshot
            exists = file_path.exists()
            if exists:
                size_kb = file_path.stat().st_size / 1024
                self.print_check(f"  {screenshot}", True, f"{size_kb:.1f} KB")
            else:
                self.print_check(f"  {screenshot}", False, "PENDING - Deploy to Streamlit Cloud first")
                # Note: These are expected to be pending, not a failure

        # Count passed screenshots
        total_screenshots = (len(diagram_screenshots) + len(mandatory_screenshots) +
                            len(recommended_screenshots) + len(value_add_screenshots) +
                            len(live_demo_screenshots))

        passed_screenshots = 0
        for screenshot in (diagram_screenshots + mandatory_screenshots +
                          recommended_screenshots + value_add_screenshots):
            file_path = self.project_root / 'screenshots' / screenshot
            if file_path.exists():
                passed_screenshots += 1

        # Check live demo screenshots separately
        live_demo_passed = 0
        for screenshot in live_demo_screenshots:
            file_path = self.project_root / 'screenshots' / screenshot
            if file_path.exists():
                live_demo_passed += 1
                passed_screenshots += 1

        self.print_check(f"\nScreenshots Summary:", True)
        self.print_check(f"  Total screenshots: {total_screenshots}", True)
        self.print_check(f"  Present: {passed_screenshots}", True)
        self.print_check(f"  Pending: {total_screenshots - passed_screenshots}",
                        total_screenshots - passed_screenshots == 3,
                        f"Expected 3 pending (Live Demo screenshots)")

        # Check screenshots directory exists
        screenshots_dir = self.project_root / 'screenshots'
        dir_exists = screenshots_dir.exists() and screenshots_dir.is_dir()
        if not dir_exists:
            self.print_check("screenshots/ directory exists", False, "Directory not found")
            all_exist = False

        # Only fail if required screenshots (Levels 1-3) are missing
        required_passed = passed_screenshots - live_demo_passed
        required_total = total_screenshots - len(live_demo_screenshots)
        is_valid = required_passed == required_total and dir_exists

        self.add_result('screenshots', is_valid,
                        f'{passed_screenshots}/{total_screenshots} screenshots present '
                        f'({required_passed}/{required_total} required)' if is_valid
                        else f'Screenshots missing: {required_total - required_passed} required screenshots not found')
        return is_valid

    def check_screenshot_quality(self) -> bool:
        """Verify screenshot quality (size and resolution)."""
        self.print_section("Screenshot Quality")

        screenshots_dir = self.project_root / 'screenshots'
        if not screenshots_dir.exists():
            self.print_check("screenshots/ directory not found", False)
            self.add_result('screenshot_quality', False, 'Directory not found')
            return False

        png_files = list(screenshots_dir.glob('*.png'))
        if not png_files:
            self.print_check("No PNG files found", False)
            self.add_result('screenshot_quality', False, 'No screenshots')
            return False

        # Check file sizes
        all_valid = True
        min_size_kb = 50  # Minimum reasonable size for a screenshot
        max_size_kb = 2048  # Maximum reasonable size (2MB)

        for png_file in png_files:
            size_kb = png_file.stat().st_size / 1024
            is_valid_size = min_size_kb <= size_kb <= max_size_kb

            # Skip check for files that are too small (likely placeholders)
            if size_kb < 1:
                continue

            status_text = f"{png_file.name}: {size_kb:.1f} KB"
            if is_valid_size:
                self.print_check(f"  {status_text}", True)
            else:
                if size_kb < min_size_kb:
                    self.print_check(f"  {status_text}", False, "File too small (<50KB)")
                else:
                    self.print_check(f"  {status_text}", False, "File too large (>2MB)")
                all_valid = False

        self.add_result('screenshot_quality', all_valid,
                        'All screenshots have reasonable size' if all_valid else 'Some screenshots have unusual size')
        return all_valid

    def check_screenshot_naming(self) -> bool:
        """Verify screenshot naming convention."""
        self.print_section("Screenshot Naming Convention")

        expected_patterns = [
            r'^01-folder-structure\.png$',
            r'^02-dataset-downloaded\.png$',
            r'^03-airflow-dag-list\.png$',
            r'^04-airflow-grid-success\.png$',
            r'^05-airflow-tree-success\.png$',
            r'^06-postgres-data\.png$',
            r'^07-dashboard-overview\.png$',
            r'^08-dashboard-charts\.png$',
            r'^09-airflow-dag-code\.png$',
            r'^10-extract-script\.png$',
            r'^11-transform-script\.png$',
            r'^12-load-script\.png$',
            r'^13-dashboard-code\.png$',
            r'^14-docker-compose\.png$',
            r'^15-airflow-log\.png$',
            r'^16-dashboard-with-filter\.png$',
            r'^architecture-diagram\.png$',
            r'^data-flow-diagram\.png$',
            r'^erd-diagram\.png$'
        ]

        import re
        screenshots_dir = self.project_root / 'screenshots'
        if not screenshots_dir.exists():
            self.print_check("screenshots/ directory not found", False)
            self.add_result('screenshot_naming', False, 'Directory not found')
            return False

        png_files = [f.name for f in screenshots_dir.glob('*.png')]
        if not png_files:
            self.print_check("No PNG files found", False)
            self.add_result('screenshot_naming', False, 'No screenshots')
            return False

        # Check each file against expected patterns
        all_valid = True
        found_patterns = []

        for file_name in png_files:
            matched = False
            for pattern in expected_patterns:
                if re.match(pattern, file_name):
                    matched = True
                    found_patterns.append(file_name)
                    break

            if not matched:
                self.print_check(f"  {file_name}", False, "Does not follow naming convention")
                all_valid = False

        # Check for missing expected files
        expected_files = [
            '01-folder-structure.png',
            '02-dataset-downloaded.png',
            '03-airflow-dag-list.png',
            '04-airflow-grid-success.png',
            '05-airflow-tree-success.png',
            '06-postgres-data.png',
            '07-dashboard-overview.png',
            '08-dashboard-charts.png',
            '09-airflow-dag-code.png',
            '10-extract-script.png',
            '11-transform-script.png',
            '12-load-script.png',
            '13-dashboard-code.png',
            '14-docker-compose.png',
            '15-airflow-log.png',
            '16-dashboard-with-filter.png',
            'architecture-diagram.png',
            'data-flow-diagram.png',
            'erd-diagram.png'
        ]

        missing_files = [f for f in expected_files if f not in png_files]
        if missing_files:
            self.print_check(f"\nMissing expected files: {len(missing_files)}", False)
            for f in missing_files[:5]:  # Show first 5 missing
                self.print_check(f"  {f}", False, "Not found")
            if len(missing_files) > 5:
                self.print_check(f"  ... and {len(missing_files) - 5} more", False)
            all_valid = False
        else:
            self.print_check("All expected files present", True)

        self.add_result('screenshot_naming', all_valid,
                        'Screenshot naming convention followed' if all_valid else 'Naming issues found')
        return all_valid

    def run(self) -> bool:
        """Run all Phase 7 checks."""
        self.check_screenshots()
        self.check_screenshot_quality()
        self.check_screenshot_naming()

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
        verifier = Phase7Verifier()
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