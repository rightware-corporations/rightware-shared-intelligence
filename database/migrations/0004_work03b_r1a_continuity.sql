-- RIGHTWARE WORK-03B R1A: task-bound agent runs, sources and unverified observations.
-- Dedicated PostgreSQL >=15 only; review before any non-lab use.
-- Additive, no Mem0/LLM side effects. No source URLs fetched here.
BEGIN;

CREATE TABLE si_agent_runs (
    id UUID PRIMARY KEY,
    project_id TEXT NOT NULL,
    task_id UUID NOT NULL,
    actor_id TEXT NOT NULL REFERENCES si_principals(id),
    correlation_id UUID NOT NULL UNIQUE,
    runtime_label TEXT NOT NULL CHECK (length(runtime_label) BETWEEN 1 AND 120),
    task_version_started INTEGER NOT NULL CHECK (task_version_started > 0),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (project_id,task_id) REFERENCES si_tasks(project_id,id),
    UNIQUE (project_id,task_id,id),
    UNIQUE (project_id,task_id,actor_id,task_version_started)
);
CREATE INDEX ix_si_agent_runs_project_task ON si_agent_runs(project_id,task_id,started_at);

CREATE TABLE si_source_records (
    id UUID PRIMARY KEY,
    project_id TEXT NOT NULL,
    task_id UUID NOT NULL,
    agent_run_id UUID NOT NULL,
    recorded_by TEXT NOT NULL REFERENCES si_principals(id),
    source_kind TEXT NOT NULL CHECK (source_kind IN ('GIT_REF','TOOL_RECEIPT')),
    source_uri TEXT NOT NULL CHECK (length(source_uri) BETWEEN 1 AND 2048),
    source_revision TEXT NOT NULL CHECK (length(source_revision) BETWEEN 1 AND 128),
    digest_sha256 CHAR(64),
    observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (project_id,task_id) REFERENCES si_tasks(project_id,id),
    FOREIGN KEY (project_id,task_id,agent_run_id)
        REFERENCES si_agent_runs(project_id,task_id,id),
    UNIQUE (project_id,task_id,id),
    UNIQUE (project_id,task_id,source_kind,source_uri,source_revision),
    CHECK (digest_sha256 IS NULL OR digest_sha256 ~ '^[a-f0-9]{64}$')
);
CREATE INDEX ix_si_source_records_run ON si_source_records(project_id,task_id,agent_run_id);

CREATE TABLE si_observations (
    id UUID PRIMARY KEY,
    project_id TEXT NOT NULL,
    task_id UUID NOT NULL,
    agent_run_id UUID NOT NULL,
    asserted_by TEXT NOT NULL REFERENCES si_principals(id),
    claim_text TEXT NOT NULL CHECK (length(claim_text) BETWEEN 1 AND 2000),
    trust_state TEXT NOT NULL DEFAULT 'ASSERTED' CHECK (trust_state = 'ASSERTED'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (project_id,task_id) REFERENCES si_tasks(project_id,id),
    FOREIGN KEY (project_id,task_id,agent_run_id)
        REFERENCES si_agent_runs(project_id,task_id,id),
    UNIQUE (project_id,task_id,id)
);
CREATE INDEX ix_si_observations_task ON si_observations(project_id,task_id,created_at,id);

CREATE TABLE si_observation_sources (
    project_id TEXT NOT NULL,
    task_id UUID NOT NULL,
    observation_id UUID NOT NULL,
    source_id UUID NOT NULL,
    PRIMARY KEY (project_id,task_id,observation_id,source_id),
    FOREIGN KEY (project_id,task_id,observation_id)
        REFERENCES si_observations(project_id,task_id,id),
    FOREIGN KEY (project_id,task_id,source_id)
        REFERENCES si_source_records(project_id,task_id,id)
);
CREATE INDEX ix_si_observation_sources_src ON si_observation_sources(project_id,task_id,source_id);

-- si_events is uniquely keyed by (task_id,task_version) for lifecycle
-- transitions. Append independent continuity events without changing task
-- status or version for each observation/source registration.
CREATE TABLE si_continuity_events (
    id BIGSERIAL PRIMARY KEY,
    project_id TEXT NOT NULL,
    task_id UUID NOT NULL,
    actor_id TEXT NOT NULL REFERENCES si_principals(id),
    task_version INTEGER NOT NULL CHECK (task_version > 0),
    event_type TEXT NOT NULL CHECK (event_type IN (
        'AGENT_RUN_STARTED','SOURCE_REGISTERED','OBSERVATION_ASSERTED'
    )),
    entity_id UUID NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (project_id,task_id) REFERENCES si_tasks(project_id,id)
);
CREATE INDEX ix_si_continuity_events_task ON si_continuity_events(project_id,task_id,id);
COMMIT;
