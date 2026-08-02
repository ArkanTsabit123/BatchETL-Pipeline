# BATCHETL PIPELINE - TECHNICAL BLUEPRINT

## Document Information

| Property | Value |
|----------|-------|
| **Version** | 1.0.0 |
| **Last Updated** | 2026-08-02 |
| **Status** | Production Ready |
| **Orchestration** | Apache Airflow 2.7.3 |
| **Database** | PostgreSQL 15 / MySQL 8.0 |
| **Dashboard** | Streamlit 1.29.0 |

---

## Project Overview

### Core Goals

1. Build **end-to-end batch ETL pipeline** for NYC Taxi trip data
2. Implement **automated data transformation** using Pandas
3. Create **interactive dashboard** with Streamlit + Plotly
4. Use **containerized deployment** with Docker Compose
5. Provide **comprehensive documentation** with 19 screenshots + 3 architecture diagrams

### Success Metrics

- Fully automated daily pipeline execution
- 100% data quality validation (duplicate removal, outlier filtering)
- < 30 seconds pipeline execution time (2.96M+ rows)
- Interactive dashboard with 5 KPIs + 4 chart types

---

## System Architecture

### Architecture Diagram

> **SCREENSHOT COMPLETED:** `screenshots/architecture-diagram.png`
> *Professional diagram generated from Python script (600 DPI)*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DOCKER CONTAINER ENVIRONMENT                        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     ORCHESTRATION LAYER (Airflow)                   │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │   dags/etl_pipeline.py                                      │   │    │
│  │  │   - DAG ID: etl_pipeline                                   │   │    │
│  │  │   - Schedule: 0 0 * * * (daily at midnight)               │   │    │
│  │  │   - Retries: 1                                             │   │    │
│  │  │   - Catchup: False                                         │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  └──────────────────────────────┬──────────────────────────────────────┘    │
│                                 │                                           │
│                                 ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     PROCESSING LAYER (Python + Pandas)               │    │
│  │                                                                     │    │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │    │
│  │  │  EXTRACT    │    │  TRANSFORM  │    │    LOAD     │             │    │
│  │  │             │    │             │    │             │             │    │
│  │  │ extract.py  │───▶│ transform.py│───▶│  load.py    │             │    │
│  │  │  (Pandas)   │    │  (Pandas)   │    │ (SQLAlchemy)│             │    │
│  │  └─────────────┘    └─────────────┘    └─────────────┘             │    │
│  └──────────────────────────────┬──────────────────────────────────────┘    │
│                                 │                                           │
│                    ┌────────────┼────────────┐                              │
│                    ▼            ▼            ▼                              │
│  ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐   │
│  │   Raw CSV           │ │   Staging           │ │   PostgreSQL 15     │   │
│  │   Dataset           │ │   (Clean)           │ │   / MySQL 8.0       │   │
│  │   (2.96M rows)      │ │                     │ │                     │   │
│  │   data/raw/         │ │   data/staging/     │ │   fact_trips        │   │
│  └─────────────────────┘ └─────────────────────┘ └──────────┬──────────┘   │
│                                                             │                │
│                                                             ▼                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     VISUALIZATION LAYER (Streamlit)                 │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │   dashboard/app.py                                          │   │    │
│  │  │   - 5 KPIs (Total Trips, Avg Fare, Avg Distance, etc.)     │   │    │
│  │  │   - 4 charts (Revenue by Day, Trips per Hour, etc.)        │   │    │
│  │  │   - 5 filters (Fare, Distance, Day, Payment, Vendor)       │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

*Figure 1: Complete ETL pipeline architecture showing Airflow → Pandas → PostgreSQL → Streamlit flow*

### Architecture Deep Dive

| Component | Purpose | Why Chosen |
|-----------|---------|------------|
| **Apache Airflow** | Orchestration | Industry-standard, reliable scheduling, UI monitoring, retry logic |
| **Pandas** | Data Processing | Powerful transformations, easy to use, Python-native |
| **PostgreSQL/MySQL** | Data Warehouse | ACID-compliant, robust, widely used in production |
| **Streamlit** | Dashboard | Python-native, rapid development, interactive |
| **Plotly** | Charts | Interactive visualizations, modern, Python-friendly |
| **Docker** | Deployment | Consistent environment, easy to distribute |

