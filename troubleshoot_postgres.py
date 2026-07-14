# troubleshoot_postgres.py
"""
BatchETL Pipeline - PostgreSQL Troubleshooting

Checks:
    - PostgreSQL container status
    - PostgreSQL connection
    - Database exists (warehouse)
    - fact_trips table exists
    - Data count
    - Data quality (outliers, nulls)
    - Indexes exist
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple, List, Dict, Optional


class Colors:
    """Terminal color codes."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str) -> None:
    """Print formatted header."""
    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}\n")


def print_check(text: str, status: bool, detail: str = "") -> None:
    """Print check result."""
    icon = "✓" if status else "✗"
    color = Colors.GREEN if status else Colors.RED
    if detail:
        print(f"  {color}{icon} {text}{Colors.END}")
        print(f"     {Colors.CYAN}-> {detail}{Colors.END}")
    else:
        print(f"  {color}{icon} {text}{Colors.END}")


def run_command(command: List[str]) -> Tuple[bool, str]:
    """Run a shell command and return status and output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return False, str(e)


def run_psql(query: str) -> Tuple[bool, str]:
    """Run a PostgreSQL query via docker exec."""
    return run_command([
        'docker', 'exec', 'batch-etl-postgres',
        'psql', '-U', 'admin', '-d', 'warehouse',
        '-t', '-c', query
    ])


def check_postgres_container() -> bool:
    """Check if PostgreSQL container is running."""
    print_header("POSTGRESQL CONTAINER")

    success, output = run_command([
        'docker', 'ps', '--filter', 'name=batch-etl-postgres',
        '--format', '{{.Status}}'
    ])

    if success and output:
        print_check("PostgreSQL container is running", True, output)
        return True
    else:
        exists, _ = run_command([
            'docker', 'ps', '-a', '--filter', 'name=batch-etl-postgres',
            '--format', '{{.Status}}'
        ])

        if exists and output:
            print_check("PostgreSQL container is STOPPED", False, "Container exists but not running")
            print(f"     {Colors.YELLOW}-> Run: docker-compose start postgres{Colors.END}")
        else:
            print_check("PostgreSQL container does NOT exist", False)
            print(f"     {Colors.YELLOW}-> Run: docker-compose up -d postgres{Colors.END}")
        return False


def check_postgres_connection() -> bool:
    """Check if PostgreSQL is accessible."""
    print_header("POSTGRESQL CONNECTION")

    success, output = run_psql("SELECT 1")

    if success:
        print_check("PostgreSQL connection successful", True)
        return True
    else:
        print_check("PostgreSQL connection FAILED", False, output or "Check container status")
        return False


def check_database_exists() -> bool:
    """Check if warehouse database exists."""
    print_header("DATABASE EXISTENCE")

    success, output = run_psql("SELECT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'warehouse');")

    if success and 't' in output.lower():
        print_check("Database 'warehouse' exists", True)
        return True
    else:
        print_check("Database 'warehouse' NOT found", False)
        print(f"     {Colors.YELLOW}-> Database should be created automatically on container start{Colors.END}")
        return False


def check_table_exists() -> bool:
    """Check if fact_trips table exists."""
    print_header("TABLE EXISTENCE")

    success, output = run_psql(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'fact_trips');"
    )

    if success and 't' in output.lower():
        print_check("Table 'fact_trips' exists", True)
        return True
    else:
        print_check("Table 'fact_trips' NOT found", False)
        print(f"     {Colors.YELLOW}-> Run init.sql: docker exec -i batch-etl-postgres psql -U admin -d warehouse < warehouse/init.sql{Colors.END}")
        return False


def check_data_count() -> bool:
    """Check data count in fact_trips."""
    print_header("DATA COUNT")

    success, output = run_psql("SELECT COUNT(*) FROM fact_trips;")

    if success:
        try:
            count = int(output.strip())
            if count > 0:
                print_check(f"Total rows: {count:,}", True)
                print_check("Data exists in fact_trips", True, f"{count:,} rows")
                return True
            else:
                print_check("No data in fact_trips", False)
                print(f"     {Colors.YELLOW}-> Trigger DAG to load data{Colors.END}")
                return False
        except ValueError:
            print_check("Could not parse row count", False, output)
            return False
    else:
        print_check("Could not query row count", False, output)
        return False


def check_indexes() -> bool:
    """Check if indexes exist."""
    print_header("INDEXES")

    expected_indexes = ['idx_pickup_datetime', 'idx_pickup_day', 'idx_fare_amount']

    success, output = run_psql(
        "SELECT indexname FROM pg_indexes WHERE tablename = 'fact_trips';"
    )

    if success:
        existing = [idx.strip() for idx in output.split('\n') if idx.strip()]

        all_exist = True
        for idx in expected_indexes:
            exists = idx in existing
            print_check(f"Index: {idx}", exists)
            if not exists:
                all_exist = False

        return all_exist
    else:
        print_check("Could not check indexes", False, output)
        return False


def check_data_quality() -> bool:
    """Check data quality."""
    print_header("DATA QUALITY")

    checks = [
        ("fare_amount values > 0", "SELECT COUNT(*) FROM fact_trips WHERE fare_amount <= 0;"),
        ("trip_distance values > 0", "SELECT COUNT(*) FROM fact_trips WHERE trip_distance <= 0;"),
        ("fare_amount < 500", "SELECT COUNT(*) FROM fact_trips WHERE fare_amount >= 500;"),
        ("trip_distance < 100", "SELECT COUNT(*) FROM fact_trips WHERE trip_distance >= 100;"),
        ("NULL pickup_datetime", "SELECT COUNT(*) FROM fact_trips WHERE pickup_datetime IS NULL;"),
    ]

    all_passed = True
    for name, query in checks:
        success, output = run_psql(query)
        if success:
            try:
                count = int(output.strip())
                passed = count == 0
                print_check(f"{name}: {count} rows", passed)
                if not passed:
                    all_passed = False
            except ValueError:
                print_check(f"{name}: Could not parse", False)
                all_passed = False
        else:
            print_check(f"{name}: Query failed", False)
            all_passed = False

    return all_passed


def main() -> None:
    """Main entry point."""
    print_header("BATCHETL PIPELINE - POSTGRESQL TROUBLESHOOTING")

    results = {
        'container': check_postgres_container(),
        'connection': check_postgres_connection(),
        'database': check_database_exists(),
        'table': check_table_exists(),
    }

    if results['table']:
        results['data_count'] = check_data_count()
        results['indexes'] = check_indexes()
        results['data_quality'] = check_data_quality()

    print_header("POSTGRESQL TROUBLESHOOTING SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n  Total Checks: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {total - passed}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All PostgreSQL checks passed!{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some PostgreSQL checks failed.{Colors.END}")
        print(f"{Colors.YELLOW}Please fix the issues above before proceeding.{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()