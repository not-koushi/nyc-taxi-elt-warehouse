-- ============================================================
-- NYC Taxi ELT Warehouse
-- Database: taxi_warehouse
-- Purpose: Initialize warehouse schemas
-- ============================================================

-- Raw layer: source data as ingested
CREATE SCHEMA IF NOT EXISTS raw;

-- Staging layer: cleaned and standardized data
CREATE SCHEMA IF NOT EXISTS staging;

-- Mart layer: analytical data models
CREATE SCHEMA IF NOT EXISTS mart;
