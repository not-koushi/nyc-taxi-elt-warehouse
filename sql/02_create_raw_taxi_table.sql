-- ============================================================
-- NYC Taxi ELT Warehouse
-- Raw yellow taxi trips table
-- ============================================================

CREATE TABLE IF NOT EXISTS raw.yellow_taxi_trips (
    vendorid TEXT,
    tpep_pickup_datetime TEXT,
    tpep_dropoff_datetime TEXT,
    passenger_count TEXT,
    trip_distance TEXT,
    ratecodeid TEXT,
    store_and_fwd_flag TEXT,
    pulocationid TEXT,
    dolocationid TEXT,
    payment_type TEXT,
    fare_amount TEXT,
    extra TEXT,
    mta_tax TEXT,
    tip_amount TEXT,
    tolls_amount TEXT,
    improvement_surcharge TEXT,
    total_amount TEXT,
    congestion_surcharge TEXT,
    airport_fee TEXT,
    cbd_congestion_fee TEXT,

    source_month DATE NOT NULL,
    source_file TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL,
    batch_id TEXT NOT NULL
);