---

## Data Flow Details

> **SCREENSHOT COMPLETED:** `screenshots/data-flow-diagram.png`
> *Professional diagram generated from Python script (600 DPI)*

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW PIPELINE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 1: EXTRACT (extract.py)                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Input:  data/raw/taxi_data.csv (2.96M rows)               │   │
│  │  Action: pd.read_csv() → CSV to DataFrame                  │   │
│  │  Output: data/staging/taxi_raw.csv                         │   │
│  │  Time:   ~2-4 seconds                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  Step 2: TRANSFORM (transform.py)                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Input:  data/staging/taxi_raw.csv                         │   │
│  │  Actions:                                                  │   │
│  │   1. Drop duplicates                                        │   │
│  │   2. Drop nulls on critical columns                        │   │
│  │   3. Convert datetime (pickup, dropoff)                    │   │
│  │   4. Feature engineering (hour, day, month)                │   │
│  │   5. Filter outliers (distance: 0-100, fare: 0-500)       │   │
│  │   6. Validate pickup < dropoff                             │   │
│  │   7. Select 11 columns for warehouse                       │   │
│  │  Output: data/staging/taxi_clean.csv (2.87M rows)          │   │
│  │  Time:   ~8-12 seconds                                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  Step 3: LOAD (load.py)                                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Input:  data/staging/taxi_clean.csv                       │   │
│  │  Action: df.to_sql('fact_trips', engine, if_exists='append')│   │
│  │  Output: PostgreSQL/MySQL fact_trips table                 │   │
│  │  Time:   ~5-8 seconds                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  Step 4: VISUALIZATION (Streamlit Dashboard)                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Query:  PostgreSQL/MySQL fact_trips                       │   │
│  │  KPIs:   Total Trips, Avg Fare, Avg Distance,             │   │
│  │          Avg Passengers, Total Revenue                     │   │
│  │  Charts: Revenue by Day, Trips per Hour,                  │   │
│  │          Fare Distribution, Distance vs Fare               │   │
│  │  Filters: Fare Range, Distance Range, Day of Week,        │   │
│  │           Payment Type, Vendor ID                          │   │
│  │  Time:   < 200ms per query                                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

*Figure 2: Detailed data flow showing Extract → Transform → Load → Visualize pipeline*

### Pipeline Components

| Layer | Component | Technology | Role |
|-------|-----------|------------|------|
| **Orchestration** | Airflow DAG | Apache Airflow 2.7.3 | Schedules and monitors ETL tasks |
| **Processing** | ETL Scripts | Python + Pandas | Extract, transform, load data |
| **Storage** | Data Warehouse | PostgreSQL 15 / MySQL 8.0 | Stores fact table (fact_trips) |
| **Visualization** | Dashboard | Streamlit 1.29.0 | Interactive analytics dashboard |

### Data Flow Summary

1. **Extract**: Read CSV file from `data/raw/taxi_data.csv` using Pandas
2. **Stage**: Save raw data to `data/staging/taxi_raw.csv`
3. **Transform**: Clean data (duplicates, nulls, outliers), feature engineering (hour, day, month)
4. **Stage Clean**: Save transformed data to `data/staging/taxi_clean.csv`
5. **Load**: Insert clean data into PostgreSQL/MySQL `fact_trips` table using SQLAlchemy
6. **Visualize**: Streamlit dashboard queries database for real-time analytics

---

## Entity Relationship Diagram

