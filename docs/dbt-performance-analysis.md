# dbt Performance Analysis

## Environment

- Warehouse: PostgreSQL 16
- Transformation framework: dbt
- Adapter: dbt-postgres
- Dataset: January 2025 NYC Yellow Taxi data
- Records: 3,475,226

## Rebuild Performance

| Model | Materialization | Execution |
|---|---|---:|
| dim_payment_type | Table | 0.17 sec |
| dim_rate_code | Table | 0.17 sec |
| dim_taxi_zone | Table | 0.16 sec |
| dim_vendor | Table | 0.17 sec |
| stg_yellow_taxi_trips | View | 0.05 sec |
| int_yellow_taxi_trips | View | 0.03 sec |
| dim_date | Table | 1.09 sec |
| fact_trips | Table | 12.51 sec |

Full dbt rebuild: 13.98 seconds.

## Storage

- fact_trips: 835 MB
- Fact table indexes: None

## Query Performance

| Query | Execution |
|---|---:|
| Borough aggregation | 794.921 ms |
| Monthly aggregation | 781.333 ms |

## Execution Plan Findings

- PostgreSQL used parallel sequential scans on fact_trips.
- PostgreSQL used hash joins against small dimensions.
- Partial hash aggregations were executed in parallel.
- Final aggregation and sorting were performed after parallel workers completed.
- Sequential scans were appropriate for queries that processed most of the fact table.

## Optimization Decisions

- Retained staging and intermediate views.
- Retained dimension and fact table materializations.
- Did not introduce indexes because no measured workload justified them.
- Did not introduce partitioning for a single-month dataset.
- Deferred incremental fact processing to a later architectural phase.

## Known Limitation

The fact table currently uses ROW_NUMBER() for trip_key generation.

This key is unique in the current rebuild but is not guaranteed to remain stable across future rebuilds, especially when records are inserted or ordering ties occur.

A stable record identification strategy will be evaluated during incremental pipeline development.

## Conclusion

The current warehouse performs well for the available dataset.

The fact table rebuild completed in approximately 12.51 seconds, while the tested analytical queries completed in approximately 0.8 seconds.

No additional performance optimizations were introduced because the measured execution plans demonstrated appropriate PostgreSQL execution strategies.
