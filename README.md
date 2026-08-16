# BatchETL Pipeline

## End-to-End Data Engineering Project with Apache Airflow, PostgreSQL, and Streamlit

[![Pipeline Status](https://img.shields.io/badge/status-production%20ready-brightgreen)](https://github.com/ArkanTsabit123/BatchETL-Pipeline)
[![Airflow](https://img.shields.io/badge/Airflow-2.7.3-blue)](https://airflow.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit%20Cloud-brightgreen)](https://batchetl.streamlit.app)

---

## Project Overview

BatchETL Pipeline is a production-ready data engineering project that demonstrates an end-to-end ETL pipeline for NYC Taxi trip data. The pipeline extracts data from CSV files, transforms it using Pandas, loads it into PostgreSQL, and visualizes insights through an interactive Streamlit dashboard.

### Key Highlights

- **2.96+ Million Rows** processed from NYC Taxi trip data
- **Automated ETL Pipeline** with data cleaning, deduplication, and outlier removal
- **Interactive Dashboard** with 5 KPIs, 4 charts, and 5 filters
- **Containerized Deployment** using Docker Compose
- **Apache Airflow Orchestration** with daily scheduling
- **Live Demo** on Streamlit Cloud

### Quick Stats

| Metric | Value |
|--------|-------|
| Input Rows | 2,964,624 |
| Output Rows | 2,869,525 |
| Execution Time | 15-25 seconds |
| Dashboard KPIs | 5 |
| Charts | 4 |
| Filters | 5 |
| Screenshots | 22 |
| Verification Checks | 156 |

---

## Live Demo

### Streamlit Cloud Dashboard

[https://batchetl.streamlit.app](https://batchetl.streamlit.app)

The dashboard is deployed on Streamlit Cloud with 100,000 rows of sample data for fast and responsive performance.

**Features:**
- 5 KPIs: Total Trips, Average Fare, Avg Distance, Avg Passengers, Total Revenue
- 4 Charts: Revenue by Day, Trips per Hour, Fare Distribution, Distance vs Fare
- 5 Filters: Fare Range, Distance Range, Day of Week, Payment Type, Vendor ID
- Sample data: 100,000 rows of NYC Taxi trip records

---

## Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Orchestration | Apache Airflow | 2.7.3 |
| Containerization | Docker Compose | 3.8 |
| Database | PostgreSQL | 15 |
| Data Processing | Pandas | 2.0.3 |
| Dashboard | Streamlit | 1.29.0 |
| Visualization | Plotly | 5.18.0 |
| Database Adapter | SQLAlchemy | 2.0.19 |
| Python | Python | 3.10+ |

---

## System Architecture

### Architecture Diagram

![System Architecture](screenshots/architecture-diagram.png)

### Data Flow Diagram

![Data Flow Diagram](screenshots/data-flow-diagram.png)

### Entity Relationship Diagram

![ERD Diagram](screenshots/erd-diagram.png)

---

## Quick Start

```bash
# Clone repository
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

| Filter | Type | Options |
|--------|------|---------|
| Fare Range | Slider | Min-Max from data |
| Distance Range | Slider | Min-Max from data |
| Day of Week | Multiselect | Monday-Sunday |
| Payment Type | Selectbox | 1-6 |
| Vendor ID | Selectbox | 1-2 |

---

## Verification System

### 9-Phase Verification

| Phase | Name | Checks | Status |
|-------|------|--------|--------|
| 1 | Setup & Environment | 16 | 100% |
| 2 | Docker & Container Setup | 13 | 100% |
| 3 | Airflow DAG Creation | 12 | 100% |
| 4 | Pipeline Execution | 13 | 100% |
| 5 | PostgreSQL Data Verification | 14 | 100% |
| 6 | Dashboard Verification (Local) | 23 | 100% |
| 7 | Screenshots Documentation | 22 | 100% |
| 8 | Documentation & Deployment | 20 | 100% |
| 9 | Streamlit Cloud Deployment | 17 | 100% |
| **TOTAL** | **All Phases** | **156** | **100%** |

```bash
# Run all verifications
python run_all_verifications.py

# Individual verification
python verify-phase-1.py
python verify-phase-2.py
# ... up to verify-phase-9.py
```

---

## Quick Commands

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

# CHECK DATA
docker exec -it batch-etl-postgres psql -U admin -d warehouse -c "SELECT COUNT(*) FROM fact_trips;"

# RUN SCRIPTS MANUALLY
python scripts/extract.py && python scripts/transform.py && python scripts/load.py

# DOCKER CLEANUP
docker system prune -f
```

---

## Documentation

For complete project documentation, please refer to the `/docs/` directory:

| File | Purpose |
|------|---------|
| [blueprint.md](/docs/blueprint.md) | Technical blueprint |
| [cheatsheets.md](/docs/cheatsheets.md) | Quick reference commands |
| [verification-checklist.md](/docs/verification-checklist.md) | Testing checklist |
| [CHANGELOG.md](/CHANGELOG.md) | Release history |

---

## Performance

| Metric | Value |
|--------|-------|
| Input Rows | 2,964,624 |
| Output Rows | 2,869,525 |
| Extract Time | 43 seconds |
| Transform Time | 27 seconds |
| Load Time | 4-5 minutes |
| **Total Time** | **5-6 minutes** |
| PostgreSQL Size | ~300 MB |

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| Report generation | 2+ hours manual | 5 minutes automated |
| Data freshness | Daily manual | Fully automated daily |
| Human error risk | High | Eliminated |
| Decision-making latency | High | Low (instant access) |

---

## Troubleshooting

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

1. Never expose ports to public internet in production
2. Change all default credentials before production deployment
3. Use environment variables for sensitive data
4. Implement network isolation using Docker networks
5. Regularly update Docker images for security patches

---

## Quick Links

| Resource | URL |
|----------|-----|
| **Live Demo** | https://batchetl.streamlit.app |
| **Airflow UI** | http://localhost:8080 |
| **Dashboard (Local)** | http://localhost:8501 |
| **NYC Taxi Data** | https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page |
| **Airflow Docs** | https://airflow.apache.org/docs/ |
| **PostgreSQL Docs** | https://www.postgresql.org/docs/ |
| **Streamlit Docs** | https://docs.streamlit.io/ |
| **Plotly Docs** | https://plotly.com/python/ |

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
- **GitHub**: https://github.com/ArkanTsabit123
- **LinkedIn**: https://linkedin.com/in/arkan-tsabit

---

Built by Arkan Tsabit | Data Engineer