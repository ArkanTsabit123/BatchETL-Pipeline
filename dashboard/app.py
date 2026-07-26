# dashboard/app.py

"""
NYC Taxi Analytics Dashboard.

Streamlit dashboard for visualizing NYC Taxi trip data from PostgreSQL.
Features KPI cards, interactive charts, and filters.
"""

import calendar
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import streamlit as st


# Constants
DATABASE_URL = "postgresql+psycopg2://admin:admin@postgres:5432/warehouse"
PAGE_TITLE = "NYC Taxi Analytics Dashboard"
LAYOUT = "wide"
CACHE_TTL = 300
SAMPLE_SIZE = 1000
DATA_LIMIT = 100000
FARE_BINS = 50


def configure_page() -> None:
    """Set Streamlit page configuration."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        layout=LAYOUT,
    )


@st.cache_resource
def get_database_engine():
    """
    Create and return SQLAlchemy database engine.

    Returns:
        Engine: SQLAlchemy engine instance.
    """
    return create_engine(DATABASE_URL)


@st.cache_data(ttl=CACHE_TTL)
def load_trip_data() -> pd.DataFrame:
    """
    Load trip data from PostgreSQL with row limit for performance.

    Returns:
        DataFrame: Trip data from fact_trips table.

    Raises:
        Exception: If database connection fails.
    """
    try:
        engine = get_database_engine()
        query = f"""
            SELECT *
            FROM fact_trips
            ORDER BY trip_id
            LIMIT {DATA_LIMIT}
        """
        return pd.read_sql(query, engine)
    except Exception as e:
        raise Exception(f"Database connection failed: {str(e)}")


def render_header() -> None:
    """Display dashboard header."""
    st.title(PAGE_TITLE)
    st.markdown("### Real-time analytics from NYC Taxi Trip Data")


def get_filters(dataframe: pd.DataFrame) -> dict:
    """
    Create sidebar filters.

    Args:
        dataframe: Source data for filter ranges.

    Returns:
        dict: Dictionary containing filter values.
    """
    st.sidebar.header("Filters")

    fare_min = float(dataframe["fare_amount"].min())
    fare_max = float(dataframe["fare_amount"].max())
    fare_range = st.sidebar.slider(
        "Fare Range ($)",
        min_value=fare_min,
        max_value=fare_max,
        value=(fare_min, fare_max),
        step=1.0,
    )

    dist_min = float(dataframe["trip_distance"].min())
    dist_max = float(dataframe["trip_distance"].max())
    distance_range = st.sidebar.slider(
        "Distance Range (miles)",
        min_value=dist_min,
        max_value=dist_max,
        value=(dist_min, dist_max),
        step=0.5,
    )

    days = list(calendar.day_name)
    selected_days = st.sidebar.multiselect(
        "Day of Week",
        options=days,
        default=days,
    )

    payment_types = sorted(dataframe["payment_type"].dropna().unique())
    payment_options = ["All"] + [int(p) for p in payment_types]
    selected_payment = st.sidebar.selectbox(
        "Payment Type",
        options=payment_options,
        index=0,
        format_func=lambda x: "All" if x == "All" else f"Type {x}",
    )

    vendor_ids = sorted(dataframe["vendor_id"].dropna().unique())
    vendor_options = ["All"] + [int(v) for v in vendor_ids]
    selected_vendor = st.sidebar.selectbox(
        "Vendor ID",
        options=vendor_options,
        index=0,
        format_func=lambda x: "All" if x == "All" else f"Vendor {x}",
    )

    return {
        "fare_range": fare_range,
        "distance_range": distance_range,
        "selected_days": selected_days,
        "selected_payment": selected_payment,
        "selected_vendor": selected_vendor,
    }


def apply_filters(dataframe: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Apply filters to the dataset.

    Args:
        dataframe: Source data.
        filters: Dictionary with filter values.

    Returns:
        DataFrame: Filtered data.
    """
    df = dataframe[
        (dataframe["fare_amount"] >= filters["fare_range"][0])
        & (dataframe["fare_amount"] <= filters["fare_range"][1])
        & (dataframe["trip_distance"] >= filters["distance_range"][0])
        & (dataframe["trip_distance"] <= filters["distance_range"][1])
        & (dataframe["pickup_day"].isin(filters["selected_days"]))
    ]

    if filters["selected_payment"] != "All":
        df = df[df["payment_type"] == filters["selected_payment"]]

    if filters["selected_vendor"] != "All":
        df = df[df["vendor_id"] == filters["selected_vendor"]]

    return df


