WITH payment_types AS (

    SELECT 0 AS payment_type_id, 'Flex Fare or Unspecified' AS payment_type_name
    UNION ALL
    SELECT 1, 'Credit Card'
    UNION ALL
    SELECT 2, 'Cash'
    UNION ALL
    SELECT 3, 'No Charge'
    UNION ALL
    SELECT 4, 'Dispute'
    UNION ALL
    SELECT 5, 'Unknown'

)

SELECT
    ROW_NUMBER() OVER (ORDER BY payment_type_id) AS payment_type_key,
    payment_type_id,
    payment_type_name

FROM payment_types
