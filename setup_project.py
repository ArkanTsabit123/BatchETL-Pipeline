# setup_project.py
"""
Setup script for BatchETL Pipeline Project.

Creates project structure, configuration files, and development environment
for the NYC Taxi Data ETL pipeline.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class Colors:
    """Terminal color codes."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ProjectSetup:
    """Project setup and configuration manager."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / 'venv'
        self.requirements_file = self.project_root / 'requirements.txt'
        self.env_file = self.project_root / '.env'
        self.gitignore_file = self.project_root / '.gitignore'

    def print_header(self, text: str) -> None:
        """Print formatted header."""
        print(f"\n{Colors.CYAN}{'=' * 70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 70}{Colors.END}\n")

    def print_section(self, text: str) -> None:
        """Print section header."""
        print(f"\n{Colors.YELLOW}{text}{Colors.END}")
        print(f"{Colors.YELLOW}{'-' * 50}{Colors.END}")

    def print_status(self, text: str, status: bool, detail: str = "") -> None:
        """Print status message with color."""
        icon = "[OK]" if status else "[FAIL]"
        color = Colors.GREEN if status else Colors.RED
        print(f"  {color}{icon} {text}{Colors.END}")
        if detail:
            print(f"     {Colors.CYAN}-> {detail}{Colors.END}")

    def create_directory_structure(self) -> bool:
        """Create project directory structure."""
        self.print_section("Creating Directory Structure")

        directories = [
            'archive',
            'dags',
            'scripts',
            'data/raw',
            'data/staging',
            'warehouse',
            'dashboard',
            'screenshots',
            'docs/diagrams',
            'batchetl-streamlit/data',
            'batchetl-streamlit/.streamlit'
        ]

        all_created = True
        for directory in directories:
            path = self.project_root / directory
            try:
                path.mkdir(parents=True, exist_ok=True)
                self.print_status(f"Created: {directory}", True)
            except Exception as e:
                self.print_status(f"Failed: {directory}", False, str(e))
                all_created = False

        return all_created

    def create_init_files(self) -> bool:
        """Create __init__.py files for Python packages."""
        self.print_section("Creating Python Package Files")

        init_files = [
            'dags/__init__.py',
            'scripts/__init__.py',
            'dashboard/__init__.py'
        ]

        all_created = True
        for init_file in init_files:
            path = self.project_root / init_file
            try:
                path.touch(exist_ok=True)
                self.print_status(f"Created: {init_file}", True)
            except Exception as e:
                self.print_status(f"Failed: {init_file}", False, str(e))
                all_created = False

        return all_created

    def create_requirements(self) -> bool:
        """Create requirements.txt file."""
        self.print_section("Creating Requirements File")

        requirements_content = """
# Core ETL dependencies
pandas==2.0.3
numpy==1.24.3
psycopg2-binary==2.9.9
sqlalchemy==2.0.19

# Orchestration
apache-airflow==2.7.3

# Dashboard
streamlit==1.29.0
plotly==5.18.0

# Development
python-dotenv==1.0.0
requests==2.31.0
        """.strip()

        try:
            with open(self.requirements_file, 'w') as f:
                f.write(requirements_content)
            self.print_status("Created: requirements.txt", True)
            return True
        except Exception as e:
            self.print_status("Failed: requirements.txt", False, str(e))
            return False

    def create_env_file(self) -> bool:
        """Create .env file."""
        self.print_section("Creating Environment File")

        env_content = """
# Airflow Configuration
AIRFLOW_UID=50000
AIRFLOW_GID=50000
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__WEBSERVER__SECRET_KEY=your-secret-key-here
AIRFLOW__WEBSERVER__DEFAULT_UI_TIMEZONE=Asia/Jakarta

# PostgreSQL Configuration
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=warehouse
POSTGRES_PORT=5432

# Airflow Connection
AIRFLOW_CONN_POSTGRES=postgresql://admin:admin@postgres:5432/warehouse

