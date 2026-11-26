from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


PROJECT_DIR = "/opt/airflow/project"


with DAG(
    dag_id="nyc_taxi_elt_pipeline",
    description="End-to-end NYC Taxi ELT pipeline with ingestion, dbt and quality auditing",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["nyc-taxi", "elt", "dbt", "data-quality"],
) as dag:

    ingest_data = BashOperator(
        task_id="ingest_yellow_taxi_data",
        bash_command="PYTHONPATH=/opt/airflow/project python ingestion/load_yellow_taxi.py",
        cwd=PROJECT_DIR,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="/opt/dbt-venv/bin/dbt run",
        cwd=f"{PROJECT_DIR}/dbt",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="/opt/dbt-venv/bin/dbt test",
        cwd=f"{PROJECT_DIR}/dbt",
    )

    quality_audit = BashOperator(
        task_id="run_quality_audit",
        bash_command="PYTHONPATH=/opt/airflow/project python scripts/quality/run_quality_audit.py",
        cwd=PROJECT_DIR,
    )

    quality_report = BashOperator(
        task_id="generate_quality_report",
        bash_command="PYTHONPATH=/opt/airflow/project python scripts/quality/generate_quality_report.py",
        cwd=PROJECT_DIR,
    )

    ingest_data >> dbt_run >> dbt_test >> quality_audit >> quality_report
