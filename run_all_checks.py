# troubleshoot.py

"""
BatchETL Pipeline - Run All Checks

Runs all troubleshooting and verification checks and generates
comprehensive reports in JSON, TXT, and HTML formats.

Usage:
    python run_all_checks.py
    python run_all_checks.py --skip-data
    python run_all_checks.py --skip-verification
    python run_all_checks.py --skip-troubleshooting
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from troubleshoot_utils import (
    Colors, print_header, print_check, print_warning, print_error,
    print_success
)
from troubleshoot_config import (
    VERIFICATION_SCRIPTS, TROUBLESHOOTING_SCRIPTS,
    REPORT_CONFIG
)


class AllChecksRunner:
    """Run all checks and generate report."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.results: Dict[str, Any] = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'modules': {},
            'summary': {}
        }
        self.failed_modules: List[str] = []
        self.passed_modules: List[str] = []
        self.skipped_modules: List[str] = []

    def run_script(self, script_name: str, timeout: int = 120) -> bool:
        """Run a script and return success status."""
        script_path = self.project_root / script_name

        if not script_path.exists():
            print_warning(f"Script not found: {script_name}")
            return False

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=False,
                timeout=timeout
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print_error(f"Script timed out: {script_name}")
            return False
        except Exception as e:
            print_error(f"Error running {script_name}: {str(e)}")
            return False

    def run_verification_scripts(self) -> None:
        """Run all verification scripts."""
        print_header("RUNNING VERIFICATION SCRIPTS")

        for script in VERIFICATION_SCRIPTS:
            print(f"\n{Colors.BOLD}Running: {script}{Colors.END}")
            success = self.run_script(script)
            self.results['modules'][script] = {
                'status': 'passed' if success else 'failed',
                'timestamp': datetime.now().isoformat()
            }

            if success:
                self.passed_modules.append(script)
            else:
                self.failed_modules.append(script)

    def run_troubleshooting_scripts(self) -> None:
        """Run all troubleshooting scripts."""
        print_header("RUNNING TROUBLESHOOTING SCRIPTS")

        for script in TROUBLESHOOTING_SCRIPTS:
            print(f"\n{Colors.BOLD}Running: {script}{Colors.END}")
            success = self.run_script(script)
            self.results['modules'][script] = {
                'status': 'passed' if success else 'failed',
                'timestamp': datetime.now().isoformat()
            }

            if success:
                self.passed_modules.append(script)
            else:
                self.failed_modules.append(script)

    def run_data_inspection(self) -> None:
        """Run data inspection script."""
        print_header("RUNNING DATA INSPECTION")

        script = 'data_inspection.py'
        print(f"\n{Colors.BOLD}Running: {script} --report{Colors.END}")

        script_path = self.project_root / script

        if not script_path.exists():
            print_warning(f"Script not found: {script}")
            self.results['modules'][script] = {
                'status': 'skipped',
                'reason': 'File not found'
            }
            self.skipped_modules.append(script)
            return

        try:
            result = subprocess.run(
                [sys.executable, str(script_path), '--report'],
                capture_output=False,
                timeout=300
            )
            success = result.returncode == 0
            self.results['modules'][script] = {
                'status': 'passed' if success else 'failed',
                'timestamp': datetime.now().isoformat()
            }

            if success:
                self.passed_modules.append(script)
            else:
                self.failed_modules.append(script)
        except subprocess.TimeoutExpired:
            print_error(f"Script timed out: {script}")
            self.results['modules'][script] = {
                'status': 'failed',
                'reason': 'Timeout'
            }
            self.failed_modules.append(script)
        except Exception as e:
            print_error(f"Error running {script}: {str(e)}")
            self.results['modules'][script] = {
                'status': 'failed',
                'reason': str(e)
            }
            self.failed_modules.append(script)

    def generate_json_report(self) -> None:
        """Generate JSON report."""
        report_path = self.project_root / REPORT_CONFIG['json_file']
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print_check(f"JSON report saved to: {report_path}", True)

    def generate_text_report(self) -> None:
        """Generate text report."""
        report_path = self.project_root / REPORT_CONFIG['text_file']

        with open(report_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("BATCHETL PIPELINE - ALL CHECKS REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Success Rate: {self.results['summary']['success_rate']:.1f}%\n")
            f.write(f"Passed: {self.results['summary']['passed']}, Failed: {self.results['summary']['failed']}\n")
            f.write("=" * 60 + "\n\n")

            f.write("MODULE STATUS:\n")
            for module, data in self.results['modules'].items():
                status = data.get('status', 'unknown')
                icon = "PASS" if status == 'passed' else "FAIL" if status == 'failed' else "SKIP"
                f.write(f"  {icon} {module}: {status}\n")

            if self.failed_modules:
                f.write("\nFAILED MODULES:\n")
                for module in self.failed_modules:
                    f.write(f"  - {module}\n")

            if self.skipped_modules:
                f.write("\nSKIPPED MODULES:\n")
                for module in self.skipped_modules:
                    f.write(f"  - {module}\n")

        print_check(f"Text report saved to: {report_path}", True)

    def generate_html_report(self) -> None:
        """Generate HTML report."""
        report_path = self.project_root / REPORT_CONFIG['html_file']

        summary = self.results['summary']
        total = summary['total_modules']
        passed = summary['passed']
        failed = summary['failed']
        rate = summary['success_rate']

        if failed == 0:
            status_color = '#4CAF50'
            status_text = 'PASSED'
        elif rate > 50:
            status_color = '#FF9800'
            status_text = 'WARNING'
        else:
            status_color = '#F44336'
            status_text = 'FAILED'

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BatchETL - All Checks Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 40px;
            background: #f5f7fa;
            color: #333;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a237e;
            border-bottom: 3px solid #1a237e;
            padding-bottom: 10px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 6px 18px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            background: {status_color};
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e9ecef;
        }}
        .summary-card .number {{
            font-size: 28px;
            font-weight: bold;
        }}
        .summary-card .label {{
            color: #6c757d;
            font-size: 14px;
        }}
        .module-list {{
            margin: 20px 0;
        }}
        .module-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
            font-family: monospace;
        }}
        .module-item.passed {{
            border-left: 4px solid #4CAF50;
        }}
        .module-item.failed {{
            border-left: 4px solid #F44336;
        }}
        .module-item.skipped {{
            border-left: 4px solid #FFC107;
        }}
        .status-passed {{ color: #4CAF50; }}
        .status-failed {{ color: #F44336; }}
        .status-skipped {{ color: #FFC107; }}
        .timestamp {{
            color: #6c757d;
            font-size: 14px;
            margin-top: 20px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #6c757d;
            font-size: 14px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>BatchETL Pipeline - All Checks Report</h1>
        <p>
            <span class="status-badge">{status_text}</span>
            <span style="margin-left:15px;color:#6c757d;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
        </p>

        <div class="summary-grid">
            <div class="summary-card">
                <div class="number">{total}</div>
                <div class="label">Total Modules</div>
            </div>
            <div class="summary-card">
                <div class="number" style="color:#4CAF50;">{passed}</div>
                <div class="label">Passed</div>
            </div>
            <div class="summary-card">
                <div class="number" style="color:#F44336;">{failed}</div>
                <div class="label">Failed</div>
            </div>
            <div class="summary-card">
                <div class="number">{rate:.1f}%</div>
                <div class="label">Success Rate</div>
            </div>
        </div>

        <h2>Module Status</h2>
        <div class="module-list">
"""

        for module, data in self.results['modules'].items():
            status = data.get('status', 'unknown')
            icon = 'PASS' if status == 'passed' else 'FAIL' if status == 'failed' else 'SKIP'
            css_class = 'passed' if status == 'passed' else 'failed' if status == 'failed' else 'skipped'
            status_text_display = status.upper()
            html += f"""
            <div class="module-item {css_class}">
                <span>{icon} {module}</span>
                <span class="status-{css_class}">{status_text_display}</span>
            </div>
"""

        html += """
        </div>

        <div class="timestamp">
            <strong>Project Root:</strong> """ + str(self.project_root) + """
        </div>

        <div class="footer">
            BatchETL Pipeline - Automated Check Report
        </div>
    </div>
</body>
</html>
"""

        with open(report_path, 'w') as f:
            f.write(html)
        print_check(f"HTML report saved to: {report_path}", True)

    def generate_report(self) -> None:
        """Generate comprehensive report."""
        print_header("GENERATING REPORTS")

        total_modules = len(self.results['modules'])
        total_passed = len(self.passed_modules)
        total_failed = len(self.failed_modules)
        total_skipped = len(self.skipped_modules)

        self.results['summary'] = {
            'total_modules': total_modules,
            'passed': total_passed,
            'failed': total_failed,
            'skipped': total_skipped,
            'success_rate': round((total_passed / (total_modules - total_skipped) * 100)
                                  if (total_modules - total_skipped) > 0 else 0, 1),
            'overall_status': 'pass' if total_failed == 0 else 'fail'
        }

        self.generate_json_report()
        self.generate_text_report()
        self.generate_html_report()

        print_success("All reports generated successfully.")

    def run(self, skip_verification: bool = False,
            skip_troubleshooting: bool = False,
            skip_data: bool = False) -> None:
        """Run all checks."""
        print_header("BATCHETL PIPELINE - RUN ALL CHECKS")
        print(f"Project Root: {self.project_root}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if not skip_troubleshooting:
            self.run_troubleshooting_scripts()

        if not skip_verification:
            self.run_verification_scripts()

        if not skip_data:
            self.run_data_inspection()

        self.generate_report()

        print_header("ALL CHECKS COMPLETE")

        summary = self.results['summary']
        print(f"\n  Total Modules: {summary['total_modules']}")
        print(f"  Passed: {summary['passed']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Skipped: {summary['skipped']}")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")

        if summary['failed'] == 0:
            print_success("All checks passed.")
            sys.exit(0)
        else:
            print_error(f"Some checks failed. Failed modules: {', '.join(self.failed_modules)}")
            sys.exit(1)


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run all checks for BatchETL Pipeline")
    parser.add_argument('--skip-troubleshooting', action='store_true',
                        help='Skip troubleshooting scripts')
    parser.add_argument('--skip-verification', action='store_true',
                        help='Skip verification scripts')
    parser.add_argument('--skip-data', action='store_true',
                        help='Skip data inspection')

    args = parser.parse_args()

    try:
        runner = AllChecksRunner()
        runner.run(
            skip_verification=args.skip_verification,
            skip_troubleshooting=args.skip_troubleshooting,
            skip_data=args.skip_data
        )
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user.{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()