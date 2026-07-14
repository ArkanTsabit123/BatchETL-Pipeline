# dags/etl_pipeline.py
"""
BatchETL Pipeline - Airflow DAG

Orchestrates the ETL pipeline for NYC Taxi trip data:
1. Extract: Read CSV from data/raw/taxi_data.csv
2. Transform: Clean data, feature engineering, remove outliers
3. Load: Insert into PostgreSQL fact_trips table
"""

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

# DAG Configuration
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

# Define DAG
dag = DAG(
    DAG_ID,
    default_args=default_args,
    description='Extract, Transform, Load NYC Taxi Data',
    schedule_interval=SCHEDULE_INTERVAL,
    catchup=CATCHUP,
    tags=['etl', 'batch', 'taxi', 'nyc'],
)

# Tasks
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