# verify-phase-3.py
"""
Phase 3: Airflow DAG Creation Verification

Checks performed:
    - DAG file valid Python syntax
    - DAG imports
    - DAG definition
    - Tasks defined
    - Task dependencies
    - DAG tags
    - DAG description
"""

import os
import sys
import json
import subprocess
import ast
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
# Phase 3: Airflow DAG Creation
# ============================================

class Phase3Verifier(PhaseVerifier):
    """Verifier for Phase 3: Airflow DAG Creation."""

    def __init__(self):
        super().__init__(3, "Airflow DAG Creation")

    def check_dag_syntax(self) -> bool:
        """Verify DAG file has valid Python syntax."""
        self.print_section("DAG File Syntax")

        dag_path = self.project_root / 'dags' / 'etl_pipeline.py'
        exists = dag_path.exists()

        if not exists:
            self.print_check("DAG file exists", False, "dags/etl_pipeline.py not found")
            self.add_result('dag_syntax', False, 'DAG file not found')
            return False

        try:
            with open(dag_path, 'r') as f:
                content = f.read()
            ast.parse(content)
            self.print_check("DAG file syntax valid", True)
            self.add_result('dag_syntax', True, 'Syntax valid')
            return True
        except SyntaxError as e:
            self.print_check("DAG file syntax INVALID", False, f"Line {e.lineno}: {e.msg}")
            self.add_result('dag_syntax', False, f'Syntax error: {e.msg}')
            return False

    def check_dag_imports(self) -> bool:
        """Verify DAG file imports required modules."""
        self.print_section("DAG Imports")

        dag_path = self.project_root / 'dags' / 'etl_pipeline.py'
        if not dag_path.exists():
            self.print_check("DAG file exists", False)
            self.add_result('dag_imports', False, 'DAG file not found')
            return False

        try:
            with open(dag_path, 'r') as f:
                content = f.read()

            # Check imports
            imports_to_check = [
                ('from airflow import DAG', 'from airflow'),
                ('from airflow.operators.python import PythonOperator', 'from airflow.operators.python'),
            ]
            
            # Check datetime and timedelta
            has_datetime = 'from datetime import datetime' in content or 'datetime' in content
            has_timedelta = 'from datetime import timedelta' in content or 'timedelta' in content
            
            all_imported = True
            
            for imp, display in imports_to_check:
                exists = imp in content
                self.print_check(f"Import: {display}", exists)
                if not exists:
                    all_imported = False
            
            # Check datetime
            self.print_check("Import: datetime", has_datetime)
            if not has_datetime:
                all_imported = False
            
            # Check timedelta (combined with datetime)
            if not has_timedelta:
                # timedelta might be imported with datetime
                if not ('from datetime import datetime, timedelta' in content or 
                       'from datetime import timedelta' in content):
                    all_imported = False

            self.add_result('dag_imports', all_imported, 'All imports present' if all_imported else 'Some imports missing')
            return all_imported
        except Exception as e:
            self.print_check("DAG imports check failed", False, str(e))
            self.add_result('dag_imports', False, 'Check failed')
            return False

    def check_dag_definition(self) -> bool:
        """Verify DAG is properly defined."""
        self.print_section("DAG Definition")

        dag_path = self.project_root / 'dags' / 'etl_pipeline.py'
        if not dag_path.exists():
            self.print_check("DAG file exists", False)
            self.add_result('dag_definition', False, 'DAG file not found')
            return False

        try:
            with open(dag_path, 'r') as f:
                content = f.read()

            # Check for DAG ID
            has_dag_id = 'DAG_ID' in content or "dag_id='etl_pipeline'" in content or 'dag_id="etl_pipeline"' in content
            self.print_check("DAG ID defined", has_dag_id)

            # Check for schedule
            has_schedule = '@daily' in content or "schedule_interval" in content
            self.print_check("Schedule interval defined", has_schedule)

            # Check for default_args
            has_default_args = 'default_args' in content
            self.print_check("default_args defined", has_default_args)

            # Check for DAG instantiation
            has_dag = 'DAG(' in content
            self.print_check("DAG instantiated", has_dag)

            all_defined = has_dag_id and has_schedule and has_default_args and has_dag
            self.add_result('dag_definition', all_defined, 'DAG properly defined' if all_defined else 'Some definitions missing')
            return all_defined
        except Exception as e:
            self.print_check("DAG definition check failed", False, str(e))
            self.add_result('dag_definition', False, 'Check failed')
            return False

    def check_tasks_defined(self) -> bool:
        """Verify all tasks are defined."""
        self.print_section("Tasks Definition")

        dag_path = self.project_root / 'dags' / 'etl_pipeline.py'
        if not dag_path.exists():
            self.print_check("DAG file exists", False)
            self.add_result('tasks_defined', False, 'DAG file not found')
            return False

        try:
            with open(dag_path, 'r') as f:
                content = f.read()

            tasks = [
                ('extract_task', 'extract_data'),
                ('transform_task', 'transform_data'),
                ('load_task', 'load_data')
            ]

            all_defined = True
            for task_name, function_name in tasks:
                has_task = task_name in content or function_name in content
                self.print_check(f"Task: {task_name}", has_task)
                if not has_task:
                    all_defined = False

            self.add_result('tasks_defined', all_defined, 'All tasks defined' if all_defined else 'Some tasks missing')
            return all_defined
        except Exception as e:
            self.print_check("Tasks check failed", False, str(e))
            self.add_result('tasks_defined', False, 'Check failed')
            return False

    def check_task_dependencies(self) -> bool:
        """Verify task dependencies are set."""
        self.print_section("Task Dependencies")

        dag_path = self.project_root / 'dags' / 'etl_pipeline.py'
        if not dag_path.exists():
            self.print_check("DAG file exists", False)
            self.add_result('task_dependencies', False, 'DAG file not found')
            return False

        try:
            with open(dag_path, 'r') as f:
                content = f.read()

            # Check for dependency operators
            has_dependency = '>>' in content or 'set_downstream' in content or 'set_upstream' in content
            self.print_check("Dependencies defined (>>)", has_dependency)

            # Check specific dependency chain
            has_extract_transform = 'extract_task >> transform_task' in content
            has_transform_load = 'transform_task >> load_task' in content
            self.print_check("extract >> transform", has_extract_transform)
            self.print_check("transform >> load", has_transform_load)

            all_dependencies = has_dependency and has_extract_transform and has_transform_load
            self.add_result('task_dependencies', all_dependencies, 'Dependencies properly set' if all_dependencies else 'Some dependencies missing')
            return all_dependencies
        except Exception as e:
            self.print_check("Dependencies check failed", False, str(e))
            self.add_result('task_dependencies', False, 'Check failed')
            return False

    def check_dag_tags(self) -> bool:
        """Verify DAG tags are configured."""
        self.print_section("DAG Tags")

        dag_path = self.project_root / 'dags' / 'etl_pipeline.py'
        if not dag_path.exists():
            self.print_check("DAG file exists", False)
            self.add_result('dag_tags', False, 'DAG file not found')
            return False

        try:
            with open(dag_path, 'r') as f:
                content = f.read()

            tags = ['etl', 'batch', 'taxi', 'nyc']
            tags_found = []

            for tag in tags:
                if tag in content:
                    tags_found.append(tag)

            has_tags = len(tags_found) > 0
            self.print_check(f"Tags found: {', '.join(tags_found) if tags_found else 'None'}", has_tags)

            all_tags = len(tags_found) >= 3
            self.print_check("Expected tags: etl, batch, taxi, nyc", all_tags)

            self.add_result('dag_tags', all_tags, f'Tags configured: {", ".join(tags_found)}' if tags_found else 'No tags found')
            return all_tags
        except Exception as e:
            self.print_check("Tags check failed", False, str(e))
            self.add_result('dag_tags', False, 'Check failed')
            return False

    def check_dag_description(self) -> bool:
        """Verify DAG has a description."""
        self.print_section("DAG Description")

        dag_path = self.project_root / 'dags' / 'etl_pipeline.py'
        if not dag_path.exists():
            self.print_check("DAG file exists", False)
            self.add_result('dag_description', False, 'DAG file not found')
            return False

        try:
            with open(dag_path, 'r') as f:
                content = f.read()

            has_description = "description=" in content or "description =" in content
            self.print_check("DAG description defined", has_description)

            if has_description:
                import re
                match = re.search(r'description\s*=\s*[\'"]([^\'"]+)[\'"]', content)
                if match:
                    desc = match.group(1)
                    self.print_check(f"Description: {desc}", True)

            self.add_result('dag_description', has_description, 'Description defined' if has_description else 'Description missing')
            return has_description
        except Exception as e:
            self.print_check("Description check failed", False, str(e))
            self.add_result('dag_description', False, 'Check failed')
            return False

    def run(self) -> bool:
        """Run all Phase 3 checks."""
        self.check_dag_syntax()
        self.check_dag_imports()
        self.check_dag_definition()
        self.check_tasks_defined()
        self.check_task_dependencies()
        self.check_dag_tags()
        self.check_dag_description()

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
        verifier = Phase3Verifier()
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