import csv
import io
import logging
import os
import uuid
from datetime import datetime, timezone

import psycopg2
import pyarrow.parquet as pq
from dotenv import load_dotenv

from ingestion.validation import (
    validate_source_file,
    validate_batch,
    validate_loaded_rows,
)

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

DATA_FILE = "data/raw/yellow_tripdata_2025-01.parquet"
SOURCE_MONTH = "2025-01-01"
BATCH_SIZE = 100_000

SOURCE_FILE = os.path.basename(DATA_FILE)

DB_CONFIG = {
    "host": "localhost",
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


def create_batch_buffer(batch, source_file, ingested_at, batch_id):
    """
    Convert one Arrow batch into a CSV buffer
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
            SOURCE_MONTH,
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


def load_batch(cursor, batch, source_file, ingested_at, batch_id):

    buffer = create_batch_buffer(
        batch=batch,
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
# PIPELINE
# --------------------------------------------------

def main():

    source_validation = validate_source_file(DATA_FILE)

    logger.info("Starting ingestion pipeline")
    logger.info("Source file: %s", SOURCE_FILE)

    parquet_file = pq.ParquetFile(DATA_FILE)

    total_rows = source_validation["row_count"]
    total_loaded = 0
    total_batches = 0

    ingestion_id = str(uuid.uuid4())
    batch_id = str(uuid.uuid4())

    started_at = datetime.now(timezone.utc)
    ingested_at = started_at.isoformat()

    connection = psycopg2.connect(**DB_CONFIG)

    try:

        with connection.cursor() as cursor:

            # --------------------------------------------------
            # IDEMPOTENCY CHECK
            # --------------------------------------------------

            if file_already_ingested(cursor, SOURCE_FILE):

                logger.info(
                    "Source file has already been successfully ingested."
                )

                logger.info("Skipping ingestion.")
                return

            # --------------------------------------------------
            # TRANSACTION START
            # --------------------------------------------------

            logger.info(
                "Beginning transaction for source file."
            )

            # The first implementation loaded this file without
            # a tracking entry. Remove those legacy rows as part
            # of this transaction before performing the new load.
            logger.info(
                "Removing existing rows for this source file, if any."
            )

            delete_previous_source_data(cursor, SOURCE_FILE)

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
                    SOURCE_FILE,
                    SOURCE_MONTH,
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
                    source_file=SOURCE_FILE,
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
            # MARK SUCCESS
            # --------------------------------------------------

            validate_loaded_rows(
                source_rows=total_rows,
                loaded_rows=total_loaded,
            )

            completed_at = datetime.now(timezone.utc)

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

        # Commit the data and tracking record together.
        connection.commit()

        logger.info("----------------------------------")
        logger.info("INGESTION SUCCESSFUL")
        logger.info("Rows loaded: %s", total_loaded)
        logger.info("Batches loaded: %s", total_batches)
        logger.info("Ingestion ID: %s", ingestion_id)
        logger.info("Batch ID: %s", batch_id)
        logger.info("----------------------------------")

    except Exception as error:

        # Roll back the data and RUNNING record together.
        connection.rollback()

        logger.exception("Ingestion failed.")

        # Record failure independently, outside the rolled-back
        # transaction, so failure information is preserved.
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
                        SOURCE_FILE,
                        SOURCE_MONTH,
                        started_at,
                        datetime.now(timezone.utc),
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
# ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()
