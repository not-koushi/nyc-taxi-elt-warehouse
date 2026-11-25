SELECT

    payment.payment_type_name,

    COUNT(*) AS total_trips,

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
    ) AS average_tip_amount,

    ROUND(
        SUM(fact.tip_amount),
        2
    ) AS total_tip_amount,

    ROUND(
        SUM(fact.tip_amount)
        / NULLIF(SUM(fact.total_amount), 0)
        * 100,
        2
    ) AS tip_percentage

FROM mart.fact_trips AS fact

JOIN mart.dim_payment_type AS payment

    ON fact.payment_type_key = payment.payment_type_key

WHERE fact.is_valid_trip_record = TRUE

GROUP BY payment.payment_type_name

ORDER BY total_trip_revenue DESC;
