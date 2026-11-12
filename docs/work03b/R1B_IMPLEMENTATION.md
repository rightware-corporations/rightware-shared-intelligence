# WORK-03B R1B — Immutable Checkpoint and Read-Only Resume

**State at implementation commit:** CODE COMMITTED, CI PENDING. Synthetic PostgreSQL-only continuity demo; NOT production readiness or full product acceptance.
**Branch:** develop only. main, Jarvis, PULSE and vendored Mem0 remain unchanged.

## What's new
- Migration 0005: `si_task_checkpoints`, `si_checkpoint_observations`, immutable DB update/delete triggers, `CHECKPOINT_RECORDED` audit events, and a per-task `checkpoint_seq` monotonic sequence.
- `ContinuityCore.record_checkpoint`: Active work lease, same-run ownership, current task version, `checkpoint:write`, `task:execute` and `context:read` required. Caller supplies `expected_checkpoint_seq` for concurrency protection and source-linked same-task Observation refs. Contents are **ASSERTED** and never approved.
- `ContinuityCore.resume_task`: fresh single repeatable-read read-only transaction, reauthorizes `task:read` + `context:read`, returns task status/version, latest checkpoint, assertion records and sanitized source identifiers, and latest handoff status. **Never issues a lease. Never uses Mem0.**
- HTTP POST `/v1/projects/{project_id}/tasks/{task_id}/checkpoints`; HTTP GET `/v1/projects/{project_id}/tasks/{task_id}/resume` (strict Pydantic, bearer).
- MCP adds `resume_task` tool read-only via the same authenticated REST route (no writes). Current browser/Claude/ChatGPT hosts and Jarvis staging are **not** integration-tested.
- Real PostgreSQL/REST tests `tests/test_work03b_r1b.py` plus MCP SDK tests `tests/test_work03b_r1b_mcp.py`. Independent two-process E2E `scripts/work03b_r1b_real_resume_e2e.py` runs before Ollama, proving A exits, B accepts and reads canonical checkpoint without A's chat.
- Canonical contract now records **16 implemented / 4 proposed** REST routes; M01–M18 remain PENDING_FULL_E2E.

## Security/authority contract
- Task lifecycle events remain governed by si_events; checkpoint_seq increases independently **without changing task.version**.
- Every checkpoint write requires valid lease and optimistic task/checkpoint versions; stale or revoked lease/grant denies.
- Source and observations must belong to the same project+task. The checkpoint can refer to earlier run observations by a different authorized principal within that task, but no role is elevated to VERIFIED.
- Read-only resume does not fetch raw source URLs by default; it returns source_id, kind, revision and optional digest. Host/model prompts must treat summary, blockers, next_actions and claims as **untrusted data**, never system instructions.
- `memory_status=NOT_QUERIED` is intentional: service remains usable when Mem0/Ollama are off; this is not a claim that semantic memory was available.
- Checkpoint DB triggers block UPDATE/DELETE and every write adds a continuity event in the same transaction. Database superuser and destructive TRUNCATE remain out of threat model; add roles/tamper-evidence in production security phase.
- New B process only receives its own bearer and handoff ID; NOT A's chat, A's lease, or PostgreSQL/VM credentials. The E2E test uses synthetic data only.

## Design limitations (not hidden)
- Handoff still stores only a summary, not a binding to a checkpoint ID/version (R1C). GET resume returns latest checkpoint and explicitly marks checkpoint_binding NOT_IMPLEMENTED_R1B. After handoff, checkpoint.task_version_recorded can be 3 while task.version is 5; consumers must **not** infer the checkpoint is fresh executable authority.
- No pagination or snapshot caching/TTL. Resource/subject-level consent and individual source ACL are not implemented; do NOT store private information in this lab.
- No memory projection/outbox, evidence verification, reviewer DONE, external effects or lease secret recovery; no production TLS/OIDC/backup.
- R1B is read-only recovery of current canonical data, **not automatic execution** and **not a complete transferable checkpoint-bound bundle**.

## CI gate
GitHub Actions 0001–0005 migrations in disposable local PostgreSQL16 /rw_test; existing regression unit/REST/MCP; R1B checkpoint tests and SDK test; independent A/B subprocess real HTTP without Mem0; existing real Mem0 OSS+Ollama+pgvector E2E. Record actual status and count in a separate MASTER adenda after the CI completes.

## Next
WORK-03B R1C: atomic checkpoint-bound handoff, lease generation fencing/recovery, stale snapshot/cached-read revocation, deterministic two-process restart repeats. Followed by R1D memory outbox/consent and R2 independent evidence/reviewer.
