# BatchETL Pipeline - Cheat Sheet (Apache Airflow with Docker)

---

## Quick Commands

### Virtual Environment

```bash
# One Command Start (Windows PowerShell)
venv\Scripts\activate; docker-compose up -d; docker-compose ps; start http://localhost:8080

# One Command Start (Mac/Linux)
source venv/bin/activate && docker-compose up -d && docker-compose ps && open http://localhost:8080

# Create venv
python -m venv venv

# Activate venv (Windows)
venv\Scripts\activate

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

## Docker Commands

### Start & Stop Services

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

### Container Status & Logs

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

### Docker URLs

```bash
# Airflow UI
http://localhost:8080

# Streamlit Dashboard
http://localhost:8501

# PostgreSQL
localhost:5432
```

### Docker Default Credentials

```bash
Airflow UI:
  Username: admin
  Password: admin

PostgreSQL:
  Username: admin
  Password: admin
  Database: warehouse
```

### Port Mapping Summary

| Service | Port | Container Name |
|---------|------|----------------|
| Airflow UI | 8080 | batch-etl-airflow |
| PostgreSQL | 5432 | batch-etl-postgres |
| Streamlit | 8501 | batch-etl-streamlit |

---

## Airflow Commands

**Note:** Run these inside the Airflow container or via `docker exec`

### DAG Management

```bash
# Trigger DAG
docker exec -it batch-etl-airflow airflow dags trigger etl_pipeline

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
```

### Alternative (Using Docker Exec)

```bash
# Open bash inside Airflow container
docker exec -it batch-etl-airflow bash

# Then run Airflow commands
airflow dags trigger etl_pipeline
airflow dags list
exit
```

---

## PostgreSQL Commands

### Connect to Database

```bash
# Connect via docker exec
docker exec -it batch-etl-postgres psql -U admin -d warehouse

# Connect with custom host/port
psql -h localhost -p 5432 -U admin -d warehouse
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

-- Exit psql
\q
```

---

## Python Package Management

### Technology Versions

| Tool | Version |
|------|---------|
| Apache Airflow | 2.7.3 |
| PostgreSQL | 15 |
| Streamlit | 1.29.0 |
| Pandas | 2.0.3 |
| SQLAlchemy | 2.0.19 |
| Plotly | 5.18.0 |
| Python | 3.9+ |

### Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Install specific packages
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
```

---

## Running the Pipeline

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
start http://localhost:8501   # Windows
open http://localhost:8501    # Mac
```

### Manual Pipeline Run

```bash
# Run each script manually (for testing)

# Extract
python scripts/extract.py

# Transform
python scripts/transform.py

# Load
python scripts/load.py
```

### Check Pipeline Status

```bash
# Check DAG run status
docker exec -it batch-etl-airflow airflow dags list-runs --dag-id etl_pipeline

# View logs
docker-compose logs airflow -f

# Check data in PostgreSQL
docker exec -it batch-etl-postgres psql -U admin -d warehouse -c "SELECT COUNT(*) FROM fact_trips;"
```

---

## Project Structure Quick Reference

| Folder | Content |
|--------|---------|
| `dags/` | Airflow DAG files (etl_pipeline.py) |
| `scripts/` | ETL Python scripts (extract, transform, load) |
| `data/raw/` | Raw dataset (taxi_data.csv) |
| `data/staging/` | Intermediate files (taxi_raw.csv, taxi_clean.csv) |
| `warehouse/` | Database initialization (init.sql) |
| `dashboard/` | Streamlit app (app.py) + Dockerfile |
| `screenshots/` | Documentation screenshots (16 images) |

---

## Troubleshooting

### Docker Issues

| Issue | Solution |
|-------|----------|
| Docker not running | Start Docker Desktop first |
| Port already in use | Change port in docker-compose.yml |
| Container not starting | `docker-compose logs` to see errors |
| Permission denied | Run terminal as admin |
| Volume conflicts | `docker-compose down -v` |
| Image pull failed | Check internet connection |

### Airflow Issues

| Issue | Solution |
|-------|----------|
| DAG not showing | Wait 30s, restart scheduler |
| Task failed | Check logs in UI |
| Task stuck in running | Clear task and retry |
| Cannot connect to PostgreSQL | Wait for Postgres to initialize |
| Authentication failed | Use admin/admin |

### Common Errors & Solutions

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `Port 8080 already in use` | Change to `8081:8080` |
| `No such file: taxi_data.csv` | Download dataset to `data/raw/` |
| `Connection refused` | Start Docker first |
| `No data in dashboard` | Run DAG first to load data |
| `DAG not found in UI` | Check file in `dags/` folder |
| `airflow: command not found` | Use `docker exec` |

### Quick Troubleshooting Flow

```bash
# 1. Check status of all containers
docker-compose ps

