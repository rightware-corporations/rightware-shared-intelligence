# WORK-03B R1A — Operational Continuity Foundation

**Status at implementation commit: code committed / CI pending.** Experimental authenticated lab functionality only; not the complete UC-CORE-01. Main, Jarvis/PULSE, and Mem0 submodule unchanged.

## Implemented components
- SQL migration 0004 (database/migrations/0004_work03b_r1a_continuity.sql): task-bound agent runs, sources, unverified observations, cross-source association and separate continuity event stream.
- Backend continuity.py: reuse WorkCore transactional/idempotency/lease checks. Every write runs under the active task lease, server-derived actor, scoped grant, expected task version and an idempotency key.
- Four REST operations: POST /v1/projects/{project_id}/tasks/{task_id}/runs [task:execute]; POST /v1/projects/{project_id}/sources [source:write]; POST /v1/projects/{project_id}/observations [observation:write]; GET /v1/projects/{project_id}/tasks/{task_id}/observations [task:read AND context:read].
- New real disposable PostgreSQL tests in tests/test_work03b_r1a.py cover run/source/observation positive flow, idempotency, old lease denial, cross-project/task isolation, revocation, bad source URLs, and source-linked trust.
- Canonical R0 machine-readable contract updated from 10/7 routes to 14 live / 6 future; original 14-step journey remains pending. M02 is only R1A_LAB_PARTIAL.

## Product-facing semantics
An operator creates/publishes a synthetic task and Agent A claims a valid lease. A starts an AgentRun and registers a revisioned GIT_REF (HTTPS github.com pointer) or TOOL_RECEIPT (safe urn:rw: pointer). A writes an Observation linked to at least one same-task source. The claim is always ASSERTED; its task remains IN_PROGRESS at the same version. Server-generated correlation ID and source/event references provide provenance.

Observations live in PostgreSQL. The new si_continuity_events table records event identities and task_version without duplicating si_events lifecycle entries; the event payload stores references rather than raw untrusted claim text. A source URL is NEVER dereferenced by this implementation. Access control is checked on write and again on list.

## Restrictions / known risks
- No ContextSnapshot, TaskCheckpoint, resume in a new process, memory projection/outbox, evidence verifier, decision review or automatic completion. M01-M18 full E2E remain pending.
- No production OIDC, resource-level source ACL or consent/retention system. Do not ingest personal or confidential data into this experimental lab.
- The read API is limited to the oldest 100 assertions (no cursor yet); truncated=true flags a possible larger history.
- AgentRun has start/correlation metadata but no lifecycle heartbeats/close-on-handoff; not a dependable execution-status monitor yet.
- SQL data is append-only by application convention, not tamper-proof with a dedicated PostgreSQL role. DB privilege separation remains pending.
- Lease token never persists raw in idempotency store (WORK-02D). Retries of lease-issuing operations remain 409; safe recovery is deferred.
- No external model invocation or tool action is performed by these new operations; source pointer is NOT evidence of successful execution.

## Remaining work
R1B: immutable checkpoint and resource-authorized continuation snapshot with read-only resume, tested using a second process with Mem0 offline. R1C: checkpoint-bound handoff, lease recovery, fencing. R1D: consent-aware outbox/memory projection. R2: independently verified evidence, reviewer approval, retention/deletion.

## Evidence
GitHub Actions CI will apply migrations 0001-0004, run existing regressions and new R1A tests, then rerun real MCP/REST/PostgreSQL/Mem0/Ollama synthetic E2E. Record observed PASS/FAIL and run link as a separate MASTER entry; never infer from test code alone.