def display_filtered_count(dataframe: pd.DataFrame) -> None:
    """Display filtered row count in sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.metric("Filtered Rows", f"{len(dataframe):,}")


def render_kpi_cards(dataframe: pd.DataFrame) -> None:
    """
    Display KPI metric cards.

    Args:
        dataframe: Filtered data for calculations.
    """
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Trips", f"{len(dataframe):,}")

    with col2:
        st.metric("Average Fare", f"${dataframe['fare_amount'].mean():.2f}")

    with col3:
        st.metric("Avg Distance", f"{dataframe['trip_distance'].mean():.2f} miles")

    with col4:
        st.metric("Avg Passengers", f"{dataframe['passenger_count'].mean():.1f}")

    with col5:
        st.metric("Total Revenue", f"${dataframe['total_amount'].sum():,.2f}")


def render_revenue_by_day(dataframe: pd.DataFrame) -> None:
    """
    Display revenue by day bar chart.

    Args:
        dataframe: Filtered data.
    """
    st.subheader("Revenue by Day")
    revenue_data = dataframe.groupby("pickup_day")["fare_amount"].sum().reset_index()
    fig = px.bar(
        revenue_data,
        x="pickup_day",
        y="fare_amount",
        title="Revenue by Day of Week",
        color="fare_amount",
        color_continuous_scale="Viridis",
        labels={"pickup_day": "Day", "fare_amount": "Revenue ($)"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_trips_by_hour(dataframe: pd.DataFrame) -> None:
    """
    Display trips per hour bar chart.

    Args:
        dataframe: Filtered data.
    """
    st.subheader("Trips per Hour")
    trips_data = dataframe.groupby("pickup_hour").size().reset_index(name="count")
    fig = px.bar(
        trips_data,
        x="pickup_hour",
        y="count",
        title="Trips by Hour of Day",
        color="count",
        color_continuous_scale="Plasma",
        labels={"pickup_hour": "Hour", "count": "Number of Trips"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_fare_distribution(dataframe: pd.DataFrame) -> None:
    """
    Display fare distribution histogram.

    Args:
        dataframe: Filtered data.
    """
    st.subheader("Fare Distribution")
    fig = px.histogram(
        dataframe,
        x="fare_amount",
        nbins=FARE_BINS,
        title="Distribution of Fare Amounts",
        color_discrete_sequence=["#636EFA"],
        labels={"fare_amount": "Fare ($)"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_distance_vs_fare(dataframe: pd.DataFrame) -> None:
    """
    Display distance vs fare scatter plot.

    Args:
        dataframe: Filtered data.
    """
    st.subheader("Distance vs Fare")
    sample_data = dataframe.sample(min(SAMPLE_SIZE, len(dataframe)))
    fig = px.scatter(
        sample_data,
        x="trip_distance",
        y="fare_amount",
        title="Trip Distance vs Fare Amount",
        color="passenger_count",
        color_continuous_scale="Viridis",
        labels={"trip_distance": "Distance (miles)", "fare_amount": "Fare ($)"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_raw_data(dataframe: pd.DataFrame) -> None:
    """Display raw data in expandable section."""
    with st.expander("View Raw Data"):
        st.dataframe(dataframe)


def render_footer() -> None:
    """Display dashboard footer."""
    st.markdown("---")
    st.markdown(
        "Data source: NYC Taxi & Limousine Commission | Updated in real-time"
    )


def handle_data_error(error: Exception) -> None:
    """
    Handle data loading errors gracefully.

    Args:
        error: Exception that occurred during data loading.
    """
    st.error(f"Error loading data: {str(error)}")
    st.info("Make sure PostgreSQL is running and data has been loaded.")
    st.stop()


def main() -> None:
    """Main application entry point."""
    configure_page()
    render_header()

    try:
        data = load_trip_data()

        if len(data) == 0:
            st.warning("No data found. Please run the ETL pipeline first.")
            return

    except Exception as error:
        st.error(f"Error loading data: {str(error)}")
        st.info("Make sure PostgreSQL is running and data has been loaded.")
        return

    filters = get_filters(data)
    filtered_data = apply_filters(data, filters)

    display_filtered_count(filtered_data)
    render_kpi_cards(filtered_data)

    col1, col2 = st.columns(2)
    with col1:
        render_revenue_by_day(filtered_data)
    with col2:
        render_trips_by_hour(filtered_data)

    col3, col4 = st.columns(2)
    with col3:
        render_fare_distribution(filtered_data)
    with col4:
        render_distance_vs_fare(filtered_data)

    render_raw_data(filtered_data)
    render_footer()


if __name__ == "__main__":
    main()