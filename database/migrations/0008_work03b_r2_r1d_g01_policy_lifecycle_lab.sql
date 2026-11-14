-- G01: synthetic lab-only policy lifecycle. Existing pinned policies remain immutable.
BEGIN;
CREATE TABLE si_policy_lifecycle_events (
 id UUID PRIMARY KEY,
 sequence BIGINT GENERATED ALWAYS AS IDENTITY UNIQUE,
 project_id TEXT NOT NULL, task_id UUID NOT NULL, evidence_id UUID NOT NULL,
 policy_id UUID NOT NULL, event_type TEXT NOT NULL
   CHECK(event_type IN ('PROPOSED','ACTIVATED','DISABLED','SUPERSEDED')),
 actor_id TEXT NOT NULL REFERENCES si_principals(id),
 idempotency_key TEXT NOT NULL CHECK(length(idempotency_key) BETWEEN 8 AND 128),
 valid_until TIMESTAMPTZ, successor_policy_id UUID, reason_code TEXT,
 recorded_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
 FOREIGN KEY(project_id,task_id,evidence_id,policy_id)
   REFERENCES si_evidence_verification_policies(project_id,task_id,evidence_id,id),
 UNIQUE(policy_id,event_type), UNIQUE(project_id,actor_id,idempotency_key),
 CHECK((event_type='ACTIVATED' AND valid_until IS NOT NULL AND reason_code IS NULL AND successor_policy_id IS NULL)
 OR (event_type='PROPOSED' AND valid_until IS NULL AND reason_code IS NULL AND successor_policy_id IS NULL)
 OR (event_type='DISABLED' AND valid_until IS NULL AND successor_policy_id IS NULL AND reason_code ~ '^[A-Z0-9_]{3,64}$')
 OR (event_type='SUPERSEDED' AND valid_until IS NULL AND reason_code IS NULL AND successor_policy_id IS NOT NULL))
);
CREATE INDEX ix_si_policy_events_scope ON si_policy_lifecycle_events(project_id,policy_id,sequence);
CREATE UNIQUE INDEX uq_si_policy_terminal ON si_policy_lifecycle_events(policy_id)
 WHERE event_type IN ('DISABLED','SUPERSEDED');
CREATE TRIGGER trg_si_policy_lifecycle_immutable
 BEFORE UPDATE OR DELETE ON si_policy_lifecycle_events
 FOR EACH ROW EXECUTE FUNCTION si_r2_guard_append_only();
COMMIT;
