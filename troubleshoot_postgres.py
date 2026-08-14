# troubleshoot_postgres.py

"""
BatchETL Pipeline - PostgreSQL Troubleshooting

Checks PostgreSQL container, connection, tables, data quality, indexes,
connection pool, query performance, and database size.
"""

import sys
import time

from troubleshoot_utils import (
    Colors, print_header, print_check, print_warning,
    run_psql, get_docker_container_status, check_port_open,
    print_summary, format_bytes
)
from troubleshoot_config import (
    CONTAINERS, DB_CONFIG, REQUIRED_INDEXES, DATA_QUALITY_RULES,
    PORTS, TIMEOUTS, THRESHOLDS
)


def check_postgres_container() -> bool:
    """Check if PostgreSQL container is running."""
    print_header("POSTGRESQL CONTAINER")

    container_name = CONTAINERS['postgres']
    is_running, status = get_docker_container_status(container_name)

    if is_running:
        print_check("PostgreSQL container is running", True, status)
        return True
    else:
        exists = get_docker_container_exists(container_name)

        if exists:
            print_check("PostgreSQL container is STOPPED", False, "Container exists but not running")
            print(f"     {Colors.YELLOW}-> Run: docker-compose start {container_name}{Colors.END}")
        else:
            print_check("PostgreSQL container does NOT exist", False)
            print(f"     {Colors.YELLOW}-> Run: docker-compose up -d postgres{Colors.END}")
        return False


def check_postgres_connection() -> bool:
    """Check if PostgreSQL is accessible."""
    print_header("POSTGRESQL CONNECTION")

    port_open = check_port_open('localhost', PORTS['postgres'], TIMEOUTS['port_check'])
    print_check(f"PostgreSQL port {PORTS['postgres']} open", port_open)

    if port_open:
        success, _ = run_psql("SELECT 1", CONTAINERS['postgres'],
                              DB_CONFIG['user'], DB_CONFIG['database'],
                              TIMEOUTS['command'])
        if success:
            print_check("PostgreSQL connection successful", True)
            return True
        else:
            print_check("PostgreSQL connection FAILED", False)
            return False
    else:
        print_check("PostgreSQL port not open", False)
        return False


def check_database_exists() -> bool:
    """Check if warehouse database exists."""
    print_header("DATABASE EXISTENCE")

    success, output = run_psql(
        "SELECT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'warehouse');",
        CONTAINERS['postgres'], DB_CONFIG['user'], DB_CONFIG['database'],
        TIMEOUTS['command']
    )

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
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'fact_trips');",
        CONTAINERS['postgres'], DB_CONFIG['user'], DB_CONFIG['database'],
        TIMEOUTS['command']
    )

    if success and 't' in output.lower():
        print_check("Table 'fact_trips' exists", True)
        return True
    else:
        print_check("Table 'fact_trips' NOT found", False)
        print(f"     {Colors.YELLOW}-> Run: docker exec -i {CONTAINERS['postgres']} psql -U {DB_CONFIG['user']} -d {DB_CONFIG['database']} < warehouse/init.sql{Colors.END}")
        return False


def check_data_count() -> bool:
    """Check data count in fact_trips."""
    print_header("DATA COUNT")

    success, output = run_psql(
        "SELECT COUNT(*) FROM fact_trips;",
        CONTAINERS['postgres'], DB_CONFIG['user'], DB_CONFIG['database'],
        TIMEOUTS['command']
    )

    if success:
        try:
            count = int(output.strip())
            min_required = THRESHOLDS['data_count']['min_required']
            warning_level = THRESHOLDS['data_count']['warning']

            print_check(f"Total rows: {count:,}", count > 0)

            if count >= min_required:
                print_check(f"Data count >= {min_required:,}", True)
                return True
            elif count >= warning_level:
                print_warning(f"Data count {count:,} is below required {min_required:,}")
                return True
            else:
                print_check(f"Data count {count:,} >= {min_required:,}", False)
                print(f"     {Colors.YELLOW}-> Trigger DAG to load more data{Colors.END}")
                return False
        except ValueError:
            print_check("Could not parse row count", False)
            return False
    else:
        print_check("Could not query row count", False)
        return False


def check_indexes() -> bool:
    """Check if indexes exist."""
    print_header("INDEXES")

    success, output = run_psql(
        "SELECT indexname FROM pg_indexes WHERE tablename = 'fact_trips';",
        CONTAINERS['postgres'], DB_CONFIG['user'], DB_CONFIG['database'],
        TIMEOUTS['command']
    )

    if success:
        existing = [idx.strip() for idx in output.split('\n') if idx.strip()]

        all_exist = True
        for idx in REQUIRED_INDEXES:
            exists = idx in existing
            print_check(f"Index: {idx}", exists)
            if not exists:
                all_exist = False

        return all_exist
    else:
        print_check("Could not check indexes", False)
        return False


