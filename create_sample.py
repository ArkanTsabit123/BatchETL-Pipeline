# create_sample.py
import pandas as pd
import os

def create_sample():
    """Create 100,000 row sample from full dataset."""
    
    # Read full dataset
    df = pd.read_csv('data/staging/taxi_clean.csv')
    print(f'Full dataset: {len(df):,} rows')
    
    # Take first 100,000 rows
    df_sample = df.head(100000)
    print(f'Sample: {len(df_sample):,} rows')
    
    # Save to data/staging
    df_sample.to_csv('data/staging/taxi_clean_sample.csv', index=False)
    print('Saved to: data/staging/taxi_clean_sample.csv')
    
    # Also save to batchetl-streamlit/data for cloud deployment
    os.makedirs('batchetl-streamlit/data', exist_ok=True)
    df_sample.to_csv('batchetl-streamlit/data/taxi_clean_sample.csv', index=False)
    print('Saved to: batchetl-streamlit/data/taxi_clean_sample.csv')

if __name__ == '__main__':
    create_sample()