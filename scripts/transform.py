# scripts/transform.py
"""
Transform raw data with cleaning and feature engineering.
"""

import pandas as pd
import os
from datetime import datetime


def transform_data():
    """Transform raw data with cleaning and feature engineering."""
    # Path lokal Windows
    raw_path = 'data/staging/taxi_raw.csv'
    clean_path = 'data/staging/taxi_clean.csv'
    
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