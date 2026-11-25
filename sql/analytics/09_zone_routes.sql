SELECT

    pickup_zone.borough AS pickup_borough,

    pickup_zone.zone AS pickup_zone,

    dropoff_zone.borough AS dropoff_borough,

    dropoff_zone.zone AS dropoff_zone,

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
    pickup_zone.zone,

    dropoff_zone.borough,
    dropoff_zone.zone

ORDER BY total_trips DESC

LIMIT 25;
