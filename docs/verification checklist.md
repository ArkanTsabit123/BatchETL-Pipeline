# Verification Checklist - BatchETL Pipeline

---

## Document Information

| Property | Value |
|----------|-------|
| **Version** | 1.0.0 |
| **Last Updated** | 2026-07-14 |
| **Status** | Ready for Verification |
| **Total Checks** | 105 |

---

## Reference Documentation

| Document | Purpose |
|----------|---------|
| [Technical Blueprint](blueprint.md) | Technical specifications and architecture |
| [README](README.md) | Project overview and quick start |
| [Cheat Sheet](cheatsheets.md) | Quick commands reference |

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Pending / Not yet started |
| ✅ | Complete / Passed |
| 🔄 | In Progress |
| ❌ | Failed / Needs attention |
| ⚠️ | Warning / Needs review |

---

## Phase 1: Setup & Environment

**Phase Goal:** All project files and environment configured correctly

| # | Task | Reference | Status | Notes |
|---|------|-----------|--------|-------|
| 1.1 | Project folder structure created | README#project-structure | ⬜ | batch-etl/ with all subfolders |
| 1.2 | Virtual environment created | README#development-setup | ⬜ | python -m venv venv |
| 1.3 | Virtual environment activated | README#development-setup | ⬜ | (venv) active |
| 1.4 | requirements.txt created | blueprint.md#requirements | ⬜ | All dependencies listed |
| 1.5 | All dependencies installed | README#requirements | ⬜ | pip install -r requirements.txt |
| 1.6 | .env file created | blueprint.md#environment | ⬜ | Environment variables |
| 1.7 | Docker Desktop installed | README#prerequisites | ⬜ | docker --version |
| 1.8 | Docker Compose installed | README#prerequisites | ⬜ | docker-compose --version |
| 1.9 | docker-compose.yml created | blueprint.md#docker-compose | ⬜ | 3 services (postgres, airflow, streamlit) |
| 1.10 | Dataset downloaded | README#deployment | ⬜ | data/raw/taxi_data.csv (100K+ rows) |
| 1.11 | warehouse/init.sql created | blueprint.md#init-sql | ⬜ | Database initialization script |
| 1.12 | DAG file created | blueprint.md#dag | ⬜ | dags/etl_pipeline.py |
| 1.13 | Script files created | blueprint.md#scripts | ⬜ | extract.py, transform.py, load.py |
| 1.14 | Dashboard file created | blueprint.md#dashboard | ⬜ | dashboard/app.py |
| 1.15 | Dashboard Dockerfile created | blueprint.md#dashboard | ⬜ | dashboard/Dockerfile |
| 1.16 | Screenshots folder created | README#screenshots | ⬜ | screenshots/ directory exists |

**Phase 1 Checks:** 16 | **Passed:** 0 | **Failed:** 0 | **Pending:** 16 | **Progress:** 0%

---

## Phase 2: Docker & Container Setup

**Phase Goal:** All Docker containers running and accessible

| # | Task | Reference | Status | Notes |
|---|------|-----------|--------|-------|
| 2.1 | PostgreSQL container running | cheatsheets.md#docker | ⬜ | docker-compose ps |
| 2.2 | Airflow container running | cheatsheets.md#docker | ⬜ | docker-compose ps |
| 2.3 | Streamlit container running | cheatsheets.md#docker | ⬜ | docker-compose ps |
| 2.4 | All containers healthy | cheatsheets.md#docker | ⬜ | No exit codes |
| 2.5 | PostgreSQL accessible | cheatsheets.md#postgres | ⬜ | Port 5432 |
| 2.6 | Airflow UI accessible | cheatsheets.md#urls | ⬜ | http://localhost:8080 |
| 2.7 | Airflow default login works | cheatsheets.md#credentials | ⬜ | admin/admin |
| 2.8 | Database initialized | blueprint.md#data-model | ⬜ | fact_trips table exists |
| 2.9 | Docker volumes created | blueprint.md#volumes | ⬜ | postgres_data |
| 2.10 | Docker network created | blueprint.md#docker-compose | ⬜ | batch-etl-network |
| 2.11 | Streamlit dashboard accessible | cheatsheets.md#urls | ⬜ | http://localhost:8501 |

