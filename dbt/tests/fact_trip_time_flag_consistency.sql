SELECT
    trip_key

FROM {{ ref('fact_trips') }}

WHERE is_valid_trip_time <>
    CASE
        WHEN pickup_date_key IS NOT NULL
         AND dropoff_date_key IS NOT NULL
         AND trip_duration_minutes > 0
        THEN TRUE
        ELSE FALSE
    END
