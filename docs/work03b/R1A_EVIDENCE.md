# WORK-03B R1A — Verified Engineering Evidence

**Status:** VERIFIED IN SYNTHETIC LAB. **Not** production approved or full UC-CORE-01 acceptance.
**Date:** 2026-11-12, Africa/Maputo.
**Branch / tested code SHA:** develop / 538eb1b67628e8a0905b6511da9fddf9f0d1313c
**CI:** https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43157921966 — SUCCESS.

## GitHub Actions observed results
- HANDOFF_POLICY_PASS audited_commits=1: both master/current handoffs updated with implementation.
- Migration 0001_work02_core.sql: MIGRATION_PASS (PostgreSQL16 synthetic /rw_test).
- Migration 0002_work02b_api_credentials.sql: MIGRATION_PASS.
- Migration 0003_work02d_scrub_lease_replays.sql: MIGRATION_PASS.
- Migration 0004_work03b_r1a_continuity.sql: MIGRATION_PASS.
- **Ran 69 tests; OK** — 60 baseline tests + eight real PostgreSQL/TestClient tests + one new static contract coverage test.
- WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS: real external stdio MCP process -> REST authenticated -> PostgreSQL / project grants -> Mem0 OSS actual + Ollama local embedding + pgvector (synthetic only).
- No observed unmasked ephemeral internal API key in run logs.

## What 8 R1A tests actually established
- Authenticated task lease ownership and expected task.version gate before run/source/observation writes.
- Server identity and project grants enforced; deny unauthorized Beta, reviewer without context:read and forged body actor/trust fields.
- Each unverified Observation refers to a same-task SourceRecord; persisted/read back with PostgreSQL and independent continuity events.
- Task lifecycle version remains unchanged for simple run/source/observation writes; actual work status is not accepted/approved.
- Duplicate request with same safe Idempotency-Key returns original reference; different payload conflicts; new key cannot silently create second run under same lease version.
- Token revoked or source:write grant removed -> subsequent operations denied.
- Cross-task source or run association rejected, including after second task starts.
- Handoff invalidates A's old writer lease; B's own lease can start a different run and write source-linked observations.
- Unsafe source URI and fabricated APPROVED observation state rejected. Source pointer is NOT externally verified.

## Integrity and scope
- New files: backend/rightware_si/continuity.py, database/migrations/0004_work03b_r1a_continuity.sql, tests/test_work03b_r1a.py, docs/work03b/R1A_IMPLEMENTATION.md.
- Existing REST/task/MCP/Mem0 code and services continue to pass regression. R1A exposes FOUR new REST endpoints, NOT MCP mutation tools.
- Contract JSON updated to 14 current routes, 6 proposed; M02 marked R1A_LAB_PARTIAL, all M01–M18 PENDING_FULL_E2E.
- main not merged/changed, vendor Mem0 gitlink unchanged, Jarvis/PULSE production not modified, no paid inference or customer data.

## Known limits requiring follow-up
- No TaskCheckpoint, ContextSnapshot, resume from a different process without chat, or real semantic projection of these new observations.
- AgentRun has correlation metadata but no end/heartbeat/state transition on handoff yet.
- No source-level classification/consent, individual resource ACL, retention/erasure, pagination or permanent deletion.
- No verified external Git/CI receipts, reviewer independent DONE approval, outbox, production workload identities/TLS/backups.
- Source pointers can be asserted by an agent and are not evidence of truth; no external effect execution is included.
- Database event stream relies on application append-only discipline rather than a dedicated least-privilege DB role/trigger.

## Next step
WORK-03B R1B: server-side versioned Checkpoint and read-only Resume manifest scoped by project+task+current grants, with a genuinely new client process and Mem0-down fallback. Later R1C checkpoint-bound handoff and secure lease recovery; then R2 verification/lifecycle.

**Note:** The subsequent documentation-only commit recording these results has its own CI run. It must be checked separately; this ledger records observed R1A code SHA above.
