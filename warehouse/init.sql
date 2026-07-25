-- =============================================================================
-- BATCHETL PIPELINE - DATA WAREHOUSE SCHEMA
-- =============================================================================
-- Database: MySQL
-- Table: fact_trips
-- =============================================================================


-- =============================================================================
-- 1. CREATE DATABASE
-- =============================================================================

DROP DATABASE IF EXISTS warehouse;

CREATE DATABASE warehouse
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE warehouse;


-- =============================================================================
-- 2. DROP TABLE IF EXISTS
-- =============================================================================

DROP TABLE IF EXISTS fact_trips CASCADE;


-- =============================================================================
-- 3. CREATE FACT TABLE
-- =============================================================================

CREATE TABLE fact_trips (
    trip_id             SERIAL          PRIMARY KEY,
    vendor_id           SMALLINT        NULL,
    payment_type        SMALLINT        NULL,
    pickup_datetime     TIMESTAMP       NULL,
    dropoff_datetime    TIMESTAMP       NULL,
    pickup_hour         SMALLINT        NULL,
    pickup_day          VARCHAR(20)     NULL,
    pickup_month        SMALLINT        NULL,
    passenger_count     SMALLINT        NULL,
    trip_distance       REAL            NULL,
    fare_amount         REAL            NULL,
    total_amount        REAL            NULL
) COMMENT='Central fact table for NYC Taxi trip analytics';


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
-- 5. ADD COLUMN COMMENTS (MySQL Syntax)
-- =============================================================================

ALTER TABLE fact_trips MODIFY COLUMN trip_id SERIAL COMMENT 'Surrogate primary key - auto-incrementing serial';
ALTER TABLE fact_trips MODIFY COLUMN vendor_id SMALLINT COMMENT 'Vendor code: 1 = CMT, 2 = VeriFone';
ALTER TABLE fact_trips MODIFY COLUMN payment_type SMALLINT COMMENT 'Payment code: 1=Credit, 2=Cash, 3=No Charge, 4=Dispute, 5=Unknown';
ALTER TABLE fact_trips MODIFY COLUMN pickup_datetime TIMESTAMP COMMENT 'Trip start timestamp in NYC local time';
ALTER TABLE fact_trips MODIFY COLUMN dropoff_datetime TIMESTAMP COMMENT 'Trip end timestamp in NYC local time';
ALTER TABLE fact_trips MODIFY COLUMN passenger_count SMALLINT COMMENT 'Number of passengers in the trip';
ALTER TABLE fact_trips MODIFY COLUMN trip_distance REAL COMMENT 'Trip distance in miles';
ALTER TABLE fact_trips MODIFY COLUMN fare_amount REAL COMMENT 'Base fare amount in USD';
ALTER TABLE fact_trips MODIFY COLUMN total_amount REAL COMMENT 'Total amount including all fees in USD';
ALTER TABLE fact_trips MODIFY COLUMN pickup_hour SMALLINT COMMENT 'Hour of pickup extracted from pickup_datetime (0-23)';
ALTER TABLE fact_trips MODIFY COLUMN pickup_day VARCHAR(20) COMMENT 'Day name extracted from pickup_datetime (Monday-Sunday)';
ALTER TABLE fact_trips MODIFY COLUMN pickup_month SMALLINT COMMENT 'Month number extracted from pickup_datetime (1-12)';


-- =============================================================================
-- 6. CREATE VIEWS
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
-- 7. CREATE FUNCTION
-- =============================================================================

DELIMITER $$

CREATE FUNCTION fn_trip_stats(
    p_start_date DATETIME,
    p_end_date DATETIME
)
RETURNS JSON
DETERMINISTIC
BEGIN
    DECLARE v_result JSON;
    
    SELECT JSON_OBJECT(
        'total_trips', COUNT(*),
        'avg_fare', AVG(fare_amount),
        'avg_distance', AVG(trip_distance),
        'total_revenue', SUM(total_amount),
        'avg_passengers', AVG(passenger_count)
    ) INTO v_result
    FROM fact_trips
    WHERE pickup_datetime BETWEEN p_start_date AND p_end_date;
    
    RETURN v_result;
END$$

DELIMITER ;


-- =============================================================================
-- 8. VERIFICATION QUERIES
-- =============================================================================

SELECT 'Database: warehouse' AS info;
SELECT 'Table: fact_trips created successfully' AS status;
SELECT COUNT(*) AS table_count FROM information_schema.tables WHERE table_schema = 'warehouse';

-- Check views
SELECT TABLE_NAME FROM information_schema.views WHERE table_schema = 'warehouse';

-- Check indexes
SELECT INDEX_NAME FROM information_schema.statistics 
WHERE table_schema = 'warehouse' AND table_name = 'fact_trips'
GROUP BY INDEX_NAME;

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