> **SCREENSHOT COMPLETED:** `screenshots/erd-diagram.png`
> *Professional diagram generated from draw.io and dbdiagram.io*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENTITY RELATIONSHIP DIAGRAM                              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │                        fact_trips                                   │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  trip_id           SERIAL         PRIMARY KEY               │   │    │
│  │  │  vendor_id         INTEGER                                  │   │    │
│  │  │  pickup_datetime   TIMESTAMP WITHOUT TIME ZONE              │   │    │
│  │  │  dropoff_datetime  TIMESTAMP WITHOUT TIME ZONE              │   │    │
│  │  │  passenger_count   INTEGER                                  │   │    │
│  │  │  trip_distance     NUMERIC(10,2)                            │   │    │
│  │  │  fare_amount       NUMERIC(10,2)                            │   │    │
│  │  │  total_amount      NUMERIC(10,2)                            │   │    │
│  │  │  payment_type      INTEGER                                  │   │    │
│  │  │  pickup_hour       INTEGER                                  │   │    │
│  │  │  pickup_day        VARCHAR(20)                              │   │    │
│  │  │  pickup_month      INTEGER                                  │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  Indexes:                                                           │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  idx_pickup_datetime  →  Faster time-based queries          │   │    │
│  │  │  idx_pickup_day       →  Faster day-of-week aggregation    │   │    │
│  │  │  idx_fare_amount      →  Faster fare-based filtering       │   │    │
│  │  │  idx_trip_distance    →  Faster distance-based queries     │   │    │
│  │  │  idx_vendor_id        →  Faster vendor filtering           │   │    │
│  │  │  idx_pickup_hour      →  Faster hour-based queries         │   │    │
│  │  │  idx_payment_type     →  Faster payment type filtering     │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         DATA QUALITY RULES                          │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  Rule                      Condition        Action          │   │    │
│  │  ├─────────────────────────────────────────────────────────────┤   │    │
│  │  │  trip_distance             BETWEEN 0-100     Filter         │   │    │
│  │  │  fare_amount               BETWEEN 0-500     Filter         │   │    │
│  │  │  passenger_count           >= 0              Filter         │   │    │
│  │  │  pickup_datetime           < dropoff         Validate       │   │    │
│  │  │  Critical columns          NOT NULL         Drop Row        │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

