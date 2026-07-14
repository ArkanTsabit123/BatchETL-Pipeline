# BATCHETL-PIPELINE - TECHNICAL BLUEPRINT

## Document Information

| Property | Value |
|----------|-------|
| **Version** | 1.0.0 |
| **Last Updated** | 2026-07-14 |
| **Status** | Production Ready |
| **Orchestration** | Apache Airflow 2.7.3 |
| **Database** | PostgreSQL 15 |
| **Dashboard** | Streamlit 1.29.0 |

---

## Project Overview

### Core Goals
1. Build **end-to-end batch ETL pipeline** for NYC Taxi trip data
2. Implement **automated data transformation** using Pandas
3. Create **interactive dashboard** with Streamlit + Plotly
4. Use **containerized deployment** with Docker Compose
5. Provide **comprehensive documentation** with 16 screenshots + 2 architecture diagrams

### Success Metrics
- Fully automated daily pipeline execution
- 100% data quality validation (duplicate removal, outlier filtering)
- < 10 seconds pipeline execution time (100,000+ rows)
- Interactive dashboard with 5 KPIs + 4 chart types

---

## System Architecture

### Architecture Diagram

> **SCREENSHOT REQUIRED:** `screenshots/architecture-diagram.png`
> *Create a professional diagram from the ASCII below using draw.io or similar tool*

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
│  │  │   - Schedule: @daily                                       │   │    │
│  │  │   - Retries: 1                                             │   │    │
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
│  │   Dataset           │ │   (Clean)           │ │   Warehouse         │   │
│  │   (100K+ rows)      │ │                     │ │                     │   │
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
│  │  │   - 3 filters (Fare Range, Distance Range, Day of Week)    │   │    │
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
| **PostgreSQL** | Data Warehouse | ACID-compliant, robust, widely used in production |
| **Streamlit** | Dashboard | Python-native, rapid development, interactive |
| **Plotly** | Charts | Interactive visualizations, modern, Python-friendly |
| **Docker** | Deployment | Consistent environment, easy to distribute |

### Data Flow Details

> **📷 SCREENSHOT REQUIRED:** `screenshots/data-flow-diagram.png`
> *Create a professional diagram from the ASCII below using draw.io or similar tool*

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW PIPELINE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 1: EXTRACT (extract.py)                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Input:  data/raw/taxi_data.csv (100K+ rows)               │   │
│  │  Action: pd.read_csv() → CSV to DataFrame                  │   │
│  │  Output: data/staging/taxi_raw.csv                         │   │
│  │  Time:   ~1 second                                         │   │
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
│  │   5. Filter outliers (distance < 100, fare < 500)          │   │
│  │   6. Select 11 columns for warehouse                       │   │
│  │  Output: data/staging/taxi_clean.csv (~95K rows)           │   │
│  │  Time:   ~3-5 seconds                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  Step 3: LOAD (load.py)                                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Input:  data/staging/taxi_clean.csv                       │   │
│  │  Action: df.to_sql('fact_trips', engine, if_exists='append')│   │
│  │  Output: PostgreSQL fact_trips table                       │   │
│  │  Time:   ~2-3 seconds                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  Step 4: VISUALIZATION (Streamlit Dashboard)                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Query:  PostgreSQL fact_trips                             │   │
│  │  KPIs:   Total Trips, Avg Fare, Avg Distance,             │   │
│  │          Avg Passengers, Total Revenue                     │   │
│  │  Charts: Revenue by Day, Trips per Hour,                  │   │
│  │          Fare Distribution, Distance vs Fare               │   │
│  │  Filters: Fare Range, Distance Range, Day of Week         │   │
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
| **Storage** | Data Warehouse | PostgreSQL 15 | Stores fact table (fact_trips) |
| **Visualization** | Dashboard | Streamlit 1.29.0 | Interactive analytics dashboard |

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
│   ├── architecture-diagram.png    # Architecture diagram (from ASCII)
│   ├── data-flow-diagram.png       # Data flow diagram (from ASCII)
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
├── blueprint.md                    # This file
├── cheatsheets.md                  # Quick reference
└── verification checklist.md       # Testing checklist
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
| Streamlit | `./data` | `/app/data` |

