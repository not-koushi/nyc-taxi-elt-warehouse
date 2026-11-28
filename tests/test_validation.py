import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from ingestion.validation import (
    EXPECTED_COLUMNS,
    validate_batch,
    validate_loaded_rows,
    validate_source_file,
)

# --------------------------------------------------
# TEST: VALID PARQUET FILE
# --------------------------------------------------

def test_valid_parquet_file_passes(tmp_path):

    file_path = tmp_path / "valid.parquet"

    columns = {
        column: [1, 2]
        for column in EXPECTED_COLUMNS
    }

    table = pa.table(columns)

    pq.write_table(table, file_path)

    result = validate_source_file(file_path)

    assert result["row_count"] == 2
    assert result["columns"] == EXPECTED_COLUMNS
    assert result["file_size_bytes"] > 0


# --------------------------------------------------
# TEST: MISSING FILE
# --------------------------------------------------

def test_missing_file_raises_error(tmp_path):

    file_path = tmp_path / "missing.parquet"

    with pytest.raises(FileNotFoundError):
        validate_source_file(file_path)


# --------------------------------------------------
# TEST: EMPTY FILE
# --------------------------------------------------

def test_empty_file_raises_error(tmp_path):

    file_path = tmp_path / "empty.parquet"

    file_path.write_bytes(b"")

    with pytest.raises(ValueError):
        validate_source_file(file_path)


# --------------------------------------------------
# TEST: MISSING REQUIRED COLUMN
# --------------------------------------------------

def test_missing_required_column_raises_error(tmp_path):

    file_path = tmp_path / "missing_column.parquet"

    columns = {
        column: [1]
        for column in EXPECTED_COLUMNS
    }

    columns.pop("trip_distance")

    table = pa.table(columns)

    pq.write_table(table, file_path)

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_source_file(file_path)


# --------------------------------------------------
# TEST: ZERO ROW PARQUET
# --------------------------------------------------

def test_zero_row_parquet_raises_error(tmp_path):

    file_path = tmp_path / "zero_rows.parquet"

    columns = {
        column: pa.array([], type=pa.int64())
        for column in EXPECTED_COLUMNS
    }

    table = pa.table(columns)

    pq.write_table(table, file_path)

    with pytest.raises(ValueError, match="zero rows"):
        validate_source_file(file_path)


# --------------------------------------------------
# TEST: EMPTY BATCH
# --------------------------------------------------

def test_empty_batch_raises_error():

    batch = pa.record_batch(
        [pa.array([], type=pa.int64())],
        names=["test_column"],
    )

    with pytest.raises(ValueError, match="empty batch"):
        validate_batch(batch)


# --------------------------------------------------
# TEST: VALID BATCH
# --------------------------------------------------

def test_valid_batch_passes():

    batch = pa.record_batch(
        [pa.array([1, 2, 3])],
        names=["test_column"],
    )

    assert validate_batch(batch) is True


# --------------------------------------------------
# TEST: ROW COUNT MISMATCH
# --------------------------------------------------

def test_row_count_mismatch_raises_error():

    with pytest.raises(ValueError, match="Row-count mismatch"):
        validate_loaded_rows(
            source_rows=100,
            loaded_rows=95,
        )


# --------------------------------------------------
# TEST: MATCHING ROW COUNTS
# --------------------------------------------------

def test_matching_row_counts_pass():

    assert validate_loaded_rows(
        source_rows=100,
        loaded_rows=100,
    ) is True