**Phase 2 Checks:** 11 | **Passed:** 0 | **Failed:** 0 | **Pending:** 11 | **Progress:** 0%

---

## Phase 3: Airflow DAG Creation

**Phase Goal:** DAG properly configured and visible in Airflow UI

| # | Task | Reference | Status | Notes |
|---|------|-----------|--------|-------|
| 3.1 | DAG file valid Python syntax | blueprint.md#dag | ⬜ | No syntax errors |
| 3.2 | DAG appears in Airflow UI | cheatsheets.md#airflow | ⬜ | DAGs list |
| 3.3 | DAG is unpaused | cheatsheets.md#airflow | ⬜ | Toggle on |
| 3.4 | DAG has correct schedule | blueprint.md#dag-config | ⬜ | @daily |
| 3.5 | DAG has correct default_args | blueprint.md#dag-config | ⬜ | owner, retries, start_date |
| 3.6 | Extract task defined | blueprint.md#dag | ⬜ | PythonOperator |
| 3.7 | Transform task defined | blueprint.md#dag | ⬜ | PythonOperator |
| 3.8 | Load task defined | blueprint.md#dag | ⬜ | PythonOperator |
| 3.9 | Task dependencies set | blueprint.md#dag | ⬜ | extract >> transform >> load |
| 3.10 | DAG tags configured | blueprint.md#dag | ⬜ | ['etl', 'batch', 'taxi', 'nyc'] |
| 3.11 | DAG description set | blueprint.md#dag | ⬜ | 'Extract, Transform, Load NYC Taxi Data' |

**Phase 3 Checks:** 11 | **Passed:** 0 | **Failed:** 0 | **Pending:** 11 | **Progress:** 0%

---

## Phase 4: Pipeline Execution

**Phase Goal:** All tasks execute successfully without errors

| # | Task | Reference | Status | Notes |
|---|------|-----------|--------|-------|
| 4.1 | DAG triggered successfully | cheatsheets.md#airflow | ⬜ | Click "Trigger DAG" |
| 4.2 | Extract task status = Success | blueprint.md#pipeline-phases | ⬜ | Green in Grid View |
| 4.3 | Transform task status = Success | blueprint.md#pipeline-phases | ⬜ | Green in Grid View |
| 4.4 | Load task status = Success | blueprint.md#pipeline-phases | ⬜ | Green in Grid View |
| 4.5 | Extract task logs show row count | blueprint.md#extract | ⬜ | Log verification |
| 4.6 | Transform task logs show cleaning stats | blueprint.md#transform | ⬜ | Duplicates, nulls, outliers |
| 4.7 | Load task logs show row count | blueprint.md#load | ⬜ | Successfully loaded N rows |
| 4.8 | Airflow Tree View all green | README#screenshots | ⬜ | Visual confirmation |
| 4.9 | Pipeline execution time < 10 seconds | blueprint.md#performance | ⬜ | For 100K rows |
| 4.10 | No Airflow task errors | cheatsheets.md#troubleshooting | ⬜ | Check logs |
| 4.11 | Staging files created | blueprint.md#pipeline-phases | ⬜ | taxi_raw.csv and taxi_clean.csv exist |

**Phase 4 Checks:** 11 | **Passed:** 0 | **Failed:** 0 | **Pending:** 11 | **Progress:** 0%

---

## Phase 5: PostgreSQL Data Verification

**Phase Goal:** Data properly loaded into PostgreSQL with correct schema

