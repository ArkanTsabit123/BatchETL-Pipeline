# scripts/load.py
"""
Load clean data into PostgreSQL.
"""

import pandas as pd
from sqlalchemy import create_engine


def load_data():
    """Load clean data into PostgreSQL."""
    # Path lokal Windows
    clean_path = 'data/staging/taxi_clean.csv'
    
    # Database connection (gunakan localhost untuk lokal, postgres untuk Docker)
    DATABASE_URL = 'postgresql+psycopg2://admin:admin@localhost:5432/warehouse'
    engine = create_engine(DATABASE_URL)
    
    # Read clean data
    df = pd.read_csv(clean_path)
    
    # Load to PostgreSQL
    df.to_sql('fact_trips', engine, if_exists='append', index=False)
    
    print(f"Loaded {len(df)} rows into fact_trips table")
    return f"Loaded {len(df)} rows"


if __name__ == "__main__":
    load_data()