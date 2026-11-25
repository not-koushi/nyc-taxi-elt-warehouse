SELECT
    fact.trip_key

FROM {{ ref('fact_trips') }} AS fact

LEFT JOIN {{ ref('dim_vendor') }} AS vendor
    ON fact.vendor_key = vendor.vendor_key

LEFT JOIN {{ ref('dim_date') }} AS pickup_date
    ON fact.pickup_date_key = pickup_date.date_key

LEFT JOIN {{ ref('dim_date') }} AS dropoff_date
    ON fact.dropoff_date_key = dropoff_date.date_key

LEFT JOIN {{ ref('dim_taxi_zone') }} AS pickup_zone
    ON fact.pickup_zone_key = pickup_zone.zone_key

LEFT JOIN {{ ref('dim_taxi_zone') }} AS dropoff_zone
    ON fact.dropoff_zone_key = dropoff_zone.zone_key

LEFT JOIN {{ ref('dim_payment_type') }} AS payment
    ON fact.payment_type_key = payment.payment_type_key

LEFT JOIN {{ ref('dim_rate_code') }} AS rate
    ON fact.rate_code_key = rate.rate_code_key

WHERE
    vendor.vendor_key IS NULL
    OR pickup_date.date_key IS NULL
    OR dropoff_date.date_key IS NULL
    OR pickup_zone.zone_key IS NULL
    OR dropoff_zone.zone_key IS NULL
    OR payment.payment_type_key IS NULL
    OR rate.rate_code_key IS NULL
