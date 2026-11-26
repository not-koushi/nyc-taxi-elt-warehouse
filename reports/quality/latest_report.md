# Data Quality Audit Report

**Audit Run ID:** `667d9852-b587-483e-a8a0-11c1fc32bd56`

**Execution time:** 2026-11-26T11:53:09.706820+00:00

## Scorecard

| Metric | Result |
|---|---:|
| Total checks | 25 |
| PASS | 16 |
| WARN | 9 |
| FAIL | 0 |
| Check-health score | 82.00% |

### Score calculation

- PASS = 1 point
- WARN = 0.5 points
- FAIL = 0 points

This is a check-level monitoring score, not a measure of the percentage of individual records that are valid.

## Detailed Results

| Check | Category | Status | Actual Value | Expected |
|---|---|---|---:|---|
| Q01_fact_row_count | Completeness | PASS | 3475226 | Greater than zero |
| Q02_null_pickup_datetime | Completeness | PASS | 0 | 0 |
| Q03_null_dropoff_datetime | Completeness | PASS | 0 | 0 |
| Q04_null_trip_distance | Completeness | PASS | 0 | 0 |
| Q05_null_total_amount | Completeness | PASS | 0 | 0 |
| Q06_null_vendor_keys | Referential integrity | PASS | 0 | 0 |
| Q07_null_pickup_zone_keys | Referential integrity | PASS | 0 | 0 |
| Q08_null_dropoff_zone_keys | Referential integrity | PASS | 0 | 0 |
| Q09_null_payment_keys | Referential integrity | PASS | 0 | 0 |
| Q10_null_rate_code_keys | Referential integrity | PASS | 0 | 0 |
| Q11_duplicate_trip_fingerprints | Uniqueness | PASS | 0 | 0 duplicate groups |
| Q12_invalid_duration_flag_consistency | Consistency | PASS | 0 | 0 |
| Q13_overall_quality_flag_consistency | Consistency | PASS | 0 | 0 |
| Q14_zero_distance_records | Validity | WARN | 90893 | 0 for valid trips |
| Q15_negative_total_amount | Financial validity | WARN | 63037 | 0 for valid trips |
| Q16_negative_fare_amount | Financial validity | WARN | 144118 | 0 for valid trips |
| Q17_negative_tip_amount | Financial validity | WARN | 124 | 0 for valid trips |
| Q18_invalid_time_order | Temporal validity | WARN | 2051 | 0 for valid trips |
| Q19_excessive_trip_duration | Statistical anomaly | WARN | 20 | 0 trips over 24 hours |
| Q20_excessive_trip_distance | Statistical anomaly | WARN | 162 | 0 trips over 100 miles |
| Q21_null_passenger_count | Completeness | WARN | 540149 | 0 |
| Q22_null_fare_amount | Completeness | PASS | 0 | 0 |
| Q23_null_tip_amount | Completeness | PASS | 0 | 0 |
| Q24_null_source_file_metadata | Lineage | PASS | 0 | 0 |
| Q25_unmapped_pickup_borough | Geographic completeness | WARN | 9521 | Investigate unmapped pickup boroughs |

## Warnings and Failures

| Check | Category | Status | Actual Value |
|---|---|---|---:|
| Q14_zero_distance_records | Validity | WARN | 90893 |
| Q15_negative_total_amount | Financial validity | WARN | 63037 |
| Q16_negative_fare_amount | Financial validity | WARN | 144118 |
| Q17_negative_tip_amount | Financial validity | WARN | 124 |
| Q18_invalid_time_order | Temporal validity | WARN | 2051 |
| Q19_excessive_trip_duration | Statistical anomaly | WARN | 20 |
| Q20_excessive_trip_distance | Statistical anomaly | WARN | 162 |
| Q21_null_passenger_count | Completeness | WARN | 540149 |
| Q25_unmapped_pickup_borough | Geographic completeness | WARN | 9521 |

## Audit Outcome

**COMPLETED WITH WARNINGS:** No critical checks failed, but anomalies require monitoring.

## Interpretation

Warnings do not necessarily represent invalid records. They may indicate legitimate source-data conditions, unusual observations, or classification limitations.

This audit does not automatically remove or modify records.
