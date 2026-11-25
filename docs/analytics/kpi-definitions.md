# NYC Taxi Warehouse — KPI Definitions

## Dataset

- Source: NYC TLC Yellow Taxi trip data
- Dataset period: January 2025
- Warehouse fact table: mart.fact_trips
- Total source records: 3,475,226

## Data Quality Definition

A valid trip must satisfy all three conditions:

1. Pickup timestamp precedes dropoff timestamp.
2. Trip distance is greater than zero.
3. Total amount is greater than or equal to zero.

The warehouse retains both valid and invalid records.

Business analytics queries use valid trips unless otherwise specified.

## KPIs

### Total Trips

Count of records in the fact table.

### Valid Trips

Count of records where is_valid_trip_record = TRUE.

### Trip Revenue

Sum of total_amount for valid trips.

This metric represents trip-level total amounts and is not equivalent
to net income or accounting revenue.

### Average Trip Amount

Average total_amount across valid trips.

### Average Trip Distance

Average trip_distance across valid trips.

### Average Trip Duration

Average trip_duration_minutes across valid trips.

### Tip Revenue

Sum of tip_amount across valid trips.

### Average Tip

Average tip_amount across valid trips.

### Tip Percentage

Sum of tip_amount divided by sum of total_amount,
multiplied by 100, across valid trips.

Only calculated where the aggregate total_amount is positive.

### Trips by Pickup Borough

Valid trip counts grouped by the borough of the pickup zone.

### Trips by Dropoff Borough

Valid trip counts grouped by the borough of the dropoff zone.

### Trips by Pickup Hour

Valid trip counts grouped by the pickup hour.

### Trips by Pickup Date

Valid trip counts grouped by pickup date.

### Payment Distribution

Valid trip counts, total amounts, and average trip amounts
grouped by payment type.

### Vendor Performance

Valid trip counts, total amounts, average trip distances,
average durations, and average trip amounts grouped by vendor.

## Analytical Conventions

- Use valid trips for business analytics.
- Use pickup zones for pickup-location analytics.
- Use dropoff zones for dropoff-location analytics.
- Use total_amount for the trip-level monetary metric.
- Preserve unknown and unmapped location categories.
- Treat these KPIs as analytical metrics rather than accounting metrics.
