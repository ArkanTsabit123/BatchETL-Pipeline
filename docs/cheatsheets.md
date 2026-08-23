# BATCHETL PIPELINE - CHEAT SHEET

---

## Document Information

| Property | Value |
|----------|-------|
| Version | 4.0.0 |
| Last Updated | 2026-08-23 |
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
8. [Monitoring Commands](#8-monitoring-commands)
9. [AWS Commands](#9-aws-commands)
10. [Terraform Commands](#10-terraform-commands)
11. [Project Structure Quick Reference](#11-project-structure-quick-reference)
12. [Troubleshooting](#12-troubleshooting)
13. [DAG Structure Template](#13-dag-structure-template)
14. [One-Liner Commands](#14-one-liner-commands)
15. [Important URLs](#15-important-urls)
16. [Documentation Links](#16-documentation-links)
17. [Quick Tips](#17-quick-tips)
18. [File Paths Reference](#18-file-paths-reference)
19. [Environment Variables](#19-environment-variables)
20. [Verification Commands](#20-verification-commands)
21. [Pipeline Execution Results](#21-pipeline-execution-results)

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
# Start all services (PostgreSQL, Airflow, Streamlit, Prometheus, Grafana, PostgreSQL Exporter)
docker-compose up -d

# Start with logs
docker-compose up

# Start specific service
docker-compose up -d postgres
docker-compose up -d airflow
docker-compose up -d streamlit
docker-compose up -d prometheus
docker-compose up -d grafana
docker-compose up -d postgres-exporter

# Start monitoring services only
docker-compose up -d prometheus grafana postgres-exporter

# Stop all services
docker-compose down

# Stop and remove volumes (clean reset)
docker-compose down -v

# Restart services
docker-compose restart

# Restart specific service
docker-compose restart airflow
docker-compose restart prometheus
docker-compose restart grafana
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
docker-compose logs prometheus -f
docker-compose logs grafana -f
docker-compose logs postgres-exporter -f

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

# Prometheus
http://localhost:9090

# Grafana
http://localhost:3000

# PostgreSQL Exporter
http://localhost:9187/metrics

# PostgreSQL
localhost:5432
```

### Docker Default Credentials

```bash
Airflow UI:
  Username: admin
  Password: admin
  URL: http://localhost:8080

Grafana:
  Username: admin
  Password: admin
  URL: http://localhost:3000

PostgreSQL:
  Username: admin
  Password: admin
  Database: warehouse
  Host: localhost
  Port: 5432

Prometheus:
  No authentication required
  URL: http://localhost:9090
```

### Port Mapping Summary

| Service | Host Port | Container Port | Container Name |
|---------|-----------|----------------|----------------|
| Airflow UI | 8080 | 8080 | batch-etl-airflow |
| PostgreSQL | 5432 | 5432 | batch-etl-postgres |
| Streamlit | 8501 | 8501 | batch-etl-streamlit |
| Prometheus | 9090 | 9090 | batch-etl-prometheus |
| Grafana | 3000 | 3000 | batch-etl-grafana |
| PostgreSQL Exporter | 9187 | 9187 | batch-etl-postgres-exporter |

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
| Grafana | 10.2.0 |
| Prometheus | 2.47.0 |
| Terraform | 1.5.0 |
| AWS CLI | Latest |

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

## 8. Monitoring Commands

### Prometheus

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Prometheus metrics
curl http://localhost:9090/api/v1/query?query=up

# Query specific metrics
curl 'http://localhost:9090/api/v1/query?query=airflow_dag_run_duration_seconds'

# Query all metrics
curl 'http://localhost:9090/api/v1/query?query={__name__=~".+"}'

# Reload Prometheus configuration
curl -X POST http://localhost:9090/-/reload

# Check Prometheus health
curl http://localhost:9090/-/healthy

# Check Prometheus rules
curl http://localhost:9090/api/v1/rules
```

### PostgreSQL Exporter

```bash
# Check PostgreSQL Exporter metrics
curl http://localhost:9187/metrics

# Check PostgreSQL Exporter health
curl http://localhost:9187/health

# Check specific PostgreSQL metrics
curl http://localhost:9187/metrics | grep pg_stat_database
```

### Grafana

```bash
# Check Grafana health
curl http://localhost:3000/api/health

# Check Grafana version
curl http://localhost:3000/api/frontend/settings

# Login to Grafana (for API calls)
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"user":"admin","password":"admin"}'

# List Grafana datasources
curl -H "Authorization: Bearer <token>" http://localhost:3000/api/datasources

# Reload Grafana dashboards
curl -X POST http://localhost:3000/api/admin/provisioning/dashboards/reload
```

### Airflow Metrics

```bash
# Check Airflow metrics
curl http://localhost:8080/admin/metrics

# Check specific Airflow metrics
curl http://localhost:8080/admin/metrics | grep airflow_dag

# Check Airflow health
curl http://localhost:8080/health
```

### Alerting

```bash
# Check Prometheus alerts
curl http://localhost:9090/api/v1/alerts

# Check Alertmanager status (if configured)
curl http://localhost:9093/api/v1/alerts
```

---

## 9. AWS Commands

### AWS CLI Configuration

```bash
# Configure AWS CLI
aws configure
# AWS Access Key ID: AKIAXXXXXXXX
# AWS Secret Access Key: xxxxxxxxxxxxxxxx
# Default region: us-east-1
# Default output format: json

# Check AWS configuration
aws configure list

# Check AWS identity
aws sts get-caller-identity
```

### S3 Commands

```bash
# Create S3 bucket
aws s3 mb s3://batchetl-data-lake --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket batchetl-data-lake \
  --versioning-configuration Status=Enabled

# List buckets
aws s3 ls

# List bucket contents
aws s3 ls s3://batchetl-data-lake/

# Upload files
aws s3 sync ./dags/ s3://batchetl-airflow-bucket/dags/
aws s3 cp ./requirements.txt s3://batchetl-airflow-bucket/requirements.txt

# Download files
aws s3 cp s3://batchetl-data-lake/data/taxi_data.csv ./

# Delete bucket contents
aws s3 rm s3://batchetl-data-lake --recursive

# Delete bucket
aws s3 rb s3://batchetl-data-lake --force
```

### RDS Commands

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier batchetl-db \
  --db-instance-class db.t4g.medium \
  --engine postgres \
  --engine-version 15.3 \
  --master-username admin \
  --master-user-password SecurePassword123! \
  --allocated-storage 100 \
  --storage-type gp3 \
  --multi-az \
  --backup-retention-period 7

# List RDS instances
aws rds describe-db-instances

# Describe specific RDS instance
aws rds describe-db-instances --db-instance-identifier batchetl-db

# Get RDS endpoint
aws rds describe-db-instances \
  --db-instance-identifier batchetl-db \
  --query 'DBInstances[0].Endpoint.Address'

# Delete RDS instance
aws rds delete-db-instance \
  --db-instance-identifier batchetl-db \
  --skip-final-snapshot

# Create RDS snapshot
aws rds create-db-snapshot \
  --db-instance-identifier batchetl-db \
  --db-snapshot-identifier batchetl-db-snapshot-$(date +%Y%m%d)
```

### MWAA Commands

```bash
# Create MWAA environment
aws mwaa create-environment \
  --name batchetl-airflow \
  --airflow-version 2.7.3 \
  --environment-class mwaa.medium \
  --execution-role-arn arn:aws:iam::123456789012:role/mwaa-execution-role \
  --source-bucket-arn arn:aws:s3:::batchetl-airflow-bucket

# List MWAA environments
aws mwaa list-environments

# Describe MWAA environment
aws mwaa get-environment --name batchetl-airflow

# Get MWAA webserver URL
aws mwaa get-environment \
  --name batchetl-airflow \
  --query 'Environment.WebserverUrl'

# Check MWAA status
aws mwaa get-environment \
  --name batchetl-airflow \
  --query 'Environment.Status'

# Update MWAA environment
aws mwaa update-environment \
  --name batchetl-airflow \
  --source-bucket-arn arn:aws:s3:::batchetl-airflow-bucket

# Delete MWAA environment
aws mwaa delete-environment --name batchetl-airflow
```

### CloudWatch Commands

```bash
# List CloudWatch log groups
aws logs describe-log-groups --log-group-name-prefix /aws/mwaa

# Get CloudWatch logs
aws logs get-log-events \
  --log-group-name /aws/mwaa/batchetl-airflow \
  --log-stream-name scheduler

# Create CloudWatch alarm
aws cloudwatch put-metric-alarm \
  --alarm-name batchetl-rds-cpu-high \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --metric-name CPUUtilization \
  --namespace AWS/RDS \
  --period 300 \
  --statistic Average \
  --threshold 70 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts
```

### IAM Commands

```bash
# Create IAM role for MWAA
aws iam create-role \
  --role-name mwaa-execution-role \
  --assume-role-policy-document file://trust-policy.json

# Attach policy to role
aws iam attach-role-policy \
  --role-name mwaa-execution-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonMWAAExecutionRolePolicy

# List IAM roles
aws iam list-roles

# Get IAM role details
aws iam get-role --role-name mwaa-execution-role
```

---

## 10. Terraform Commands

### Initialization

```bash
# Initialize Terraform
cd terraform
terraform init

# Initialize with backend configuration
terraform init -backend-config="environments/dev/backend.tfvars"

# Get modules
terraform get

# Validate configuration
terraform validate
```

### Planning

```bash
# Plan infrastructure changes (dev)
terraform plan -var-file="environments/dev/terraform.tfvars"

# Plan with detailed output
terraform plan -var-file="environments/dev/terraform.tfvars" -out=tfplan

# Plan with refresh
terraform plan -var-file="environments/dev/terraform.tfvars" -refresh=true

# Plan for specific module
terraform plan -var-file="environments/dev/terraform.tfvars" -target=module.rds
```

### Applying

```bash
# Apply infrastructure (dev)
terraform apply -var-file="environments/dev/terraform.tfvars" -auto-approve

# Apply with plan file
terraform apply tfplan

# Apply specific resource
terraform apply -var-file="environments/dev/terraform.tfvars" -target=module.s3

# Apply with parallel execution
terraform apply -var-file="environments/dev/terraform.tfvars" -parallelism=10
```

### Destroying

```bash
# Destroy infrastructure (dev)
terraform destroy -var-file="environments/dev/terraform.tfvars" -auto-approve

# Destroy specific resource
terraform destroy -var-file="environments/dev/terraform.tfvars" -target=module.rds

# Destroy with force
terraform destroy -var-file="environments/dev/terraform.tfvars" -force
```

### State Management

```bash
# List resources in state
terraform state list

# Show resource details
terraform state show module.rds.aws_db_instance.main

# Move resource in state
terraform state mv module.rds.aws_db_instance.main module.rds.aws_db_instance.prod

# Remove resource from state
terraform state rm module.rds.aws_db_instance.main

# Pull state
terraform state pull > state.json

# Push state
terraform state push state.json
```

### Outputs

```bash
# List outputs
terraform output

# Get specific output
terraform output rds_endpoint

# Get sensitive output
terraform output -json db_connection_string

# Get all outputs in JSON
terraform output -json
```

### Workspace Management

```bash
# List workspaces
terraform workspace list

# Create workspace
terraform workspace new dev

# Switch workspace
terraform workspace select staging

# Delete workspace
terraform workspace delete dev
```

### Formatting and Linting

```bash
# Format Terraform files
terraform fmt -recursive

# Check formatting
terraform fmt -check

# Validate configuration
terraform validate

# Lint with tflint (if installed)
tflint
```

### Other Useful Commands

```bash
# Get Terraform version
terraform version

# Show resource graph
terraform graph | dot -Tpng > graph.png

# Show providers
terraform providers

# Refresh state
terraform refresh -var-file="environments/dev/terraform.tfvars"

# Import existing resource
terraform import module.rds.aws_db_instance.main <db-instance-id>

# Generate provider documentation
terraform providers schema -json > schema.json
```

---

## 11. Project Structure Quick Reference

| Folder | Content |
|--------|---------|
| archive/ | Diagram generator scripts (architecture, data flow, ERD) |
| dags/ | Airflow DAG files (etl_pipeline.py) |
| scripts/ | ETL Python scripts (extract, transform, load) |
| data/raw/ | Raw dataset (taxi_data.csv - 2.96M rows) |
| data/staging/ | Intermediate files (taxi_raw.csv, taxi_clean.csv) |
| warehouse/ | Database initialization (init.sql) |
| dashboard/ | Streamlit app (app.py) + Dockerfile |
| monitoring/ | Prometheus, Grafana, alerting configuration |
| terraform/ | Terraform modules for AWS infrastructure |
| screenshots/ | Documentation screenshots |
| docs/ | Documentation files (blueprint, cheatsheet, checklist) |
| docs/diagrams/ | Diagram source files (PDF, XML, DBML, drawio, MWB) |
| batchetl-streamlit/ | Streamlit Cloud deployment files |

---

## 12. Troubleshooting

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

### Monitoring Issues

| Issue | Solution |
|-------|----------|
| Prometheus no targets | Check targets endpoint, verify service health |
| Grafana no data | Check datasource config, verify Prometheus connection |
| PostgreSQL Exporter fails | Check DATA_SOURCE_NAME environment variable |
| Dashboards not loading | Check provisioning directory, restart Grafana |
| Alert rules not firing | Check Prometheus evaluation interval, verify expression |
| Metrics not showing | Check scrape interval, verify metrics path |

### AWS + Terraform Issues

| Issue | Solution |
|-------|----------|
| Terraform apply fails | Check AWS credentials, IAM permissions |
| RDS connection timeout | Check security groups, subnet configuration |
| MWAA environment not ready | Wait 20-30 minutes for provisioning |
| S3 access denied | Check bucket policies, IAM role permissions |
| CloudWatch no logs | Check log group configuration, wait for propagation |

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
docker-compose logs prometheus --tail=50
docker-compose logs grafana --tail=50

# 4. Restart Airflow (if DAG doesn't appear)
docker-compose restart airflow

# 5. Restart PostgreSQL (if connection issue)
docker-compose restart postgres

# 6. Restart monitoring services (if no metrics)
docker-compose restart prometheus grafana postgres-exporter

# 7. Restart all services
docker-compose restart

# 8. Full reset (if all else fails)
docker-compose down -v && docker-compose up -d

# 9. Check disk space
df -h

# 10. Check container resource usage
docker stats
```

---

## 13. DAG Structure Template

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

## 14. One-Liner Commands

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
venv\Scripts\Activate.ps1; docker-compose up -d; start http://localhost:8080; start http://localhost:8501; start http://localhost:9090; start http://localhost:3000

# Windows CMD
venv\Scripts\activate.bat && docker-compose up -d && start http://localhost:8080 && start http://localhost:8501 && start http://localhost:9090 && start http://localhost:3000

# Mac/Linux
source venv/bin/activate && docker-compose up -d && open http://localhost:8080 && open http://localhost:8501 && open http://localhost:9090 && open http://localhost:3000
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

### Monitoring Verification

```bash
# Check Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Check all metrics are available
curl -s http://localhost:9090/api/v1/query?query=up | jq '.data.result[] | {job: .metric.job, value: .value[1]}'

# Check Grafana health
curl -s http://localhost:3000/api/health | jq '.'

# Check PostgreSQL Exporter
curl -s http://localhost:9187/metrics | head -20
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

## 15. Important URLs

| Service | URL |
|---------|-----|
| Airflow UI | http://localhost:8080 |
| Streamlit Dashboard (Local) | http://localhost:8501 |
| Streamlit Dashboard (Live Demo) | https://batchetl.streamlit.app |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| PostgreSQL Exporter | http://localhost:9187/metrics |
| AWS RDS Console | https://console.aws.amazon.com/rds |
| AWS MWAA Console | https://console.aws.amazon.com/mwaa |
| AWS S3 Console | https://console.aws.amazon.com/s3 |
| PostgreSQL | localhost:5432 |
| NYC Taxi Data | https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page |

---

## 16. Documentation Links

| Resource | URL |
|----------|-----|
| Airflow Docs | https://airflow.apache.org/docs/ |
| PostgreSQL Docs | https://www.postgresql.org/docs/ |
| Streamlit Docs | https://docs.streamlit.io/ |
| Plotly Docs | https://plotly.com/python/ |
| Pandas Docs | https://pandas.pydata.org/docs/ |
| Docker Docs | https://docs.docker.com/ |
| SQLAlchemy Docs | https://docs.sqlalchemy.org/ |
| Prometheus Docs | https://prometheus.io/docs/ |
| Grafana Docs | https://grafana.com/docs/ |
| Terraform Docs | https://developer.hashicorp.com/terraform/docs |
| AWS RDS Docs | https://docs.aws.amazon.com/rds/ |
| AWS MWAA Docs | https://docs.aws.amazon.com/mwaa/ |

---

## 17. Quick Tips

1. Always use Docker on Windows for Airflow
2. Activate venv before working with Python locally
3. Check docker-compose ps to ensure all services are running
4. Use docker-compose logs -f to monitor in real-time
5. Wait for database initialization (10-15 seconds) before triggering DAG
6. Restart Airflow after adding new DAGs
7. Check ports if services won't start (8080, 5432, 8501, 9090, 3000, 9187)
8. Trigger DAG manually first, then schedule will work
9. Use verification scripts to check each phase
10. Screenshots should be 300+ DPI for documentation
11. Use --no-cache-dir with pip to save disk space
12. Set environment variables in .env file for sensitive data
13. Use docker exec for Airflow commands to avoid local installation
14. Clear task instances when retrying failed tasks
15. Monitor resource usage with docker stats
16. Use Grafana dashboards for real-time monitoring
17. Use Prometheus for metrics collection and alerting
18. Use Terraform for infrastructure as code
19. Always use AWS Secrets Manager for credentials in production
20. Enable CloudTrail for audit logging in AWS

---

## 18. File Paths Reference

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
| Prometheus Config | monitoring/prometheus.yml |
| Alert Rules | monitoring/alerts.yml |
| Grafana Dashboards | monitoring/grafana/dashboards/ |
| Grafana Datasource | monitoring/grafana/datasources/ |
| ETL Exporter | monitoring/exporters/etl_metrics.py |
| Terraform Root | terraform/main.tf |
| Terraform Variables | terraform/variables.tf |
| Terraform Outputs | terraform/outputs.tf |
| Terraform RDS Module | terraform/modules/rds/ |
| Terraform MWAA Module | terraform/modules/mwaa/ |
| Terraform S3 Module | terraform/modules/s3/ |
| Terraform Networking Module | terraform/modules/networking/ |
| Terraform Monitoring Module | terraform/modules/monitoring/ |
| Terraform Dev Config | terraform/environments/dev/terraform.tfvars |
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

## 19. Environment Variables

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

# Monitoring Environment Variables
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin
GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel
DATA_SOURCE_NAME=postgresql://admin:admin@postgres:5432/warehouse?sslmode=disable

# AWS Environment Variables
AWS_ACCESS_KEY_ID=AKIAXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxx
AWS_DEFAULT_REGION=us-east-1
```

### Set Environment Variables

```bash
# Windows PowerShell
$env:AIRFLOW_UID="50000"
$env:POSTGRES_PASSWORD="admin"
$env:GF_SECURITY_ADMIN_PASSWORD="admin"

# Windows CMD
set AIRFLOW_UID=50000
set POSTGRES_PASSWORD=admin
set GF_SECURITY_ADMIN_PASSWORD=admin

# Mac/Linux
export AIRFLOW_UID=50000
export POSTGRES_PASSWORD=admin
export GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## 20. Verification Commands

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
python verify-phase-10.py
python verify-phase-11.py
```

### Troubleshooting Modules

```bash
python troubleshoot.py
python troubleshoot_docker.py
python troubleshoot_airflow.py
python troubleshoot_postgres.py
python troubleshoot_dashboard.py
python troubleshoot_network.py
python troubleshoot_monitoring.py
python troubleshoot_aws.py
```

---

## 21. Pipeline Execution Results

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

# START MONITORING ONLY
docker-compose up -d prometheus grafana postgres-exporter

# STATUS
docker-compose ps

# LOGS
docker-compose logs -f

# LOGS - MONITORING
docker-compose logs prometheus -f
docker-compose logs grafana -f
docker-compose logs postgres-exporter -f

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

# PROMETHEUS
http://localhost:9090

# GRAFANA
http://localhost:3000 (admin/admin)

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

# CHECK PROMETHEUS TARGETS
curl http://localhost:9090/api/v1/targets

# CHECK GRAFANA HEALTH
curl http://localhost:3000/api/health

# TERRAFORM PLAN
cd terraform && terraform plan -var-file="environments/dev/terraform.tfvars"

# TERRAFORM APPLY
terraform apply -var-file="environments/dev/terraform.tfvars" -auto-approve

# AWS S3 SYNC
aws s3 sync ./dags/ s3://batchetl-airflow-bucket/dags/
```

---

*Last Updated: 2026-08-23*
*Version: 4.0.0*