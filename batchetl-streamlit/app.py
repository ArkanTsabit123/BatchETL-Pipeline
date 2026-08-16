# batchetl-streamlit/app.py
"""
BatchETL Pipeline - Standalone Dashboard for Streamlit Cloud

Reads CSV directly (no database connection).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="NYC Taxi Analytics",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data(ttl=3600)
def load_data():
    """Load sample data from CSV."""
    data_path = 'data/staging/taxi_clean_sample.csv'

    if not os.path.exists(data_path):
        st.error(f"Data file not found: {data_path}")
        return pd.DataFrame()

    df = pd.read_csv(data_path)
    return df

df = load_data()

if df.empty:
    st.stop()

# Sidebar filters
st.sidebar.title("NYC Taxi Analytics")
st.sidebar.markdown("---")

# Filter: Fare Range
fare_min = float(df['fare_amount'].min())
fare_max = float(df['fare_amount'].quantile(0.95))
fare_range = st.sidebar.slider(
    "Fare Range ($)",
    min_value=0.0,
    max_value=float(df['fare_amount'].max()),
    value=(0.0, fare_max),
    step=1.0
)

# Filter: Distance Range
dist_min = float(df['trip_distance'].min())
dist_max = float(df['trip_distance'].quantile(0.95))
dist_range = st.sidebar.slider(
    "Distance Range (miles)",
    min_value=0.0,
    max_value=float(df['trip_distance'].max()),
    value=(0.0, dist_max),
    step=0.5
)

# Filter: Day of Week
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
selected_days = st.sidebar.multiselect(
    "Day of Week",
    options=days,
    default=days
)

# Apply filters
filtered_df = df[
    (df['fare_amount'].between(fare_range[0], fare_range[1])) &
    (df['trip_distance'].between(dist_range[0], dist_range[1])) &
    (df['pickup_day'].isin(selected_days))
]

# Main header
st.title("NYC Taxi Trip Analytics")
st.caption(f"Showing {len(filtered_df):,} trips from {len(df):,} total sample rows")

# KPIs
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Trips", f"{len(filtered_df):,}")

with col2:
    avg_fare = filtered_df['fare_amount'].mean()
    st.metric("Average Fare", f"${avg_fare:.2f}")

with col3:
    avg_dist = filtered_df['trip_distance'].mean()
    st.metric("Avg Distance", f"{avg_dist:.2f} miles")

with col4:
    avg_pass = filtered_df['passenger_count'].mean()
    st.metric("Avg Passengers", f"{avg_pass:.1f}")

with col5:
    total_rev = filtered_df['total_amount'].sum()
    st.metric("Total Revenue", f"${total_rev:,.0f}")

st.divider()

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Day")
    daily_revenue = filtered_df.groupby('pickup_day')['total_amount'].sum().reindex(days)
    fig1 = px.bar(
        daily_revenue,
        x=daily_revenue.index,
        y=daily_revenue.values,
        labels={'x': 'Day', 'y': 'Revenue ($)'},
        color_discrete_sequence=['#1f77b4']
    )
    fig1.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Trips per Hour")
    hourly_trips = filtered_df.groupby('pickup_hour').size()
    fig2 = px.bar(
        hourly_trips,
        x=hourly_trips.index,
        y=hourly_trips.values,
        labels={'x': 'Hour', 'y': 'Number of Trips'},
        color_discrete_sequence=['#ff7f0e']
    )
    fig2.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Fare Distribution")
    fig3 = px.histogram(
        filtered_df,
        x='fare_amount',
        nbins=50,
        labels={'fare_amount': 'Fare ($)'},
        color_discrete_sequence=['#2ca02c']
    )
    fig3.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Distance vs Fare")
    sample_df = filtered_df.sample(min(1000, len(filtered_df)))
    fig4 = px.scatter(
        sample_df,
        x='trip_distance',
        y='fare_amount',
        labels={'trip_distance': 'Distance (miles)', 'fare_amount': 'Fare ($)'},
        color_discrete_sequence=['#d62728'],
        opacity=0.6
    )
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, use_container_width=True)

# Raw data
st.divider()
with st.expander("View Raw Data"):
    st.dataframe(filtered_df.head(100), use_container_width=True)
    st.caption(f"Showing first 100 rows of {len(filtered_df):,} filtered trips")

# Footer
st.divider()
st.caption(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("Data: NYC Taxi & Limousine Commission | Powered by Streamlit + Plotly")