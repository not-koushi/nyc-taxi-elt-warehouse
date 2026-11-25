WITH staging AS (

    SELECT *
    FROM {{ ref('stg_yellow_taxi_trips') }}

),

transformed AS (

    SELECT
        *,

        EXTRACT(
            EPOCH FROM (dropoff_datetime - pickup_datetime)
        ) / 60.0 AS trip_duration_minutes,

        CASE
            WHEN pickup_datetime < dropoff_datetime
            THEN TRUE
            ELSE FALSE
        END AS is_valid_trip_time,

        CASE
            WHEN trip_distance > 0
            THEN TRUE
            ELSE FALSE
        END AS is_valid_trip_distance,

        CASE
            WHEN total_amount >= 0
            THEN TRUE
            ELSE FALSE
        END AS is_nonnegative_total_amount

    FROM staging

)

SELECT
    *,

    CASE
        WHEN is_valid_trip_time
         AND is_valid_trip_distance
         AND is_nonnegative_total_amount
        THEN TRUE
        ELSE FALSE
    END AS is_valid_trip_record

FROM transformed
