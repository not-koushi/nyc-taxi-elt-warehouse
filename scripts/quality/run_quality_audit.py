#!/usr/bin/env python3

import os
import sys
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor


ROOT_DIR = Path(__file__).resolve().parents[2]

REPORT_DIR = ROOT_DIR / "reports" / "quality"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

AUDIT_RUN_ID = str(uuid.uuid4())


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "taxi_warehouse"),
        user=os.getenv("DB_USER", "taxi_admin"),
        password=os.getenv("DB_PASSWORD"),
    )


CHECKS = [

    {
        "name": "Q01_fact_row_count",
        "category": "Completeness",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
        """,
        "severity": "WARN",
        "expected": "Greater than zero",
        "evaluate": lambda v: "PASS" if v > 0 else "FAIL",
    },

    {
        "name": "Q02_null_pickup_datetime",
        "category": "Completeness",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE pickup_datetime IS NULL
        """,
        "severity": "FAIL",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "FAIL",
    },

    {
        "name": "Q03_null_dropoff_datetime",
        "category": "Completeness",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE dropoff_datetime IS NULL
        """,
        "severity": "FAIL",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "FAIL",
    },

    {
        "name": "Q04_null_trip_distance",
        "category": "Completeness",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE trip_distance IS NULL
        """,
        "severity": "FAIL",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "FAIL",
    },

    {
        "name": "Q05_null_total_amount",
        "category": "Completeness",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE total_amount IS NULL
        """,
        "severity": "WARN",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "WARN",
    },

    {
        "name": "Q06_null_vendor_keys",
        "category": "Referential integrity",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE vendor_key IS NULL
        """,
        "severity": "FAIL",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "FAIL",
    },

    {
        "name": "Q07_null_pickup_zone_keys",
        "category": "Referential integrity",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE pickup_zone_key IS NULL
        """,
        "severity": "FAIL",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "FAIL",
    },

    {
        "name": "Q08_null_dropoff_zone_keys",
        "category": "Referential integrity",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE dropoff_zone_key IS NULL
        """,
        "severity": "FAIL",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "FAIL",
    },

    {
        "name": "Q09_null_payment_keys",
        "category": "Referential integrity",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE payment_type_key IS NULL
        """,
        "severity": "FAIL",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "FAIL",
    },

    {
        "name": "Q10_null_rate_code_keys",
        "category": "Referential integrity",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE rate_code_key IS NULL
        """,
        "severity": "FAIL",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "FAIL",
    },

    {
        "name": "Q11_duplicate_trip_fingerprints",
        "category": "Uniqueness",
        "sql": """
            SELECT COALESCE(SUM(duplicate_count -1), 0)
            FROM (
                SELECT COUNT(*) AS duplicate_count
                FROM mart.fact_trips
                GROUP BY
                    pickup_datetime,
                    dropoff_datetime,
                    vendor_key,
                    pickup_zone_key,
                    dropoff_zone_key,
                    passenger_count,
                    trip_distance,
                    total_amount
                HAVING COUNT(*) > 1
            ) duplicates
        """,
        "severity": "WARN",
        "expected": "0 duplicate groups",
        "evaluate": lambda v: "PASS" if v == 0 else "WARN",
    },

    {
        "name": "Q12_invalid_duration_flag_consistency",
        "category": "Consistency",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE
                is_valid_trip_time <>
                (pickup_datetime < dropoff_datetime)
        """,
        "severity": "FAIL",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "FAIL",
    },

    {
        "name": "Q13_overall_quality_flag_consistency",
        "category": "Consistency",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE
                is_valid_trip_record <>
                (
                    is_valid_trip_time
                    AND is_valid_trip_distance
                    AND is_nonnegative_total_amount
                )
        """,
        "severity": "FAIL",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "FAIL",
    },

    {
        "name": "Q14_zero_distance_records",
        "category": "Validity",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE trip_distance = 0
        """,
        "severity": "WARN",
        "expected": "0 for valid trips",
        "evaluate": lambda v: "PASS" if v == 0 else "WARN",
    },

    {
        "name": "Q15_negative_total_amount",
        "category": "Financial validity",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE total_amount < 0
        """,
        "severity": "WARN",
        "expected": "0 for valid trips",
        "evaluate": lambda v: "PASS" if v == 0 else "WARN",
    },

    {
        "name": "Q16_negative_fare_amount",
        "category": "Financial validity",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE fare_amount < 0
        """,
        "severity": "WARN",
        "expected": "0 for valid trips",
        "evaluate": lambda v: "PASS" if v == 0 else "WARN",
    },

    {
        "name": "Q17_negative_tip_amount",
        "category": "Financial validity",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE tip_amount < 0
        """,
        "severity": "WARN",
        "expected": "0 for valid trips",
        "evaluate": lambda v: "PASS" if v == 0 else "WARN",
    },

    {
        "name": "Q18_invalid_time_order",
        "category": "Temporal validity",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE pickup_datetime >= dropoff_datetime
        """,
        "severity": "WARN",
        "expected": "0 for valid trips",
        "evaluate": lambda v: "PASS" if v == 0 else "WARN",
    },

    {
        "name": "Q19_excessive_trip_duration",
        "category": "Statistical anomaly",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE trip_duration_minutes > 1440
        """,
        "severity": "WARN",
        "expected": "0 trips over 24 hours",
        "evaluate": lambda v: "PASS" if v == 0 else "WARN",
    },

    {
        "name": "Q20_excessive_trip_distance",
        "category": "Statistical anomaly",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE trip_distance > 100
        """,
        "severity": "WARN",
        "expected": "0 trips over 100 miles",
        "evaluate": lambda v: "PASS" if v == 0 else "WARN",
    },

    {
        "name": "Q21_null_passenger_count",
        "category": "Completeness",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE passenger_count IS NULL
        """,
        "severity": "WARN",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "WARN",
    },

    {
        "name": "Q22_null_fare_amount",
        "category": "Completeness",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE fare_amount IS NULL
        """,
        "severity": "WARN",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "WARN",
    },

    {
        "name": "Q23_null_tip_amount",
        "category": "Completeness",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE tip_amount IS NULL
        """,
        "severity": "WARN",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "WARN",
    },

    {
        "name": "Q24_null_source_file_metadata",
        "category": "Lineage",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips
            WHERE source_file IS NULL
        """,
        "severity": "FAIL",
        "expected": "0",
        "evaluate": lambda v: "PASS" if v == 0 else "FAIL",
    },

    {
        "name": "Q25_unmapped_pickup_borough",
        "category": "Geographic completeness",
        "sql": """
            SELECT COUNT(*)
            FROM mart.fact_trips AS fact
            JOIN mart.dim_taxi_zone AS zone
                ON fact.pickup_zone_key = zone.zone_key
            WHERE
                zone.borough IS NULL
                OR zone.borough IN ('Unknown', 'N/A')
        """,
        "severity": "WARN",
        "expected": "Investigate unmapped pickup boroughs",
        "evaluate": lambda v: "PASS" if v == 0 else "WARN",
    },

]


def run_audit():

    if not os.getenv("DB_PASSWORD"):
        print("ERROR: DB_PASSWORD environment variable is not set.")
        sys.exit(1)

    connection = get_connection()

    results = []

    try:

        with connection.cursor() as cursor:

            for check in CHECKS:

                cursor.execute(check["sql"])
                actual_value = cursor.fetchone()[0]

                status = check["evaluate"](actual_value)

                results.append({
                    "audit_run_id": AUDIT_RUN_ID,
                    "check_name": check["name"],
                    "category": check["category"],
                    "status": status,
                    "actual_value": actual_value,
                    "expected_value": check["expected"],
                })

                print(
                    f'{check["name"]:<45} '
                    f'{status:<6} '
                    f'{actual_value}'
                )

        with connection.cursor() as cursor:

            for result in results:

                cursor.execute(
                    """
                    INSERT INTO quality.audit_results (
                        audit_run_id,
                        check_name,
                        category,
                        status,
                        actual_value,
                        expected_value,
                        details
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        result["audit_run_id"],
                        result["check_name"],
                        result["category"],
                        result["status"],
                        result["actual_value"],
                        result["expected_value"],
                        None,
                    ),
                )

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()

    summary = {
        "audit_run_id": AUDIT_RUN_ID,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "total_checks": len(results),
        "pass": sum(r["status"] == "PASS" for r in results),
        "warn": sum(r["status"] == "WARN" for r in results),
        "fail": sum(r["status"] == "FAIL" for r in results),
        "results": results,
    }

    report_file = REPORT_DIR / f"audit_{AUDIT_RUN_ID}.json"

    with open(report_file, "w", encoding="utf-8") as file:

        json.dump(
            summary,
            file,
            indent=4,
            default=str,
        )

    print("\n" + "=" * 70)
    print("QUALITY AUDIT SUMMARY")
    print("=" * 70)

    print(f'Total checks : {summary["total_checks"]}')
    print(f'PASS         : {summary["pass"]}')
    print(f'WARN         : {summary["warn"]}')
    print(f'FAIL         : {summary["fail"]}')

    print(f"\nJSON report: {report_file}")

    if summary["fail"] > 0:

        print("\nAUDIT RESULT: FAILED")

        sys.exit(1)

    print("\nAUDIT RESULT: COMPLETED")


if __name__ == "__main__":
    run_audit()
