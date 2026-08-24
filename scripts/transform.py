# scripts/transform.py
"""
Transform raw data with cleaning and feature engineering using chunking.
Processes data in batches to avoid OOM (Out of Memory) errors.
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
    Transform raw data with cleaning and feature engineering using chunking.

    Returns:
        Dict[str, Any]: Dictionary containing transformation statistics.

    Raises:
        FileNotFoundError: If raw staging file does not exist.
        Exception: For other transformation errors.
    """
    raw_path = '/opt/airflow/data/staging/taxi_raw.csv'
    clean_path = '/opt/airflow/data/staging/taxi_clean.csv'

    try:
        # Check if raw file exists
        if not os.path.exists(raw_path):
            raise FileNotFoundError(f"Raw staging file not found: {raw_path}")

        # ============================================
        # PROCESS IN CHUNKS TO AVOID OOM
        # ============================================
        chunk_size = 100000
        chunks = []
        total_rows = 0
        total_duplicates = 0
        total_nulls = 0
        total_outliers = 0
        chunk_count = 0

        # Define columns to keep
        cols_to_keep = [
            'VendorID',
            'tpep_pickup_datetime',
            'tpep_dropoff_datetime',
            'passenger_count',
            'trip_distance',
            'fare_amount',
            'total_amount',
            'payment_type'
        ]

        # Critical columns for null check
        critical_cols = [
            'tpep_pickup_datetime',
            'tpep_dropoff_datetime',
            'trip_distance',
            'fare_amount'
        ]

        logger.info(f"Reading raw data from: {raw_path}")
        logger.info(f"Processing in chunks of {chunk_size:,} rows...")

        # Read CSV in chunks
        for chunk_df in pd.read_csv(raw_path, chunksize=chunk_size, low_memory=False):
            chunk_count += 1
            original_len = len(chunk_df)
            logger.info(f"Processing chunk {chunk_count}: {original_len:,} rows")

            # 1. Keep only required columns
            chunk_df = chunk_df[cols_to_keep]

            # 2. Drop duplicates
            before_dup = len(chunk_df)
            chunk_df = chunk_df.drop_duplicates()
            dup_removed = before_dup - len(chunk_df)
            total_duplicates += dup_removed

            # 3. Drop nulls on critical columns
            before_null = len(chunk_df)
            chunk_df = chunk_df.dropna(subset=critical_cols)
            null_removed = before_null - len(chunk_df)
            total_nulls += null_removed

            # 4. Convert datetime
            chunk_df['tpep_pickup_datetime'] = pd.to_datetime(
                chunk_df['tpep_pickup_datetime'], errors='coerce'
            )
            chunk_df['tpep_dropoff_datetime'] = pd.to_datetime(
                chunk_df['tpep_dropoff_datetime'], errors='coerce'
            )

            # 5. Remove invalid datetimes
            chunk_df = chunk_df[
                chunk_df['tpep_pickup_datetime'].notna() &
                chunk_df['tpep_dropoff_datetime'].notna()
            ]

            # 5b. Remove invalid trip durations (pickup >= dropoff)
            # Gunakan < (bukan <=) untuk menghapus pickup == dropoff juga
            before_duration = len(chunk_df)
            chunk_df = chunk_df[
                chunk_df['tpep_pickup_datetime'] < chunk_df['tpep_dropoff_datetime']
            ]
            duration_removed = before_duration - len(chunk_df)
            total_outliers += duration_removed
            if duration_removed > 0:
                logger.info(f"Chunk {chunk_count}: Removed {duration_removed} rows with invalid duration")

            # 6. Feature engineering
            chunk_df['pickup_hour'] = chunk_df['tpep_pickup_datetime'].dt.hour
            chunk_df['pickup_day'] = chunk_df['tpep_pickup_datetime'].dt.day_name()
            chunk_df['pickup_month'] = chunk_df['tpep_pickup_datetime'].dt.month

            # 7. Filter outliers
            before_outlier = len(chunk_df)
            chunk_df = chunk_df[
                (chunk_df['trip_distance'] > 0) &
                (chunk_df['trip_distance'] < 100) &
                (chunk_df['fare_amount'] > 0) &
                (chunk_df['fare_amount'] < 500)
            ]
            outlier_removed = before_outlier - len(chunk_df)
            total_outliers += outlier_removed

            # 8. Rename columns
            chunk_df.columns = [
                'vendor_id',
                'pickup_datetime',
                'dropoff_datetime',
                'passenger_count',
                'trip_distance',
                'fare_amount',
                'total_amount',
                'payment_type',
                'pickup_hour',
                'pickup_day',
                'pickup_month'
            ]

            # 9. Fix null passenger_count
            chunk_df['passenger_count'] = chunk_df['passenger_count'].fillna(1)
            chunk_df['passenger_count'] = chunk_df['passenger_count'].astype(int)

            # 10. Downcast numeric columns
            for col in chunk_df.select_dtypes(include=['int64']).columns:
                chunk_df[col] = pd.to_numeric(chunk_df[col], downcast='integer')

            for col in chunk_df.select_dtypes(include=['float64']).columns:
                chunk_df[col] = pd.to_numeric(chunk_df[col], downcast='float')

            chunks.append(chunk_df)
            total_rows += len(chunk_df)
            logger.info(f"Chunk {chunk_count} done: {len(chunk_df):,} rows kept")

        # Combine all chunks
        if chunks:
            logger.info(f"Combining {len(chunks)} chunks...")
            df_clean = pd.concat(chunks, ignore_index=True)

            # Sort columns for consistency
            df_clean = df_clean.reindex(sorted(df_clean.columns), axis=1)

            # Save clean data
            os.makedirs(os.path.dirname(clean_path), exist_ok=True)
            df_clean.to_csv(clean_path, index=False)

            # Summary
            logger.info("=" * 50)
            logger.info("TRANSFORMATION SUMMARY")
            logger.info("=" * 50)
            logger.info(f"Original rows: 2,964,624")
            logger.info(f"Duplicates removed: {total_duplicates:,}")
            logger.info(f"Nulls removed: {total_nulls:,}")
            logger.info(f"Outliers removed: {total_outliers:,}")
            logger.info(f"Final rows: {len(df_clean):,}")
            logger.info(f"Final columns: {len(df_clean.columns)}")
            logger.info(f"Clean data saved to: {clean_path}")
            logger.info("=" * 50)

            return {
                'original_count': 2964624,
                'duplicates_removed': total_duplicates,
                'nulls_removed': total_nulls,
                'outliers_removed': total_outliers,
                'final_count': len(df_clean)
            }
        else:
            raise Exception("No data processed - all chunks empty")

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