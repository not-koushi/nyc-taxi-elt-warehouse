
import pytest

from ingestion.load_yellow_taxi import (
    discover_source_files,
    extract_source_month,
)

# --------------------------------------------------
# SOURCE MONTH PARSING
# --------------------------------------------------

@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("yellow_tripdata_2025-01.parquet", "2025-01-01"),
        ("yellow_tripdata_2025-02.parquet", "2025-02-01"),
        ("yellow_tripdata_2024-12.parquet", "2024-12-01"),
        ("yellow_tripdata_2030-11.parquet", "2030-11-01"),
    ],
)
def test_extract_source_month_valid(filename, expected):

    assert extract_source_month(filename) == expected


@pytest.mark.parametrize(
    "filename",
    [
        "yellow_tripdata_2025-13.parquet",
        "yellow_tripdata_2025-00.parquet",
        "yellow_tripdata_2025-1.parquet",
        "yellow_tripdata_2025.parquet",
        "green_tripdata_2025-01.parquet",
        "yellow_tripdata_2025-01.csv",
        "random_file.parquet",
    ],
)
def test_extract_source_month_invalid(filename):

    with pytest.raises(ValueError):
        extract_source_month(filename)


# --------------------------------------------------
# FILE DISCOVERY
# --------------------------------------------------

def test_discover_source_files_returns_sorted_files(tmp_path):

    filenames = [
        "yellow_tripdata_2025-03.parquet",
        "yellow_tripdata_2025-01.parquet",
        "yellow_tripdata_2025-02.parquet",
    ]

    for filename in filenames:
        (tmp_path / filename).touch()

    discovered = discover_source_files(tmp_path)

    assert [file.name for file in discovered] == [
        "yellow_tripdata_2025-01.parquet",
        "yellow_tripdata_2025-02.parquet",
        "yellow_tripdata_2025-03.parquet",
    ]


def test_discover_source_files_ignores_other_files(tmp_path):

    (tmp_path / "yellow_tripdata_2025-01.parquet").touch()
    (tmp_path / "notes.txt").touch()
    (tmp_path / "other.parquet").touch()

    discovered = discover_source_files(tmp_path)

    assert [file.name for file in discovered] == [
        "yellow_tripdata_2025-01.parquet",
    ]


def test_discover_source_files_rejects_invalid_matching_filename(
    tmp_path,
):

    (tmp_path / "yellow_tripdata_2025-13.parquet").touch()

    with pytest.raises(ValueError):
        discover_source_files(tmp_path)


def test_discover_source_files_empty_directory(tmp_path):

    assert discover_source_files(tmp_path) == []


def test_discover_source_files_missing_directory(tmp_path):

    missing_directory = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        discover_source_files(missing_directory)
