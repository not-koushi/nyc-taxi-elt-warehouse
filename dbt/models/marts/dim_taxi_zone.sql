WITH source_data AS (

    SELECT
        "LocationID" AS location_id,
        "Borough" AS borough,
        "Zone" AS zone,
        service_zone

    FROM {{ ref('taxi_zone_lookup') }}

),

dimension_data AS (

    SELECT
        ROW_NUMBER() OVER (
            ORDER BY location_id
        ) AS zone_key,

        location_id,
        borough,
        zone,
        service_zone

    FROM source_data

)

SELECT *
FROM dimension_data
