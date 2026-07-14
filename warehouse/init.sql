-- BatchETL Pipeline Database Initialization
-- NYC Taxi Data Warehouse Schema

CREATE TABLE IF NOT EXISTS fact_trips (
    trip_id SERIAL PRIMARY KEY,
    vendor_id INTEGER,
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    passenger_count INTEGER,
    trip_distance FLOAT,
    fare_amount FLOAT,
    total_amount FLOAT,
    payment_type INTEGER,
    pickup_hour INTEGER,
    pickup_day VARCHAR(20),
    pickup_month INTEGER
);

CREATE INDEX IF NOT EXISTS idx_pickup_datetime ON fact_trips(pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_pickup_day ON fact_trips(pickup_day);
CREATE INDEX IF NOT EXISTS idx_fare_amount ON fact_trips(fare_amount);
