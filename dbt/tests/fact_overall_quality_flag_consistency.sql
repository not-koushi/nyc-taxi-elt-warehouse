SELECT
    trip_key

FROM {{ ref('fact_trips') }}

WHERE is_valid_trip_record <>
    (
        is_valid_trip_time
        AND is_valid_trip_distance
        AND is_nonnegative_total_amount
    )