# Project Paths
PYTHONPATH=/opt/airflow
DATA_PATH=/opt/airflow/data
        """.strip()

        try:
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            self.print_status("Created: .env", True)
            return True
        except Exception as e:
            self.print_status("Failed: .env", False, str(e))
            return False

    def create_gitignore(self) -> bool:
        """Create .gitignore file."""
        self.print_section("Creating Git Ignore File")

        gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
.coverage
htmlcov/
.tox/
.mypy_cache/
.dmypy.json
dmypy.json
*.log

# Environment
.env
.venv
.env.local
.env.*.local

# Data files
*.csv
*.parquet
*.db
*.sqlite
*.sqlite3
data/raw/*.csv
data/staging/*.csv
!data/raw/.gitkeep
!data/staging/.gitkeep

# Docker
*.pid
docker-compose.override.yml

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# Airflow
logs/
airflow.db
airflow.cfg
webserver_config.py
dags/__pycache__/
airflow-scheduler.pid
airflow-webserver.pid

# Streamlit
.streamlit/secrets.toml

# Screenshots (keep directory structure)
screenshots/*.png
!screenshots/.gitkeep

# Reports
phase*_verification.json
phase*_verification_report.txt
verification_results.json

# Jupyter
.ipynb_checkpoints/
*.ipynb
        """.strip()

        try:
            with open(self.gitignore_file, 'w') as f:
                f.write(gitignore_content)
            self.print_status("Created: .gitignore", True)
            return True
        except Exception as e:
            self.print_status("Failed: .gitignore", False, str(e))
            return False

    def create_docker_compose(self) -> bool:
        """Create docker-compose.yml file."""
        self.print_section("Creating Docker Compose File")

        compose_content = """
services:
  postgres:
    image: postgres:15
    container_name: batch-etl-postgres
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin
      POSTGRES_DB: warehouse
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./warehouse/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "5432:5432"
    networks:
      batch-etl-network:
        ipv4_address: 172.28.0.10
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d warehouse"]
      interval: 10s
      timeout: 5s
      retries: 5

  airflow:
    image: apache/airflow:2.7.3
    container_name: batch-etl-airflow
    environment:
      AIRFLOW__CORE__EXECUTOR: SequentialExecutor
      AIRFLOW__WEBSERVER__DEFAULT_UI_TIMEZONE: Asia/Jakarta
      AIRFLOW__WEBSERVER__SECRET_KEY: 'your-secret-key-here'
      AIRFLOW_CONN_POSTGRES: 'postgresql://admin:admin@postgres:5432/warehouse'
      PYTHONPATH: '/opt/airflow'
      DATA_PATH: '/opt/airflow/data'
      _AIRFLOW_WWW_USER_CREATE: "true"
      _AIRFLOW_WWW_USER_USERNAME: admin
      _AIRFLOW_WWW_USER_PASSWORD: admin
    volumes:
      - ./dags:/opt/airflow/dags
      - ./scripts:/opt/airflow/scripts
      - ./data:/opt/airflow/data
      - ./warehouse:/opt/airflow/warehouse
    ports:
      - "8080:8080"
    networks:
      batch-etl-network:
        ipv4_address: 172.28.0.20
    command: standalone
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 5
    depends_on:
      postgres:
        condition: service_healthy

  streamlit:
    build:
      context: ./dashboard
      dockerfile: Dockerfile
    container_name: batch-etl-streamlit
    volumes:
      - ./data:/app/data
    ports:
      - "8501:8501"
    networks:
      batch-etl-network:
        ipv4_address: 172.28.0.30
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 5

volumes:
  postgres_data:

networks:
  batch-etl-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
        """.strip()

        compose_file = self.project_root / 'docker-compose.yml'
        try:
            with open(compose_file, 'w') as f:
                f.write(compose_content)
            self.print_status("Created: docker-compose.yml", True)
            return True
        except Exception as e:
            self.print_status("Failed: docker-compose.yml", False, str(e))
            return False

    def create_init_sql(self) -> bool:
        """Create warehouse/init.sql file."""
        self.print_section("Creating Database Initialization SQL")

        sql_content = """
-- ============================================================
-- Database Initialization Script
-- NYC Taxi Data Warehouse
-- ============================================================

-- Create fact_trips table
CREATE TABLE IF NOT EXISTS fact_trips (
    trip_id SERIAL PRIMARY KEY,
    vendor_id INTEGER,
    pickup_datetime TIMESTAMP WITHOUT TIME ZONE,
    dropoff_datetime TIMESTAMP WITHOUT TIME ZONE,
    passenger_count INTEGER,
    trip_distance NUMERIC(10,2),
    fare_amount NUMERIC(10,2),
    total_amount NUMERIC(10,2),
    payment_type INTEGER,
    pickup_hour INTEGER,
    pickup_day VARCHAR(20),
    pickup_month INTEGER
);

-- Create indexes for query performance
CREATE INDEX IF NOT EXISTS idx_pickup_datetime ON fact_trips(pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_pickup_day ON fact_trips(pickup_day);
CREATE INDEX IF NOT EXISTS idx_fare_amount ON fact_trips(fare_amount);
CREATE INDEX IF NOT EXISTS idx_trip_distance ON fact_trips(trip_distance);
CREATE INDEX IF NOT EXISTS idx_vendor_id ON fact_trips(vendor_id);
CREATE INDEX IF NOT EXISTS idx_pickup_hour ON fact_trips(pickup_hour);
CREATE INDEX IF NOT EXISTS idx_payment_type ON fact_trips(payment_type);

-- Create composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_pickup_day_hour ON fact_trips(pickup_day, pickup_hour);
CREATE INDEX IF NOT EXISTS idx_fare_distance ON fact_trips(fare_amount, trip_distance);

-- Verify table creation
SELECT 'Table fact_trips created successfully' as status;
SELECT COUNT(*) as row_count FROM fact_trips;
        """.strip()

        init_sql_path = self.project_root / 'warehouse' / 'init.sql'
        try:
            with open(init_sql_path, 'w') as f:
                f.write(sql_content)
            self.print_status("Created: warehouse/init.sql", True)
            return True
        except Exception as e:
            self.print_status("Failed: warehouse/init.sql", False, str(e))
            return False

    def create_dashboard_dockerfile(self) -> bool:
        """Create dashboard/Dockerfile."""
        self.print_section("Creating Dashboard Dockerfile")

        dockerfile_content = """
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
        """.strip()

        dockerfile_path = self.project_root / 'dashboard' / 'Dockerfile'
        try:
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            self.print_status("Created: dashboard/Dockerfile", True)
            return True
        except Exception as e:
            self.print_status("Failed: dashboard/Dockerfile", False, str(e))
            return False

    def create_dashboard_requirements(self) -> bool:
        """Create dashboard/requirements.txt."""
        self.print_section("Creating Dashboard Requirements")

        req_content = """
pandas==2.0.3
streamlit==1.29.0
plotly==5.18.0
numpy==1.24.3
psycopg2-binary==2.9.9
sqlalchemy==2.0.19
python-dotenv==1.0.0
        """.strip()

        req_path = self.project_root / 'dashboard' / 'requirements.txt'
        try:
            with open(req_path, 'w') as f:
                f.write(req_content)
            self.print_status("Created: dashboard/requirements.txt", True)
            return True
        except Exception as e:
            self.print_status("Failed: dashboard/requirements.txt", False, str(e))
            return False

    def create_streamlit_config(self) -> bool:
        """Create batchetl-streamlit/.streamlit/config.toml."""
        self.print_section("Creating Streamlit Cloud Config")

        config_content = """
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
enableCORS = true
enableXsrfProtection = true

[browser]
gatherUsageStats = false
        """.strip()

        config_path = self.project_root / 'batchetl-streamlit' / '.streamlit' / 'config.toml'
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                f.write(config_content)
            self.print_status("Created: batchetl-streamlit/.streamlit/config.toml", True)
            return True
        except Exception as e:
            self.print_status("Failed: batchetl-streamlit/.streamlit/config.toml", False, str(e))
            return False

    def create_license(self) -> bool:
        """Create LICENSE file."""
        self.print_section("Creating License File")

        license_content = """
MIT License

Copyright (c) 2026 Arkan Tsabit

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
        """.strip()

        license_path = self.project_root / 'LICENSE'
        try:
            with open(license_path, 'w') as f:
                f.write(license_content)
            self.print_status("Created: LICENSE", True)
            return True
        except Exception as e:
            self.print_status("Failed: LICENSE", False, str(e))
            return False

    def create_placeholder_files(self) -> bool:
        """Create placeholder .gitkeep files in empty directories."""
        self.print_section("Creating Placeholder Files")

        placeholders = [
            'data/raw/.gitkeep',
            'data/staging/.gitkeep',
            'screenshots/.gitkeep'
        ]

        all_created = True
        for placeholder in placeholders:
            path = self.project_root / placeholder
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch(exist_ok=True)
                self.print_status(f"Created: {placeholder}", True)
            except Exception as e:
                self.print_status(f"Failed: {placeholder}", False, str(e))
                all_created = False

        return all_created

    def create_virtual_environment(self) -> bool:
        """Create Python virtual environment."""
        self.print_section("Creating Virtual Environment")

        if self.venv_path.exists():
            self.print_status("Virtual environment already exists", True, str(self.venv_path))
            return True

        try:
            subprocess.run(
                [sys.executable, '-m', 'venv', str(self.venv_path)],
                capture_output=True,
                text=True,
                check=True
            )
            self.print_status("Created virtual environment", True, str(self.venv_path))
            return True
        except subprocess.CalledProcessError as e:
            self.print_status("Failed to create virtual environment", False, e.stderr)
            return False

    def install_dependencies(self) -> bool:
        """Install Python dependencies in virtual environment."""
        self.print_section("Installing Dependencies")

        if not self.venv_path.exists():
            self.print_status("Virtual environment not found", False, "Run setup first")
            return False

        # Determine pip path based on OS
        if sys.platform == 'win32':
            pip_path = self.venv_path / 'Scripts' / 'pip'
        else:
            pip_path = self.venv_path / 'bin' / 'pip'

        if not pip_path.exists():
            self.print_status("Pip not found in virtual environment", False)
            return False

        try:
            subprocess.run(
                [str(pip_path), 'install', '--upgrade', 'pip'],
                capture_output=True,
                text=True,
                check=True
            )
            self.print_status("Pip upgraded", True)

            subprocess.run(
                [str(pip_path), 'install', '-r', str(self.requirements_file)],
                capture_output=True,
                text=True,
                check=True
            )
            self.print_status("Dependencies installed", True)
            return True
        except subprocess.CalledProcessError as e:
            self.print_status("Failed to install dependencies", False, e.stderr)
            return False

    def display_completion_summary(self, success: bool) -> None:
        """Display setup completion summary."""
        self.print_header("SETUP COMPLETION SUMMARY")

        if success:
            print(f"\n  {Colors.GREEN}{Colors.BOLD}Project setup completed successfully!{Colors.END}")
            print(f"\n  {Colors.BOLD}Next Steps:{Colors.END}")
            print(f"  1. Activate virtual environment:")
            print(f"     {Colors.CYAN}  Windows: venv\\Scripts\\activate{Colors.END}")
            print(f"     {Colors.CYAN}  Mac/Linux: source venv/bin/activate{Colors.END}")
            print(f"  2. Download NYC Taxi data to: data/raw/taxi_data.csv")
            print(f"  3. Start Docker containers:")
            print(f"     {Colors.CYAN}  docker-compose up -d{Colors.END}")
            print(f"  4. Verify setup:")
            print(f"     {Colors.CYAN}  python run_all_verifications.py{Colors.END}")
            print(f"\n  {Colors.BOLD}Useful Commands:{Colors.END}")
            print(f"  - Airflow UI: {Colors.CYAN}http://localhost:8080{Colors.END}")
            print(f"  - Dashboard: {Colors.CYAN}http://localhost:8501{Colors.END}")
        else:
            print(f"\n  {Colors.RED}{Colors.BOLD}Setup completed with errors.{Colors.END}")
            print(f"  {Colors.YELLOW}Please fix the failed items and run the script again.{Colors.END}")

        print(f"\n{Colors.CYAN}{'=' * 70}{Colors.END}")

    def run(self) -> bool:
        """Run all setup tasks."""
        self.print_header("BATCHETL PIPELINE - PROJECT SETUP")
        print(f"Project Root: {self.project_root}")
        print(f"Python Version: {sys.version}")

        all_success = True

        # Create directory structure
        if not self.create_directory_structure():
            all_success = False

        # Create init files
        if not self.create_init_files():
            all_success = False

        # Create configuration files
        if not self.create_requirements():
            all_success = False

        if not self.create_env_file():
            all_success = False

        if not self.create_gitignore():
            all_success = False

        if not self.create_docker_compose():
            all_success = False

        if not self.create_init_sql():
            all_success = False

        if not self.create_dashboard_dockerfile():
            all_success = False

        if not self.create_dashboard_requirements():
            all_success = False

        if not self.create_streamlit_config():
            all_success = False

        if not self.create_license():
            all_success = False

        if not self.create_placeholder_files():
            all_success = False

        # Create and configure virtual environment
        if not self.create_virtual_environment():
            all_success = False
        else:
            if not self.install_dependencies():
                all_success = False

        self.display_completion_summary(all_success)
        return all_success


def main() -> None:
    """Main entry point."""
    try:
        setup = ProjectSetup()
        success = setup.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup interrupted by user.{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()