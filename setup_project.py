# setup_project.py
"""
Setup script for BatchETL Pipeline Project.

Creates project structure, configuration files, and development environment
for the NYC Taxi Data ETL pipeline.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class ProjectSetup:
    """Initializes project structure and configuration files."""

    def __init__(self) -> None:
        """Initialize setup with root directory and color codes."""
        self.root: Path = Path.cwd()
        self.colors: Dict[str, str] = {
            'GREEN': '\033[92m',
            'RED': '\033[91m',
            'BLUE': '\033[94m',
            'CYAN': '\033[96m',
            'BOLD': '\033[1m',
            'END': '\033[0m'
        }

    def print_header(self, text: str) -> None:
        """Display formatted section header."""
        print(f"\n{self.colors['CYAN']}{'=' * 60}{self.colors['END']}")
        print(f"{self.colors['BOLD']}{self.colors['BLUE']}{text}{self.colors['END']}")
        print(f"{self.colors['CYAN']}{'=' * 60}{self.colors['END']}\n")

    def print_check(self, text: str, success: bool, detail: str = "") -> None:
        """Display check result with status indicator."""
        icon = "[OK]" if success else "[FAIL]"
        color = self.colors['GREEN'] if success else self.colors['RED']
        print(f"{color}{icon} {text}{self.colors['END']}")
        if detail:
            print(f"   └─ {detail}")

    def _ensure_directory(self, path: Path) -> bool:
        """Create directory if it doesn't exist."""
        if path.exists():
            return True
        path.mkdir(parents=True)
        return False

    def create_folders(self) -> None:
        """Create required project directory structure."""
        self.print_header("CREATING FOLDER STRUCTURE")

        folders = [
            'data/raw',
            'data/staging',
            'warehouse',
            'dashboard',
            'dags',
            'scripts',
            'screenshots',
        ]

        for folder in folders:
            folder_path = self.root / folder
            exists = folder_path.exists()
            if not exists:
                folder_path.mkdir(parents=True)
            self.print_check(
                f"Folder '{folder}/'",
                success=True,
                detail="already exists" if exists else "created"
            )

    def create_gitkeep(self) -> None:
        """Create .gitkeep files in empty directories."""
        self.print_header("CREATING .GITKEEP FILES")

        folders = ['data/raw', 'data/staging', 'warehouse', 'screenshots']
        for folder in folders:
            file_path = self.root / folder / '.gitkeep'
            exists = file_path.exists()
            if not exists:
                file_path.touch()
            self.print_check(
                f"{folder}/.gitkeep",
                success=True,
                detail="already exists" if exists else "created"
            )

    def create_requirements(self) -> None:
        """Create main requirements.txt file."""
        self.print_header("CHECKING REQUIREMENTS")

        req_path = self.root / 'requirements.txt'
        if req_path.exists():
            self.print_check("requirements.txt", success=True, detail="already exists")
            return

        content = """# BatchETL Pipeline Dependencies
# NYC Taxi Data ETL - Python 3.9+

# Orchestration
apache-airflow==2.7.3

# Data Processing
pandas==2.0.3
numpy==1.24.3

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.19

# Dashboard & Visualization
streamlit==1.29.0
plotly==5.18.0

# Utilities
python-dotenv==1.0.0

# Development
pytest==7.4.3
black==23.12.1
"""

        req_path.write_text(content)
        self.print_check("requirements.txt", success=True, detail="created")

    def create_gitignore(self) -> None:
        """Create .gitignore file."""
        self.print_header("CHECKING .GITIGNORE")

        gitignore_path = self.root / '.gitignore'
        if gitignore_path.exists():
            self.print_check(".gitignore", success=True, detail="already exists")
            return

        content = """# Virtual Environment
venv/
env/
.venv/

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
*.whl

# Airflow
airflow.db
airflow.cfg
webserver_config.py
logs/
plugins/
*.pid

# Docker
.docker/
docker-compose.override.yml

# PostgreSQL
postgres_data/
*.duckdb
*.db
*.log

# Data Files
data/raw/*.csv
data/staging/*.csv
!data/raw/.gitkeep
!data/staging/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# OS
Thumbs.db
desktop.ini

# Logs
logs/
*.log

# Streamlit
.streamlit/
.streamlit/config.toml

# Testing
.pytest_cache/
.coverage
htmlcov/

# Environment
.env
.env.local

# Backup
*.bak
*.tmp
*.zip
*.tar.gz
"""

        gitignore_path.write_text(content)
        self.print_check(".gitignore", success=True, detail="created")

    def create_docker_compose(self) -> None:
        """Create docker-compose.yml file."""
        self.print_header("CHECKING DOCKER COMPOSE")

        compose_path = self.root / 'docker-compose.yml'
        if compose_path.exists():
            self.print_check("docker-compose.yml", success=True, detail="already exists")
            return

        content = """version: '3.8'

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
      - batch-etl-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d warehouse"]
      interval: 10s
      timeout: 5s
      retries: 5

  airflow:
    image: apache/airflow:2.7.3
    container_name: batch-etl-airflow
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://admin:admin@postgres/warehouse
      AIRFLOW_WEBSERVER_DEFAULT_UI_TIMEZONE: Asia/Jakarta
    volumes:
      - ./dags:/opt/airflow/dags
      - ./scripts:/opt/airflow/scripts
      - ./data:/opt/airflow/data
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - batch-etl-network
    command: >
      bash -c "airflow db init &&
               airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com &&
               airflow standalone"

  streamlit:
    build:
      context: ./dashboard
      dockerfile: Dockerfile
    container_name: batch-etl-streamlit
    volumes:
      - ./data:/app/data
    ports:
      - "8501:8501"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - batch-etl-network

volumes:
  postgres_data:

networks:
  batch-etl-network:
    driver: bridge
"""

        compose_path.write_text(content)
        self.print_check("docker-compose.yml", success=True, detail="created")

    def create_init_sql(self) -> None:
        """Create PostgreSQL initialization script."""
        self.print_header("CHECKING INIT.SQL")

        init_path = self.root / 'warehouse' / 'init.sql'
        if init_path.exists():
            self.print_check("warehouse/init.sql", success=True, detail="already exists")
            return

        content = """-- BatchETL Pipeline Database Initialization
-- NYC Taxi Data Warehouse Schema

CREATE TABLE IF NOT EXISTS fact_trips (
    trip_id SERIAL PRIMARY KEY,
    vendor_id INTEGER,
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    passenger_count INTEGER,
    trip_distance FLOAT,
    fare_amount FLOAT,
    total_amount FLOAT,
    payment_type INTEGER,
    pickup_hour INTEGER,
    pickup_day VARCHAR(20),
    pickup_month INTEGER
);

CREATE INDEX IF NOT EXISTS idx_pickup_datetime ON fact_trips(pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_pickup_day ON fact_trips(pickup_day);
CREATE INDEX IF NOT EXISTS idx_fare_amount ON fact_trips(fare_amount);
"""

        init_path.write_text(content)
        self.print_check("warehouse/init.sql", success=True, detail="created")

    def create_dashboard_dockerfile(self) -> None:
        """Create Dockerfile for Streamlit dashboard."""
        self.print_header("CHECKING DASHBOARD DOCKERFILE")

        dockerfile_path = self.root / 'dashboard' / 'Dockerfile'
        if dockerfile_path.exists():
            self.print_check("dashboard/Dockerfile", success=True, detail="already exists")
            return

        content = """FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""

        dockerfile_path.write_text(content)
        self.print_check("dashboard/Dockerfile", success=True, detail="created")

    def create_dashboard_requirements(self) -> None:
        """Create dashboard-specific requirements file."""
        self.print_header("CHECKING DASHBOARD REQUIREMENTS")

        req_path = self.root / 'dashboard' / 'requirements.txt'
        if req_path.exists():
            self.print_check("dashboard/requirements.txt", success=True, detail="already exists")
            return

        content = """streamlit==1.29.0
