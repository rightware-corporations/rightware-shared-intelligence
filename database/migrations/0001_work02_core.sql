-- RIGHTWARE Shared Intelligence WORK-02A: transactional core.
-- EXPERIMENTAL. Apply only on a dedicated test database with PostgreSQL >= 15.
-- No credentials, data migration from Mem0, or production deployment included.
BEGIN;

CREATE TABLE IF NOT EXISTS si_organizations (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS si_projects (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES si_organizations(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS si_principals (
  id TEXT PRIMARY KEY,
  principal_kind TEXT NOT NULL CHECK (principal_kind IN ('HUMAN','AGENT','SERVICE'))
);
CREATE TABLE IF NOT EXISTS si_project_grants (
  project_id TEXT NOT NULL REFERENCES si_projects(id),
  principal_id TEXT NOT NULL REFERENCES si_principals(id),
  permission TEXT NOT NULL,
  PRIMARY KEY (project_id, principal_id, permission)
);
CREATE TABLE IF NOT EXISTS si_tasks (
  id UUID PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES si_projects(id),
  created_by TEXT NOT NULL REFERENCES si_principals(id),
  title TEXT NOT NULL CHECK (length(title) BETWEEN 1 AND 200),
  acceptance_criteria JSONB NOT NULL DEFAULT '[]'::jsonb,
  status TEXT NOT NULL CHECK (status IN ('DRAFT','READY','IN_PROGRESS','BLOCKED','IN_REVIEW','DONE','CANCELLED')),
  version INTEGER NOT NULL CHECK (version > 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (project_id,id)
);
CREATE INDEX IF NOT EXISTS ix_si_tasks_project ON si_tasks(project_id,status);
CREATE TABLE IF NOT EXISTS si_task_leases (
  task_id UUID PRIMARY KEY REFERENCES si_tasks(id) ON DELETE CASCADE,
  holder_id TEXT NOT NULL REFERENCES si_principals(id),
  token_hash TEXT NOT NULL,
  generation INTEGER NOT NULL CHECK (generation > 0),
  expires_at TIMESTAMPTZ NOT NULL
);
CREATE TABLE IF NOT EXISTS si_handoffs (
  id UUID PRIMARY KEY,
  project_id TEXT NOT NULL,
  task_id UUID NOT NULL,
  from_principal_id TEXT NOT NULL REFERENCES si_principals(id),
  to_principal_id TEXT NOT NULL REFERENCES si_principals(id),
  summary TEXT NOT NULL CHECK (length(summary) BETWEEN 1 AND 8000),
  status TEXT NOT NULL CHECK (status IN ('OFFERED','ACCEPTED','DECLINED','REVOKED','EXPIRED')),
  offered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  accepted_at TIMESTAMPTZ,
  FOREIGN KEY (project_id, task_id) REFERENCES si_tasks(project_id,id)
);
CREATE INDEX IF NOT EXISTS ix_si_handoffs_task ON si_handoffs(task_id,status);
CREATE TABLE IF NOT EXISTS si_evidence_refs (
  id UUID PRIMARY KEY,
  project_id TEXT NOT NULL,
  task_id UUID NOT NULL,
  submitted_by TEXT NOT NULL REFERENCES si_principals(id),
  uri TEXT NOT NULL CHECK (length(uri) BETWEEN 1 AND 2048),
  verification_state TEXT NOT NULL DEFAULT 'REFERENCED'
    CHECK (verification_state IN ('REFERENCED','CHECKING','PASS','FAIL','INCONCLUSIVE')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  FOREIGN KEY (project_id, task_id) REFERENCES si_tasks(project_id,id)
);
CREATE TABLE IF NOT EXISTS si_events (
  id BIGSERIAL PRIMARY KEY,
  project_id TEXT NOT NULL,
  task_id UUID NOT NULL,
  task_version INTEGER NOT NULL CHECK (task_version > 0),
  actor_id TEXT NOT NULL REFERENCES si_principals(id),
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  FOREIGN KEY (project_id, task_id) REFERENCES si_tasks(project_id,id),
  UNIQUE (task_id,task_version)
);
CREATE INDEX IF NOT EXISTS ix_si_events_project ON si_events(project_id,id);
-- Enforced at the domain transaction boundary; never exposed as a web-user field.
CREATE TABLE IF NOT EXISTS si_idempotency (
  project_id TEXT NOT NULL REFERENCES si_projects(id),
  principal_id TEXT NOT NULL REFERENCES si_principals(id),
  action TEXT NOT NULL,
  idem_key TEXT NOT NULL,
  payload_hash TEXT NOT NULL,
  response JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (project_id,principal_id,action,idem_key)
);
COMMIT;
