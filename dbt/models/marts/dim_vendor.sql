WITH vendors AS (

    SELECT 1 AS vendor_id, 'Creative Mobile Technologies' AS vendor_name
    UNION ALL
    SELECT 2, 'VeriFone Inc'
    UNION ALL
    SELECT 6, 'Vendor ID 6'
    UNION ALL
    SELECT 7, 'Vendor ID 7'

)

SELECT
    ROW_NUMBER() OVER (ORDER BY vendor_id) AS vendor_key,
    vendor_id,
    vendor_name

FROM vendors