### Environment Variables

| Service | Variable | Value |
|---------|----------|-------|
| PostgreSQL | POSTGRES_USER | admin |
| PostgreSQL | POSTGRES_PASSWORD | admin |
| PostgreSQL | POSTGRES_DB | warehouse |
| Airflow | AIRFLOW__CORE__EXECUTOR | LocalExecutor |
| Airflow | AIRFLOW_WEBSERVER_DEFAULT_UI_TIMEZONE | Asia/Jakarta |

### docker-compose.yml

```yaml
version: '3.8'

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

# Add scripts directory to path
sys.path.insert(0, '/opt/airflow/scripts')

from extract import extract_data
from transform import transform_data
from load import load_data

DAG_ID = 'etl_pipeline'
SCHEDULE_INTERVAL = '@daily'
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

dag = DAG(
    DAG_ID,
    default_args=default_args,
    description='Extract, Transform, Load NYC Taxi Data',
    schedule_interval=SCHEDULE_INTERVAL,
    catchup=CATCHUP,
    tags=['etl', 'batch', 'taxi', 'nyc'],
)

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag,
)

# Task Dependencies
extract_task >> transform_task >> load_task
```

### Pipeline Phases

| Phase | Script | Input | Output | Description |
|-------|--------|-------|--------|-------------|
| Extract | `extract.py` | `data/raw/taxi_data.csv` | `data/staging/taxi_raw.csv` | Read CSV, stage data |
| Transform | `transform.py` | `data/staging/taxi_raw.csv` | `data/staging/taxi_clean.csv` | Clean, engineer features |
| Load | `load.py` | `data/staging/taxi_clean.csv` | PostgreSQL `fact_trips` | Insert into database |

### ETL Scripts

#### extract.py

```python
import pandas as pd
import os

def extract_data():
    """Extract data from raw CSV and save to staging"""
    raw_path = '/opt/airflow/data/raw/taxi_data.csv'
    staging_path = '/opt/airflow/data/staging/taxi_raw.csv'
    
    # Create staging directory if it doesn't exist
    os.makedirs(os.path.dirname(staging_path), exist_ok=True)
    
    # Read CSV
    df = pd.read_csv(raw_path)
    
    # Save to staging
    df.to_csv(staging_path, index=False)
    
    print(f"Extracted {len(df)} rows from {raw_path}")
    return f"Extracted {len(df)} rows"

if __name__ == "__main__":
    extract_data()
```

#### transform.py

```python
import pandas as pd
import os
from datetime import datetime

def transform_data():
    """Transform raw data with cleaning and feature engineering"""
    raw_path = '/opt/airflow/data/staging/taxi_raw.csv'
    clean_path = '/opt/airflow/data/staging/taxi_clean.csv'
    
    # Read raw data
    df = pd.read_csv(raw_path)
    original_count = len(df)
    
    # 1. Drop duplicates
    df = df.drop_duplicates()
    duplicates_removed = original_count - len(df)
    
    # 2. Drop nulls on critical columns
    critical_columns = ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'trip_distance', 'fare_amount']
    df_before_nulls = df.copy()
    df = df.dropna(subset=critical_columns)
    nulls_removed = len(df_before_nulls) - len(df)
    
    # 3. Convert datetime
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
    
    # 4. Feature engineering
    df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
    df['pickup_day'] = df['tpep_pickup_datetime'].dt.day_name()
    df['pickup_month'] = df['tpep_pickup_datetime'].dt.month
    df['trip_duration'] = (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds() / 60
    
    # 5. Filter outliers
    df_before_outliers = df.copy()
    df = df[(df['trip_distance'] > 0) & (df['trip_distance'] < 100)]
    df = df[(df['fare_amount'] > 0) & (df['fare_amount'] < 500)]
    df = df[df['trip_duration'] > 0]
    outliers_removed = len(df_before_outliers) - len(df)
    
    # 6. Select final columns
    final_columns = [
        'VendorID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime',
        'passenger_count', 'trip_distance', 'fare_amount', 'total_amount',
        'payment_type', 'pickup_hour', 'pickup_day', 'pickup_month'
    ]
    df = df[final_columns]
    
    # Rename columns to match warehouse schema
    df = df.rename(columns={
        'VendorID': 'vendor_id',
        'tpep_pickup_datetime': 'pickup_datetime',
        'tpep_dropoff_datetime': 'dropoff_datetime',
        'passenger_count': 'passenger_count',
        'trip_distance': 'trip_distance',
        'fare_amount': 'fare_amount',
        'total_amount': 'total_amount',
        'payment_type': 'payment_type'
    })
    
    # Save clean data
    df.to_csv(clean_path, index=False)
    
    print(f"Original rows: {original_count}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Nulls removed: {nulls_removed}")
    print(f"Outliers removed: {outliers_removed}")
    print(f"Final rows: {len(df)}")
    
    return {
        'original_count': original_count,
        'duplicates_removed': duplicates_removed,
        'nulls_removed': nulls_removed,
        'outliers_removed': outliers_removed,
        'final_count': len(df)
    }

if __name__ == "__main__":
    transform_data()
```

