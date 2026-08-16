-- Runs once on first DB init (mounted into docker-entrypoint-initdb.d).
-- Enable PostGIS so we can store geometry columns for stations/tracks/blocks.
CREATE EXTENSION IF NOT EXISTS postgis;
