# scripts/extract.py
"""
Extract data from raw CSV and save to staging.
"""

import pandas as pd
import os
from pathlib import Path


def extract_data():
    """Extract data from raw CSV and save to staging."""
    # Path lokal Windows
    raw_path = 'data/raw/taxi_data.csv'
    staging_path = 'data/staging/taxi_raw.csv'
    
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