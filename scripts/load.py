# scripts/load.py
"""
Load clean data into PostgreSQL.

This module reads the transformed data from staging
and inserts it into the PostgreSQL data warehouse.
"""

import pandas as pd
from sqlalchemy import create_engine, text, inspect
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_data() -> str:
    """
    Load clean data into PostgreSQL.

    Returns:
        str: Status message with row count.

    Raises:
        FileNotFoundError: If clean staging file does not exist.
        Exception: For other loading errors.
    """
    # Define paths and connection
    clean_path = '/opt/airflow/data/staging/taxi_clean.csv'
    database_url = 'postgresql+psycopg2://admin:admin@postgres:5432/warehouse'

    try:
        # Check if clean file exists
        if not os.path.exists(clean_path):
            raise FileNotFoundError(f"Clean staging file not found: {clean_path}")

        # Create database engine with connection pooling
        logger.info("Creating database engine...")
        engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600
        )

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"Database connection successful: {version[:50]}...")

        # Read clean data
        logger.info(f"Reading clean data from: {clean_path}")
        df = pd.read_csv(clean_path)
        total_rows = len(df)
        logger.info(f"Total rows to load: {total_rows:,}")

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
            logger.error(f"Missing columns: {missing_columns}")
            logger.info(f"Available columns: {df.columns.tolist()}")
            raise ValueError(f"Missing columns: {missing_columns}")

        # Check for nulls in critical columns
        critical_columns = ['pickup_datetime', 'dropoff_datetime', 'trip_distance', 'fare_amount']
        null_counts = df[critical_columns].isnull().sum()
        if null_counts.sum() > 0:
            logger.warning(f"Found nulls in critical columns: {null_counts.to_dict()}")
            # Drop rows with nulls in critical columns
            df = df.dropna(subset=critical_columns)
            logger.info(f"Rows after dropping nulls: {len(df):,}")

        # Check if table exists
        inspector = inspect(engine)
        table_exists = inspector.has_table('fact_trips')

        if table_exists:
            # Get existing row count
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM fact_trips"))
                existing_count = result.scalar()
                logger.info(f"Existing rows in fact_trips: {existing_count:,}")
        else:
            logger.info("Table 'fact_trips' does not exist. Will be created.")

        # Load to PostgreSQL with chunking for large datasets
        chunk_size = 100000
        total_loaded = 0

        # Use a transaction for the entire load
        with engine.begin() as conn:
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i:i+chunk_size]
                chunk.to_sql(
                    'fact_trips',
                    engine,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
                total_loaded += len(chunk)
                logger.info(f"Loaded {total_loaded:,} / {len(df):,} rows...")

        # Verify row count
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM fact_trips"))
            db_count = result.scalar()

        message = f"Loaded {total_loaded:,} rows into fact_trips table. Total in DB: {db_count:,}"
        logger.info(message)
        return message

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise
    except pd.errors.EmptyDataError:
        logger.error("CSV file is empty")
        raise
    except Exception as e:
        logger.error(f"Load failed: {str(e)}")
        raise


if __name__ == "__main__":
    load_data()