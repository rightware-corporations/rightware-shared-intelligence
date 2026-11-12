-- WORK-03B R1B: immutable source-linked task checkpoint for scoped read-only resume.
-- Lab-only additive migration; retains all WORK-02A/02D/R1A task/lease semantics.
BEGIN;

CREATE TABLE si_task_checkpoints (
    id UUID PRIMARY KEY,
    project_id TEXT NOT NULL,
    task_id UUID NOT NULL,
    agent_run_id UUID NOT NULL,
    recorded_by TEXT NOT NULL REFERENCES si_principals(id),
    checkpoint_seq INTEGER NOT NULL CHECK (checkpoint_seq > 0),
    task_version_recorded INTEGER NOT NULL CHECK (task_version_recorded > 0),
    summary TEXT NOT NULL CHECK (length(summary) BETWEEN 1 AND 2000),
    next_actions JSONB NOT NULL CHECK (
        jsonb_typeof(next_actions)='array'
        AND jsonb_array_length(next_actions) BETWEEN 1 AND 12
    ),
    blockers JSONB NOT NULL DEFAULT '[]'::jsonb CHECK (
        jsonb_typeof(blockers)='array'
        AND jsonb_array_length(blockers) <= 12
    ),
    trust_state TEXT NOT NULL DEFAULT 'ASSERTED' CHECK (trust_state='ASSERTED'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (project_id,task_id) REFERENCES si_tasks(project_id,id),
    FOREIGN KEY (project_id,task_id,agent_run_id)
        REFERENCES si_agent_runs(project_id,task_id,id),
    UNIQUE (project_id,task_id,id),
    UNIQUE (project_id,task_id,checkpoint_seq)
);
CREATE INDEX ix_si_task_checkpoints_latest
    ON si_task_checkpoints(project_id,task_id,checkpoint_seq DESC);

CREATE TABLE si_checkpoint_observations (
    project_id TEXT NOT NULL,
    task_id UUID NOT NULL,
    checkpoint_id UUID NOT NULL,
    observation_id UUID NOT NULL,
    PRIMARY KEY (project_id,task_id,checkpoint_id,observation_id),
    FOREIGN KEY (project_id,task_id,checkpoint_id)
        REFERENCES si_task_checkpoints(project_id,task_id,id),
    FOREIGN KEY (project_id,task_id,observation_id)
        REFERENCES si_observations(project_id,task_id,id)
);
CREATE INDEX ix_si_checkpoint_observation_ref
    ON si_checkpoint_observations(project_id,task_id,observation_id);

-- An application user cannot UPDATE/DELETE persisted checkpoint rows; real
-- immutability also requires a restricted DB role and backup policy.
CREATE FUNCTION si_reject_checkpoint_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'checkpoint records are immutable'
        USING ERRCODE = '23514';
END;
$$;
CREATE TRIGGER trg_si_checkpoints_immutable
BEFORE UPDATE OR DELETE ON si_task_checkpoints
FOR EACH ROW EXECUTE FUNCTION si_reject_checkpoint_mutation();
CREATE TRIGGER trg_si_checkpoint_observations_immutable
BEFORE UPDATE OR DELETE ON si_checkpoint_observations
FOR EACH ROW EXECUTE FUNCTION si_reject_checkpoint_mutation();

-- The existing non-task-versioned continuity event stream is independently
-- append-only in the application; extend its narrow allowed event vocabulary.
ALTER TABLE si_continuity_events
    DROP CONSTRAINT si_continuity_events_event_type_check;
ALTER TABLE si_continuity_events
    ADD CONSTRAINT si_continuity_events_event_type_check
    CHECK (event_type IN (
        'AGENT_RUN_STARTED','SOURCE_REGISTERED',
        'OBSERVATION_ASSERTED','CHECKPOINT_RECORDED'
    ));
COMMIT;
