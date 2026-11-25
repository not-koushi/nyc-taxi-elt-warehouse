import logging
from pathlib import Path

import pyarrow.parquet as pq


logger = logging.getLogger(__name__)


EXPECTED_COLUMNS = {
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
}


def validate_source_file(file_path):
    """
    Validate the source Parquet file before ingestion.

    Checks:
    - File exists
    - File is not empty
    - File is readable as Parquet
    - Contains records
    - Contains expected columns
    """

    file_path = Path(file_path)

    logger.info("Validating source file: %s", file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Source file does not exist: {file_path}"
        )

    if file_path.stat().st_size == 0:
        raise ValueError("Source file is empty.")

    parquet_file = pq.ParquetFile(file_path)

    source_columns = set(parquet_file.schema.names)
    row_count = parquet_file.metadata.num_rows

    if row_count == 0:
        raise ValueError("Parquet file contains zero rows.")

    missing_columns = EXPECTED_COLUMNS - source_columns
    unexpected_columns = source_columns - EXPECTED_COLUMNS

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if unexpected_columns:
        logger.warning(
            "Unexpected source columns detected: %s",
            sorted(unexpected_columns),
        )

    logger.info("Source file validation passed.")
    logger.info("Rows detected: %s", row_count)
    logger.info("Columns detected: %s", len(source_columns))

    return {
        "row_count": row_count,
        "columns": source_columns,
        "file_size_bytes": file_path.stat().st_size,
    }


def validate_batch(batch):

    if batch is None:
        raise ValueError("Received a null batch.")

    if batch.num_rows == 0:
        raise ValueError("Received an empty batch.")

    logger.debug(
        "Batch validation passed: %s rows",
        batch.num_rows,
    )

    return True


def validate_loaded_rows(source_rows, loaded_rows):

    if source_rows != loaded_rows:

        raise ValueError(
            "Row-count mismatch: "
            f"source={source_rows}, loaded={loaded_rows}"
        )

    logger.info(
        "Row-count validation passed: %s rows",
        loaded_rows,
    )

    return True