| # | Task | Reference | Status | Notes |
|---|------|-----------|--------|-------|
| 5.1 | fact_trips table exists | cheatsheets.md#postgres | ⬜ | \dt in psql |
| 5.2 | Data loaded successfully | cheatsheets.md#postgres | ⬜ | SELECT COUNT(*) |
| 5.3 | Row count > 90,000 | blueprint.md#performance | ⬜ | After cleaning |
| 5.4 | Indexes created | blueprint.md#indexes | ⬜ | \di in psql |
| 5.5 | Primary key exists | blueprint.md#data-model | ⬜ | trip_id SERIAL |
| 5.6 | All columns present | blueprint.md#data-model | ⬜ | 11 columns |
| 5.7 | Correct data types | blueprint.md#data-model | ⬜ | TIMESTAMP, FLOAT, INTEGER |
| 5.8 | No duplicate trip_ids | blueprint.md#data-quality | ⬜ | SELECT COUNT(DISTINCT trip_id) |
| 5.9 | pickup_datetime not null | blueprint.md#data-quality | ⬜ | CHECK constraint |
| 5.10 | Sample query returns data | cheatsheets.md#postgres | ⬜ | SELECT * LIMIT 10 |
| 5.11 | fare_amount values between 0-500 | blueprint.md#data-quality | ⬜ | Outliers filtered |
| 5.12 | trip_distance values between 0-100 | blueprint.md#data-quality | ⬜ | Outliers filtered |

**Phase 5 Checks:** 12 | **Passed:** 0 | **Failed:** 0 | **Pending:** 12 | **Progress:** 0%

---

## Phase 6: Dashboard Verification

**Phase Goal:** All dashboard features working correctly

| # | Task | Reference | Status | Notes |
|---|------|-----------|--------|-------|
| 6.1 | Dashboard accessible | cheatsheets.md#urls | ⬜ | http://localhost:8501 |
| 6.2 | Dashboard loads without errors | README#dashboard | ⬜ | No exceptions |
| 6.3 | Data connection successful | blueprint.md#dashboard | ⬜ | Connection to PostgreSQL |
| 6.4 | Total Trips KPI displayed | blueprint.md#kpis | ⬜ | With count |
| 6.5 | Average Fare KPI displayed | blueprint.md#kpis | ⬜ | With $ sign |
| 6.6 | Avg Distance KPI displayed | blueprint.md#kpis | ⬜ | With miles |
| 6.7 | Avg Passengers KPI displayed | blueprint.md#kpis | ⬜ | With 1 decimal |
| 6.8 | Total Revenue KPI displayed | blueprint.md#kpis | ⬜ | With $ and commas |
| 6.9 | Revenue by Day chart renders | blueprint.md#charts | ⬜ | Bar chart |
| 6.10 | Trips per Hour chart renders | blueprint.md#charts | ⬜ | Bar chart |
| 6.11 | Fare Distribution chart renders | blueprint.md#charts | ⬜ | Histogram |
| 6.12 | Distance vs Fare chart renders | blueprint.md#charts | ⬜ | Scatter plot |
| 6.13 | Fare Range filter works | blueprint.md#filters | ⬜ | Slider updates data |
| 6.14 | Distance Range filter works | blueprint.md#filters | ⬜ | Slider updates data |
| 6.15 | Day of Week filter works | blueprint.md#filters | ⬜ | Multiselect updates data |
| 6.16 | Raw data table displays | blueprint.md#dashboard | ⬜ | Expandable section |
| 6.17 | Filtered row count updates | blueprint.md#dashboard | ⬜ | Dynamic text |
| 6.18 | Charts update with filters | blueprint.md#dashboard | ⬜ | Dynamic updates |
| 6.19 | KPIs update with filters | blueprint.md#dashboard | ⬜ | Dynamic updates |

**Phase 6 Checks:** 19 | **Passed:** 0 | **Failed:** 0 | **Pending:** 19 | **Progress:** 0%

---

## Phase 7: Screenshots Documentation

**Phase Goal:** All 18 images (2 diagrams + 16 screenshots) captured and saved

