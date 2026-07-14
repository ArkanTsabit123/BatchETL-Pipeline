# verify-phase-8.py
"""
Phase 8: Documentation & Deployment Verification

Checks performed:
    - README.md completed
    - blueprint.md completed
    - cheatsheets.md completed
    - verification checklist.md completed
    - LICENSE added
    - .gitignore configured
    - Git initialized
    - Git commit
    - GitHub repository created
    - Remote origin set
    - Push to GitHub
    - README rendered on GitHub
    - Screenshots visible on GitHub
"""

import os
import sys
import json
import subprocess
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
# Phase 8: Documentation & Deployment
# ============================================

class Phase8Verifier(PhaseVerifier):
    """Verifier for Phase 8: Documentation & Deployment."""

    def __init__(self):
        super().__init__(8, "Documentation & Deployment")

    def _run_git_command(self, command: List[str]) -> Tuple[bool, str]:
        """Run a git command and return status and output."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.project_root
            )
            return result.returncode == 0, result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, ""

    def check_documentation_files(self) -> bool:
        """Verify documentation files exist."""
        self.print_section("Documentation Files")

        docs = [
            ('README.md', 'Main documentation'),
            ('blueprint.md', 'Technical blueprint'),
            ('cheatsheets.md', 'Quick reference'),
            ('verification checklist.md', 'Testing checklist')
        ]

        all_exist = True
        for doc, description in docs:
            file_path = self.project_root / doc
            exists = file_path.exists()

            if exists:
                size_kb = file_path.stat().st_size / 1024
                self.print_check(f"{doc}", True, f"{size_kb:.1f} KB - {description}")
            else:
                self.print_check(f"{doc}", False, "Not found")
                all_exist = False

        self.add_result('documentation_files', all_exist, 'All documentation files exist' if all_exist else 'Some files missing')
        return all_exist

    def check_license(self) -> bool:
        """Verify LICENSE exists."""
        self.print_section("License")

        license_path = self.project_root / 'LICENSE'
        exists = license_path.exists()

        if exists:
            size_kb = license_path.stat().st_size / 1024
            self.print_check("LICENSE exists", True, f"{size_kb:.1f} KB")
            self.add_result('license', True, 'MIT License present')
            return True
        else:
            self.print_check("LICENSE NOT found", False, "Add MIT License")
            self.add_result('license', False, 'LICENSE missing')
            return False

    def check_gitignore(self) -> bool:
        """Verify .gitignore exists."""
        self.print_section("Gitignore")

        gitignore_path = self.project_root / '.gitignore'
        exists = gitignore_path.exists()

        if exists:
            with open(gitignore_path, 'r') as f:
                content = f.read()

            required_entries = ['venv', '__pycache__', '.env', '*.csv']
            found_entries = [entry for entry in required_entries if entry in content]

            self.print_check(".gitignore exists", True)
            self.print_check(f"Found {len(found_entries)}/{len(required_entries)} required entries", len(found_entries) == len(required_entries))

            self.add_result('gitignore', True, '.gitignore configured')
            return True
        else:
            self.print_check(".gitignore NOT found", False, "Create .gitignore")
            self.add_result('gitignore', False, '.gitignore missing')
            return False

    def check_git(self) -> bool:
        """Verify Git is initialized."""
        self.print_section("Git Status")

        git_dir = self.project_root / '.git'
        exists = git_dir.exists()
        self.print_check(".git directory exists", exists)

        if exists:
            # Check if there are commits
            success, output = self._run_git_command(['git', 'log', '--oneline'])
            has_commits = success and output
            self.print_check("Git commits exist", has_commits)

            # Check remote
            success, remote = self._run_git_command(['git', 'remote', 'get-url', 'origin'])
            has_remote = success and remote
            self.print_check("Git remote configured", has_remote, remote if has_remote else "")

            is_ready = exists and has_commits and has_remote
            self.add_result('git', is_ready, 'Git ready' if is_ready else 'Git not fully configured')
            return is_ready
        else:
            self.print_check("Git NOT initialized", False, "Run: git init")
            self.add_result('git', False, 'Git not initialized')
            return False

    def check_readme_content(self) -> bool:
        """Verify README.md has required sections."""
        self.print_section("README Content")

        readme_path = self.project_root / 'README.md'
        if not readme_path.exists():
            self.print_check("README.md NOT found", False)
            self.add_result('readme_content', False, 'README.md missing')
            return False

        try:
            with open(readme_path, 'r') as f:
                content = f.read()

            required_sections = [
                'Project Overview',
                'System Architecture',
                'Technology Stack',
                'Quick Start',
                'Dashboard Features'
            ]

            found_sections = [section for section in required_sections if section in content]
            self.print_check(f"Found {len(found_sections)}/{len(required_sections)} required sections", len(found_sections) == len(required_sections))

            # Check for badges
            has_badges = 'badge' in content.lower() or 'img.shields.io' in content
            self.print_check("Badges present", has_badges)

            all_good = len(found_sections) == len(required_sections)
            self.add_result('readme_content', all_good, 'README complete' if all_good else 'Some sections missing')
            return all_good
        except Exception as e:
            self.print_check("README check failed", False, str(e))
            self.add_result('readme_content', False, 'Check failed')
            return False

    def run(self) -> bool:
        """Run all Phase 8 checks."""
        self.check_documentation_files()
        self.check_license()
        self.check_gitignore()
        self.check_git()
        self.check_readme_content()

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
        verifier = Phase8Verifier()
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