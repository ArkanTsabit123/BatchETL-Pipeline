# BatchETL Pipeline

## End-to-End Data Engineering Project with Apache Airflow, PostgreSQL, and Streamlit

![Pipeline Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Airflow](https://img.shields.io/badge/Airflow-2.7.3-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Screenshots](https://img.shields.io/badge/screenshots-3%2F19-orange)
![Verification](https://img.shields.io/badge/verification-84.25%25-yellow)

---

## Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Entity Relationship Diagram](#entity-relationship-diagram)
- [Technology Stack](#technology-stack)
- [Data Model Design](#data-model-design)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Quick Start](#quick-start)
- [Deployment Guide](#deployment-guide)
- [Dashboard Features](#dashboard-features)
- [Verification System](#verification-system)
- [Troubleshooting](#troubleshooting)
- [Screenshots](#screenshots)
- [Performance](#performance)
- [Business Value](#business-value)
- [Security Considerations](#security-considerations)
- [Quick Commands Reference](#quick-commands-reference)
- [Quick Links](#quick-links)

---

## Project Overview

BatchETL Pipeline is a production-ready data engineering project that demonstrates an end-to-end ETL pipeline for NYC Taxi trip data. The pipeline extracts data from CSV files, transforms it using Pandas, loads it into PostgreSQL/MySQL, and visualizes insights through an interactive Streamlit dashboard.

### Core Features

- Processes **2.96+ million rows** of NYC Taxi trip data
- Automated ETL with data cleaning, deduplication, and outlier removal
- Interactive dashboard with 5 KPIs, 4 charts, and 5 filters
- Containerized deployment with Docker Compose
- Apache Airflow orchestration with daily scheduling

### Success Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| Pipeline Automation | Daily execution | Yes |
| Data Quality Validation | 100% | Yes |
| Execution Time | < 30 seconds | ~15-25 seconds |
| Dashboard | 5 KPIs + 4 charts + 5 filters | Yes |
| Data Rows Processed | 100,000+ | 2,869,525 |

---

## System Architecture

### Architecture Diagram

![System Architecture](screenshots/architecture-diagram.png)

*Figure 1: Complete ETL pipeline architecture showing Airflow -> Pandas -> PostgreSQL -> Streamlit flow*

### Architecture Components

| Component | Purpose | Justification |
|-----------|---------|---------------|
| Apache Airflow | Orchestration | Industry-standard, reliable scheduling, retry logic |
| Pandas | Data Processing | Powerful transformations, Python-native |
| PostgreSQL/MySQL | Data Warehouse | ACID-compliant, robust, production-ready |
| Streamlit | Dashboard | Python-native, rapid development |
| Plotly | Charts | Interactive visualizations |
| Docker | Deployment | Consistent environment, easy distribution |

### Data Flow Diagram

![Data Flow Diagram](screenshots/data-flow-diagram.png)

*Figure 2: Detailed data flow showing Extract -> Transform -> Load -> Visualize pipeline*

### Data Flow Summary

1. **Extract**: Read CSV from `data/raw/taxi_data.csv` using Pandas (2.96M rows)
2. **Stage**: Save raw data to `data/staging/taxi_raw.csv`
3. **Transform**: Clean data, remove duplicates and outliers, engineer features (hour, day, month)
4. **Stage Clean**: Save transformed data to `data/staging/taxi_clean.csv` (2.87M rows)
5. **Load**: Insert clean data into PostgreSQL/MySQL `fact_trips` table
6. **Visualize**: Streamlit dashboard queries database for real-time analytics

---

## Entity Relationship Diagram

![ERD Diagram](screenshots/erd-diagram.png)

*Figure 3: Entity Relationship Diagram showing fact_trips table structure*

### ERD Description

The `fact_trips` table serves as the central fact table in this data warehouse. It contains 12 columns organized into logical groups:

| Column Group | Columns | Description |
|--------------|---------|-------------|
| **Surrogate Key** | `trip_id` | Primary key, auto-incrementing serial |
| **Dimensions** | `vendor_id`, `payment_type` | Categorical attributes for filtering |
| **Time Dimensions** | `pickup_hour`, `pickup_day`, `pickup_month` | Extracted from pickup_datetime |
| **Measures** | `trip_distance`, `fare_amount`, `total_amount`, `passenger_count` | Numerical values for aggregation |
| **Timestamps** | `pickup_datetime`, `dropoff_datetime` | Original datetime values |

### Relationship Notes

This is a single-table fact model (denormalized) optimized for analytical queries. All dimensions are stored directly in the fact table to simplify queries and improve performance for read-heavy analytics workloads.

---

## Technology Stack

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| Orchestration | Apache Airflow | 2.7.3 | Industry standard for workflow scheduling |
| Containerization | Docker Compose | 3.8 | Multi-service orchestration |
| Database | PostgreSQL / MySQL | 15 / 8.0 | Robust, ACID-compliant data warehouse |
| Data Processing | Pandas | 2.0.3 | Data transformation and manipulation |
| Dashboard | Streamlit | 1.29.0 | Python-native web application |
| Visualization | Plotly | 5.18.0 | Interactive charting library |
| Database Adapter | SQLAlchemy | 2.0.19 | ORM for database connections |

---

## Data Model Design

### Fact Table: `fact_trips`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `trip_id` | SERIAL | NOT NULL | Surrogate key (Primary Key) |
| `vendor_id` | INTEGER | NULL | Vendor code (1 or 2) |
| `pickup_datetime` | TIMESTAMP WITHOUT TIME ZONE | NULL | Trip start time |
| `dropoff_datetime` | TIMESTAMP WITHOUT TIME ZONE | NULL | Trip end time |
| `passenger_count` | INTEGER | NULL | Number of passengers |
| `trip_distance` | NUMERIC(10,2) | NULL | Distance in miles |
| `fare_amount` | NUMERIC(10,2) | NULL | Base fare amount |
| `total_amount` | NUMERIC(10,2) | NULL | Total with all fees |
| `payment_type` | INTEGER | NULL | Payment method code |
| `pickup_hour` | INTEGER | NULL | Hour of pickup (0-23) |
| `pickup_day` | VARCHAR(20) | NULL | Day name (Monday-Sunday) |
| `pickup_month` | INTEGER | NULL | Month (1-12) |

### Indexes

```sql
CREATE INDEX idx_pickup_datetime ON fact_trips(pickup_datetime);
CREATE INDEX idx_pickup_day ON fact_trips(pickup_day);
CREATE INDEX idx_fare_amount ON fact_trips(fare_amount);
CREATE INDEX idx_trip_distance ON fact_trips(trip_distance);
CREATE INDEX idx_vendor_id ON fact_trips(vendor_id);
CREATE INDEX idx_pickup_hour ON fact_trips(pickup_hour);
CREATE INDEX idx_pickup_month ON fact_trips(pickup_month);
CREATE INDEX idx_payment_type ON fact_trips(payment_type);
```

### Data Transformations Applied

| Step | Operation | Justification |
|------|-----------|---------------|
| 1 | Drop duplicates | Data quality |
| 2 | Drop nulls on critical columns | Data integrity |
| 3 | Convert datetime | Feature engineering |
| 4 | Extract hour, day, month | Time-based analysis |
| 5 | Filter unrealistic values | Remove outliers |
| 6 | Validate pickup < dropoff | Data consistency |
| 7 | Select final columns | Warehouse schema |

### Data Quality Rules

| Rule | Condition | Action |
|------|-----------|--------|
| `trip_distance` | BETWEEN 0 AND 100 | Filter out invalid |
| `fare_amount` | BETWEEN 0 AND 500 | Filter out invalid |
| `passenger_count` | >= 0 | Remove negative |
| `pickup_datetime` | < dropoff_datetime | Validate trip duration |
| Critical columns | NOT NULL | Drop row |

---

## Project Structure

```
batch-etl/
│
├── archive/                             # Diagram generator scripts
│   ├── architecture-diagram.py
│   ├── data-flow-diagram.py
│   └── erd-diagram.py
│
├── docker-compose.yml                   # Multi-container orchestration
├── requirements.txt                     # Python dependencies
├── .gitignore                           # Git ignore rules
├── .env                                 # Environment variables
├── LICENSE                              # MIT License
│
├── dags/
│   └── etl_pipeline.py                  # Airflow DAG definition
│
├── scripts/
│   ├── extract.py                       # Extract data from CSV
│   ├── transform.py                     # Transform with Pandas
│   └── load.py                          # Load to database
│
├── data/
│   ├── raw/
│   │   └── taxi_data.csv                # Source dataset (2.96M rows)
│   └── staging/
│       ├── taxi_raw.csv                 # Extracted data
│       └── taxi_clean.csv               # Transformed data
│
├── warehouse/
│   └── init.sql                         # Database initialization
│
├── dashboard/
│   ├── Dockerfile                       # Dashboard container
│   ├── requirements.txt                 # Dashboard dependencies
│   └── app.py                           # Streamlit application
│
├── docs/
│   ├── diagrams/                        # Diagram source files
│   │   ├── architecture-diagram.pdf
│   │   ├── architecture-diagram.xml
│   │   ├── data-flow-diagram.pdf
│   │   ├── erd-diagram.dbml
│   │   ├── erd-diagram.drawio
│   │   └── erd-diagram.mwb
│   ├── blueprint.md                     # Technical blueprint
│   ├── cheatsheet.md                    # Quick reference (tunggal)
│   └── verification-checklist.md        # Testing checklist
│
├── screenshots/
│   ├── architecture-diagram.png         # Architecture diagram (600 DPI)
│   ├── data-flow-diagram.png            # Data flow diagram (600 DPI)
│   ├── erd-diagram.png                  # Entity Relationship Diagram
│   └── 01-16-*.png                      # Screenshots (pending)
│
├── verify-phase-1.py                    # Phase 1: Setup verification (16 checks)
├── verify-phase-2.py                    # Phase 2: Docker verification (13 checks)
├── verify-phase-3.py                    # Phase 3: DAG verification (12 checks)
├── verify-phase-4.py                    # Phase 4: Pipeline verification (13 checks)
├── verify-phase-5.py                    # Phase 5: Data verification (14 checks)
├── verify-phase-6.py                    # Phase 6: Dashboard verification (23 checks)
├── verify-phase-7.py                    # Phase 7: Screenshots verification (19 checks)
├── verify-phase-8.py                    # Phase 8: Documentation verification (17 checks)
├── run_all_verifications.py             # Run all verification scripts (127 checks)
│
├── troubleshoot.py                      # Main troubleshooting menu
├── troubleshoot_airflow.py              # Airflow troubleshooting
├── troubleshoot_dashboard.py            # Dashboard troubleshooting
├── troubleshoot_docker.py               # Docker troubleshooting
├── troubleshoot_network.py              # Network troubleshooting
├── troubleshoot_postgres.py             # PostgreSQL troubleshooting
│
├── README.md                            # Project documentation
├── setup_project.py                     # Project setup script
└── structure.py                         # Display project structure
```

---

## Environment Variables

Create a `.env` file in the project root:

```bash
# .env file
AIRFLOW_UID=50000
AIRFLOW_GID=50000
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=warehouse
POSTGRES_PORT=5432
MYSQL_USER=admin
MYSQL_PASSWORD=admin
MYSQL_DATABASE=warehouse
MYSQL_PORT=3306
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__WEBSERVER__SECRET_KEY=your-secret-key-here
AIRFLOW_CONN_POSTGRES=postgresql://admin:admin@postgres:5432/warehouse
PYTHONPATH=/opt/airflow
DATA_PATH=/opt/airflow/data
```

---

## Quick Start

### Prerequisites

| Item | Check Command |
|------|---------------|
| Docker Desktop | `docker --version` |
| Git | `git --version` |
| Python 3.10+ | `python --version` |

### One Command Setup

```bash
# Clone the repository
git clone https://github.com/ArkanTsabit123/BatchETL-Pipeline.git
cd BatchETL-Pipeline

# Start all containers
docker-compose up -d

# Verify containers are running
docker-compose ps

# Access Airflow UI
# http://localhost:8080 (admin/admin)

# Access Dashboard
# http://localhost:8501

# Trigger the DAG
# Airflow UI -> etl_pipeline -> Trigger DAG
```

---

## Deployment Guide

### Step-by-Step Deployment

```bash
# 1. Clone repository
git clone https://github.com/ArkanTsabit123/BatchETL-Pipeline.git
cd BatchETL-Pipeline

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start containers
docker-compose up -d

# 5. Verify containers
docker-compose ps

# 6. Access Airflow UI
# http://localhost:8080 (admin/admin)

# 7. Run ETL manually (optional)
python scripts/extract.py
python scripts/transform.py
python scripts/load.py

# 8. Launch Dashboard
# http://localhost:8501

# 9. Run verifications
python run_all_verifications.py
```

---

## Dashboard Features

### KPI Cards

| KPI | Calculation | Display Format |
|-----|-------------|----------------|
| Total Trips | `COUNT(*)` | `{value:,}` |
| Average Fare | `AVG(fare_amount)` | `${value:.2f}` |
| Avg Distance | `AVG(trip_distance)` | `{value:.2f} miles` |
| Avg Passengers | `AVG(passenger_count)` | `{value:.1f}` |
| Total Revenue | `SUM(total_amount)` | `${value:,.2f}` |

### Charts

| Chart | Type | Description |
|-------|------|-------------|
| Revenue by Day | Bar Chart | Revenue distribution across days |
| Trips per Hour | Bar Chart | Trip volume by hour of day |
| Fare Distribution | Histogram | Distribution of fare amounts |
| Distance vs Fare | Scatter Plot | Relationship between distance and fare |

### Filters

| Filter | Type | Options | Default |
|--------|------|---------|---------|
| Fare Range | Slider | Min-Max from data | [0, 100] |
| Distance Range | Slider | Min-Max from data | [0, 20] |
| Day of Week | Multiselect | Monday-Sunday | All days |
| Payment Type | Selectbox | 1-6 | All types |
| Vendor ID | Selectbox | 1-2 | All |

---

## Verification System

### 8-Phase Verification

| Phase | Name | Checks | Description | Status |
|-------|------|--------|-------------|--------|
| 1 | Setup & Environment | 16 | Folder structure, venv, dependencies | ✅ 100% |
| 2 | Docker & Container Setup | 13 | PostgreSQL, Airflow, Streamlit containers | ✅ 100% |
| 3 | Airflow DAG Creation | 12 | DAG syntax, tasks, dependencies | ✅ 100% |
| 4 | Pipeline Execution | 13 | Extract, Transform, Load tasks | ✅ 100% |
| 5 | PostgreSQL Data Verification | 14 | Schema, indexes, data quality | ✅ 100% |
| 6 | Dashboard Verification | 23 | KPIs, charts, filters, responsiveness | ⚠️ 91.30% |
| 7 | Screenshots Documentation | 19 | 19 screenshots + 3 diagrams | ⚠️ 15.79% |
| 8 | Documentation & Deployment | 17 | README, LICENSE, Git, GitHub | ⚠️ 88.24% |
| **TOTAL** | **All Phases** | **127** | **Complete verification** | **⚠️ 84.25%** |

### Run All Verifications

```bash
python run_all_verifications.py
```

### Individual Verification

```bash
python verify-phase-1.py
python verify-phase-2.py
# ... up to verify-phase-8.py
```

---

## Troubleshooting

### Run All Troubleshooting

```bash
python troubleshoot.py
# Select option 6 for all checks
```

### Individual Troubleshooting Modules

```bash
python troubleshoot_docker.py
python troubleshoot_airflow.py
python troubleshoot_postgres.py
python troubleshoot_dashboard.py
python troubleshoot_network.py
```

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Docker container not starting | Check Docker Desktop is running, verify ports are available |
| Airflow DAG not appearing | Wait 30-60 seconds, restart Airflow container |
| Task stuck in running | Clear task from UI or CLI, retry |
| Database connection refused | Wait for database to initialize (10-15 seconds) |
| No data in dashboard | Run ETL scripts or trigger DAG first |
| Port already in use | Change port in docker-compose.yml |

### Logs and Debugging

```bash
# View all container logs
docker-compose logs -f

# View specific container logs
docker-compose logs airflow -f
docker-compose logs postgres -f
docker-compose logs streamlit -f

# Check container status
docker-compose ps

# Full reset
docker-compose down -v && docker-compose up -d
```

---

## Screenshots

### Architecture Diagrams - ✅ COMPLETED

| # | Filename | Description | Status |
|---|----------|-------------|--------|
| 1 | `architecture-diagram.png` | Complete system architecture diagram (600 DPI) | ✅ Done |
| 2 | `data-flow-diagram.png` | Detailed data flow pipeline diagram (600 DPI) | ✅ Done |
| 3 | `erd-diagram.png` | Entity Relationship Diagram for fact_trips (600 DPI) | ✅ Done |

### Level 1: Mandatory (8) - ⬜ PENDING

| # | Filename | Description | Status |
|---|----------|-------------|--------|
| 4 | `01-folder-structure.png` | Project structure in VS Code | ✅ Done |
| 5 | `02-dataset-downloaded.png` | Raw CSV in `data/raw/` | ✅ Done |
| 6 | `03-airflow-dag-list.png` | DAG list with "Success" status | ✅ Done |
| 7 | `04-airflow-grid-success.png` | Grid view all green | ✅ Done |
| 8 | `05-airflow-tree-success.png` | Tree view confirmation | ✅ Done |
| 9 | `06-postgres-data.png` | `SELECT * FROM fact_trips LIMIT 10` | ✅ Done |
| 10 | `07-dashboard-overview.png` | Full dashboard page | ⬜ Pending |
| 11 | `08-dashboard-charts.png` | All 4 charts visible | ⬜ Pending |

### Level 2: Recommended (4) - ⬜ PENDING

| # | Filename | Description | Status |
|---|----------|-------------|--------|
| 12 | `09-airflow-dag-code.png` | `dags/etl_pipeline.py` | ⬜ Pending |
| 13 | `10-extract-script.png` | `scripts/extract.py` | ⬜ Pending |
| 14 | `11-transform-script.png` | `scripts/transform.py` | ⬜ Pending |
| 15 | `12-load-script.png` | `scripts/load.py` | ⬜ Pending |

### Level 3: Value-Add (4) - ⬜ PENDING

| # | Filename | Description | Status |
|---|----------|-------------|--------|
| 16 | `13-dashboard-code.png` | `dashboard/app.py` | ⬜ Pending |
| 17 | `14-docker-compose.png` | `docker-compose.yml` | ⬜ Pending |
| 18 | `15-airflow-log.png` | Task log with row count | ⬜ Pending |
| 19 | `16-dashboard-with-filter.png` | Dashboard with applied filters | ⬜ Pending |

---

## Performance

### Data Volume

| Metric | Value |
|--------|-------|
| Input Rows | 2,964,624 |
| Input Columns | ~20 |
| Output Rows | 2,869,525 (after cleaning) |
| Output Columns | 11 |
| Database Size | ~300 MB |
| Outliers Removed | 95,099 |

### Execution Time

| Task | Time |
|------|------|
| Extract | ~2-4 seconds |
| Transform | ~8-12 seconds |
| Load | ~5-8 seconds |
| **Total** | **~15-25 seconds** |

### Container Resource Usage

| Container | Memory | CPU |
|-----------|--------|-----|
| PostgreSQL | ~100-200 MB | Minimal |
| Airflow | ~200-300 MB | Minimal |
| Streamlit | ~100-150 MB | Minimal |

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| Report generation | 2+ hours manual | 5 minutes automated |
| Data freshness | Daily manual | Fully automated daily |
| Human error risk | High | Eliminated |
| Decision-making latency | High | Low (instant access) |

### Use Cases

1. **Urban Mobility Analytics**: City planners analyze ride patterns
2. **Pricing Strategy**: Identify peak demand hours
3. **Operational Efficiency**: Optimize driver availability
4. **Regulatory Reporting**: Generate transportation reports

---

## Security Considerations

### Default Credentials (Change for Production)

| Service | Username | Password |
|---------|----------|----------|
| Airflow UI | admin | admin |
| PostgreSQL | admin | admin |

### Network Ports

| Port | Service | Exposure |
|------|---------|----------|
| 8080 | Airflow UI | Localhost |
| 5432 | PostgreSQL | Localhost |
| 8501 | Dashboard | Localhost |

### Security Best Practices

1. **Never expose ports to public internet in production**
2. **Change all default credentials before production deployment**
3. **Use environment variables for sensitive data**
4. **Implement network isolation using Docker networks**
5. **Regularly update Docker images for security patches**

---

## Quick Commands Reference

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

# DASHBOARD
http://localhost:8501

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

# RUN TROUBLESHOOTING
python troubleshoot.py

# DOCKER CLEANUP
docker system prune -f

# NETWORK INFO
docker network inspect batch-etl_default

# FULL RESET
docker-compose down -v && docker-compose up -d
```

---

## Quick Links

| Resource | URL |
|----------|-----|
| **Airflow UI** | http://localhost:8080 |
| **Dashboard** | http://localhost:8501 |
| **NYC Taxi Data (Yellow)** | https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page |
| **NYC Taxi Data (Green)** | https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page |
| **Airflow Docs** | https://airflow.apache.org/docs/ |
| **PostgreSQL Docs** | https://www.postgresql.org/docs/ |
| **Streamlit Docs** | https://docs.streamlit.io/ |
| **Plotly Docs** | https://plotly.com/python/ |
| **Docker Docs** | https://docs.docker.com/ |

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- NYC Taxi & Limousine Commission for providing the data
- Apache Airflow, PostgreSQL, Streamlit, and all open-source tools used

---

## Contact

- **Project Maintainer**: Arkan Tsabit
- **GitHub**: https://github.com/ArkanTsabit123/BatchETL-Pipeline