#### load.py

```python
import pandas as pd
from sqlalchemy import create_engine
import os

def load_data():
    """Load clean data into PostgreSQL"""
    clean_path = '/opt/airflow/data/staging/taxi_clean.csv'
    
    # Database connection
    DATABASE_URL = 'postgresql+psycopg2://admin:admin@postgres:5432/warehouse'
    engine = create_engine(DATABASE_URL)
    
    # Read clean data
    df = pd.read_csv(clean_path)
    
    # Load to PostgreSQL
    df.to_sql('fact_trips', engine, if_exists='append', index=False)
    
    print(f"Loaded {len(df)} rows into fact_trips table")
    return f"Loaded {len(df)} rows"

if __name__ == "__main__":
    load_data()
```

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
| Fare Range | Slider | Min-Max from data | Full range |
| Distance Range | Slider | Min-Max from data | Full range |
| Day of Week | Multiselect | Monday-Sunday | All days |

### Performance Optimization

| Feature | Method | Description |
|---------|--------|-------------|
| Database Connection | `@st.cache_resource` | Reuse connection |
| Data Loading | `@st.cache_data(ttl=300)` | Cache 5 minutes |
| Data Sampling | `df.sample(1000)` | Faster scatter plots |

### dashboard/app.py

```python
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os
import calendar

# Page configuration
st.set_page_config(
    page_title="NYC Taxi Analytics Dashboard",
    page_icon="🚕",
    layout="wide"
)

# Database connection
@st.cache_resource
def get_connection():
    DATABASE_URL = 'postgresql+psycopg2://admin:admin@postgres:5432/warehouse'
    return create_engine(DATABASE_URL)

# Load data
@st.cache_data(ttl=300)
def load_data():
    engine = get_connection()
    query = "SELECT * FROM fact_trips"
    df = pd.read_sql(query, engine)
    return df

# Main dashboard
st.title("🚕 NYC Taxi Analytics Dashboard")
st.markdown("### Real-time analytics from NYC Taxi Trip Data")

# Load data
df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Fare range filter
fare_min = float(df['fare_amount'].min())
fare_max = float(df['fare_amount'].max())
fare_range = st.sidebar.slider(
    "Fare Range ($)",
    min_value=fare_min,
    max_value=fare_max,
    value=(fare_min, fare_max)
)

# Distance range filter
dist_min = float(df['trip_distance'].min())
dist_max = float(df['trip_distance'].max())
distance_range = st.sidebar.slider(
    "Distance Range (miles)",
    min_value=dist_min,
    max_value=dist_max,
    value=(dist_min, dist_max)
)

# Day filter
days = list(calendar.day_name)
selected_days = st.sidebar.multiselect(
    "Day of Week",
    options=days,
    default=days
)

# Apply filters
filtered_df = df[
    (df['fare_amount'] >= fare_range[0]) &
    (df['fare_amount'] <= fare_range[1]) &
    (df['trip_distance'] >= distance_range[0]) &
    (df['trip_distance'] <= distance_range[1]) &
    (df['pickup_day'].isin(selected_days))
]

# KPI Row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Trips", f"{len(filtered_df):,}")

with col2:
    avg_fare = filtered_df['fare_amount'].mean()
    st.metric("Average Fare", f"${avg_fare:.2f}")

with col3:
    avg_distance = filtered_df['trip_distance'].mean()
    st.metric("Avg Distance", f"{avg_distance:.2f} miles")

with col4:
    avg_passengers = filtered_df['passenger_count'].mean()
    st.metric("Avg Passengers", f"{avg_passengers:.1f}")

with col5:
    total_revenue = filtered_df['total_amount'].sum()
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Day")
    revenue_by_day = filtered_df.groupby('pickup_day')['fare_amount'].sum().reset_index()
    fig1 = px.bar(
        revenue_by_day,
        x='pickup_day',
        y='fare_amount',
        title='Revenue by Day of Week',
        color='fare_amount',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Trips per Hour")
    trips_by_hour = filtered_df.groupby('pickup_hour').size().reset_index(name='count')
    fig2 = px.bar(
        trips_by_hour,
        x='pickup_hour',
        y='count',
        title='Trips by Hour of Day',
        color='count',
        color_continuous_scale='Plasma'
    )
    st.plotly_chart(fig2, use_container_width=True)

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("Fare Distribution")
    fig3 = px.histogram(
        filtered_df,
        x='fare_amount',
        nbins=50,
        title='Distribution of Fare Amounts',
        color_discrete_sequence=['#636EFA']
    )
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("Distance vs Fare")
    # Sample data for better performance
    sample_df = filtered_df.sample(min(1000, len(filtered_df)))
    fig4 = px.scatter(
        sample_df,
        x='trip_distance',
        y='fare_amount',
        title='Trip Distance vs Fare Amount',
        color='passenger_count',
        color_continuous_scale='Viridis',
        labels={'trip_distance': 'Distance (miles)', 'fare_amount': 'Fare ($)'}
    )
    st.plotly_chart(fig4, use_container_width=True)

# Raw data
with st.expander("View Raw Data"):
    st.dataframe(filtered_df)

# Footer
st.markdown("---")
st.markdown("*Data source: NYC Taxi & Limousine Commission | Updated in real-time*")
```

