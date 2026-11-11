-- WORK-02B: high-entropy API credentials bound to existing principals.
-- Run after 0001_work02_core.sql, in a dedicated PostgreSQL database.
-- API credentials are never created automatically on app startup.
BEGIN;
CREATE TABLE IF NOT EXISTS si_api_tokens (
    id UUID PRIMARY KEY,
    principal_id TEXT NOT NULL REFERENCES si_principals(id) ON DELETE CASCADE,
    secret_sha256 CHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (expires_at > issued_at)
);
CREATE INDEX IF NOT EXISTS ix_si_api_tokens_principal
  ON si_api_tokens (principal_id) WHERE revoked_at IS NULL;
COMMIT;
