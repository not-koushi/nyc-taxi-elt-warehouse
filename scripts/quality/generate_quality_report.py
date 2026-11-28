#!/usr/bin/env python3

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT_DIR / "reports" / "quality"

reports = sorted(
    REPORT_DIR.glob("audit_*.json"),
    key=lambda p: p.stat().st_mtime,
)

if not reports:
    raise SystemExit("No audit JSON reports found.")

latest_report = reports[-1]

with open(latest_report, "r", encoding="utf-8") as file:
    audit = json.load(file)

results = audit["results"]

total = len(results)
passed = sum(r["status"] == "PASS" for r in results)
warned = sum(r["status"] == "WARN" for r in results)
failed = sum(r["status"] == "FAIL" for r in results)

score = (
    ((passed + 0.5 * warned) / total) * 100
    if total else 0
)

run_id = audit["audit_run_id"]

lines = [
    "# Data Quality Audit Report",
    "",
    f"**Audit Run ID:** `{run_id}`",
    "",
    f"**Execution time:** {audit.get('executed_at', 'Not available')}",
    "",
    "## Scorecard",
    "",
    "| Metric | Result |",
    "|---|---:|",
    f"| Total checks | {total} |",
    f"| PASS | {passed} |",
    f"| WARN | {warned} |",
    f"| FAIL | {failed} |",
    f"| Check-health score | {score:.2f}% |",
    "",
    "### Score calculation",
    "",
    "- PASS = 1 point",
    "- WARN = 0.5 points",
    "- FAIL = 0 points",
    "",
    ("This is a check-level monitoring score, not a measure of "
    "the percentage of individual records that are valid."),
    "",
    "## Detailed Results",
    "",
    "| Check | Category | Status | Actual Value | Expected |",
    "|---|---|---|---:|---|",
]

for result in results:

    lines.append(
        "| "
        + str(result["check_name"])
        + " | "
        + str(result["category"])
        + " | "
        + str(result["status"])
        + " | "
        + str(result["actual_value"])
        + " | "
        + str(result["expected_value"])
        + " |"
    )

lines.extend([
    "",
    "## Warnings and Failures",
    "",
])

issues = [
    r for r in results
    if r["status"] in ("WARN", "FAIL")
]

if issues:

    lines.extend([
        "| Check | Category | Status | Actual Value |",
        "|---|---|---|---:|",
    ])

    for result in issues:

        lines.append(
            "| "
            + str(result["check_name"])
            + " | "
            + str(result["category"])
            + " | "
            + str(result["status"])
            + " | "
            + str(result["actual_value"])
            + " |"
        )

else:

    lines.append("No warnings or failures detected.")

lines.extend([
    "",
    "## Audit Outcome",
    "",
])

if failed:

    lines.append(
        "**FAILED:** Critical quality checks were not satisfied."
    )

elif warned:

    lines.append(
        "**COMPLETED WITH WARNINGS:** "
        "No critical checks failed, but anomalies require monitoring."
    )

else:

    lines.append(
        "**PASS:** All quality checks satisfied their expectations."
    )

lines.extend([
    "",
    "## Interpretation",
    "",
    ("Warnings do not necessarily represent invalid records. "
    "They may indicate legitimate source-data conditions, "
    "unusual observations, or classification limitations."),
    "",
    "This audit does not automatically remove or modify records.",
    "",
])

report_text = "\n".join(lines)

report_file = REPORT_DIR / f"report_{run_id}.md"

with open(report_file, "w", encoding="utf-8") as file:
    file.write(report_text)

latest_file = REPORT_DIR / "latest_report.md"

with open(latest_file, "w", encoding="utf-8") as file:
    file.write(report_text)

print("=" * 60)
print("DATA QUALITY SCORECARD")
print("=" * 60)
print(f"Audit Run ID : {run_id}")
print(f"Total checks : {total}")
print(f"PASS         : {passed}")
print(f"WARN         : {warned}")
print(f"FAIL         : {failed}")
print(f"Health score : {score:.2f}%")
print()
print(f"Report       : {report_file}")
print(f"Latest       : {latest_file}")
