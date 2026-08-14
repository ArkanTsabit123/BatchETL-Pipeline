# scripts/extract_local.py
"""
Extract data from raw CSV and save to staging (Local Development).

This module reads the NYC Taxi trip data from CSV file
and saves it to the staging area for further processing.
"""

import pandas as pd
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_data_local() -> str:
    """
    Extract data from raw CSV and save to staging (Local Development).

    Returns:
        str: Status message with row count.

    Raises:
        FileNotFoundError: If raw CSV file does not exist.
        Exception: For other extraction errors.
    """
    # Define paths
    raw_path = Path(__file__).parent.parent / 'data/raw/taxi_data.csv'
    staging_path = Path(__file__).parent.parent / 'data/staging/taxi_raw.csv'

    try:
        # Check if raw file exists
        if not raw_path.exists():
            raise FileNotFoundError(f"Raw data file not found: {raw_path}")

        # Create staging directory if it doesn't exist
        staging_path.parent.mkdir(parents=True, exist_ok=True)

        # Read CSV
        logger.info(f"Reading data from: {raw_path}")
        df = pd.read_csv(raw_path, low_memory=False)

        # Save to staging
        df.to_csv(staging_path, index=False)

        message = f"Extracted {len(df):,} rows from {raw_path}"
        logger.info(message)
        return message

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        raise


if __name__ == "__main__":
    extract_data_local()