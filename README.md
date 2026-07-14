# BatchETL Pipeline
## End-to-End Data Engineering Project with Apache Airflow, PostgreSQL, and Streamlit

![Pipeline Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Airflow](https://img.shields.io/badge/Airflow-2.7.3-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red)
![Python](https://img.shields.io/badge/Python-3.9+-blue)

---

## Table of Contents

- [Project Overview](#project-overview)
- [Success Metrics](#success-metrics)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Data Model Design](#data-model-design)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Deployment Guide](#deployment-guide)
- [Dashboard Features](#dashboard-features)
- [Screenshots](#screenshots)
- [Performance](#performance)
- [Business Value](#business-value)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Quick Links](#quick-links)

---

## Project Overview

### What is BatchETL Pipeline?

BatchETL Pipeline is a **production-ready data engineering project** that demonstrates an end-to-end ETL pipeline for NYC Taxi trip data. The pipeline extracts data from CSV files, transforms it using Pandas, loads it into PostgreSQL, and visualizes insights through an interactive Streamlit dashboard.

### Core Goals

1. Build **end-to-end batch ETL pipeline** for NYC Taxi trip data
2. Implement **automated data transformation** using Pandas
3. Create **interactive dashboard** with Streamlit + Plotly
4. Use **containerized deployment** with Docker Compose
5. Provide **comprehensive documentation** with 16 screenshots + 2 architecture diagrams

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Pipeline Automation | Fully automated daily execution |
| Data Quality Validation | 100% (duplicate removal, outlier filtering) |
| Execution Time | < 10 seconds (100,000+ rows) |
| Dashboard | 5 KPIs + 4 chart types |
| Data Freshness | Daily automated updates |

---

## System Architecture

### Architecture Diagram

![System Architecture](screenshots/architecture-diagram.png)

*Figure 1: Complete ETL pipeline architecture showing Airflow → Pandas → PostgreSQL → Streamlit flow*

### Architecture Components

| Component | Purpose | Why Chosen |
|-----------|---------|------------|
| **Apache Airflow** | Orchestration | Industry-standard, reliable scheduling, UI monitoring, retry logic |
| **Pandas** | Data Processing | Powerful transformations, easy to use, Python-native |
| **PostgreSQL** | Data Warehouse | ACID-compliant, robust, widely used in production |
| **Streamlit** | Dashboard | Python-native, rapid development, interactive |
| **Plotly** | Charts | Interactive visualizations, modern, Python-friendly |
| **Docker** | Deployment | Consistent environment, easy to distribute |

### Data Flow Diagram

![Data Flow Diagram](screenshots/data-flow-diagram.png)

*Figure 2: Detailed data flow showing Extract → Transform → Load → Visualize pipeline*

### Data Flow Summary

1. **Extract**: Read CSV file from `data/raw/taxi_data.csv` using Pandas
2. **Stage**: Save raw data to `data/staging/taxi_raw.csv`
3. **Transform**: Clean data (duplicates, nulls, outliers), feature engineering (hour, day, month)
4. **Stage Clean**: Save transformed data to `data/staging/taxi_clean.csv`
5. **Load**: Insert clean data into PostgreSQL `fact_trips` table using SQLAlchemy
6. **Visualize**: Streamlit dashboard queries PostgreSQL for real-time analytics

---

## Technology Stack

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| **Orchestration** | Apache Airflow | 2.7.3 | Industry standard, scheduler |
| **Containerization** | Docker Compose | 3.8 | Multi-service orchestration |
| **Database** | PostgreSQL | 15 | Robust, ACID-compliant |
| **Data Processing** | Pandas | 2.0.3 | Data transformation |
| **Dashboard** | Streamlit | 1.29.0 | Python-native, rapid development |
| **Visualization** | Plotly | 5.18.0 | Interactive charts |
| **Database Adapter** | SQLAlchemy | 2.0.19 | ORM for database connection |

---

## Data Model Design

### Fact Table: `fact_trips`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `trip_id` | SERIAL | NOT NULL | Surrogate key (PK) |
| `vendor_id` | INTEGER | NULL | Vendor code (1/2) |
| `pickup_datetime` | TIMESTAMP | NULL | Trip start time |
| `dropoff_datetime` | TIMESTAMP | NULL | Trip end time |
| `passenger_count` | INTEGER | NULL | Number of passengers |
| `trip_distance` | FLOAT | NULL | Distance in miles |
| `fare_amount` | FLOAT | NULL | Base fare amount |
| `total_amount` | FLOAT | NULL | Total with all fees |
| `payment_type` | INTEGER | NULL | Payment method code |
| `pickup_hour` | INTEGER | NULL | Hour of pickup (0-23) |
| `pickup_day` | VARCHAR(20) | NULL | Day name (Monday-Sunday) |
| `pickup_month` | INTEGER | NULL | Month (1-12) |

### Indexes

```sql
CREATE INDEX idx_pickup_datetime ON fact_trips(pickup_datetime);
CREATE INDEX idx_pickup_day ON fact_trips(pickup_day);
CREATE INDEX idx_fare_amount ON fact_trips(fare_amount);
```

### Data Transformations Applied

| Step | Operation | Justification |
|------|-----------|---------------|
| 1 | Drop duplicates | Data quality |
| 2 | Drop nulls on critical columns | Data integrity |
| 3 | Convert datetime | Feature engineering |
| 4 | Extract hour, day, month | Time-based analysis |
| 5 | Calculate trip_duration | Additional insight |
| 6 | Filter unrealistic values | Remove outliers |
| 7 | Select final columns | Warehouse schema |

### Data Quality Rules

| Rule | Condition | Action |
|------|-----------|--------|
| `trip_distance` | > 0 | Filter |
| `fare_amount` | > 0 | Filter |
| `trip_duration` | > 0 | Filter |
| `trip_distance` | < 100 miles | Remove outlier |
| `fare_amount` | < $500 | Remove outlier |
| Critical columns | NOT NULL | Drop row |

---

## Project Structure

```
batch-etl/
│
├── docker-compose.yml              # Multi-container orchestration
├── .env                            # Environment variables
├── requirements.txt                # Python dependencies
│
├── dags/
│   └── etl_pipeline.py             # Main DAG definition
│
├── scripts/
│   ├── extract.py                  # Extract data from CSV
│   ├── transform.py                # Transform with Pandas
│   └── load.py                     # Load to PostgreSQL
│
├── data/
│   ├── raw/
│   │   └── taxi_data.csv           # Source dataset (100K+ rows)
│   └── staging/
│       ├── taxi_raw.csv            # Extracted data
│       └── taxi_clean.csv          # Transformed data
│
├── warehouse/
│   └── init.sql                    # Database initialization
│
├── dashboard/
│   ├── Dockerfile                  # Dashboard container
│   └── app.py                      # Streamlit application
│
├── screenshots/
│   ├── architecture-diagram.png    # Architecture diagram
│   ├── data-flow-diagram.png       # Data flow diagram
│   ├── 01-folder-structure.png     # Level 1: Mandatory (8)
│   ├── 02-dataset-downloaded.png
│   ├── 03-airflow-dag-list.png
│   ├── 04-airflow-grid-success.png
│   ├── 05-airflow-tree-success.png
│   ├── 06-postgres-data.png
│   ├── 07-dashboard-overview.png
│   ├── 08-dashboard-charts.png
│   ├── 09-airflow-dag-code.png     # Level 2: Recommended (4)
│   ├── 10-extract-script.png
│   ├── 11-transform-script.png
│   ├── 12-load-script.png
│   ├── 13-dashboard-code.png       # Level 3: Value-Add (4)
│   ├── 14-docker-compose.png
│   ├── 15-airflow-log.png
│   └── 16-dashboard-with-filter.png
│
├── README.md                       # Project documentation
├── blueprint.md                    # Technical blueprint
├── cheatsheets.md                  # Quick reference
└── verification checklist.md       # Testing checklist
```

---

## Quick Start

### Prerequisites

| Item | Check Command |
|------|---------------|
| Docker Desktop | `docker --version` |
| Git | `git --version` |
| Internet | For image pulls |

### One Command Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/batch-etl.git
cd batch-etl

# Start all containers
docker-compose up -d

# Verify containers are running
docker-compose ps

# Access Airflow UI
# http://localhost:8080 (admin/admin)

# Trigger the DAG
# Click "Trigger DAG" on etl_pipeline

# Access Dashboard
# http://localhost:8501
```

---

## Deployment Guide

### Step-by-Step Deployment

```bash
# 1. Clone or create project
mkdir batch-etl
cd batch-etl

# 2. Create all files (DAG, scripts, Dockerfile, etc.)

# 3. Download dataset
# Visit https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
# Download Jan 2024 Yellow Taxi, convert to CSV, save as data/raw/taxi_data.csv

# 4. Start containers
docker-compose up -d

# 5. Verify containers
docker-compose ps

# 6. Access Airflow UI
# http://localhost:8080 (admin/admin)

# 7. Trigger DAG
# Click Trigger DAG on etl_pipeline

# 8. Verify in PostgreSQL
docker exec -it batch-etl-postgres psql -U admin -d warehouse
SELECT COUNT(*) FROM fact_trips;
\q

# 9. Launch Dashboard
# http://localhost:8501

# 10. Capture screenshots
# Follow screenshot checklist
```

### Development Setup (Optional)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### requirements.txt

```txt
pandas==2.0.3
psycopg2-binary==2.9.9
sqlalchemy==2.0.19
streamlit==1.29.0
plotly==5.18.0
apache-airflow==2.7.3
python-dotenv==1.0.0
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
| Fare Range | Slider | Min-Max from data | Full range |
| Distance Range | Slider | Min-Max from data | Full range |
| Day of Week | Multiselect | Monday-Sunday | All days |

### Performance Optimization

| Feature | Method | Description |
|---------|--------|-------------|
| Database Connection | `@st.cache_resource` | Reuse connection |
| Data Loading | `@st.cache_data(ttl=300)` | Cache 5 minutes |
| Data Sampling | `df.sample(1000)` | Faster scatter plots |

---

## Screenshots

### Architecture Diagrams (2)

| # | Filename | Description |
|---|----------|-------------|
| 1 | `architecture-diagram.png` | Complete system architecture diagram |
| 2 | `data-flow-diagram.png` | Detailed data flow pipeline diagram |

### Level 1: Mandatory (8 screenshots)

| # | Filename | Description |
|---|----------|-------------|
| 3 | `01-folder-structure.png` | Project structure in VS Code |
| 4 | `02-dataset-downloaded.png` | Raw CSV in `data/raw/` |
| 5 | `03-airflow-dag-list.png` | DAG list with "Success" status |
| 6 | `04-airflow-grid-success.png` | Grid view all green |
| 7 | `05-airflow-tree-success.png` | Tree view confirmation |
| 8 | `06-postgres-data.png` | `SELECT * FROM fact_trips LIMIT 10` |
| 9 | `07-dashboard-overview.png` | Full dashboard page |
| 10 | `08-dashboard-charts.png` | All 4 charts visible |

### Level 2: Recommended (4 screenshots)

| # | Filename | Description |
|---|----------|-------------|
| 11 | `09-airflow-dag-code.png` | `dags/etl_pipeline.py` |
| 12 | `10-extract-script.png` | `scripts/extract.py` |
| 13 | `11-transform-script.png` | `scripts/transform.py` |
| 14 | `12-load-script.png` | `scripts/load.py` |

### Level 3: Value-Add (4 screenshots)

| # | Filename | Description |
|---|----------|-------------|
| 15 | `13-dashboard-code.png` | `dashboard/app.py` |
| 16 | `14-docker-compose.png` | `docker-compose.yml` |
| 17 | `15-airflow-log.png` | Task log with row count |
| 18 | `16-dashboard-with-filter.png` | Dashboard with applied filters |

---

## Performance

### Data Volume

| Metric | Value |
|--------|-------|
| Input Rows | 100,000+ |
| Input Columns | ~20 |
| Output Rows | ~95,000 (after cleaning) |
| Output Columns | 11 |
| PostgreSQL Size | ~10-15 MB |

### Execution Time

| Task | Time |
|------|------|
| Extract | ~1 second |
| Transform | ~3-5 seconds |
| Load | ~2-3 seconds |
| **Total** | **~6-10 seconds** |

### Container Resource Usage

| Container | Memory | CPU |
|-----------|--------|-----|
| PostgreSQL | ~50-100 MB | Minimal |
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

## Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Docker container not starting | Check Docker Desktop is running, verify ports are available |
| Airflow DAG not appearing | Wait 30 seconds, restart Airflow container |
| Task stuck in running | Clear task from UI or CLI, retry |
| PostgreSQL connection refused | Wait for PostgreSQL to initialize (10-15 seconds) |
| No data in dashboard | Trigger DAG first, verify data loaded |
| Permission denied | Run commands with admin privileges (Windows) |
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

---

## Future Enhancements

| Enhancement | Description | Complexity |
|-------------|-------------|------------|
| Incremental Loading | Load only new data | Medium |
| Data Quality Monitoring | Great Expectations | Medium |
| Alert System | Email/Slack notifications | Low |
| Star Schema Expansion | Add dimensions | Medium |
| Real-Time Processing | Kafka + Spark | High |
| Dashboard Enhancements | More charts, filters | Low |
| Machine Learning | Trip duration prediction | High |

---

## Quick Links

| Resource | URL |
|----------|-----|
| **Airflow UI** | http://localhost:8080 |
| **Dashboard** | http://localhost:8501 |
| **NYC Taxi Data** | https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page |
| **Airflow Docs** | https://airflow.apache.org/docs/ |
| **PostgreSQL Docs** | https://www.postgresql.org/docs/ |
| **Streamlit Docs** | https://docs.streamlit.io/ |
| **Plotly Docs** | https://plotly.com/python/ |
| **Docker Docs** | https://docs.docker.com/ |

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

- NYC Taxi & Limousine Commission for providing the data
- Apache Airflow, PostgreSQL, Streamlit, and all open-source tools used

---

## Contact

- **Project Maintainer**: Data Engineering Team
- **GitHub**: [https://github.com/yourusername/batch-etl](https://github.com/yourusername/batch-etl)
- **Issues**: [https://github.com/yourusername/batch-etl/issues](https://github.com/yourusername/batch-etl/issues)

---

**Built with industry-standard data engineering tools**