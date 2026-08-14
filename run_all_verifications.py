# run_all_verifications.py
"""
Run All Verifications - BatchETL Pipeline

This script runs all 9 phase verification scripts sequentially
and displays a summary of results with actual output.
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class Colors:
    """Terminal color codes for formatted output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class VerificationRunner:
    """Run all verification scripts and collect results."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.results: Dict[int, Dict] = {}
        self.start_time = datetime.now()
        self.phase_names = {
            1: "Setup and Environment",
            2: "Docker and Container Setup",
            3: "Airflow DAG Creation",
            4: "Pipeline Execution",
            5: "PostgreSQL Data Verification",
            6: "Dashboard Verification (Local)",
            7: "Screenshots Documentation",
            8: "Documentation and Local Deployment",
            9: "Streamlit Cloud Deployment"
        }

    def print_header(self, text: str) -> None:
        """Print formatted header."""
        print(f"\n{Colors.CYAN}{'=' * 70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 70}{Colors.END}\n")

    def print_section(self, text: str) -> None:
        """Print section header."""
        print(f"\n{Colors.YELLOW}{text}{Colors.END}")
        print(f"{Colors.YELLOW}{'-' * 50}{Colors.END}")

    def print_result(self, phase: int, status: str, message: str = "", details: str = "") -> None:
        """Print a verification result with appropriate formatting."""
        if status == "PASSED":
            color = Colors.GREEN
            icon = "[PASS]"
        elif status == "FAILED":
            color = Colors.RED
            icon = "[FAIL]"
        elif status == "SKIPPED":
            color = Colors.YELLOW
            icon = "[SKIP]"
        else:
            color = Colors.CYAN
            icon = "[INFO]"

        phase_str = f"Phase {phase}:".ljust(10)
        print(f"  {icon} {phase_str} {color}{status}{Colors.END}")
        if message:
            print(f"     {Colors.CYAN}-> {message}{Colors.END}")
        if details:
            print(f"     {Colors.CYAN}   {details}{Colors.END}")

    def run_phase(self, phase: int) -> Tuple[bool, str, str]:
        """
        Run a phase verification script.

        Args:
            phase: Phase number to run

        Returns:
            Tuple of (success, output, error)
        """
        script_name = f"verify-phase-{phase}.py"
        script_path = self.project_root / script_name

        if not script_path.exists():
            return False, "", f"Script not found: {script_name}"

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=120
            )

            output = result.stdout
            error = result.stderr

            success = result.returncode == 0

            if "All checks passed" in output:
                success = True
            elif "Some checks failed" in output:
                success = False

            return success, output, error

        except subprocess.TimeoutExpired:
            return False, "", "Timeout (120 seconds)"
        except Exception as e:
            return False, "", str(e)

    def load_phase_summaries(self) -> Dict[int, Dict]:
        """Load summary data from JSON report files."""
        phase_summaries = {}

        for phase in range(1, 10):
            json_file = self.project_root / f'phase{phase}_verification.json'
            if json_file.exists():
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        summary = data.get('summary', {})
                        phase_summaries[phase] = {
                            'total_checks': summary.get('total_checks', 0),
                            'passed': summary.get('passed', 0),
                            'failed': summary.get('failed', 0),
                            'success_rate': summary.get('success_rate', 0)
                        }
                except Exception:
                    pass

        return phase_summaries

    def extract_summary_output(self, output: str) -> List[str]:
        """Extract summary lines from script output."""
        summary_lines = []
        output_lines = output.split('\n')
        summary_started = False

        for line in output_lines:
            if 'Verification Summary' in line:
                summary_started = True
            if summary_started and line.strip():
                if line.strip() and '=' not in line and 'PHASE' not in line:
                    clean_line = self.strip_ansi_codes(line)
                    if clean_line.strip():
                        summary_lines.append(clean_line.strip())

        return summary_lines

    def strip_ansi_codes(self, text: str) -> str:
        """Remove ANSI color codes from text."""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def display_phase_result(self, phase: int, success: bool, elapsed: float, output: str, error: str) -> None:
        """Display the result of a single phase verification."""
        if success:
            self.print_result(phase, "PASSED", f"Completed in {elapsed:.2f}s")
        else:
            self.print_result(phase, "FAILED", f"Completed in {elapsed:.2f}s")
            if error:
                print(f"     {Colors.RED}Error: {error[:200]}{Colors.END}")

        # Display summary from output
        summary_lines = self.extract_summary_output(output)
        for line in summary_lines[:5]:
            print(f"     {Colors.CYAN}{line}{Colors.END}")

    def run_all_phases(self) -> Tuple[int, int, float]:
        """Run all verification phases and return statistics."""
        total_phases = 9
        passed_phases = 0
        failed_phases = 0
        total_time = 0

        print(f"\n{Colors.BOLD}Running {total_phases} verification phases...{Colors.END}\n")

        for phase in range(1, total_phases + 1):
            phase_name = self.phase_names.get(phase, f"Phase {phase}")
            self.print_section(f"Phase {phase}: {phase_name}")

            print(f"  Running: {Colors.BOLD}verify-phase-{phase}.py{Colors.END}")

            start_time = time.time()
            success, output, error = self.run_phase(phase)
            elapsed = time.time() - start_time
            total_time += elapsed

            print(f"  Time: {elapsed:.2f} seconds")

            self.display_phase_result(phase, success, elapsed, output, error)

            if success:
                passed_phases += 1
            else:
                failed_phases += 1

            self.results[phase] = {
                'success': success,
                'time': elapsed,
                'output': output,
                'error': error
            }

            if phase < total_phases:
                time.sleep(1)

        return passed_phases, failed_phases, total_time

    def display_final_summary(self, passed: int, failed: int, total_time: float) -> None:
        """Display final verification summary."""
        self.print_header("FINAL VERIFICATION SUMMARY")

        total = passed + failed

        print(f"\n  {Colors.BOLD}Phases Completed: {total}/9{Colors.END}")
        print(f"  {Colors.GREEN}Passed: {passed}{Colors.END}")
        print(f"  {Colors.RED}Failed: {failed}{Colors.END}")
        print(f"  Total Time: {total_time:.2f} seconds")

        phase_summaries = self.load_phase_summaries()

        if phase_summaries:
            total_checks = 0
            total_passed = 0
            total_failed = 0

            for summary in phase_summaries.values():
                total_checks += summary.get('total_checks', 0)
                total_passed += summary.get('passed', 0)
                total_failed += summary.get('failed', 0)

            if total_checks > 0:
                print(f"\n  {Colors.BOLD}Detailed Statistics:{Colors.END}")
                print(f"    Total Checks: {total_checks}")
                print(f"    {Colors.GREEN}Passed: {total_passed}{Colors.END}")
                print(f"    {Colors.RED}Failed: {total_failed}{Colors.END}")
                success_rate = (total_passed / total_checks * 100) if total_checks > 0 else 0
                print(f"    Success Rate: {success_rate:.1f}%")

        self.display_overall_status(failed)

        print(f"\n{Colors.CYAN}{'=' * 70}{Colors.END}")

    def display_overall_status(self, failed: int) -> None:
        """Display overall project status based on verification results."""
        print(f"\n{Colors.BOLD}Overall Status:{Colors.END}")
        if failed == 0:
            print(f"  {Colors.GREEN}{Colors.BOLD}[SUCCESS] ALL PHASES PASSED{Colors.END}")
            print(f"  {Colors.GREEN}Project is ready for production.{Colors.END}")
        elif failed > 0:
            print(f"  {Colors.YELLOW}{Colors.BOLD}[WARNING] PARTIAL COMPLETION{Colors.END}")
            print(f"  {Colors.YELLOW}Some phases failed. Fix the failed items before proceeding.{Colors.END}")

    def display_detailed_summary(self) -> None:
        """Display detailed phase-by-phase summary."""
        self.print_section("Phase-by-Phase Summary")

        print(f"\n  {'Phase':<6} {'Name':<30} {'Status':<10} {'Time':<10} {'Checks':<8}")
        print(f"  {'-' * 70}")

        phase_summaries = self.load_phase_summaries()

        for phase in range(1, 10):
            phase_name = self.phase_names.get(phase, f"Phase {phase}")[:30]
            result = self.results.get(phase, {})
            status = "PASSED" if result.get('success', False) else "FAILED"
            time_taken = f"{result.get('time', 0):.2f}s"

            if phase in phase_summaries:
                summary = phase_summaries[phase]
                checks = f"{summary.get('passed', 0)}/{summary.get('total_checks', 0)}"
            else:
                checks = "N/A"

            status_color = Colors.GREEN if status == "PASSED" else Colors.RED
            print(f"  Phase {phase:<2} {phase_name:<30} {status_color}{status:<10}{Colors.END} {time_taken:<10} {checks:<8}")

        print(f"  {'-' * 70}")

    def save_results(self) -> None:
        """Save verification results to JSON file."""
        results_file = self.project_root / 'verification_results.json'

        report = {
            'timestamp': self.start_time.isoformat(),
            'project_root': str(self.project_root),
            'total_phases': 9,
            'phases': {}
        }

        for phase, result in self.results.items():
            report['phases'][str(phase)] = {
                'name': self.phase_names.get(phase, f"Phase {phase}"),
                'success': result.get('success', False),
                'time': result.get('time', 0),
                'error': result.get('error', '')
            }

        phase_summaries = self.load_phase_summaries()
        for phase, summary in phase_summaries.items():
            if str(phase) in report['phases']:
                report['phases'][str(phase)]['checks'] = summary

        with open(results_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n{Colors.CYAN}Results saved to: {results_file}{Colors.END}")

    def check_scripts_exist(self) -> bool:
        """Check if all verification scripts exist."""
        missing = []
        for phase in range(1, 10):
            script_name = f"verify-phase-{phase}.py"
            script_path = self.project_root / script_name
            if not script_path.exists():
                missing.append(script_name)

        if missing:
            print(f"{Colors.RED}Missing scripts: {', '.join(missing)}{Colors.END}")
            return False

        print(f"{Colors.GREEN}All verification scripts found.{Colors.END}")
        return True

    def run(self) -> None:
        """Main execution method."""
        self.print_header("BATCHETL PIPELINE - ALL VERIFICATIONS")
        print(f"Project Root: {self.project_root}")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python Version: {sys.version}")

        if not self.check_scripts_exist():
            print(f"\n{Colors.RED}Some verification scripts are missing.{Colors.END}")
            print("Please create the missing scripts before running all verifications.")
            sys.exit(1)

        passed, failed, total_time = self.run_all_phases()

        self.display_final_summary(passed, failed, total_time)
        self.display_detailed_summary()
        self.save_results()

        print(f"\n{Colors.CYAN}All verifications complete.{Colors.END}")


def main() -> None:
    """Main entry point."""
    try:
        runner = VerificationRunner()
        runner.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Verification interrupted by user.{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()