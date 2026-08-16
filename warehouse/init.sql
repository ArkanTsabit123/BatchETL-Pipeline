-- =============================================================================
-- BATCHETL PIPELINE - DATA WAREHOUSE SCHEMA
-- =============================================================================
-- Database: PostgreSQL
-- Table: fact_trips
-- =============================================================================

-- =============================================================================
-- 1. DROP TABLE IF EXISTS
-- =============================================================================

DROP TABLE IF EXISTS fact_trips CASCADE;

-- =============================================================================
-- 2. CREATE FACT TABLE
-- =============================================================================

CREATE TABLE fact_trips (
    trip_id             SERIAL          PRIMARY KEY,
    vendor_id           INTEGER         NULL,
    payment_type        INTEGER         NULL,
    pickup_datetime     TIMESTAMP       NULL,
    dropoff_datetime    TIMESTAMP       NULL,
    pickup_hour         INTEGER         NULL,
    pickup_day          VARCHAR(20)     NULL,
    pickup_month        INTEGER         NULL,
    passenger_count     INTEGER         NULL,
    trip_distance       NUMERIC(10,2)   NULL,
    fare_amount         NUMERIC(10,2)   NULL,
    total_amount        NUMERIC(10,2)   NULL
);

-- =============================================================================
-- 3. ADD TABLE COMMENTS
-- =============================================================================

COMMENT ON TABLE fact_trips IS 'Central fact table for NYC Taxi trip analytics';
COMMENT ON COLUMN fact_trips.trip_id IS 'Surrogate primary key - auto-incrementing serial';
COMMENT ON COLUMN fact_trips.vendor_id IS 'Vendor code: 1 = CMT, 2 = VeriFone';
COMMENT ON COLUMN fact_trips.payment_type IS 'Payment code: 1=Credit, 2=Cash, 3=No Charge, 4=Dispute, 5=Unknown';
COMMENT ON COLUMN fact_trips.pickup_datetime IS 'Trip start timestamp in NYC local time';
COMMENT ON COLUMN fact_trips.dropoff_datetime IS 'Trip end timestamp in NYC local time';
COMMENT ON COLUMN fact_trips.passenger_count IS 'Number of passengers in the trip';
COMMENT ON COLUMN fact_trips.trip_distance IS 'Trip distance in miles';
COMMENT ON COLUMN fact_trips.fare_amount IS 'Base fare amount in USD';
COMMENT ON COLUMN fact_trips.total_amount IS 'Total amount including all fees in USD';
COMMENT ON COLUMN fact_trips.pickup_hour IS 'Hour of pickup extracted from pickup_datetime (0-23)';
COMMENT ON COLUMN fact_trips.pickup_day IS 'Day name extracted from pickup_datetime (Monday-Sunday)';
COMMENT ON COLUMN fact_trips.pickup_month IS 'Month number extracted from pickup_datetime (1-12)';

-- =============================================================================
-- 4. CREATE INDEXES
-- =============================================================================

CREATE INDEX idx_pickup_datetime ON fact_trips(pickup_datetime);
CREATE INDEX idx_pickup_day ON fact_trips(pickup_day);
CREATE INDEX idx_fare_amount ON fact_trips(fare_amount);
CREATE INDEX idx_trip_distance ON fact_trips(trip_distance);
CREATE INDEX idx_vendor_id ON fact_trips(vendor_id);
CREATE INDEX idx_payment_type ON fact_trips(payment_type);
CREATE INDEX idx_pickup_hour ON fact_trips(pickup_hour);
CREATE INDEX idx_pickup_month ON fact_trips(pickup_month);

-- =============================================================================
-- 5. CREATE VIEWS
-- =============================================================================

CREATE OR REPLACE VIEW v_daily_summary AS
SELECT 
    DATE(pickup_datetime) AS trip_date,
    pickup_day,
    COUNT(*) AS total_trips,
    SUM(passenger_count) AS total_passengers,
    AVG(passenger_count) AS avg_passengers,
    SUM(trip_distance) AS total_distance,
    AVG(trip_distance) AS avg_distance,
    SUM(fare_amount) AS total_fare,
    AVG(fare_amount) AS avg_fare,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS avg_revenue