| # | Filename | Description | Reference | Status |
|---|----------|-------------|-----------|--------|
| 7.1 | `architecture-diagram.png` | Complete system architecture diagram | README#screenshots | ⬜ |
| 7.2 | `data-flow-diagram.png` | Detailed data flow pipeline diagram | README#screenshots | ⬜ |
| 7.3 | `01-folder-structure.png` | Project folder structure in VS Code | README#screenshots | ⬜ |
| 7.4 | `02-dataset-downloaded.png` | Raw CSV in data/raw/ directory | README#screenshots | ⬜ |
| 7.5 | `03-airflow-dag-list.png` | Airflow UI showing etl_pipeline DAG | README#screenshots | ⬜ |
| 7.6 | `04-airflow-grid-success.png` | Grid View all tasks green | README#screenshots | ⬜ |
| 7.7 | `05-airflow-tree-success.png` | Tree View all tasks green | README#screenshots | ⬜ |
| 7.8 | `06-postgres-data.png` | PostgreSQL query results | README#screenshots | ⬜ |
| 7.9 | `07-dashboard-overview.png` | Full dashboard page | README#screenshots | ⬜ |
| 7.10 | `08-dashboard-charts.png` | All 4 charts visible | README#screenshots | ⬜ |
| 7.11 | `09-airflow-dag-code.png` | dags/etl_pipeline.py code | README#screenshots | ⬜ |
| 7.12 | `10-extract-script.png` | scripts/extract.py code | README#screenshots | ⬜ |
| 7.13 | `11-transform-script.png` | scripts/transform.py code | README#screenshots | ⬜ |
| 7.14 | `12-load-script.png` | scripts/load.py code | README#screenshots | ⬜ |
| 7.15 | `13-dashboard-code.png` | dashboard/app.py code | README#screenshots | ⬜ |
| 7.16 | `14-docker-compose.png` | docker-compose.yml code | README#screenshots | ⬜ |
| 7.17 | `15-airflow-log.png` | Task log with row count | README#screenshots | ⬜ |
| 7.18 | `16-dashboard-with-filter.png` | Dashboard with filter applied | README#screenshots | ⬜ |

**Phase 7 Checks:** 18 | **Passed:** 0 | **Failed:** 0 | **Pending:** 18 | **Progress:** 0%

---

## Phase 8: Documentation & Deployment

**Phase Goal:** All documentation complete and project deployed

| # | Task | Reference | Status | Notes |
|---|------|-----------|--------|-------|
| 8.1 | README.md completed | README | ⬜ | Full documentation |
| 8.2 | blueprint.md completed | blueprint.md | ⬜ | Technical blueprint |
| 8.3 | cheatsheets.md completed | cheatsheets.md | ⬜ | Quick reference |
| 8.4 | verification checklist.md completed | This file | ⬜ | Testing checklist |
| 8.5 | LICENSE added | - | ⬜ | MIT License |
| 8.6 | .gitignore configured | - | ⬜ | Python + Docker + Airflow |
| 8.7 | Git initialized | - | ⬜ | git init |
| 8.8 | Git commit | - | ⬜ | All files committed |
| 8.9 | GitHub repository created | - | ⬜ | Public repo |
| 8.10 | Remote origin set | - | ⬜ | git remote add origin |
| 8.11 | Push to GitHub | - | ⬜ | git push -u origin main |
| 8.12 | README rendered on GitHub | - | ⬜ | Check formatting |
| 8.13 | Screenshots visible on GitHub | - | ⬜ | Images render |
| 8.14 | LinkedIn post published | - | ⬜ | Project showcase |
| 8.15 | All badges display correctly | README | ⬜ | Status badges working |

**Phase 8 Checks:** 15 | **Passed:** 0 | **Failed:** 0 | **Pending:** 15 | **Progress:** 0%

---

## Overall Summary

| Phase | Total Checks | Passed | Failed | Pending | Progress |
|-------|--------------|--------|--------|---------|----------|
| Phase 1: Setup & Environment | 16 | 0 | 0 | 16 | 0% |
| Phase 2: Docker & Container Setup | 11 | 0 | 0 | 11 | 0% |
| Phase 3: Airflow DAG Creation | 11 | 0 | 0 | 11 | 0% |
| Phase 4: Pipeline Execution | 11 | 0 | 0 | 11 | 0% |
| Phase 5: PostgreSQL Data Verification | 12 | 0 | 0 | 12 | 0% |
| Phase 6: Dashboard Verification | 19 | 0 | 0 | 19 | 0% |
| Phase 7: Screenshots Documentation | 18 | 0 | 0 | 18 | 0% |
| Phase 8: Documentation & Deployment | 15 | 0 | 0 | 15 | 0% |
| **TOTAL** | **113** | **0** | **0** | **113** | **0% Complete** |

