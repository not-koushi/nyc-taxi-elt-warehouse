import csv
import io
import logging
import os
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path

import psycopg2
import pyarrow.parquet as pq
from dotenv import load_dotenv

from ingestion.validation import (
    validate_batch,
    validate_loaded_rows,
    validate_source_file,
)

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

DATA_DIR = Path("data/raw")
BATCH_SIZE = 100_000

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "taxi_warehouse"),
    "user": "taxi_ingest",
    "password": os.getenv("TAXI_INGEST_PASSWORD"),
}

SOURCE_COLUMNS = [
    "VendorID",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "RatecodeID",
    "store_and_fwd_flag",
    "PULocationID",
    "DOLocationID",
    "payment_type",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "Airport_fee",
    "cbd_congestion_fee",
]

# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# --------------------------------------------------
# SOURCE DISCOVERY
# --------------------------------------------------

def extract_source_month(source_file):
    """
    Extract the source month from a TLC Yellow Taxi filename.

    Expected format:
    yellow_tripdata_YYYY-MM.parquet
    """

    match = re.fullmatch(
        r"yellow_tripdata_(\d{4})-(\d{2})\.parquet",
        os.path.basename(str(source_file)),
    )

    if not match:
        raise ValueError(
            f"Invalid source filename format: {source_file}"
        )

    year, month = map(int, match.groups())

    if not 1 <= month <= 12:
        raise ValueError(
            f"Invalid source month in filename: {source_file}"
        )

    return f"{year:04d}-{month:02d}-01"


def discover_source_files(data_dir=DATA_DIR):
    """
    Discover monthly Yellow Taxi Parquet files.

    Files are returned in sorted order.
    """

    data_dir = Path(data_dir)

    if not data_dir.exists():
        raise FileNotFoundError(
            f"Source directory does not exist: {data_dir}"
        )

    files = sorted(
        data_dir.glob("yellow_tripdata_*.parquet")
    )

    # Validate filenames before processing.
    for file_path in files:
        extract_source_month(file_path.name)

    return files


# --------------------------------------------------
# DATA CONVERSION
# --------------------------------------------------

def convert_value(value):
    """
    Convert Arrow values into CSV-compatible values.

    PostgreSQL COPY uses \\N as the NULL marker.
    """

    if value is None:
        return r"\N"

    return str(value)


def create_batch_buffer(
    batch,
    source_month,
    source_file,
    ingested_at,
    batch_id,
):
    """
    Convert an Arrow batch into a CSV buffer
    suitable for PostgreSQL COPY.
    """

    buffer = io.StringIO()
    writer = csv.writer(buffer)

    batch_columns = batch.schema.names

    for row in batch.to_pylist():

        values = []

        for column in SOURCE_COLUMNS:

            if column in batch_columns:
                value = row.get(column)
            else:
                value = None

            values.append(convert_value(value))

        values.extend([
            source_month,
            source_file,
            ingested_at,
            batch_id,
        ])

        writer.writerow(values)

    buffer.seek(0)

    return buffer


# --------------------------------------------------
# DATABASE OPERATIONS
# --------------------------------------------------

