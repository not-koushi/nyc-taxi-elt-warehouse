SELECT

    vendor.vendor_name,

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
    ) AS total_trip_revenue,

    ROUND(
        AVG(fact.tip_amount),
        2
    ) AS average_tip_amount

FROM mart.fact_trips AS fact

JOIN mart.dim_vendor AS vendor

    ON fact.vendor_key = vendor.vendor_key

WHERE fact.is_valid_trip_record = TRUE

GROUP BY vendor.vendor_name

ORDER BY total_trip_revenue DESC;