# 2. Check latest errors
docker-compose logs --tail=50

# 3. Restart Airflow (if DAG doesn't appear)
docker-compose restart airflow

# 4. Restart PostgreSQL (if connection issue)
docker-compose restart postgres

# 5. Full reset (if all else fails)
docker-compose down -v && docker-compose up -d
```

---

## DAG Structure Template

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'your_name',
    'depends_on_past': False,
    'start_date': datetime(2026, 7, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'dag_name',
    default_args=default_args,
    description='Your DAG description',
    schedule_interval='@daily',
    catchup=False,
    tags=['etl', 'batch'],
)

def task_function(**context):
    print("Task executed!")
    return "Success"

task = PythonOperator(
    task_id='task_name',
    python_callable=task_function,
    dag=dag,
)
```

---

## One-Liner Commands

### Setup
```bash
# Complete project setup
python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt

# Reset everything
docker-compose down -v && rmdir /s venv && python -m venv venv
```

### Start Everything
```bash
# Windows
venv\Scripts\activate; docker-compose up -d; start http://localhost:8080; start http://localhost:8501

# Mac/Linux
source venv/bin/activate && docker-compose up -d && open http://localhost:8080 && open http://localhost:8501
```

### Data Verification
```bash
# Check row count in PostgreSQL
docker exec -it batch-etl-postgres psql -U admin -d warehouse -c "SELECT COUNT(*) FROM fact_trips;"

# Check DAG status
docker exec -it batch-etl-airflow airflow dags list-runs --dag-id etl_pipeline
```

---

## Important URLs

| Service | URL |
|---------|-----|
| Airflow UI | http://localhost:8080 |
| Streamlit Dashboard | http://localhost:8501 |
| PostgreSQL | localhost:5432 |
| NYC Taxi Data | https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page |

---

## Documentation Links

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

## Quick Tips

1. **Always use Docker** on Windows for Airflow
2. **Activate venv** before working with Python
3. **Check `docker-compose ps`** to ensure all services are running
4. **Use `docker-compose logs -f`** to monitor in real-time
5. **Wait for PostgreSQL** to initialize (10-15 seconds) before triggering DAG
6. **Restart Airflow** after adding new DAGs
7. **Check ports** if services won't start (8080, 5432, 8501)
8. **Trigger DAG manually** first, then schedule will work

---

## File Paths Reference

| File | Path |
|------|------|
| DAG | `dags/etl_pipeline.py` |
| Extract Script | `scripts/extract.py` |
| Transform Script | `scripts/transform.py` |
| Load Script | `scripts/load.py` |
| Dashboard | `dashboard/app.py` |
| Dashboard Dockerfile | `dashboard/Dockerfile` |
| Raw Data | `data/raw/taxi_data.csv` |
| Staging Data | `data/staging/taxi_raw.csv` |
| Clean Data | `data/staging/taxi_clean.csv` |
| Init SQL | `warehouse/init.sql` |
| Docker Compose | `docker-compose.yml` |
| Requirements | `requirements.txt` |
| Environment | `.env` |

---

## Quick Commands Reference Card

```bash
# START
docker-compose up -d

# STATUS
docker-compose ps

# LOGS
docker-compose logs -f

# STOP
docker-compose down

# RESET
docker-compose down -v && docker-compose up -d

# AIRFLOW UI
http://localhost:8080 (admin/admin)

# DASHBOARD
http://localhost:8501

# POSTGRES
docker exec -it batch-etl-postgres psql -U admin -d warehouse

# TRIGGER DAG
docker exec -it batch-etl-airflow airflow dags trigger etl_pipeline
```

---

**Save this cheat sheet for quick reference!**