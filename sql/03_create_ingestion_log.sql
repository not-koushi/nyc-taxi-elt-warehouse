CREATE TABLE IF NOT EXISTS raw.ingestion_log (
    ingestion_id UUID PRIMARY KEY,
    source_file TEXT NOT NULL,
    source_month DATE NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    rows_loaded BIGINT DEFAULT 0,
    error_message TEXT,

    CONSTRAINT ingestion_status_check
        CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED'))
);