---

## Quick Commands Reference

### Docker Management

```bash
# Start all containers
docker-compose up -d

# Stop all containers
docker-compose down

# Check container status
docker-compose ps

# View logs
docker-compose logs -f

# Full reset
docker-compose down -v && docker-compose up -d
```

### Airflow Commands

```bash
# Trigger DAG
docker exec -it batch-etl-airflow airflow dags trigger etl_pipeline

# List DAGs
docker exec -it batch-etl-airflow airflow dags list

# Check DAG runs
docker exec -it batch-etl-airflow airflow dags list-runs --dag-id etl_pipeline

# View logs in UI
# http://localhost:8080 → Browse → DAG Runs → Click on run
```

### PostgreSQL Commands

```bash
# Connect to PostgreSQL
docker exec -it batch-etl-postgres psql -U admin -d warehouse

# Count rows
SELECT COUNT(*) FROM fact_trips;

# View sample
SELECT * FROM fact_trips LIMIT 10;

# Check indexes
\di

# Check table structure
\d fact_trips

# Exit psql
\q
```

### Dashboard Access

```bash
# Windows
start http://localhost:8501

# Mac/Linux
open http://localhost:8501
```

### Screenshot Tips

```bash
# Windows Snipping Tool
Win + Shift + S

# Mac Screenshot
Cmd + Shift + 4

# Browser Developer Tools
Ctrl + Shift + I → Toggle Device Toolbar → Capture screenshot
```

---

## Troubleshooting Checklist

### If DAG Doesn't Appear in Airflow

```bash
# 1. Check if file exists
docker exec -it batch-etl-airflow ls -la /opt/airflow/dags/

# 2. Check Python syntax
docker exec -it batch-etl-airflow python -m py_compile /opt/airflow/dags/etl_pipeline.py

# 3. Restart Airflow
docker-compose restart airflow

# 4. Check logs
docker-compose logs airflow --tail=50

# 5. Wait 30 seconds and refresh
```

### If Pipeline Fails

```bash
# 1. Check task logs
# Go to Airflow UI → Task Instance → Log

# 2. Check data paths
docker exec -it batch-etl-airflow ls -la /opt/airflow/data/raw/
docker exec -it batch-etl-airflow ls -la /opt/airflow/data/staging/

# 3. Check PostgreSQL connection
docker exec -it batch-etl-airflow python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql+psycopg2://admin:admin@postgres:5432/warehouse'); print('Connected')"

# 4. Clear and retry
docker exec -it batch-etl-airflow airflow tasks clear -d etl_pipeline
```

### If Dashboard Shows No Data

```bash
# 1. Check PostgreSQL has data
docker exec -it batch-etl-postgres psql -U admin -d warehouse -c "SELECT COUNT(*) FROM fact_trips;"

# 2. Check connection string in dashboard
docker exec -it batch-etl-streamlit cat /app/app.py | grep DATABASE_URL

# 3. Restart dashboard
docker-compose restart streamlit
```

---

## Completion Checklist

Before finalizing the project, ensure all these items are complete:

### Documentation
- [ ] README.md complete with all sections
- [ ] blueprint.md complete with all sections
- [ ] cheatsheets.md complete with all commands
- [ ] verification checklist.md complete (this file)
- [ ] LICENSE file added (MIT)
- [ ] .gitignore properly configured

### Screenshots & Diagrams
- [ ] architecture-diagram.png created from ASCII
- [ ] data-flow-diagram.png created from ASCII
- [ ] All 16 screenshots captured
- [ ] Screenshots properly named (01-16)
- [ ] Screenshots visible in README.md
- [ ] Screenshots pushed to GitHub

### Deployment
- [ ] GitHub repository public
- [ ] All code pushed
- [ ] README rendered correctly
- [ ] Screenshots visible
- [ ] LinkedIn post published

### Verification
- [ ] All 113 checks completed
- [ ] All statuses updated
- [ ] No failed checks
- [ ] Project ready for review

---

**Updated: 2026-07-14**