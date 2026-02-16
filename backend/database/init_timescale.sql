-- ==========================================
-- GIMAT TimescaleDB Initialization Script
-- ==========================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- The tables will be created by SQLAlchemy
-- This script will be executed on database initialization
-- to ensure TimescaleDB extension is available

-- Create indexes for better performance (if not created by SQLAlchemy)
-- These are additional optimizations

-- Observations table optimizations
-- (Will be created as hypertable by Python code)

-- Predictions table optimizations
-- (Will be created as hypertable by Python code)

-- Set retention policy (optional - keep data for 5 years)
-- SELECT add_retention_policy('observations', INTERVAL '5 years', if_not_exists => TRUE);
-- SELECT add_retention_policy('predictions', INTERVAL '2 years', if_not_exists => TRUE);

-- Compression policy for older data (older than 1 month)
-- SELECT add_compression_policy('observations', INTERVAL '1 month', if_not_exists => TRUE);
-- SELECT add_compression_policy('predictions', INTERVAL '1 month', if_not_exists => TRUE);

-- Continuous aggregates for common queries (hourly, daily averages)
-- CREATE MATERIALIZED VIEW IF NOT EXISTS observations_daily
-- WITH (timescaledb.continuous) AS
-- SELECT
--     time_bucket('1 day', timestamp) AS bucket,
--     station_id,
--     river_name,
--     AVG(water_level) as avg_water_level,
--     AVG(discharge) as avg_discharge,
--     AVG(precipitation) as avg_precipitation,
--     AVG(temperature) as avg_temperature
-- FROM observations
-- GROUP BY bucket, station_id, river_name;

-- Add refresh policy for continuous aggregates
-- SELECT add_continuous_aggregate_policy('observations_daily',
--     start_offset => INTERVAL '3 days',
--     end_offset => INTERVAL '1 hour',
--     schedule_interval => INTERVAL '1 hour',
--     if_not_exists => TRUE);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gimat;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gimat;
