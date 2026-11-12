-- RIGHTWARE SI WORK-03B R2 R1B: append-only verification LAB, no DONE.
-- Must run after 0001..0006. Project/evidence scope is enforced by composite FKs.
-- Operator-seeded pinned policies only. No untrusted caller policy writes.
BEGIN;

ALTER TABLE si_evidence_refs
    ADD CONSTRAINT uq_si_evidence_refs_scope UNIQUE(project_id,task_id,id);

CREATE TABLE si_evidence_verification_policies (
    id UUID PRIMARY KEY,
    project_id TEXT NOT NULL,
    task_id UUID NOT NULL,
    evidence_id UUID NOT NULL,
    policy_version INTEGER NOT NULL CHECK (policy_version>0),
    criteria_index INTEGER NOT NULL CHECK (criteria_index BETWEEN 0 AND 29),
    repository_owner TEXT NOT NULL CHECK (length(repository_owner) BETWEEN 1 AND 100),
    repository_name TEXT NOT NULL CHECK (length(repository_name) BETWEEN 1 AND 100),
    repository_id BIGINT NOT NULL CHECK (repository_id>0),
    workflow_id BIGINT NOT NULL CHECK (workflow_id>0),
    run_id BIGINT NOT NULL CHECK (run_id>0),
    run_attempt INTEGER NOT NULL CHECK (run_attempt>0),
    expected_sha CHAR(40) NOT NULL CHECK (expected_sha ~ '^[a-f0-9]{40}$'),
    expected_event TEXT NOT NULL CHECK (expected_event IN ('push','pull_request','workflow_dispatch')),
    created_by TEXT NOT NULL REFERENCES si_principals(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (project_id,task_id,evidence_id)
      REFERENCES si_evidence_refs(project_id,task_id,id),
    UNIQUE (project_id,task_id,evidence_id,id),
    UNIQUE (project_id,evidence_id,policy_version)
);
CREATE INDEX ix_si_verification_policies_scope
  ON si_evidence_verification_policies(project_id,task_id,evidence_id);

CREATE TABLE si_verification_attempts (
    id UUID PRIMARY KEY,
    project_id TEXT NOT NULL,
    task_id UUID NOT NULL,
    evidence_id UUID NOT NULL,
    policy_id UUID NOT NULL,
    policy_version INTEGER NOT NULL CHECK(policy_version>0),
    criteria_index INTEGER NOT NULL CHECK(criteria_index BETWEEN 0 AND 29),
    task_version_checked INTEGER NOT NULL CHECK(task_version_checked>0),
    verified_by TEXT NOT NULL REFERENCES si_principals(id),
    idempotency_key TEXT NOT NULL CHECK(length(idempotency_key) BETWEEN 8 AND 128),
    result TEXT NOT NULL CHECK(result IN ('CHECKED_PASS','CHECKED_FAIL','INCONCLUSIVE')),
    reason_code TEXT NOT NULL CHECK(reason_code ~ '^[A-Z0-9_]{3,100}$'),
    source_kind TEXT NOT NULL DEFAULT 'GITHUB_WORKFLOW_RUN'
      CHECK(source_kind='GITHUB_WORKFLOW_RUN'),
    observation_channel TEXT NOT NULL CHECK(observation_channel IN ('LIVE_HTTPS','SIMULATED_TRANSPORT')),
    provider_run_id BIGINT,
    provider_repository_id BIGINT,
    provider_workflow_id BIGINT,
    provider_attempt INTEGER,
    provider_head_sha CHAR(40),
    observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (provider_run_id IS NULL OR provider_run_id>0),
    CHECK (provider_repository_id IS NULL OR provider_repository_id>0),
    CHECK (provider_workflow_id IS NULL OR provider_workflow_id>0),
    CHECK (provider_attempt IS NULL OR provider_attempt>0),
    CHECK (provider_head_sha IS NULL OR provider_head_sha ~ '^[a-f0-9]{40}$'),
    FOREIGN KEY (project_id,task_id,evidence_id)
      REFERENCES si_evidence_refs(project_id,task_id,id),
    FOREIGN KEY (project_id,task_id,evidence_id,policy_id)
      REFERENCES si_evidence_verification_policies(project_id,task_id,evidence_id,id),
    UNIQUE (project_id,verified_by,idempotency_key)
);
CREATE INDEX ix_si_verification_attempts_task
  ON si_verification_attempts(project_id,task_id,evidence_id,observed_at,id);

CREATE FUNCTION si_r2_guard_append_only() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'verification policy and attempt records are immutable'
      USING ERRCODE='23514';
END;
$$;

CREATE TRIGGER trg_si_r2_policies_immutable
BEFORE UPDATE OR DELETE ON si_evidence_verification_policies
FOR EACH ROW EXECUTE FUNCTION si_r2_guard_append_only();

CREATE TRIGGER trg_si_r2_attempts_immutable
BEFORE UPDATE OR DELETE ON si_verification_attempts
FOR EACH ROW EXECUTE FUNCTION si_r2_guard_append_only();

ALTER TABLE si_continuity_events
    DROP CONSTRAINT si_continuity_events_event_type_check;
ALTER TABLE si_continuity_events
    ADD CONSTRAINT si_continuity_events_event_type_check
    CHECK (event_type IN ('AGENT_RUN_STARTED','SOURCE_REGISTERED',
      'OBSERVATION_ASSERTED','CHECKPOINT_RECORDED','LEASE_REKEYED',
      'EVIDENCE_CHECKED'));

COMMIT;
