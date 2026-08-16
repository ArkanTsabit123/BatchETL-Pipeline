# pipeline_test.py
"""
BatchETL Pipeline Test Suite

This script performs testing of the BatchETL Pipeline including:
- Docker daemon and container status
- PostgreSQL connection and data quality
- Airflow UI, DAG, and password reset
- Streamlit dashboard accessibility
- ETL script files and DAG file existence
- docker-compose.yml validation
- Network connectivity between containers
"""

import subprocess
import sys
import os
import time
import json
import psycopg2
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

class BatchETLTest:
    """Comprehensive testing framework for BatchETL Pipeline"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        self.airflow_container = "batch-etl-airflow"
        self.postgres_container = "batch-etl-postgres"
        self.streamlit_container = "batch-etl-streamlit"
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{timestamp}]"
        
        if level == "INFO":
            print(f"{Colors.BLUE}{prefix}{Colors.END} {message}")
        elif level == "SUCCESS":
            print(f"{Colors.GREEN}{prefix} {Colors.BOLD}✓{Colors.END} {message}")
        elif level == "ERROR":
            print(f"{Colors.RED}{prefix} {Colors.BOLD}✗{Colors.END} {message}")
        elif level == "WARNING":
            print(f"{Colors.YELLOW}{prefix} ⚠ {Colors.END} {message}")
        elif level == "HEADER":
            print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.END}")
        elif level == "SKIP":
            print(f"{Colors.YELLOW}{prefix} ⊘ {Colors.END} {message}")
            
    def run_command(self, command: str, capture_output: bool = True) -> Tuple[int, str, str]:
        try:
            if capture_output:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.returncode, result.stdout.strip(), result.stderr.strip()
            else:
                result = subprocess.run(command, shell=True, timeout=30)
                return result.returncode, "", ""
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def test_docker_running(self) -> bool:
        self.log("Testing Docker daemon...", "INFO")
        code, stdout, stderr = self.run_command("docker info")
        
        if code == 0:
            self.log("Docker daemon is running", "SUCCESS")
            self.test_results.append(("Docker daemon", True))
            return True
        else:
            self.log(f"Docker daemon not running: {stderr}", "ERROR")
            self.test_results.append(("Docker daemon", False))
            return False
    
    def test_container_status(self, container_name: str) -> bool:
        code, stdout, stderr = self.run_command(
            f"docker ps --filter name={container_name} --format '{{{{.Status}}}}'"
        )
        
        if code == 0 and stdout:
            status = stdout.replace("'", "").strip()
            if status.startswith("Up") or status.startswith("Running"):
                self.log(f"Container {container_name} is running", "SUCCESS")
                self.test_results.append((f"Container {container_name}", True))
                return True
            else:
                self.log(f"Container {container_name} status: {status}", "WARNING")
                self.test_results.append((f"Container {container_name}", False))
                return False
        else:
            self.log(f"Container {container_name} not found", "ERROR")
            self.test_results.append((f"Container {container_name}", False))
            return False
    
    def test_containers(self) -> bool:
        self.log("Checking container status...", "HEADER")
        
        containers = [
            self.airflow_container,
            self.postgres_container,
            self.streamlit_container
        ]
        
        all_running = True
        for container in containers:
            if not self.test_container_status(container):
                all_running = False
        
        return all_running
    
    def test_postgres_connection(self) -> bool:
        self.log("Testing PostgreSQL connection...", "INFO")
        
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="admin",
                password="admin",
                database="warehouse",
                connect_timeout=10
            )
            
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'fact_trips'
                )
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                self.log("Table fact_trips does not exist", "ERROR")
                self.test_results.append(("PostgreSQL table exists", False))
                conn.close()
                return False
            
            cursor.execute("SELECT COUNT(*) FROM fact_trips")
            row_count = cursor.fetchone()[0]
            
            self.log(f"Table fact_trips exists with {row_count:,} rows", "SUCCESS")
            self.test_results.append(("PostgreSQL connection", True))
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    AVG(fare_amount) as avg_fare,
                    AVG(trip_distance) as avg_distance
                FROM fact_trips
                WHERE fare_amount > 0
            """)
            stats = cursor.fetchone()
            
            if stats and stats[0] > 0:
                self.log(f"Data quality check: {stats[0]:,} trips, avg fare ${stats[1]:.2f}", "SUCCESS")
                self.test_results.append(("Data quality", True))
            else:
                self.log("No valid data found in fact_trips", "WARNING")
                self.test_results.append(("Data quality", False))
            
            conn.close()
            return True
            
        except psycopg2.OperationalError as e:
            self.log(f"PostgreSQL connection failed: {e}", "ERROR")
            self.test_results.append(("PostgreSQL connection", False))
            return False
        except Exception as e:
            self.log(f"PostgreSQL test error: {e}", "ERROR")
            self.test_results.append(("PostgreSQL connection", False))
            return False
    
    def test_airflow_ui(self) -> bool:
        self.log("Testing Airflow UI...", "INFO")
        
        try:
            response = requests.get(
                "http://localhost:8080",
                timeout=10,
                allow_redirects=True
            )
            
            if response.status_code in [200, 302]:
                self.log("Airflow UI is accessible", "SUCCESS")
                self.test_results.append(("Airflow UI", True))
                return True
            else:
                self.log(f"Airflow UI returned status {response.status_code}", "ERROR")
                self.test_results.append(("Airflow UI", False))
                return False
                
        except requests.ConnectionError:
            self.log("Airflow UI connection failed", "ERROR")
            self.test_results.append(("Airflow UI", False))
            return False
        except Exception as e:
            self.log(f"Airflow UI test error: {e}", "ERROR")
            self.test_results.append(("Airflow UI", False))
            return False
    
    def test_airflow_dag(self) -> bool:
        self.log("Testing Airflow DAG...", "INFO")
        
        code, stdout, stderr = self.run_command(
            f"docker exec {self.airflow_container} airflow dags list"
        )
        
        if code == 0 and "etl_pipeline" in stdout:
            self.log("etl_pipeline DAG found in Airflow", "SUCCESS")
            self.test_results.append(("Airflow DAG exists", True))
            return True
        else:
            self.log("etl_pipeline DAG not found", "ERROR")
            self.test_results.append(("Airflow DAG exists", False))
            return False
    
    def test_streamlit_dashboard(self) -> bool:
        self.log("Testing Streamlit dashboard...", "INFO")
        
        try:
            response = requests.get(
                "http://localhost:8501",
                timeout=10,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                self.log("Streamlit dashboard is accessible", "SUCCESS")
                self.test_results.append(("Streamlit dashboard", True))
                return True
            else:
                self.log(f"Streamlit dashboard returned status {response.status_code}", "ERROR")
                self.test_results.append(("Streamlit dashboard", False))
                return False
                
        except requests.ConnectionError:
            self.log("Streamlit dashboard connection failed", "ERROR")
            self.test_results.append(("Streamlit dashboard", False))
            return False
        except Exception as e:
            self.log(f"Streamlit dashboard test error: {e}", "ERROR")
            self.test_results.append(("Streamlit dashboard", False))
            return False
    
    def test_airflow_password(self) -> bool:
        self.log("Testing Airflow password reset...", "INFO")
        
        command = f"""
            docker exec {self.airflow_container} bash -c "
                airflow users delete -u admin 2>/dev/null;
                airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com 2>/dev/null
            "
        """
        
        code, stdout, stderr = self.run_command(command)
        
        if code == 0:
            self.log("Airflow password reset successful", "SUCCESS")
            self.test_results.append(("Airflow password reset", True))
            return True
        else:
            self.log("Airflow password reset failed", "ERROR")
            self.test_results.append(("Airflow password reset", False))
            return False
    
    def test_etl_files(self) -> bool:
        self.log("Testing ETL script files...", "INFO")
        
        scripts = [
            "scripts/extract.py",
            "scripts/transform.py",
            "scripts/load.py"
        ]
        
        all_exist = True
        for script in scripts:
            if os.path.exists(script):
                self.log(f"File {script} exists", "SUCCESS")
                self.test_results.append((f"File {script}", True))
            else:
                self.log(f"File {script} not found", "ERROR")
                self.test_results.append((f"File {script}", False))
                all_exist = False
        
        return all_exist
    
    def test_dag_file(self) -> bool:
        self.log("Testing DAG file...", "INFO")
        
        if os.path.exists("dags/etl_pipeline.py"):
            self.log("DAG file exists", "SUCCESS")
            self.test_results.append(("DAG file", True))
            return True
        else:
            self.log("DAG file not found", "ERROR")
            self.test_results.append(("DAG file", False))
            return False
    
    def test_docker_compose(self) -> bool:
        self.log("Testing docker-compose.yml...", "INFO")
        
        if not os.path.exists("docker-compose.yml"):
            self.log("docker-compose.yml not found", "ERROR")
            self.test_results.append(("docker-compose.yml", False))
            return False
        
        code, stdout, stderr = self.run_command("docker-compose config -q")
        
        if code == 0:
            self.log("docker-compose.yml is valid", "SUCCESS")
            self.test_results.append(("docker-compose.yml", True))
            return True
        else:
            self.log("docker-compose.yml validation failed", "ERROR")
            self.test_results.append(("docker-compose.yml", False))
            return False
    
    def test_airflow_logs(self) -> bool:
        self.log("Checking Airflow logs...", "INFO")
        
        code, stdout, stderr = self.run_command(
            f"docker logs {self.airflow_container} 2>&1 | tail -50"
        )
        
        combined = stdout + stderr
        if "ERROR" in combined:
            errors = combined.count("ERROR")
            if errors > 5:
                self.log(f"Found {errors} errors in Airflow logs", "WARNING")
                self.test_results.append(("Airflow logs", False))
                return False
        
        self.log("Airflow logs look clean", "SUCCESS")
        self.test_results.append(("Airflow logs", True))
        return True

    def test_network_connectivity(self) -> bool:
        """Test network connectivity between containers using multiple methods"""
        self.log("Testing network connectivity...", "INFO")
        
        # Method 1: DNS Resolution Test - HAPUS 2>/dev/null
        code, stdout, stderr = self.run_command(
            f"docker exec {self.airflow_container} getent hosts {self.postgres_container}"
        )
        
        if code == 0 and stdout and len(stdout.strip()) > 0:
            self.log("Network connectivity: DNS resolution OK", "SUCCESS")
            self.test_results.append(("Network connectivity", True))
            return True
        
        # Method 2: Python socket connection - HAPUS 2>/dev/null
        code, stdout, stderr = self.run_command(
            f"docker exec {self.airflow_container} python -c \"import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(5); result = s.connect_ex(('{self.postgres_container}', 5432)); s.close(); print('OK' if result == 0 else 'FAIL')\""
        )
        
        if "OK" in stdout:
            self.log("Network connectivity: Airflow -> PostgreSQL OK (socket test)", "SUCCESS")
            self.test_results.append(("Network connectivity", True))
            return True
        
        # Method 3: Bash /dev/tcp - HAPUS 2>/dev/null
        code, stdout, stderr = self.run_command(
            f"docker exec {self.airflow_container} bash -c \"timeout 5 bash -c 'echo > /dev/tcp/{self.postgres_container}/5432' && echo 'OPEN' || echo 'CLOSED'\""
        )
        
        if "OPEN" in stdout:
            self.log("Network connectivity: Airflow -> PostgreSQL OK (bash /dev/tcp)", "SUCCESS")
            self.test_results.append(("Network connectivity", True))
            return True
        
        # Method 4: Python psycopg2 - HAPUS 2>/dev/null
        code, stdout, stderr = self.run_command(
            f"docker exec {self.airflow_container} python -c \"import psycopg2; conn = psycopg2.connect(host='{self.postgres_container}', port=5432, user='admin', password='admin', database='warehouse', connect_timeout=5); conn.close(); print('CONNECTED')\""
        )
        
        if "CONNECTED" in stdout:
            self.log("Network connectivity: Airflow -> PostgreSQL OK (psycopg2)", "SUCCESS")
            self.test_results.append(("Network connectivity", True))
            return True
        
        # Method 5: docker inspect
        code, stdout, stderr = self.run_command(
            f"docker inspect {self.airflow_container} --format '{{{{.NetworkSettings.Networks}}}}'"
        )
        
        if self.postgres_container in stdout:
            self.log("Network connectivity: Containers share same network", "SUCCESS")
            self.test_results.append(("Network connectivity", True))
            return True
        
        self.log("Network connectivity failed - no method succeeded", "ERROR")
        self.test_results.append(("Network connectivity", False))
        return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        self.log("=" * 70, "HEADER")
        self.log("BATCHETL PIPELINE - COMPREHENSIVE TEST SUITE", "HEADER")
        self.log("=" * 70, "HEADER")
        self.log(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
        self.log("=" * 70, "HEADER")
        
        tests = {
            "Docker daemon": self.test_docker_running,
            "Containers": self.test_containers,
            "PostgreSQL": self.test_postgres_connection,
            "Airflow UI": self.test_airflow_ui,
            "Airflow DAG": self.test_airflow_dag,
            "Airflow password": self.test_airflow_password,
            "Airflow logs": self.test_airflow_logs,
            "Streamlit dashboard": self.test_streamlit_dashboard,
            "ETL files": self.test_etl_files,
            "DAG file": self.test_dag_file,
            "docker-compose.yml": self.test_docker_compose,
            "Network connectivity": self.test_network_connectivity
        }
        
        results = {}
        
        for test_name, test_func in tests.items():
            try:
                results[test_name] = test_func()
            except Exception as e:
                self.log(f"Test {test_name} failed with exception: {e}", "ERROR")
                results[test_name] = False
        
        return results
    
    def print_summary(self, results: Dict[str, bool]) -> None:
        self.log("=" * 70, "HEADER")
        self.log("TEST SUMMARY", "HEADER")
        self.log("=" * 70, "HEADER")
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        failed = total - passed
        duration = (datetime.now() - self.start_time).total_seconds()
        
        for test_name, result in results.items():
            status = "PASSED" if result else "FAILED"
            color = Colors.GREEN if result else Colors.RED
            print(f"{color}{status:6}{Colors.END} - {test_name}")
        
        self.log("=" * 70, "HEADER")
        
        if failed == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED!{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}{failed} test(s) FAILED{Colors.END}")
        
        print(f"Passed: {Colors.GREEN}{passed}{Colors.END} / {total}")
        print(f"Failed: {Colors.RED}{failed}{Colors.END} / {total}")
        print(f"Duration: {duration:.2f} seconds")
        
        self.log("=" * 70, "HEADER")
        
        if failed == 0:
            self.log("PIPELINE IS PRODUCTION READY", "SUCCESS")
        else:
            self.log("PIPELINE NEEDS ATTENTION - Please check failed tests", "ERROR")
    
    def generate_report(self, results: Dict[str, bool]) -> str:
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "total_tests": len(results),
            "passed_tests": sum(1 for v in results.values() if v),
            "failed_tests": sum(1 for v in results.values() if not v),
            "results": results
        }
        
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Report saved to {report_file}", "INFO")
        return report_file


def main() -> int:
    tester = BatchETLTest()
    results = tester.run_all_tests()
    tester.print_summary(results)
    tester.generate_report(results)
    
    if all(results.values()):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())