SELECT

    COUNT(*) AS valid_trips,

    ROUND(
        AVG(trip_distance),
        2
    ) AS average_trip_distance_miles,

    ROUND(
        AVG(trip_duration_minutes),
        2
    ) AS average_trip_duration_minutes,

    ROUND(
        AVG(total_amount),
        2
    ) AS average_trip_amount,

    ROUND(
        SUM(total_amount),
        2
    ) AS total_trip_revenue,

    ROUND(
        SUM(tip_amount),
        2
    ) AS total_tip_amount,

    ROUND(
        SUM(tip_amount) / NULLIF(SUM(total_amount), 0) * 100,
        2
    ) AS tip_percentage,

    ROUND(
        AVG(passenger_count),
        2
    ) AS average_passenger_count

FROM mart.fact_trips

WHERE is_valid_trip_record = TRUE;