pandas==2.0.3
plotly==5.18.0
sqlalchemy==2.0.19
psycopg2-binary==2.9.9
"""

        req_path.write_text(content)
        self.print_check("dashboard/requirements.txt", success=True, detail="created")

    def create_license(self) -> None:
        """Create MIT License file."""
        self.print_header("CHECKING LICENSE")

        license_path = self.root / 'LICENSE'
        if license_path.exists():
            self.print_check("LICENSE", success=True, detail="already exists")
            return

        content = """MIT License

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
"""

        license_path.write_text(content)
        self.print_check("LICENSE", success=True, detail="created")

    def create_env_example(self) -> None:
        """Create example environment variables file."""
        self.print_header("CHECKING .ENV.EXAMPLE")

        env_path = self.root / '.env.example'
        if env_path.exists():
            self.print_check(".env.example", success=True, detail="already exists")
            return

        content = """# BatchETL Pipeline Environment Variables

# PostgreSQL
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=warehouse

# Airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW_WEBSERVER_DEFAULT_UI_TIMEZONE=Asia/Jakarta

# Database URL
DATABASE_URL=postgresql+psycopg2://admin:admin@postgres:5432/warehouse
"""

        env_path.write_text(content)
        self.print_check(".env.example", success=True, detail="created")

    def verify_environment(self) -> Tuple[bool, bool]:
        """Verify virtual environment status."""
        self.print_header("VIRTUAL ENVIRONMENT CHECK")

        in_venv = sys.prefix != sys.base_prefix
        venv_exists = (self.root / 'venv').exists()

        self.print_check(
            "Virtual environment active",
            success=in_venv,
            detail=sys.prefix if in_venv else "Run: venv\\Scripts\\activate"
        )
        self.print_check(
            "venv folder exists",
            success=venv_exists,
            detail="Run: python -m venv venv" if not venv_exists else ""
        )

        return in_venv, venv_exists

    def display_next_steps(self) -> None:
        """Display next steps after successful setup."""
        self.print_header("SETUP COMPLETE")

        steps = [
            "Activate venv:        venv\\Scripts\\activate",
            "Install dependencies: pip install -r requirements.txt",
            "Download dataset:     https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page",
            "Start Docker:         docker-compose up -d",
            "Airflow UI:           http://localhost:8080 (admin/admin)",
            "Dashboard:            http://localhost:8501",
        ]

        print("\nNext Steps:")
        for step in steps:
            print(f"  {step}")

        print("\nProject Structure:")
        structure = [
            ("dags/", "Airflow DAG files"),
            ("scripts/", "ETL Python scripts"),
            ("data/raw/", "Raw dataset (taxi_data.csv)"),
            ("data/staging/", "Intermediate CSV files"),
            ("warehouse/", "Database initialization"),
            ("dashboard/", "Streamlit app + Dockerfile"),
            ("screenshots/", "Documentation images"),
        ]

        for folder, description in structure:
            print(f"  ├── {folder:<12} → {description}")

    def run(self) -> None:
        """Execute all setup steps."""
        self.print_header("BATCHETL PIPELINE - PROJECT SETUP")
        print(f"Project Root: {self.root}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self.create_folders()
        self.create_gitkeep()
        self.create_requirements()
        self.create_gitignore()
        self.create_docker_compose()
        self.create_init_sql()
        self.create_dashboard_dockerfile()
        self.create_dashboard_requirements()
        self.create_license()
        self.create_env_example()
        self.verify_environment()
        self.display_next_steps()


if __name__ == "__main__":
    setup = ProjectSetup()
    setup.run()