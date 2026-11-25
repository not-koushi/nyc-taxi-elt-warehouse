WITH rate_codes AS (

    SELECT 1 AS rate_code_id, 'Standard Rate' AS rate_code_name
    UNION ALL
    SELECT 2, 'JFK'
    UNION ALL
    SELECT 3, 'Newark'
    UNION ALL
    SELECT 4, 'Nassau or Westchester'
    UNION ALL
    SELECT 5, 'Negotiated Fare'
    UNION ALL
    SELECT 6, 'Group Ride'
    UNION ALL
    SELECT 99, 'Unknown or Null Rate Code'

)

SELECT
    ROW_NUMBER() OVER (ORDER BY rate_code_id) AS rate_code_key,
    rate_code_id,
    rate_code_name

FROM rate_codes
