SELECT

    EXTRACT(
        HOUR FROM fact.pickup_datetime
    )::INTEGER AS pickup_hour,

    COUNT(*) AS total_trips,

    ROUND(
        AVG(fact.trip_distance),
        2
    ) AS average_trip_distance_miles,

    ROUND(
        AVG(fact.trip_duration_minutes),
        2
    ) AS average_trip_duration_minutes,

    ROUND(
        AVG(fact.total_amount),
        2
    ) AS average_trip_amount,

    ROUND(
        SUM(fact.total_amount),
        2
    ) AS total_trip_revenue

FROM mart.fact_trips AS fact

WHERE fact.is_valid_trip_record = TRUE

GROUP BY pickup_hour

ORDER BY pickup_hour;
