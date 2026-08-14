# scripts/transform.py
"""
Transform raw data with cleaning and feature engineering.

This module performs data cleaning, removes duplicates and outliers,
and adds new features for analysis.
"""

import pandas as pd
import os
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def transform_data() -> Dict[str, Any]:
    """
    Transform raw data with cleaning and feature engineering.

    Returns:
        Dict[str, Any]: Dictionary containing transformation statistics.

    Raises:
        FileNotFoundError: If raw staging file does not exist.
        Exception: For other transformation errors.
    """
    # Define paths
    raw_path = '/opt/airflow/data/staging/taxi_raw.csv'
    clean_path = '/opt/airflow/data/staging/taxi_clean.csv'

    try:
        # Check if raw file exists
        if not os.path.exists(raw_path):
            raise FileNotFoundError(f"Raw staging file not found: {raw_path}")

        # Read raw data
        logger.info(f"Reading raw data from: {raw_path}")
        df = pd.read_csv(raw_path)
        original_count = len(df)
        logger.info(f"Original rows: {original_count:,}")

        # 1. Drop duplicates
        df = df.drop_duplicates()
        duplicates_removed = original_count - len(df)
        logger.info(f"Duplicates removed: {duplicates_removed:,}")

        # 2. Drop nulls on critical columns
        critical_columns = ['tpep_pickup_datetime', 'tpep_dropoff_datetime',
                            'trip_distance', 'fare_amount']
        df_before_nulls = df.copy()
        df = df.dropna(subset=critical_columns)
        nulls_removed = len(df_before_nulls) - len(df)
        logger.info(f"Nulls removed: {nulls_removed:,}")

        # 3. Convert datetime
        df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
        df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

        # 4. Feature engineering
        df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
        df['pickup_day'] = df['tpep_pickup_datetime'].dt.day_name()
        df['pickup_month'] = df['tpep_pickup_datetime'].dt.month

        # Calculate trip duration in minutes
        df['trip_duration'] = (
            df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']
        ).dt.total_seconds() / 60

        # 5. Filter outliers
        df_before_outliers = df.copy()
        df = df[(df['trip_distance'] > 0) & (df['trip_distance'] < 100)]
        df = df[(df['fare_amount'] > 0) & (df['fare_amount'] < 500)]
        df = df[df['trip_duration'] > 0]
        outliers_removed = len(df_before_outliers) - len(df)
        logger.info(f"Outliers removed: {outliers_removed:,}")

        # 6. Select final columns
        final_columns = [
            'VendorID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime',
            'passenger_count', 'trip_distance', 'fare_amount', 'total_amount',
            'payment_type', 'pickup_hour', 'pickup_day', 'pickup_month'
        ]

        # Check if all columns exist
        missing_columns = [col for col in final_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Missing columns: {missing_columns}")
            # Use only available columns
            available_columns = [col for col in final_columns if col in df.columns]
            df = df[available_columns]
        else:
            df = df[final_columns]

        # 7. Rename columns to match warehouse schema
        column_mapping = {
            'VendorID': 'vendor_id',
            'tpep_pickup_datetime': 'pickup_datetime',
            'tpep_dropoff_datetime': 'dropoff_datetime',
            'passenger_count': 'passenger_count',
            'trip_distance': 'trip_distance',
            'fare_amount': 'fare_amount',
            'total_amount': 'total_amount',
            'payment_type': 'payment_type'
        }

        # Only rename columns that exist
        existing_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_mapping)

        # 8. Fix null passenger_count - fill with median (1)
        if 'passenger_count' in df.columns:
            df['passenger_count'] = df['passenger_count'].fillna(1)
            df['passenger_count'] = df['passenger_count'].astype(int)

        # 9. Downcast numeric columns for memory optimization
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')

        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')

        # 10. Ensure pickup_day is string (not categorical)
        if 'pickup_day' in df.columns:
            df['pickup_day'] = df['pickup_day'].astype(str)

        # 11. Sort columns for consistency
        df = df.reindex(sorted(df.columns), axis=1)

        # Save clean data
        os.makedirs(os.path.dirname(clean_path), exist_ok=True)
        df.to_csv(clean_path, index=False)

        logger.info(f"Clean data saved to: {clean_path}")
        logger.info(f"Final rows: {len(df):,}")
        logger.info(f"Final columns: {len(df.columns)}")

        return {
            'original_count': original_count,
            'duplicates_removed': duplicates_removed,
            'nulls_removed': nulls_removed,
            'outliers_removed': outliers_removed,
            'final_count': len(df)
        }

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise
    except pd.errors.EmptyDataError:
        logger.error("CSV file is empty")
        raise
    except Exception as e:
        logger.error(f"Transformation failed: {str(e)}")
        raise


if __name__ == "__main__":
    transform_data()