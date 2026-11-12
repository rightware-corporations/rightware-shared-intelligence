# WORK-03B R1B — Verified Evidence

**Date:** 2026-11-12 Africa/Maputo · **Branch:** develop · **Code SHA:** `5c98e9f42a481709762550d9d451cb64f7d65b31` · **Status:** VERIFIED IN SYNTHETIC LAB, NOT PRODUCT ACCEPTANCE.

## Primary evidence
- [GitHub Actions run 43160672177](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43160672177) — **SUCCESS**.
- `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`.
- `MIGRATION_PASS`: all 5 SQL migrations 0001–0005 using disposable PostgreSQL16 `rw_test`.
- **`Ran 81 tests`; `OK`** = 69 existing tests + 9 new real PostgreSQL/REST R1B tests + 2 MCP SDK read-only tool tests + 1 static contract test.
- **`WORK03B_R1B_RESUME_E2E_PASS`**: independent process A persisted an ASSERTED immutable checkpoint and exited; process B with a different bearer and handoff identifier accepted it and reconstructed checkpoint/observations via real REST/PostgreSQL without A's chat, lease or infrastructure credentials. The Mem0 service and Ollama were OFF; API canonical resume never queried them. Old A lease rejected; intruder and revoked B grants rejected.
- **`WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS`**: existing real subprocess MCP/REST/PostgreSQL/Mem0 OSS/Ollama/pgvector synthetic regression with project denial and token revocation.
- No unmasked ephemeral internal API key found in inspected logs.

## Guarantees and limits of this checkpoint
- Checkpoint stored with per-task sequence CAS, same-task observation references, and database UPDATE/DELETE blocking triggers; `task.version` unchanged for checkpoint writes.
- Current task/context grants are rechecked on each resume; data assembled as a read-only repeatable-read transaction. No new lease, DONE, approval or external side effects.
- Read-only MCP `resume_task` routes through the same REST authorization layer. `memory_status=NOT_QUERIED`; checkpoint content remains unverified `ASSERTED`.
- **Limitation:** the old handoff is not atomically bound to a checkpoint; the response explicitly marks `checkpoint_binding=NOT_IMPLEMENTED_R1B`. After A→B handoff the task version advances while the checkpoint's recorded version remains historical; this is intentional, not permission to execute stale commands.
- Checkpoint pointers are not independently verified evidence; source-level consent/revocation, outbox/retention, lost lease recovery, independent verifier, reviewer DONE, production security and Jarvis staging are still missing.
- UC-CORE-01's complete 14-step journey and M01–M18 remain `PENDING_FULL_E2E`, despite this narrower E2E PASS.

## Next checkpoint
WORK-03B R1C: checkpoint-bound handoff, freshness/fencing, safe authorized recovery of lost/expired leases, and additional negative/integration tests. No changes to main, Jarvis/PULSE or Mem0 pin during R1B.

The commit adding this evidence is documentation-only and needs its own CI verification.