---

## Screenshots Documentation

### Architecture Diagrams (2)

| # | Filename | Description | Source |
|---|----------|-------------|--------|
| 1 | `architecture-diagram.png` | Complete system architecture | From ASCII in blueprint |
| 2 | `data-flow-diagram.png` | Detailed data flow pipeline | From ASCII in blueprint |

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

## Deployment Guide

### Prerequisites

| Item | Check Command |
|------|---------------|
| Docker Desktop | `docker --version` |
| Git | `git --version` |
| Internet | For image pulls |
| Python 3.9+ | `python --version` |

### Development Setup

#### Virtual Environment (Optional)

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

#### requirements.txt

```txt
pandas==2.0.3
psycopg2-binary==2.9.9
sqlalchemy==2.0.19
streamlit==1.29.0
plotly==5.18.0
apache-airflow==2.7.3
python-dotenv==1.0.0
```

### Deployment Steps

```bash
# 1. Create project folder
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

### Alternative: Manual Pipeline Run

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate

# Run ETL scripts manually
python scripts/extract.py
python scripts/transform.py
python scripts/load.py

# Run dashboard
streamlit run dashboard/app.py
```

---

## Performance Specifications

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
| Airflow DAG not appearing | Wait 30 seconds, restart Airflow container |
| Task stuck in running | Clear task from UI or CLI, retry |
| PostgreSQL connection refused | Wait for PostgreSQL to initialize (10-15 seconds) |
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
| **NYC Taxi Data** | https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page |
| **Airflow Docs** | https://airflow.apache.org/docs/ |
| **PostgreSQL Docs** | https://www.postgresql.org/docs/ |
| **Streamlit Docs** | https://docs.streamlit.io/ |
| **Plotly Docs** | https://plotly.com/python/ |
| **Docker Docs** | https://docs.docker.com/ |

---

**Built with industry-standard data engineering tools**