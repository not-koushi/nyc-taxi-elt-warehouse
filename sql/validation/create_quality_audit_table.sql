CREATE SCHEMA IF NOT EXISTS quality;

CREATE TABLE IF NOT EXISTS quality.audit_results (
    audit_id BIGSERIAL PRIMARY KEY,

    audit_run_id UUID NOT NULL,

    check_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,

    status VARCHAR(20) NOT NULL
        CHECK (status IN ('PASS', 'WARN', 'FAIL')),

    actual_value NUMERIC,
    expected_value VARCHAR(255),

    details TEXT,

    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quality_audit_run_id
    ON quality.audit_results(audit_run_id);

CREATE INDEX IF NOT EXISTS idx_quality_audit_executed_at
    ON quality.audit_results(executed_at);
