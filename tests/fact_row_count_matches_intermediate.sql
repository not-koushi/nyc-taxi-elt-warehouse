WITH intermediate_count AS (

    SELECT COUNT(*) AS row_count
    FROM {{ ref('int_yellow_taxi_trips') }}

),

fact_count AS (

    SELECT COUNT(*) AS row_count
    FROM {{ ref('fact_trips') }}

)

SELECT
    intermediate_count.row_count AS intermediate_rows,
    fact_count.row_count AS fact_rows

FROM intermediate_count
CROSS JOIN fact_count

WHERE intermediate_count.row_count <> fact_count.row_count
