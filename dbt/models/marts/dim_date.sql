WITH date_bounds AS (

    SELECT
        MIN(trip_date) AS min_date,
        MAX(trip_date) AS max_date

    FROM (

        SELECT pickup_datetime::DATE AS trip_date
        FROM {{ ref('int_yellow_taxi_trips') }}

        UNION ALL

        SELECT dropoff_datetime::DATE AS trip_date
        FROM {{ ref('int_yellow_taxi_trips') }}

    ) AS all_trip_dates

),

date_spine AS (

    SELECT
        generate_series(
            min_date,
            max_date,
            INTERVAL '1 day'
        )::DATE AS full_date

    FROM date_bounds

),

date_attributes AS (

    SELECT
        full_date,

        EXTRACT(YEAR FROM full_date)::INTEGER AS year,
        EXTRACT(MONTH FROM full_date)::INTEGER AS month,
        TO_CHAR(full_date, 'Month') AS month_name,
        EXTRACT(QUARTER FROM full_date)::INTEGER AS quarter,

        EXTRACT(DAY FROM full_date)::INTEGER AS day,
        EXTRACT(DOW FROM full_date)::INTEGER AS day_of_week,
        TO_CHAR(full_date, 'Day') AS day_name,

        CASE
            WHEN EXTRACT(DOW FROM full_date) IN (0, 6)
            THEN TRUE
            ELSE FALSE
        END AS is_weekend

    FROM date_spine

)

SELECT
    TO_CHAR(full_date, 'YYYYMMDD')::INTEGER AS date_key,

    full_date,
    year,
    month,
    TRIM(month_name) AS month_name,
    quarter,
    day,
    day_of_week,
    TRIM(day_name) AS day_name,
    is_weekend

FROM date_attributes