FROM fact_trips
GROUP BY DATE(pickup_datetime), pickup_day
ORDER BY trip_date DESC;

CREATE OR REPLACE VIEW v_hourly_distribution AS
SELECT 
    pickup_hour,
    COUNT(*) AS total_trips,
    AVG(trip_distance) AS avg_distance,
    AVG(fare_amount) AS avg_fare,
    SUM(total_amount) AS total_revenue
FROM fact_trips
GROUP BY pickup_hour
ORDER BY pickup_hour;

CREATE OR REPLACE VIEW v_vendor_performance AS
SELECT 
    vendor_id,
    COUNT(*) AS total_trips,
    AVG(trip_distance) AS avg_distance,
    AVG(fare_amount) AS avg_fare,
    SUM(total_amount) AS total_revenue
FROM fact_trips
WHERE vendor_id IS NOT NULL
GROUP BY vendor_id
ORDER BY total_trips DESC;

CREATE OR REPLACE VIEW v_payment_analysis AS
SELECT 
    payment_type,
    COUNT(*) AS total_trips,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS avg_revenue
FROM fact_trips
WHERE payment_type IS NOT NULL
GROUP BY payment_type
ORDER BY total_trips DESC;

CREATE OR REPLACE VIEW v_monthly_trend AS
SELECT 
    pickup_month,
    COUNT(*) AS total_trips,
    SUM(total_amount) AS total_revenue,
    AVG(fare_amount) AS avg_fare,
    AVG(trip_distance) AS avg_distance
FROM fact_trips
GROUP BY pickup_month
ORDER BY pickup_month;

-- =============================================================================
-- 6. CREATE FUNCTION
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_trip_stats(
    p_start_date TIMESTAMP,
    p_end_date TIMESTAMP
)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_result JSON;
BEGIN
    SELECT JSON_BUILD_OBJECT(
        'total_trips', COUNT(*),
        'avg_fare', AVG(fare_amount),
        'avg_distance', AVG(trip_distance),
        'total_revenue', SUM(total_amount),
        'avg_passengers', AVG(passenger_count)
    ) INTO v_result
    FROM fact_trips
    WHERE pickup_datetime BETWEEN p_start_date AND p_end_date;
    
    RETURN v_result;
END;
$$;

-- =============================================================================
-- 7. VERIFICATION QUERIES
-- =============================================================================

SELECT 'Database: warehouse' AS info;
SELECT 'Table: fact_trips created successfully' AS status;
SELECT COUNT(*) AS table_count FROM information_schema.tables WHERE table_name = 'fact_trips';

-- Check views
SELECT table_name FROM information_schema.views 
WHERE table_name LIKE 'v_%'
ORDER BY table_name;

-- Check indexes
SELECT indexname FROM pg_indexes 
WHERE tablename = 'fact_trips'
ORDER BY indexname;

-- Check column data types
SELECT 
    column_name,
    data_type,
    numeric_precision,
    numeric_scale
FROM information_schema.columns 
WHERE table_name = 'fact_trips'
ORDER BY ordinal_position;

-- =============================================================================
-- 8. SAMPLE QUERIES (Commented out for production)
-- =============================================================================

-- Count total rows
-- SELECT COUNT(*) FROM fact_trips;

-- View sample data
-- SELECT * FROM fact_trips LIMIT 10;

-- Check daily summary
-- SELECT * FROM v_daily_summary LIMIT 10;

-- Check hourly distribution
-- SELECT * FROM v_hourly_distribution;

-- Check vendor performance
-- SELECT * FROM v_vendor_performance;

-- Check payment analysis
-- SELECT * FROM v_payment_analysis;

-- Check monthly trend
-- SELECT * FROM v_monthly_trend;

-- Test function
-- SELECT fn_trip_stats('2024-01-01', '2024-01-31') AS stats;

-- =============================================================================
-- END OF SCRIPT
-- =============================================================================