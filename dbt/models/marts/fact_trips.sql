WITH trips AS (

    SELECT *
    FROM {{ ref('int_yellow_taxi_trips') }}

),

joined AS (

    SELECT

        -- Source identifiers used to derive warehouse keys
        trips.vendor_id,
        trips.pickup_datetime,
        trips.dropoff_datetime,
        trips.pickup_location_id,
        trips.dropoff_location_id,
        trips.payment_type,
        trips.rate_code_id,

        -- Dimension surrogate keys
        vendor.vendor_key,

        pickup_date.date_key AS pickup_date_key,
        dropoff_date.date_key AS dropoff_date_key,

        pickup_zone.zone_key AS pickup_zone_key,
        dropoff_zone.zone_key AS dropoff_zone_key,

        payment.payment_type_key,

        rate.rate_code_key,

        -- Trip measurements
        trips.passenger_count,
        trips.trip_distance,
        trips.trip_duration_minutes,

        trips.fare_amount,
        trips.extra,
        trips.mta_tax,
        trips.tip_amount,
        trips.tolls_amount,
        trips.improvement_surcharge,
        trips.congestion_surcharge,
        trips.airport_fee,
        trips.cbd_congestion_fee,
        trips.total_amount,

        -- Data quality flags
        trips.is_valid_trip_time,
        trips.is_valid_trip_distance,
        trips.is_nonnegative_total_amount,
        trips.is_valid_trip_record,

        -- Ingestion metadata
        trips.source_file,
        trips.ingested_at,
        trips.batch_id

    FROM trips

    LEFT JOIN {{ ref('dim_vendor') }} AS vendor
        ON trips.vendor_id = vendor.vendor_id

    LEFT JOIN {{ ref('dim_date') }} AS pickup_date
        ON trips.pickup_datetime::DATE = pickup_date.full_date

    LEFT JOIN {{ ref('dim_date') }} AS dropoff_date
        ON trips.dropoff_datetime::DATE = dropoff_date.full_date

    LEFT JOIN {{ ref('dim_taxi_zone') }} AS pickup_zone
        ON trips.pickup_location_id = pickup_zone.location_id

    LEFT JOIN {{ ref('dim_taxi_zone') }} AS dropoff_zone
        ON trips.dropoff_location_id = dropoff_zone.location_id

    LEFT JOIN {{ ref('dim_payment_type') }} AS payment
        ON trips.payment_type = payment.payment_type_id

    LEFT JOIN {{ ref('dim_rate_code') }} AS rate
        ON COALESCE(trips.rate_code_id, -1) = rate.rate_code_id

)

SELECT

    ROW_NUMBER() OVER (
        ORDER BY pickup_datetime,
                 dropoff_datetime,
                 vendor_id,
                 pickup_location_id,
                 dropoff_location_id,
                 total_amount
    ) AS trip_key,

    vendor_key,

    pickup_date_key,
    dropoff_date_key,

    pickup_datetime,
    dropoff_datetime,

    pickup_zone_key,
    dropoff_zone_key,

    payment_type_key,
    rate_code_key,

    passenger_count,
    trip_distance,
    trip_duration_minutes,

    fare_amount,
    extra,
    mta_tax,
    tip_amount,
    tolls_amount,
    improvement_surcharge,
    congestion_surcharge,
    airport_fee,
    cbd_congestion_fee,
    total_amount,

    is_valid_trip_time,
    is_valid_trip_distance,
    is_nonnegative_total_amount,
    is_valid_trip_record,

    source_file,
    ingested_at,
    batch_id

FROM joined