*Figure 3: Entity Relationship Diagram showing fact_trips table structure with indexes and data quality rules*

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
| **Orchestration** | Apache Airflow | 2.7.3 | Industry standard, scheduler |
| **Containerization** | Docker Compose | 3.8 | Multi-service orchestration |
| **Database** | PostgreSQL / MySQL | 15 / 8.0 | Robust, ACID-compliant |
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
| `pickup_datetime` | < dropoff_datetime | Valid trip duration |
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
├── dags/
│   └── etl_pipeline.py                  # Main DAG definition
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
│   ├── cheatsheet.md                    # Quick reference
│   └── verification-checklist.md        # Testing checklist
│
├── screenshots/                         # Screenshot images
│   ├── architecture-diagram.png         # Architecture diagram (600 DPI)
│   ├── data-flow-diagram.png            # Data flow diagram (600 DPI)
│   ├── erd-diagram.png                  # Entity Relationship Diagram
│   ├── 01-folder-structure.png          # Level 1: Mandatory (8)
│   ├── 02-dataset-downloaded.png
│   ├── 03-airflow-dag-list.png
│   ├── 04-airflow-grid-success.png
│   ├── 05-airflow-tree-success.png
│   ├── 06-postgres-data.png
│   ├── 07-dashboard-overview.png
│   ├── 08-dashboard-charts.png
│   ├── 09-airflow-dag-code.png          # Level 2: Recommended (4)
│   ├── 10-extract-script.png
│   ├── 11-transform-script.png
│   ├── 12-load-script.png
│   ├── 13-dashboard-code.png            # Level 3: Value-Add (4)
│   ├── 14-docker-compose.png
│   ├── 15-airflow-log.png
│   └── 16-dashboard-with-filter.png
│
├── README.md                            # Project documentation
├── blueprint.md                         # This file
├── cheatsheet.md                        # Quick reference
└── verification-checklist.md            # Testing checklist
```

---

## Docker Compose Configuration

### Services

| Service | Image | Container Name | Port |
|---------|-------|----------------|------|
| PostgreSQL | postgres:15 | batch-etl-postgres | 5432 |
| Airflow | apache/airflow:2.7.3 | batch-etl-airflow | 8080 |
| Streamlit | Custom Dockerfile | batch-etl-streamlit | 8501 |

### Volume Mounts

| Service | Mount | Container Path |
|---------|-------|----------------|
| PostgreSQL | `postgres_data` | `/var/lib/postgresql/data` |
| PostgreSQL | `./warehouse/init.sql` | `/docker-entrypoint-initdb.d/` |
| Airflow | `./dags` | `/opt/airflow/dags` |
| Airflow | `./scripts` | `/opt/airflow/scripts` |
| Airflow | `./data` | `/opt/airflow/data` |
| Airflow | `./warehouse` | `/opt/airflow/warehouse` |
| Streamlit | `./data` | `/app/data` |

### Environment Variables

| Service | Variable | Value |
|---------|----------|-------|
| PostgreSQL | POSTGRES_USER | admin |
| PostgreSQL | POSTGRES_PASSWORD | admin |
| PostgreSQL | POSTGRES_DB | warehouse |
| Airflow | AIRFLOW__CORE__EXECUTOR | SequentialExecutor |
| Airflow | AIRFLOW__WEBSERVER__DEFAULT_UI_TIMEZONE | Asia/Jakarta |
| Airflow | AIRFLOW__WEBSERVER__SECRET_KEY | your-secret-key-here |
| Airflow | AIRFLOW_CONN_POSTGRES | postgresql://admin:admin@postgres:5432/warehouse |
| Airflow | PYTHONPATH | /opt/airflow |
| Airflow | DATA_PATH | /opt/airflow/data |

### docker-compose.yml

```yaml
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
```

---

## Implementation Details

### DAG Configuration

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, '/opt/airflow/scripts')

from extract import extract_data
from transform import transform_data
from load import load_data

DAG_ID = 'etl_pipeline'
SCHEDULE_INTERVAL = '0 0 * * *'  # Daily at midnight
START_DATE = datetime(2026, 7, 1)
CATCHUP = False
RETRIES = 1
RETRY_DELAY = timedelta(minutes=5)

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': START_DATE,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': RETRIES,
    'retry_delay': RETRY_DELAY,
}

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description='Extract, Transform, Load NYC Taxi Data',
    schedule_interval=SCHEDULE_INTERVAL,
    catchup=CATCHUP,
    tags=['etl', 'batch', 'taxi', 'nyc'],
    max_active_runs=1,
) as dag:

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )

    load_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
    )

    extract_task >> transform_task >> load_task
```

### Pipeline Phases

| Phase | Script | Input | Output | Description |
|-------|--------|-------|--------|-------------|
| Extract | `extract.py` | `data/raw/taxi_data.csv` | `data/staging/taxi_raw.csv` | Read CSV, stage data |
| Transform | `transform.py` | `data/staging/taxi_raw.csv` | `data/staging/taxi_clean.csv` | Clean, engineer features |
| Load | `load.py` | `data/staging/taxi_clean.csv` | Database `fact_trips` | Insert into database |

---

## Dashboard Specifications

### KPI Cards

| KPI | Calculation | Display Format |
|-----|-------------|----------------|
| Total Trips | `COUNT(*)` | `{value:,}` |
| Average Fare | `AVG(fare_amount)` | `${value:.2f}` |
| Avg Distance | `AVG(trip_distance)` | `{value:.2f} miles` |
| Avg Passengers | `AVG(passenger_count)` | `{value:.1f}` |
| Total Revenue | `SUM(total_amount)` | `${value:,.2f}` |

### Charts

| Chart | Type | Data | Filter |
|-------|------|------|--------|
| Revenue by Day | Bar (Plotly) | `fare_amount` by `pickup_day` | None |
| Trips per Hour | Bar (Plotly) | `COUNT(trip_id)` by `pickup_hour` | None |
| Fare Distribution | Histogram (Plotly) | `fare_amount` (50 bins) | None |
| Distance vs Fare | Scatter (Plotly) | `trip_distance` vs `fare_amount` | None |

