# Data Quality Framework

## Objective

The data quality framework independently evaluates the integrity,
completeness, consistency and validity of the NYC Taxi Analytics Warehouse.

The framework supplements dbt model tests by measuring operational
data-quality conditions and persisting audit results.

## Architecture

The framework consists of:

- Python audit runner
- PostgreSQL quality schema
- Persistent audit results table
- SQL-based quality checks
- JSON audit reports

## Audit categories

### Completeness

Measures the presence of required attributes and records.

### Referential integrity

Measures missing warehouse dimension keys.

### Uniqueness

Identifies duplicate trip fingerprints.

### Consistency

Validates the consistency of quality flags and calculations.

### Validity

Identifies suspicious or invalid numeric values.

### Temporal validity

Evaluates chronological trip timestamps.

### Statistical anomaly detection

Identifies unusually long trips and excessive distances.

## Audit checks

| Check | Category |
|---|---|
| Q01 | Fact row count |
| Q02 | Null pickup datetime |
| Q03 | Null dropoff datetime |
| Q04 | Null trip distance |
| Q05 | Null total amount |
| Q06 | Null vendor key |
| Q07 | Null pickup zone key |
| Q08 | Null dropoff zone key |
| Q09 | Null payment key |
| Q10 | Null rate-code key |
| Q11 | Duplicate trip fingerprints |
| Q12 | Duration flag consistency |
| Q13 | Overall quality flag consistency |
| Q14 | Zero distance |
| Q15 | Negative total amount |
| Q16 | Negative fare amount |
| Q17 | Negative tip amount |
| Q18 | Invalid time ordering |
| Q19 | Excessive trip duration |
| Q20 | Excessive trip distance |
| Q21 | Null passenger count |
| Q22 | Null fare amount |
| Q23 | Null tip amount |
| Q24 | Null source file metadata |
| Q25 | Unmapped pickup borough |

## Status definitions

- PASS: The check satisfies its defined expectation.
- WARN: The check detected an anomaly that requires investigation.
- FAIL: The check violates a critical data-quality expectation.

Warnings do not automatically imply incorrect data.

## Execution

Run the audit from the repository root:

    python scripts/quality/run_quality_audit.py

The runner executes SQL checks, persists results in
quality.audit_results, and generates a JSON report.

## Audit history

Every execution receives a unique audit_run_id.

This permits historical comparisons across audit executions
and supports future monitoring through orchestration.

## Limitations

- Duplicate detection uses a composite fingerprint and may identify
  legitimate identical trips as duplicates.
- Statistical thresholds are initial heuristics.
- Negative amounts and zero distances may represent legitimate
  taxi records.
- The framework does not currently remediate records.
- Audit results measure the current warehouse state.

## Quality Scorecard

A Markdown scorecard is generated from the latest audit JSON report.

The scorecard contains:

- Audit run ID
- Execution timestamp
- Total checks
- PASS, WARN and FAIL counts
- Check-health score
- Detailed check results
- Warnings and failures
- Audit outcome

### Check-health score

The score uses the following check-level weighting:

- PASS: 1.0
- WARN: 0.5
- FAIL: 0.0

The score is calculated as:

    ((PASS + 0.5 * WARN) / TOTAL CHECKS) * 100

This is a check-level monitoring indicator.
It does not represent the percentage of valid records.

### Report generation

Generate the Markdown report using:

    python scripts/quality/generate_quality_report.py

The generator creates:

- A run-specific Markdown report
- latest_report.md

Reports are stored under reports/quality/.
