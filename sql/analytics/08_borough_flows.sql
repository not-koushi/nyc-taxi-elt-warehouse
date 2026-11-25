SELECT

    pickup_zone.borough AS pickup_borough,

    dropoff_zone.borough AS dropoff_borough,

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

JOIN mart.dim_taxi_zone AS pickup_zone

    ON fact.pickup_zone_key = pickup_zone.zone_key

JOIN mart.dim_taxi_zone AS dropoff_zone

    ON fact.dropoff_zone_key = dropoff_zone.zone_key

WHERE fact.is_valid_trip_record = TRUE

GROUP BY

    pickup_zone.borough,
    dropoff_zone.borough

ORDER BY total_trips DESC;
