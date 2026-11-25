# Warehouse Architecture

## Database

PostgreSQL

Database name: taxi_warehouse

## Schema Layers

### raw

Stores source data as ingested.

Responsibilities:

- Preserve source records.
- Record ingestion metadata.
- Support reprocessing.
- Avoid destructive transformations.

### staging

Stores cleaned and standardized data.

Responsibilities:

- Standardize column names.
- Normalize data types.
- Handle invalid and null values.
- Apply basic cleaning logic.

### mart

Stores analytical data.

Responsibilities:

- Dimensional modelling.
- Fact and dimension tables.
- Business-oriented metrics.
- Support dashboard queries.

## Database Roles

### taxi_admin

Administrative database role.

### taxi_ingest

Responsible for writing ingestion data
into the raw schema.

### taxi_transform

Responsible for reading raw data
and building staging and mart models.

### taxi_analytics

Read-only analytical access to mart data.

## Data Flow

Public NYC Taxi Data
    |
    v
Python Ingestion
    |
    v
raw
    |
    v
staging
    |
    v
mart
    |
    v
Metabase
