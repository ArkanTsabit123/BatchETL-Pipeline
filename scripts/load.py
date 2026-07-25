# scripts/load.py
"""
Load clean data into PostgreSQL.

This module reads the transformed data from staging
and inserts it into the PostgreSQL data warehouse.
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os


def load_data() -> str:
    """
    Load clean data into PostgreSQL.

    Returns:
        str: Status message with row count.
    """
    # Define paths and connection
    clean_path = '/opt/airflow/data/staging/taxi_clean.csv'
    database_url = 'postgresql+psycopg2://admin:admin@postgres:5432/warehouse'
    
    # Create database engine
    engine = create_engine(database_url)
    
    # Read clean data
    df = pd.read_csv(clean_path)
    
    # Validate data before loading
    required_columns = [
        'vendor_id', 'pickup_datetime', 'dropoff_datetime',
        'passenger_count', 'trip_distance', 'fare_amount',
        'total_amount', 'payment_type', 'pickup_hour',
        'pickup_day', 'pickup_month'
    ]
    
    # Check if all required columns exist
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")
    
    # Check for nulls in critical columns
    critical_columns = ['pickup_datetime', 'dropoff_datetime', 'trip_distance', 'fare_amount']
    null_counts = df[critical_columns].isnull().sum()
    if null_counts.sum() > 0:
        print(f"Warning: Found nulls in critical columns: {null_counts.to_dict()}")
        # Drop rows with nulls in critical columns
        df = df.dropna(subset=critical_columns)
    
    # Load to PostgreSQL with chunking for large datasets
    chunk_size = 100000
    total_loaded = 0
    
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        chunk.to_sql('fact_trips', engine, if_exists='append', index=False)
        total_loaded += len(chunk)
        print(f"Loaded {total_loaded} rows...")
    
    # Verify row count
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM fact_trips"))
        db_count = result.scalar()
    
    message = f"Loaded {total_loaded} rows into fact_trips table. Total in DB: {db_count:,}"
    print(message)
    return message


if __name__ == "__main__":
    load_data()