def file_already_ingested(cursor, source_file):

    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM raw.ingestion_log
            WHERE source_file = %s
              AND status = 'SUCCESS'
        );
        """,
        (source_file,),
    )

    return cursor.fetchone()[0]


def delete_previous_source_data(cursor, source_file):

    cursor.execute(
        """
        DELETE FROM raw.yellow_taxi_trips
        WHERE source_file = %s;
        """,
        (source_file,),
    )


def load_batch(
    cursor,
    batch,
    source_month,
    source_file,
    ingested_at,
    batch_id,
):

    buffer = create_batch_buffer(
        batch=batch,
        source_month=source_month,
        source_file=source_file,
        ingested_at=ingested_at,
        batch_id=batch_id,
    )

    copy_sql = """
        COPY raw.yellow_taxi_trips (
            vendorid,
            tpep_pickup_datetime,
            tpep_dropoff_datetime,
            passenger_count,
            trip_distance,
            ratecodeid,
            store_and_fwd_flag,
            pulocationid,
            dolocationid,
            payment_type,
            fare_amount,
            extra,
            mta_tax,
            tip_amount,
            tolls_amount,
            improvement_surcharge,
            total_amount,
            congestion_surcharge,
            airport_fee,
            cbd_congestion_fee,
            source_month,
            source_file,
            ingested_at,
            batch_id
        )
        FROM STDIN
        WITH (
            FORMAT CSV,
            NULL '\\N'
        );
    """

    cursor.copy_expert(copy_sql, buffer)


# --------------------------------------------------
# SINGLE-FILE PIPELINE
# --------------------------------------------------

def load_file(data_file):

    data_file = Path(data_file)
    source_file = data_file.name
    source_month = extract_source_month(source_file)

    source_validation = validate_source_file(data_file)

    logger.info("----------------------------------")
    logger.info("Starting file ingestion")
    logger.info("Source file: %s", source_file)
    logger.info("Source month: %s", source_month)
    logger.info("Source rows: %s", source_validation["row_count"])
    logger.info("----------------------------------")

    parquet_file = pq.ParquetFile(data_file)

    total_rows = source_validation["row_count"]
    total_loaded = 0
    total_batches = 0

    ingestion_id = str(uuid.uuid4())
    batch_id = str(uuid.uuid4())

    started_at = datetime.now(UTC)
    ingested_at = started_at.isoformat()

    connection = psycopg2.connect(**DB_CONFIG)

    try:

        with connection.cursor() as cursor:

            # --------------------------------------------------
            # IDEMPOTENCY CHECK
            # --------------------------------------------------

            if file_already_ingested(cursor, source_file):

                logger.info(
                    "File already successfully ingested: %s",
                    source_file,
                )

                logger.info("Skipping file.")
                return "SKIPPED"

            # --------------------------------------------------
            # TRANSACTION START
            # --------------------------------------------------

            logger.info(
                "Beginning transaction for %s",
                source_file,
            )

            # Replace legacy or incomplete data for this file
            # inside the transaction.
            delete_previous_source_data(
                cursor,
                source_file,
            )

            # --------------------------------------------------
            # TRACKING RECORD
            # --------------------------------------------------

            cursor.execute(
                """
                INSERT INTO raw.ingestion_log (
                    ingestion_id,
                    source_file,
                    source_month,
                    started_at,
                    status,
                    rows_loaded
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    'RUNNING',
                    0
                );
                """,
                (
                    ingestion_id,
                    source_file,
                    source_month,
                    started_at,
                ),
            )

            # --------------------------------------------------
            # BATCH LOADING
            # --------------------------------------------------

            for batch in parquet_file.iter_batches(
                batch_size=BATCH_SIZE
            ):

                total_batches += 1

                validate_batch(batch)

                batch_rows = batch.num_rows

                logger.info(
                    "Loading batch %s: %s rows",
                    total_batches,
                    batch_rows,
                )

                load_batch(
                    cursor=cursor,
                    batch=batch,
                    source_month=source_month,
                    source_file=source_file,
                    ingested_at=ingested_at,
                    batch_id=batch_id,
                )

                total_loaded += batch_rows

                logger.info(
                    "Progress: %s / %s rows",
                    total_loaded,
                    total_rows,
                )

            # --------------------------------------------------
            # ROW COUNT VALIDATION
            # --------------------------------------------------

            validate_loaded_rows(
                source_rows=total_rows,
                loaded_rows=total_loaded,
            )

            # --------------------------------------------------
            # MARK SUCCESS
            # --------------------------------------------------

            completed_at = datetime.now(UTC)

            cursor.execute(
                """
                UPDATE raw.ingestion_log
                SET
                    completed_at = %s,
                    status = 'SUCCESS',
                    rows_loaded = %s,
                    error_message = NULL
                WHERE ingestion_id = %s;
                """,
                (
                    completed_at,
                    total_loaded,
                    ingestion_id,
                ),
            )

        # Data and successful tracking record
        # commit together.
        connection.commit()

        logger.info("----------------------------------")
        logger.info("INGESTION SUCCESSFUL")
        logger.info("Source file: %s", source_file)
        logger.info("Rows loaded: %s", total_loaded)
        logger.info("Batches loaded: %s", total_batches)
        logger.info("Ingestion ID: %s", ingestion_id)
        logger.info("Batch ID: %s", batch_id)
        logger.info("----------------------------------")

        return "SUCCESS"

    except Exception as error:

        # Roll back source data and RUNNING record.
        connection.rollback()

        logger.exception(
            "Ingestion failed for %s",
            source_file,
        )

        # Record failure independently.
        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO raw.ingestion_log (
                        ingestion_id,
                        source_file,
                        source_month,
                        started_at,
                        completed_at,
                        status,
                        rows_loaded,
                        error_message
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        'FAILED',
                        %s,
                        %s
                    );
                    """,
                    (
                        ingestion_id,
                        source_file,
                        source_month,
                        started_at,
                        datetime.now(UTC),
                        total_loaded,
                        str(error)[:4000],
                    ),
                )

            connection.commit()

        except Exception:

            connection.rollback()

            logger.exception(
                "Could not record the failure in ingestion_log."
            )

        raise

    finally:

        connection.close()


# --------------------------------------------------
# MULTI-FILE PIPELINE
# --------------------------------------------------

def main():

    source_files = discover_source_files(DATA_DIR)

    if not source_files:

        logger.warning(
            "No Yellow Taxi Parquet files found in %s",
            DATA_DIR,
        )

        return

    logger.info(
        "Discovered %s source file(s).",
        len(source_files),
    )

    results = {
        "SUCCESS": 0,
        "SKIPPED": 0,
        "FAILED": 0,
    }

    for data_file in source_files:

        logger.info(
            "Processing %s",
            data_file.name,
        )

        try:

            result = load_file(data_file)
            results[result] += 1

        except Exception:

            results["FAILED"] += 1

            logger.exception(
                "Failed to process file: %s",
                data_file.name,
            )

            # Continue processing other files.
            # A failed monthly file does not prevent
            # subsequent files from being processed.

    logger.info("----------------------------------")
    logger.info("MULTI-FILE INGESTION SUMMARY")
    logger.info("Successful: %s", results["SUCCESS"])
    logger.info("Skipped: %s", results["SKIPPED"])
    logger.info("Failed: %s", results["FAILED"])
    logger.info("----------------------------------")

    if results["FAILED"] > 0:
        raise RuntimeError(
            f"{results['FAILED']} source file(s) failed ingestion."
        )


# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()