### Filters

| Filter | Type | Options | Default |
|--------|------|---------|---------|
| Fare Range | Slider | Min-Max from data | [0, 100] |
| Distance Range | Slider | Min-Max from data | [0, 20] |
| Day of Week | Multiselect | Monday-Sunday | All days |
| Payment Type | Selectbox | 1-6 | All types |
| Vendor ID | Selectbox | 1-2 | All |

### Performance Optimization

| Feature | Method | Description |
|---------|--------|-------------|
| Database Connection | `@st.cache_resource` | Reuse connection |
| Data Loading | `@st.cache_data(ttl=300)` | Cache 5 minutes |
| Data Sampling | `df.sample(1000)` | Faster scatter plots |

---

## Screenshots Documentation

### Architecture Diagrams (3) - ✅ COMPLETED

| # | Filename | Description | Status |
|---|----------|-------------|--------|
| 1 | `architecture-diagram.png` | Complete system architecture | ✅ Done |
| 2 | `data-flow-diagram.png` | Detailed data flow pipeline | ✅ Done |
| 3 | `erd-diagram.png` | Entity Relationship Diagram | ✅ Done |

### Level 1: Mandatory (8 screenshots) - ✅ COMPLETED

| # | Filename | Description | Status |
|---|----------|-------------|--------|
| 4 | `01-folder-structure.png` | Project structure in VS Code | ✅ Done |
| 5 | `02-dataset-downloaded.png` | Raw CSV in `data/raw/` | ✅ Done |
| 6 | `03-airflow-dag-list.png` | DAG list with "Success" status | ✅ Done |
| 7 | `04-airflow-grid-success.png` | Grid view all green | ✅ Done |
| 8 | `05-airflow-tree-success.png` | Tree view confirmation | ✅ Done |
| 9 | `06-postgres-data.png` | `SELECT * FROM fact_trips LIMIT 10` | ✅ Done |
| 10 | `07-dashboard-overview.png` | Full dashboard page | ✅ Done |
| 11 | `08-dashboard-charts.png` | All 4 charts visible | ✅ Done |

### Level 2: Recommended (4 screenshots) - ✅ COMPLETED

| # | Filename | Description | Status |
|---|----------|-------------|--------|
| 12 | `09-airflow-dag-code.png` | `dags/etl_pipeline.py` | ✅ Done |
| 13 | `10-extract-script.png` | `scripts/extract.py` | ✅ Done |
| 14 | `11-transform-script.png` | `scripts/transform.py` | ✅ Done |
| 15 | `12-load-script.png` | `scripts/load.py` | ✅ Done |

### Level 3: Value-Add (4 screenshots) - ✅ COMPLETED

| # | Filename | Description | Status |
|---|----------|-------------|--------|
| 16 | `13-dashboard-code.png` | `dashboard/app.py` | ✅ Done |
| 17 | `14-docker-compose.png` | `docker-compose.yml` | ✅ Done |
| 18 | `15-airflow-log.png` | Task log with row count | ✅ Done |
| 19 | `16-dashboard-with-filter.png` | Dashboard with applied filters | ✅ Done |

---

## Performance Specifications

### Data Volume

| Metric | Value |
|--------|-------|
| Input Rows | 2,964,624 |
| Input Columns | ~20 |
| Output Rows | 2,869,525 (after cleaning) |
| Output Columns | 11 |
| PostgreSQL Size | ~300 MB |

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

## Troubleshooting Guide

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Docker container not starting | Check Docker Desktop is running, verify ports are available |
| Airflow DAG not appearing | Wait 30-60 seconds, restart Airflow container |
| Task stuck in running | Clear task from UI or CLI, retry |
| Database connection refused | Wait for database to initialize (10-15 seconds) |
| No data in dashboard | Trigger DAG first, verify data loaded |
| Permission denied | Run commands with admin privileges (Windows) |

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
| API Layer | REST API for data access | Medium |

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