# scripts/extract.py
"""
Extract data from raw CSV and save to staging.

This module reads the NYC Taxi trip data from CSV file
and saves it to the staging area for further processing.
"""

import pandas as pd
import os
from pathlib import Path


def extract_data() -> str:
    """
    Extract data from raw CSV and save to staging.

    Returns:
        str: Status message with row count.
    """
    # Define paths
    raw_path = '/opt/airflow/data/raw/taxi_data.csv'
    staging_path = '/opt/airflow/data/staging/taxi_raw.csv'
    
    # Create staging directory if it doesn't exist
    os.makedirs(os.path.dirname(staging_path), exist_ok=True)
    
    # Read CSV with low_memory=False to avoid DtypeWarning
    df = pd.read_csv(raw_path, low_memory=False)
    
    # Save to staging
    df.to_csv(staging_path, index=False)
    
    message = f"Extracted {len(df)} rows from {raw_path}"
    print(message)
    return message


if __name__ == "__main__":
    extract_data()