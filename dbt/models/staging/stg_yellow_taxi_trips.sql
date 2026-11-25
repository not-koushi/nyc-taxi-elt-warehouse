SELECT
    vendorid::INTEGER AS vendor_id,

    tpep_pickup_datetime::TIMESTAMP AS pickup_datetime,
    tpep_dropoff_datetime::TIMESTAMP AS dropoff_datetime,

    passenger_count::NUMERIC AS passenger_count,
    trip_distance::NUMERIC AS trip_distance,

    ratecodeid::INTEGER AS rate_code_id,

    store_and_fwd_flag AS store_and_forward_flag,

    pulocationid::INTEGER AS pickup_location_id,
    dolocationid::INTEGER AS dropoff_location_id,

    payment_type::INTEGER AS payment_type,

    fare_amount::NUMERIC AS fare_amount,
    extra::NUMERIC AS extra,
    mta_tax::NUMERIC AS mta_tax,
    tip_amount::NUMERIC AS tip_amount,
    tolls_amount::NUMERIC AS tolls_amount,
    improvement_surcharge::NUMERIC AS improvement_surcharge,
    total_amount::NUMERIC AS total_amount,
    congestion_surcharge::NUMERIC AS congestion_surcharge,
    airport_fee::NUMERIC AS airport_fee,
    cbd_congestion_fee::NUMERIC AS cbd_congestion_fee,

    source_month,
    source_file,
    ingested_at,
    batch_id

FROM {{ source('taxi_raw', 'yellow_taxi_trips') }}
