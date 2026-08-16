# BATCHETL PIPELINE - CHEAT SHEET

---

## Document Information

| Property | Value |
|----------|-------|
| Version | 3.0.0 |
| Last Updated | 2026-08-17 |
| Purpose | Quick reference for development and deployment |

---

## Table of Contents

1. [Quick Commands](#1-quick-commands)
2. [Docker Commands](#2-docker-commands)
3. [Airflow Commands](#3-airflow-commands)
4. [Database Commands](#4-database-commands)
5. [Python Package Management](#5-python-package-management)
6. [Running the Pipeline](#6-running-the-pipeline)
7. [Dashboard Configuration](#7-dashboard-configuration)
8. [Project Structure Quick Reference](#8-project-structure-quick-reference)
9. [Troubleshooting](#9-troubleshooting)
10. [DAG Structure Template](#10-dag-structure-template)
11. [One-Liner Commands](#11-one-liner-commands)
12. [Important URLs](#12-important-urls)
13. [Documentation Links](#13-documentation-links)
14. [Quick Tips](#14-quick-tips)
15. [File Paths Reference](#15-file-paths-reference)
16. [Environment Variables](#16-environment-variables)
17. [Verification Commands](#17-verification-commands)
18. [Pipeline Execution Results](#18-pipeline-execution-results)

---

## 1. Quick Commands

### Virtual Environment

```bash
# One Command Start (Windows PowerShell)
venv\Scripts\Activate.ps1; docker-compose up -d; docker-compose ps; start http://localhost:8080

# One Command Start (Windows CMD)
venv\Scripts\activate.bat && docker-compose up -d && docker-compose ps && start http://localhost:8080

# One Command Start (Mac/Linux)
source venv/bin/activate && docker-compose up -d && docker-compose ps && open http://localhost:8080

# Create venv
python -m venv venv

# Activate venv (Windows PowerShell)
venv\Scripts\Activate.ps1

# Activate venv (Windows CMD)
venv\Scripts\activate.bat

# Activate venv (Mac/Linux)
source venv/bin/activate

# Deactivate venv
deactivate

# Delete venv (Windows)
rmdir /s venv

# Delete venv (Mac/Linux)
rm -rf venv
```

---

## 2. Docker Commands

### Start and Stop Services

```bash
# Start all services (PostgreSQL, Airflow, Streamlit)
docker-compose up -d

# Start with logs
docker-compose up

# Start specific service
docker-compose up -d postgres
docker-compose up -d airflow
docker-compose up -d streamlit

# Stop all services
docker-compose down

# Stop and remove volumes (clean reset)
docker-compose down -v

# Restart services
docker-compose restart

# Restart specific service
docker-compose restart airflow
```

### Container Status and Logs

```bash
# Check container status
docker-compose ps

# View all logs
docker-compose logs -f

# View specific container logs
docker-compose logs postgres -f
docker-compose logs airflow -f
docker-compose logs streamlit -f

# View last 50 lines
docker-compose logs --tail=50

# Check resource usage
docker stats

# Clean up unused images/containers
docker system prune -f
```

### Docker Network Commands

```bash
# Check networks
docker network ls

# Inspect network
docker network inspect batchetlpipeline_batch-etl-network

# Connect container to network
docker network connect batchetlpipeline_batch-etl-network container_name

# Disconnect container from network
docker network disconnect batchetlpipeline_batch-etl-network container_name
```

### Docker URLs

```bash
# Airflow UI
http://localhost:8080

# Streamlit Dashboard (Local)
http://localhost:8501

# Streamlit Dashboard (Live Demo)
https://batchetl.streamlit.app

# PostgreSQL
localhost:5432
```

### Docker Default Credentials

```bash
Airflow UI:
  Username: admin
  Password: admin
  URL: http://localhost:8080

PostgreSQL:
  Username: admin
  Password: admin
  Database: warehouse
  Host: localhost
  Port: 5432
```

### Port Mapping Summary

| Service | Host Port | Container Port | Container Name |
|---------|-----------|----------------|----------------|
| Airflow UI | 8080 | 8080 | batch-etl-airflow |
| PostgreSQL | 5432 | 5432 | batch-etl-postgres |
| Streamlit | 8501 | 8501 | batch-etl-streamlit |

---

## 3. Airflow Commands

**Note:** Run these commands inside the Airflow container or via `docker exec`

### DAG Management

```bash
# Trigger DAG (Airflow 2.x)
docker exec -it batch-etl-airflow airflow dags trigger etl_pipeline

# Alternative trigger command
docker exec -it batch-etl-airflow airflow dag trigger etl_pipeline

# List all DAGs
docker exec -it batch-etl-airflow airflow dags list

# List DAG runs
docker exec -it batch-etl-airflow airflow dags list-runs --dag-id etl_pipeline

# Pause DAG
docker exec -it batch-etl-airflow airflow dags pause etl_pipeline

# Unpause DAG
docker exec -it batch-etl-airflow airflow dags unpause etl_pipeline

# Show DAG details
docker exec -it batch-etl-airflow airflow dags show etl_pipeline

# Get DAG status
docker exec -it batch-etl-airflow airflow dags state etl_pipeline 2026-07-26
```

### Task Management

```bash
# List tasks in DAG
docker exec -it batch-etl-airflow airflow tasks list etl_pipeline

# Test a single task
docker exec -it batch-etl-airflow airflow tasks test etl_pipeline extract_data 2026-07-01

# Clear task instances
docker exec -it batch-etl-airflow airflow tasks clear -d etl_pipeline

# Show task state
docker exec -it batch-etl-airflow airflow tasks state etl_pipeline extract_data 2026-07-01

# Clear specific task
docker exec -it batch-etl-airflow airflow tasks clear -t extract_data etl_pipeline
```

### Alternative (Using Docker Exec)

```bash
# Open bash inside Airflow container
docker exec -it batch-etl-airflow bash

# Then run Airflow commands
airflow dags trigger etl_pipeline
airflow dags list
airflow dags list-runs --dag-id etl_pipeline
exit
```

---

## 4. Database Commands

### PostgreSQL

```bash
# Connect via docker exec
docker exec -it batch-etl-postgres psql -U admin -d warehouse

# Connect with custom host/port
psql -h localhost -p 5432 -U admin -d warehouse

# Execute single query
docker exec -it batch-etl-postgres psql -U admin -d warehouse -c "SELECT COUNT(*) FROM fact_trips;"

# Export query to CSV
docker exec -it batch-etl-postgres psql -U admin -d warehouse -c "\COPY (SELECT * FROM fact_trips) TO '/tmp/output.csv' CSV HEADER;"
```

### Useful SQL Queries

```sql
-- List all tables
\dt

-- List all indexes
\di

-- Describe table structure
\d fact_trips

-- Count total rows
SELECT COUNT(*) FROM fact_trips;

-- View sample data
SELECT * FROM fact_trips LIMIT 10;

-- Check duplicates
SELECT trip_id, COUNT(*) FROM fact_trips GROUP BY trip_id HAVING COUNT(*) > 1;

-- Summary statistics
SELECT 
    COUNT(*) as total_trips,
    AVG(fare_amount) as avg_fare,
    AVG(trip_distance) as avg_distance,
    SUM(total_amount) as total_revenue
FROM fact_trips;

-- Daily revenue
SELECT pickup_day, COUNT(*) as trips, SUM(total_amount) as revenue
FROM fact_trips
GROUP BY pickup_day
ORDER BY revenue DESC;

-- Peak hours
SELECT pickup_hour, COUNT(*) as trips
FROM fact_trips
GROUP BY pickup_hour
ORDER BY trips DESC
LIMIT 5;

-- Revenue by payment type
SELECT payment_type, COUNT(*) as trips, SUM(total_amount) as revenue
FROM fact_trips
GROUP BY payment_type
ORDER BY revenue DESC;

-- Exit psql
\q
```

---

## 5. Python Package Management

### Technology Versions

| Tool | Version |
|------|---------|
| Apache Airflow | 2.7.3 |
| PostgreSQL | 15 |
| Streamlit | 1.29.0 |
| Pandas | 2.0.3 |
| SQLAlchemy | 1.4.50 |
| Plotly | 5.18.0 |
| Python | 3.10+ |
| psycopg2-binary | 2.9.9 |

### Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Install specific packages (recommended - one line)
pip install pandas==2.0.3 psycopg2-binary==2.9.9 sqlalchemy==2.0.19 streamlit==1.29.0 plotly==5.18.0 apache-airflow==2.7.3

# Install individual packages
pip install pandas==2.0.3
pip install psycopg2-binary==2.9.9
pip install sqlalchemy==2.0.19
pip install streamlit==1.29.0
pip install plotly==5.18.0
pip install apache-airflow==2.7.3

# Upgrade pip
python -m pip install --upgrade pip

# List installed packages
pip list

# Freeze requirements
pip freeze > requirements.txt

# Uninstall package
pip uninstall package_name
```

### Verify Installation

```bash
# Check Python version
python --version

# Test imports
python -c "import pandas; print(f'Pandas {pandas.__version__} OK')"
python -c "import psycopg2; print('PostgreSQL OK')"
python -c "import streamlit; print(f'Streamlit {streamlit.__version__} OK')"
python -c "import plotly; print(f'Plotly {plotly.__version__} OK')"
python -c "import sqlalchemy; print(f'SQLAlchemy {sqlalchemy.__version__} OK')"
python -c "import airflow; print(f'Airflow {airflow.__version__} OK')"
```

---

## 6. Running the Pipeline

### Quick Start

```bash
# 1. Start all containers
docker-compose up -d

# 2. Check if containers are running
docker-compose ps

# 3. Open Airflow UI
start http://localhost:8080   # Windows
open http://localhost:8080    # Mac

# 4. Trigger DAG (via UI or CLI)
# Click "Trigger DAG" on etl_pipeline

# 5. Open Dashboard
start http://localhost:8501   # Windows (Local)
open http://localhost:8501    # Mac (Local)
# Or open live demo: https://batchetl.streamlit.app
```

### Manual Pipeline Run

```bash
# Run each script manually (for testing)
# Make sure you're in project root with venv activated

# Extract
python scripts/extract.py

# Transform
python scripts/transform.py

# Load
python scripts/load.py

# Or run all in sequence
python scripts/extract.py && python scripts/transform.py && python scripts/load.py
```

### Check Pipeline Status

```bash
# Check DAG run status
docker exec -it batch-etl-airflow airflow dags list-runs --dag-id etl_pipeline

# View logs
docker-compose logs airflow -f

# Check data in PostgreSQL
docker exec -it batch-etl-postgres psql -U admin -d warehouse -c "SELECT COUNT(*) FROM fact_trips;"

# Check sample data
docker exec -it batch-etl-postgres psql -U admin -d warehouse -c "SELECT * FROM fact_trips LIMIT 5;"
```

---

## 7. Dashboard Configuration

### Data Limit Configuration

Dashboard by default displays 100,000 rows for fast performance. To change:

```python
# dashboard/app.py - Line ~25

# For 100,000 rows (default - fast)
DATA_LIMIT = 100000

# For ALL data (full - slower)
DATA_LIMIT = None

# For custom amount (e.g., 500,000)
DATA_LIMIT = 500000
```

### Mode Comparison

| Mode | DATA_LIMIT | Speed | Accuracy | Use Case |
|------|--------------|-------|----------|----------|
| Default | 100000 | Very Fast | Sample only | Demo, testing, screenshots |
| Full Data | None | Slow (30-60s) | 100% accurate | Serious analysis |
| Custom | 500000 | Fast | Partial | Balance performance and accuracy |

### Query Generated

```python
# Function load_trip_data() generates:
if DATA_LIMIT:
    query = f"SELECT * FROM fact_trips ORDER BY trip_id LIMIT {DATA_LIMIT}"
else:
    query = "SELECT * FROM fact_trips ORDER BY trip_id"  # No LIMIT
```

### After Changing DATA_LIMIT

**If using Docker:**
```bash
# Rebuild container
docker-compose stop streamlit
docker-compose rm -f streamlit
docker-compose build --no-cache streamlit
docker-compose up -d streamlit

# Check logs
docker logs batch-etl-streamlit -f
```

**If using Local:**
```bash
# Stop (Ctrl+C), then restart
streamlit run dashboard/app.py
```

### Performance Tips

| Data Size | Load Time | RAM Required |
|-----------|-----------|--------------|
| 100,000 rows | 2-5 seconds | ~200 MB |
| 1,000,000 rows | 10-15 seconds | ~800 MB |
| 2,869,525 rows | 30-60 seconds | ~2-3 GB |
| 20,117,150 rows | 60-120 seconds | ~4-5 GB |

---

## 8. Project Structure Quick Reference

| Folder | Content |
|--------|---------|
| archive/ | Diagram generator scripts (architecture, data flow, ERD) |
| dags/ | Airflow DAG files (etl_pipeline.py) |
| scripts/ | ETL Python scripts (extract, transform, load) |
| data/raw/ | Raw dataset (taxi_data.csv - 2.96M rows) |
| data/staging/ | Intermediate files (taxi_raw.csv, taxi_clean.csv) |
| warehouse/ | Database initialization (init.sql) |
| dashboard/ | Streamlit app (app.py) + Dockerfile |
| screenshots/ | Documentation screenshots |
| docs/ | Documentation files (blueprint, cheatsheet, checklist) |
| docs/diagrams/ | Diagram source files (PDF, XML, DBML, drawio, MWB) |
| batchetl-streamlit/ | Streamlit Cloud deployment files |

---

## 9. Troubleshooting

### Docker Issues

| Issue | Solution |
|-------|----------|
| Docker not running | Start Docker Desktop first |
| Port already in use | Change port in docker-compose.yml |
| Container not starting | docker-compose logs to see errors |
| Permission denied | Run terminal as admin |
| Volume conflicts | docker-compose down -v |
| Image pull failed | Check internet connection |
| Container exits immediately | Check logs for error messages |

### Airflow Issues

| Issue | Solution |
|-------|----------|
| DAG not showing | Wait 30-60s, restart container, check file in dags/ |
| Task failed | Check logs in UI, verify database connection |
| Task stuck in running | Clear task and retry |
| Cannot connect to database | Wait for database to initialize (10-15s) |
| Authentication failed | Use admin/admin credentials |
| API 401 Unauthorized | Login to UI first or use session auth |
| Import error in DAG | Check Python dependencies in container |
| Scheduler not running | Restart airflow-scheduler container |

### Database Issues

| Issue | Solution |
|-------|----------|
| Connection refused | Wait for database to initialize (10-15s) |
| Table not found | Run init.sql first, check schema name |
| Permission denied | Check credentials (admin/admin) |
| Data not loaded | Trigger DAG first or run scripts manually |
| Duplicate key error | Check primary key constraints, clear data |
| Encoding issues | Set proper encoding in connection string |

### Common Errors and Solutions

| Error | Solution |
|-------|----------|
| ModuleNotFoundError | pip install -r requirements.txt (activate venv first) |
| ImportError: cannot import name | Check package version compatibility |
| Port 8080 already in use | Change host port in docker-compose.yml |
| No such file: taxi_data.csv | Download dataset to data/raw/ |
| Connection refused | Start Docker first and wait for services |
| No data in dashboard | Run DAG first to load data |
| DAG not found in UI | Check file in dags/ folder, wait 30s |
| airflow: command not found | Use docker exec or install airflow locally |
| Permission denied: /var/run/docker.sock | Add user to docker group or run as admin |
| SQLAlchemy error | Check DATABASE_URL in environment variables |

### Quick Troubleshooting Flow

```bash
# 1. Check status of all containers
docker-compose ps

# 2. Check latest errors
docker-compose logs --tail=50

# 3. Check specific service logs
docker-compose logs airflow --tail=50

# 4. Restart Airflow (if DAG doesn't appear)
docker-compose restart airflow

# 5. Restart PostgreSQL (if connection issue)
docker-compose restart postgres

# 6. Restart all services
docker-compose restart

# 7. Full reset (if all else fails)
docker-compose down -v && docker-compose up -d

# 8. Check disk space
df -h

# 9. Check container resource usage
docker stats
```

---

## 10. DAG Structure Template

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'your_name',
    'depends_on_past': False,
    'start_date': datetime(2026, 7, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='dag_name',
    default_args=default_args,
    description='Your DAG description',
    schedule_interval='@daily',
    catchup=False,
    tags=['etl', 'batch'],
    max_active_runs=1,
) as dag:

    def extract_task(**context):
        """Extract data from source"""
        print("Extracting data...")
        return "Extraction complete"

    def transform_task(**context):
        """Transform extracted data"""
        print("Transforming data...")
        return "Transformation complete"

    def load_task(**context):
        """Load transformed data"""
        print("Loading data...")
        return "Load complete"

    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_task,
    )

    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_task,
    )

    load = PythonOperator(
        task_id='load',
        python_callable=load_task,
    )

    extract >> transform >> load
```

---

## 11. One-Liner Commands

### Setup

```bash
# Complete project setup (Windows PowerShell)
python -m venv venv && venv\Scripts\Activate.ps1 && pip install -r requirements.txt

# Complete project setup (Windows CMD)
python -m venv venv && venv\Scripts\activate.bat && pip install -r requirements.txt

# Complete project setup (Mac/Linux)
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Reset everything (Windows PowerShell)
docker-compose down -v && rmdir /s venv && python -m venv venv

# Reset everything (Mac/Linux)
docker-compose down -v && rm -rf venv && python -m venv venv
```

### Start Everything

```bash
# Windows PowerShell
venv\Scripts\Activate.ps1; docker-compose up -d; start http://localhost:8080; start http://localhost:8501

# Windows CMD
venv\Scripts\activate.bat && docker-compose up -d && start http://localhost:8080 && start http://localhost:8501

# Mac/Linux
source venv/bin/activate && docker-compose up -d && open http://localhost:8080 && open http://localhost:8501
```

### Data Verification

```bash
# Check row count in PostgreSQL
docker exec -it batch-etl-postgres psql -U admin -d warehouse -c "SELECT COUNT(*) FROM fact_trips;"

# Check DAG status
docker exec -it batch-etl-airflow airflow dags list-runs --dag-id etl_pipeline

# Check latest DAG run
docker exec -it batch-etl-airflow airflow dags list-runs --dag-id etl_pipeline --limit 1
```

### Cleanup

```bash
# Stop all containers and remove volumes
docker-compose down -v

# Remove all unused containers, networks, images
docker system prune -a

# Remove venv and cache
rm -rf venv __pycache__ .pytest_cache
```

---

## 12. Important URLs

| Service | URL |
|---------|-----|
| Airflow UI | http://localhost:8080 |
| Streamlit Dashboard (Local) | http://localhost:8501 |
| Streamlit Dashboard (Live Demo) | https://batchetl.streamlit.app |
| PostgreSQL | localhost:5432 |
| NYC Taxi Data | https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page |

---

## 13. Documentation Links

| Resource | URL |
|----------|-----|
| Airflow Docs | https://airflow.apache.org/docs/ |
| PostgreSQL Docs | https://www.postgresql.org/docs/ |
| Streamlit Docs | https://docs.streamlit.io/ |
| Plotly Docs | https://plotly.com/python/ |
| Pandas Docs | https://pandas.pydata.org/docs/ |
| Docker Docs | https://docs.docker.com/ |
| SQLAlchemy Docs | https://docs.sqlalchemy.org/ |

---

## 14. Quick Tips

1. Always use Docker on Windows for Airflow
2. Activate venv before working with Python locally
3. Check docker-compose ps to ensure all services are running
4. Use docker-compose logs -f to monitor in real-time
5. Wait for database initialization (10-15 seconds) before triggering DAG
6. Restart Airflow after adding new DAGs
7. Check ports if services won't start (8080, 5432, 8501)
8. Trigger DAG manually first, then schedule will work
9. Use verification scripts to check each phase
10. Screenshots should be 300+ DPI for documentation
11. Use --no-cache-dir with pip to save disk space
12. Set environment variables in .env file for sensitive data
13. Use docker exec for Airflow commands to avoid local installation
14. Clear task instances when retrying failed tasks
15. Monitor resource usage with docker stats

---

## 15. File Paths Reference

| File | Path |
|------|------|
| DAG | dags/etl_pipeline.py |
| Extract Script | scripts/extract.py |
| Transform Script | scripts/transform.py |
| Load Script | scripts/load.py |
| Dashboard (Local) | dashboard/app.py |
| Dashboard (Cloud) | batchetl-streamlit/app.py |
| Dashboard Dockerfile | dashboard/Dockerfile |
| Raw Data | data/raw/taxi_data.csv |
| Staging Data | data/staging/taxi_raw.csv |
| Clean Data | data/staging/taxi_clean.csv |
| Sample Data | data/staging/taxi_clean_sample.csv |
| Init SQL | warehouse/init.sql |
| Docker Compose | docker-compose.yml |
| Requirements | requirements.txt |
| Environment | .env |
| Blueprint | docs/blueprint.md |
| Cheatsheet | docs/cheatsheets.md |
| Verification Checklist | docs/verification-checklist.md |
| Changelog | CHANGELOG.md |
| Architecture Diagram Script | archive/architecture-diagram.py |
| Data Flow Diagram Script | archive/data-flow-diagram.py |
| ERD Diagram Script | archive/erd-diagram.py |
| Architecture Diagram | screenshots/architecture-diagram.png |
| Data Flow Diagram | screenshots/data-flow-diagram.png |
| ERD Diagram | screenshots/erd-diagram.png |

---

## 16. Environment Variables

### Required Environment Variables

```bash
# .env file example
AIRFLOW_UID=50000
AIRFLOW_GID=50000
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=warehouse
POSTGRES_PORT=5432
DATA_PATH=./data
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__WEBSERVER__SECRET_KEY=your-secret-key-here
AIRFLOW_CONN_POSTGRES=postgresql://admin:admin@postgres:5432/warehouse
PYTHONPATH=/opt/airflow
```

### Set Environment Variables

```bash
# Windows PowerShell
$env:AIRFLOW_UID="50000"
$env:POSTGRES_PASSWORD="admin"

# Windows CMD
set AIRFLOW_UID=50000
set POSTGRES_PASSWORD=admin

# Mac/Linux
export AIRFLOW_UID=50000
export POSTGRES_PASSWORD=admin
```

---

## 17. Verification Commands

### Run All Verifications

```bash
python run_all_verifications.py
```

### Individual Phase Verification

```bash
python verify-phase-1.py
python verify-phase-2.py
python verify-phase-3.py
python verify-phase-4.py
python verify-phase-5.py
python verify-phase-6.py
python verify-phase-7.py
python verify-phase-8.py
python verify-phase-9.py
```

### Troubleshooting Modules

```bash
python troubleshoot.py
python troubleshoot_docker.py
python troubleshoot_airflow.py
python troubleshoot_postgres.py
python troubleshoot_dashboard.py
python troubleshoot_network.py
```

---

## 18. Pipeline Execution Results

### Actual Execution Results

| Phase | Rows | Time | Status |
|-------|------|------|--------|
| Extract | 2,964,624 | 43 seconds | SUCCESS |
| Transform | 2,869,525 | 27 seconds | SUCCESS |
| Load | 2,869,525 | ~4-5 minutes | SUCCESS |
| **Total** | **2,869,525** | **~5-6 minutes** | **SUCCESS** |

### Database Results

| Metric | Value |
|--------|-------|
| Existing Rows | 19,217,150 |
| New Rows Loaded | 2,869,525 |
| **Total Rows in DB** | **22,086,675** |

---

## Quick Commands Reference Card

```bash
# START SERVICES
docker-compose up -d

# STATUS
docker-compose ps

# LOGS
docker-compose logs -f

# STOP SERVICES
docker-compose down

# RESET
docker-compose down -v && docker-compose up -d

# AIRFLOW UI
http://localhost:8080 (admin/admin)

# DASHBOARD (LOCAL)
http://localhost:8501

# DASHBOARD (LIVE DEMO)
https://batchetl.streamlit.app

# POSTGRES CONNECT
docker exec -it batch-etl-postgres psql -U admin -d warehouse

# TRIGGER DAG
docker exec -it batch-etl-airflow airflow dags trigger etl_pipeline

# LIST DAGS
docker exec -it batch-etl-airflow airflow dags list

# CHECK DAG RUNS
docker exec -it batch-etl-airflow airflow dags list-runs --dag-id etl_pipeline

# CLEAR TASKS
docker exec -it batch-etl-airflow airflow tasks clear -d etl_pipeline

# CHECK DATA
docker exec -it batch-etl-postgres psql -U admin -d warehouse -c "SELECT COUNT(*) FROM fact_trips;"

# VIEW AIRFLOW LOGS
docker-compose logs airflow -f

# RUN SCRIPTS MANUALLY
python scripts/extract.py && python scripts/transform.py && python scripts/load.py

# RUN VERIFICATIONS
python run_all_verifications.py

# DOCKER CLEANUP
docker system prune -f

# NETWORK INFO
docker network inspect batchetlpipeline_batch-etl-network

# FULL RESET
docker-compose down -v && docker-compose up -d
```

---

*Last Updated: 2026-08-17*
*Version: 3.0.0*