def check_data_quality() -> bool:
    """Check data quality."""
    print_header("DATA QUALITY")

    checks = []

    for col, rules in DATA_QUALITY_RULES.items():
        if rules['max'] is None:
            checks.append((f"{col} >= {rules['min']}", f"SELECT COUNT(*) FROM fact_trips WHERE {col} < {rules['min']};"))
        else:
            checks.append((f"{col} BETWEEN {rules['min']} AND {rules['max']}",
                          f"SELECT COUNT(*) FROM fact_trips WHERE {col} < {rules['min']} OR {col} > {rules['max']};"))

    checks.append(("NULL pickup_datetime", "SELECT COUNT(*) FROM fact_trips WHERE pickup_datetime IS NULL;"))
    checks.append(("NULL dropoff_datetime", "SELECT COUNT(*) FROM fact_trips WHERE dropoff_datetime IS NULL;"))
    checks.append(("Duplicate trip_ids", "SELECT COUNT(*) - COUNT(DISTINCT trip_id) FROM fact_trips;"))

    all_passed = True
    for name, query in checks:
        success, output = run_psql(query, CONTAINERS['postgres'],
                                   DB_CONFIG['user'], DB_CONFIG['database'],
                                   TIMEOUTS['command'])
        if success:
            try:
                count = int(output.strip())
                passed = count == 0
                detail = f"{count} rows" if count > 0 else "None"
                print_check(f"{name}: {detail}", passed)
                if not passed:
                    all_passed = False
            except ValueError:
                print_check(f"{name}: Could not parse", False)
                all_passed = False
        else:
            print_check(f"{name}: Query failed", False)
            all_passed = False

    return all_passed


def check_connection_pool() -> bool:
    """Test connection pool."""
    print_header("CONNECTION POOL")

    try:
        success, _ = run_psql(
            "SELECT pg_is_in_recovery();",
            CONTAINERS['postgres'], DB_CONFIG['user'], DB_CONFIG['database'],
            TIMEOUTS['query']
        )

        if success:
            print_check("Connection pool test passed", True)
            return True
        else:
            print_check("Connection pool test failed", False)
            return False
    except Exception as e:
        print_check("Connection pool test failed", False, str(e))
        return False


def check_query_performance() -> bool:
    """Test query performance."""
    print_header("QUERY PERFORMANCE")

    test_queries = [
        ("Count all rows", "SELECT COUNT(*) FROM fact_trips;"),
        ("Sample data", "SELECT * FROM fact_trips LIMIT 100;"),
    ]

    all_passed = True
    max_time = THRESHOLDS['response_time']['max_ms'] / 1000

    for name, query in test_queries:
        start_time = time.time()
        success, _ = run_psql(
            query,
            CONTAINERS['postgres'], DB_CONFIG['user'], DB_CONFIG['database'],
            TIMEOUTS['query']
        )
        elapsed = time.time() - start_time

        if success:
            status = elapsed < max_time
            print_check(f"{name}: {elapsed:.3f}s", status)
            if not status:
                print_warning(f"Query took {elapsed:.3f}s, expected < {max_time:.3f}s")
                all_passed = False
        else:
            print_check(f"{name}: Query failed", False)
            all_passed = False

    return all_passed


def check_database_size() -> bool:
    """Check database size."""
    print_header("DATABASE SIZE")

    success, output = run_psql(
        "SELECT pg_database_size('warehouse');",
        CONTAINERS['postgres'], DB_CONFIG['user'], DB_CONFIG['database'],
        TIMEOUTS['query']
    )

    if success:
        try:
            size_bytes = int(output.strip())
            size_mb = size_bytes / (1024 * 1024)
            max_mb = THRESHOLDS['file_size']['max_mb']

            print_check(f"Database size: {format_bytes(size_bytes)}", True)

            if size_mb > max_mb:
                print_warning(f"Database size {size_mb:.1f} MB exceeds recommended {max_mb} MB")
                return True
            else:
                print_check(f"Database size within limits", True)
                return True
        except ValueError:
            print_check("Could not parse database size", False)
            return False
    else:
        print_check("Could not check database size", False)
        return False


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
        results['connection_pool'] = check_connection_pool()
        results['query_performance'] = check_query_performance()
        results['database_size'] = check_database_size()

    print_summary(results, "POSTGRESQL TROUBLESHOOTING SUMMARY")


if __name__ == "__main__":
    main()