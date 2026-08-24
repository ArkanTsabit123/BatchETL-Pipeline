# Status Monitor.py
"""
Status Monitor for BatchETL Pipeline
This script checks the status of various components in the BatchETL pipeline:
- Apache Airflow DAG status
- PostgreSQL database status
- Grafana dashboards
- Prometheus metrics
Usage:
    python Status Monitor.py
"""

import subprocess
import requests
import time
from datetime import datetime
from typing import Dict, Any, List, Tuple
import json
import socket

# Configuration
AIRFLOW_URL = "http://localhost:8080"
AIRFLOW_USER = "admin"
AIRFLOW_PASSWORD = "DNad5swKETyFGms2"
GRAFANA_URL = "http://localhost:3000"
PROMETHEUS_URL = "http://localhost:9090"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432


def run_command(command: str) -> Tuple[str, str]:
    """Execute shell command and return output"""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "", "Command timed out"
    except Exception as e:
        return "", str(e)


def check_port(host: str, port: int, timeout: int = 2) -> bool:
    """Check if a network port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except socket.error:
        return False


def check_airflow_dag_status() -> Dict[str, Any]:
    """Check Airflow DAG status"""
    print("\n" + "=" * 60)
    print("AIRFLOW DAG STATUS")
    print("=" * 60)

    result = {
        "dag_name": "etl_pipeline",
        "status": "unknown",
        "last_run": None,
        "extract": None,
        "transform": None,
        "load": None
    }

    if not check_port("localhost", 8080):
        print("[FAIL] Airflow not running (port 8080 closed)")
        result["status"] = "not_running"
        return result

    try:
        # Get DAG runs
        cmd = "docker exec -it batch-etl-airflow airflow dags list-runs --dag-id etl_pipeline --output json"
        stdout, stderr = run_command(cmd)

        if stdout:
            try:
                runs = json.loads(stdout)
                if runs:
                    latest = runs[0]
                    result["status"] = latest.get("state", "unknown")
                    result["last_run"] = latest.get("execution_date")
                    print(f"[OK] DAG Status: {result['status']}")
                    print(f"   Last Run: {result['last_run']}")
                else:
                    print("[WARN] No DAG runs found")
            except json.JSONDecodeError:
                # Fallback to text parsing
                lines = stdout.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split('|')
                    if len(parts) >= 3:
                        result["status"] = parts[2].strip()
                        print(f"[OK] DAG Status: {result['status']}")
                else:
                    print("[WARN] No DAG runs found")
        else:
            print("[WARN] No output from airflow command")

    except Exception as e:
        print(f"[FAIL] Error checking Airflow: {e}")

    return result


def check_grafana_dashboards() -> Dict[str, Any]:
    """Check if Grafana has data"""
    print("\n" + "=" * 60)
    print("GRAFANA DASHBOARDS")
    print("=" * 60)

    result = {
        "pipeline": {"status": "unknown", "has_data": False},
        "database": {"status": "unknown", "has_data": False},
        "quality": {"status": "unknown", "has_data": False}
    }

    if not check_port("localhost", 3000):
        print("[FAIL] Grafana not running (port 3000 closed)")
        return result

    try:
        # Check Grafana health
        response = requests.get(f"{GRAFANA_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Grafana is running")
        else:
            print("[WARN] Grafana API not responding")
            return result
    except requests.RequestException:
        print("[WARN] Grafana not responding")
        return result

    # Check dashboards via API
    try:
        auth = (AIRFLOW_USER, AIRFLOW_PASSWORD)
        response = requests.get(
            f"{GRAFANA_URL}/api/search",
            auth=auth,
            timeout=5
        )
        if response.status_code == 200:
            dashboards = response.json()
            found = []
            for d in dashboards:
                title = d.get("title", "")
                if "Pipeline" in title or "ETL" in title:
                    result["pipeline"]["status"] = "found"
                    found.append("ETL Pipeline")
                elif "Database" in title:
                    result["database"]["status"] = "found"
                    found.append("Database Performance")
                elif "Quality" in title:
                    result["quality"]["status"] = "found"
                    found.append("Data Quality")

            if found:
                print(f"[OK] Found dashboards: {', '.join(found)}")
            else:
                print("[WARN] No dashboards found")
        else:
            print(f"[WARN] Grafana API returned status: {response.status_code}")
    except requests.RequestException as e:
        print(f"[WARN] Could not check Grafana dashboards: {e}")

    return result


def check_prometheus_metrics() -> Dict[str, Any]:
    """Check if Prometheus has metrics"""
    print("\n" + "=" * 60)
    print("PROMETHEUS METRICS")
    print("=" * 60)

    result = {
        "airflow_metrics": False,
        "postgres_metrics": False,
        "etl_metrics": False,
        "targets": []
    }

    if not check_port("localhost", 9090):
        print("[FAIL] Prometheus not running (port 9090 closed)")
        return result

    # Check targets
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/targets", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                targets = data.get("data", {}).get("activeTargets", [])
                up_targets = []
                for target in targets:
                    state = target.get("health", "unknown")
                    labels = target.get("labels", {})
                    job = labels.get("job", "unknown")
                    if state == "up":
                        up_targets.append(job)
                        result["targets"].append({"job": job, "status": "UP"})
                    else:
                        result["targets"].append({"job": job, "status": state})

                print(f"[OK] Prometheus targets: {len(up_targets)}/{len(targets)} UP")
                for t in result["targets"]:
                    print(f"   - {t['job']}: {t['status']}")
    except requests.RequestException as e:
        print(f"[WARN] Could not check Prometheus: {e}")

    # Check specific metrics
    metrics_queries = {
        "airflow_dag_run_state": "airflow_metrics",
        "pg_stat_database_numbackends": "postgres_metrics",
        "etl_rows_processed": "etl_metrics"
    }

    for query, key in metrics_queries.items():
        try:
            response = requests.get(
                f"{PROMETHEUS_URL}/api/v1/query?query={query}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    results = data.get("data", {}).get("result", [])
                    if results:
                        result[key] = True
                        print(f"[OK] {query} has data")
                    else:
                        print(f"[WARN] {query} has no data yet")
                else:
                    print(f"[WARN] {query} query failed")
            else:
                print(f"[WARN] Prometheus API returned status: {response.status_code}")
        except requests.RequestException as e:
            print(f"[WARN] Could not query {query}: {e}")

    return result


def check_postgresql() -> Dict[str, Any]:
    """Check PostgreSQL status and data"""
    print("\n" + "=" * 60)
    print("POSTGRESQL STATUS")
    print("=" * 60)

    result = {
        "running": False,
        "total_rows": 0,
        "table_exists": False
    }

    if not check_port("localhost", 5432):
        print("[FAIL] PostgreSQL not running (port 5432 closed)")
        return result

    result["running"] = True
    print("[OK] PostgreSQL is running")

    # Check row count
    cmd = "docker exec -it batch-etl-postgres psql -U admin -d warehouse -t -c 'SELECT COUNT(*) FROM fact_trips;' 2>&1"
    stdout, stderr = run_command(cmd)

    if stdout and stdout.isdigit():
        result["total_rows"] = int(stdout)
        result["table_exists"] = True
        print(f"[OK] Total rows in fact_trips: {result['total_rows']:,}")
    elif "does not exist" in stderr or "does not exist" in stdout:
        print("[WARN] fact_trips table does not exist yet")
        result["table_exists"] = False
    else:
        print("[WARN] Could not query fact_trips")

    return result


def check_streamlit_dashboard() -> Dict[str, Any]:
    """Check Streamlit dashboard status"""
    print("\n" + "=" * 60)
    print("STREAMLIT DASHBOARD")
    print("=" * 60)

    result = {
        "local": False,
        "cloud": False
    }

    # Check local Streamlit
    if check_port("localhost", 8501):
        result["local"] = True
        print("[OK] Local Streamlit running: http://localhost:8501")
    else:
        print("[WARN] Local Streamlit not running (port 8501 closed)")

    # Check cloud
    try:
        response = requests.get("https://batchetl.streamlit.app", timeout=10)
        if response.status_code == 200:
            result["cloud"] = True
            print("[OK] Cloud Streamlit running: https://batchetl.streamlit.app")
        else:
            print(f"[WARN] Cloud Streamlit returned: {response.status_code}")
    except requests.RequestException:
        print("[WARN] Could not reach cloud Streamlit")

    return result


def check_screenshots() -> Dict[str, Any]:
    """Check screenshot status"""
    print("\n" + "=" * 60)
    print("SCREENSHOTS STATUS")
    print("=" * 60)

    import os

    screenshots_folder = "screenshots/"
    required = [
        "01-folder-structure.png",
        "02-dataset-downloaded.png",
        "03-airflow-dag-list.png",
        "04-airflow-grid-success.png",
        "05-airflow-tree-success.png",
        "06-postgres-data.png",
        "07-dashboard-overview.png",
        "08-dashboard-charts.png",
        "09-airflow-dag-code.png",
        "10-extract-script.png",
        "11-transform-script.png",
        "12-load-script.png",
        "13-dashboard-code.png",
        "14-docker-compose.png",
        "15-airflow-log.png",
        "16-dashboard-with-filter.png",
        "17-streamlit-cloud-deploy.png",
        "18-live-demo-dashboard.png",
        "19-live-demo-url.png",
        "architecture-diagram.png",
        "data-flow-diagram.png",
        "erd-diagram.png",
        "20-grafana-pipeline.png",
        "21-grafana-database.png",
        "22-grafana-data-quality.png",
        "23-prometheus-targets.png"
    ]

    result = {
        "present": [],
        "missing": []
    }

    if os.path.exists(screenshots_folder):
        files = os.listdir(screenshots_folder)
        for req in required:
            if req in files:
                result["present"].append(req)
            else:
                result["missing"].append(req)

        print(f"[OK] Screenshots present: {len(result['present'])}")
        print(f"[WARN] Screenshots missing: {len(result['missing'])}")
        if result["missing"]:
            print("   Missing:")
            for m in result["missing"]:
                print(f"     - {m}")
    else:
        print("[FAIL] Screenshots folder not found")

    return result


def check_services() -> Dict[str, Any]:
    """Check all services status"""
    print("\n" + "=" * 60)
    print("SERVICES STATUS")
    print("=" * 60)

    services = {
        "airflow": check_port("localhost", 8080),
        "postgres": check_port("localhost", 5432),
        "grafana": check_port("localhost", 3000),
        "prometheus": check_port("localhost", 9090),
        "streamlit": check_port("localhost", 8501),
        "postgres_exporter": check_port("localhost", 9187)
    }

    for name, status in services.items():
        if status:
            print(f"[OK] {name} is running")
        else:
            print(f"[FAIL] {name} is not running")

    return services


def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("BATCHETL - CHECK EVERYTHING")
    print("=" * 60)
    print(f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # Check services
    results["services"] = check_services()

    # Check PostgreSQL
    results["postgresql"] = check_postgresql()

    # Check Airflow DAG
    results["airflow"] = check_airflow_dag_status()

    # Check Prometheus
    results["prometheus"] = check_prometheus_metrics()

    # Check Grafana
    results["grafana"] = check_grafana_dashboards()

    # Check Streamlit
    results["streamlit"] = check_streamlit_dashboard()

    # Check Screenshots
    results["screenshots"] = check_screenshots()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print("\nServices:")
    for name, status in results["services"].items():
        print(f"   {name}: {'RUNNING' if status else 'STOPPED'}")

    print(f"\nPostgreSQL: {results['postgresql']['total_rows']:,} rows")
    print(f"\nAirflow DAG: {results['airflow']['status']}")

    print("\nPrometheus Targets:")
    for t in results["prometheus"]["targets"]:
        print(f"   - {t['job']}: {t['status']}")

    print("\nScreenshots:")
    present = len(results["screenshots"]["present"])
    missing = len(results["screenshots"]["missing"])
    print(f"   Present: {present}")
    print(f"   Missing: {missing}")

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)

    if missing > 0:
        print("\n1. Screenshots to capture:")
        for m in results["screenshots"]["missing"]:
            if m.startswith("20") or m.startswith("21") or m.startswith("22") or m.startswith("23"):
                print(f"   - {m} (Grafana/Prometheus - capture after pipeline runs)")
            else:
                print(f"   - {m}")

    if results["airflow"]["status"] == "queued":
        print("\n2. Trigger DAG:")
        print("   docker exec -it batch-etl-airflow airflow dags trigger etl_pipeline")

    if not results["prometheus"]["airflow_metrics"]:
        print("\n3. Wait for metrics to appear (5-10 min after DAG completes)")

    print("\n" + "=" * 60)

    # Save to file
    filename = f"check_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nDetailed report saved to: {filename}")


if __name__ == "__main__":
    main()