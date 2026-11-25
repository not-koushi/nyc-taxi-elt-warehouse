SELECT

    pickup_date.full_date,

    pickup_date.day_name,

    pickup_date.is_weekend,

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

JOIN mart.dim_date AS pickup_date

    ON fact.pickup_date_key = pickup_date.date_key

WHERE fact.is_valid_trip_record = TRUE

GROUP BY

    pickup_date.full_date,
    pickup_date.day_name,
    pickup_date.is_weekend

ORDER BY pickup_date.full_date;
