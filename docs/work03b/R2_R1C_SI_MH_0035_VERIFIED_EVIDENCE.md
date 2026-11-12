# WORK-03B R2 R1C — SI-MH-0035: Final verified laboratory CI + security coverage matrix

**Date:** 2026-11-12 (Africa/Maputo). **Classification:** VERIFIED LABORATORY REGRESSION, NOT PRODUCTION RELEASE.

## Verified run

- **Implementation/test harness SHA:** `develop@f4732da8de086c9f869b3833a66f168a35e82a40`.
- **Github Actions run:** [43251091244](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43251091244) — completed, conclusion **SUCCESS**, job `real-mcp-mem0`.
- **Exact log:** `Ran 158 tests in 23.501s`, `OK`, after duplicate collection was fixed in SI-MH-0034. The suite is now **158 distinct test executions**, not 174 inflated by duplicate `unittest.TestCase` imports.
- `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`.
- PostgreSQL migration 0001 through 0007: `MIGRATION_PASS`.
- `WORK03B_R2_R1A_GITHUB_LIVE_PASS`: LIVE GitHub workflow identity reads (specific run/commit), no task DONE.
- `WORK03B_R2_R1B_LEDGER_LIVE_PASS`: LIVE GitHub API + authenticated SERVICE → append-only PostgreSQL, `CHECKED_PASS` scoped, idempotent, revoked read denied; task remains `IN_REVIEW`; evidence remains `REFERENCED`; no review or DONE.
- `WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS`: two independent agents, bound checkpoint, fencing generation, lease rekey and secret replay denial without Mem0.
- `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS`: real MCP stdio → REST → PostgreSQL → pinned Mem0 OSS → Ollama embeddings with scoped denial/revocation, synthetic data.
- New R2 R1C HTTP integration tests use FastAPI TestClient + PostgreSQL + injected httpx.MockTransport. Their GitHub responses are **SIMULATED_TRANSPORT**; this CI does **not** prove the new REST endpoint against a real GitHub provider in one single call chain.
- PostgreSQL ERROR lines for deliberately blocked immutable record changes are expected negative-test observations; the full job concluded SUCCESS.

## Crosswalk for the 16 proposed API negative cases

Every mapped case below had its named **narrow** lab test execute and pass in the 158-test suite. `LAB_COVERED` does not confer production acceptance; `PARTIAL` requires expanded cases, `BLOCKED` requires feature design and `OPEN` needs a targeted test.

| Oracle | Closest executed R2 R1C test | Status | Remaining limitation |
|---|---|---|---|
| API-NEG-01 | `test_03_missing_bearer_401` | LAB_COVERED | No bearer; no attempt |
| API-NEG-02 | `test_04_agent_even_with_verify_grant_403` | PARTIAL | AGENT denied; HUMAN-with-grant case not exercised via new REST |
| API-NEG-03 | `test_05_service_missing_grant_403` | PARTIAL | Missing evidence:verify; missing task:read not isolated via REST |
| API-NEG-04 | `test_15_cross_project_policy_not_found` | LAB_COVERED | Cross-project policy lookup denied |
| API-NEG-05 | `test_06_path_policy_mismatch_rejected_before_network` | LAB_COVERED | Wrong path evidence ID rejected without provider fetch |
| API-NEG-06 | `test_07_missing_policy_404` | PARTIAL | Missing policy tested; cross-task mismatched existing policy not separately tested |
| API-NEG-07 | `test_08_stale_task_version_409` | PARTIAL | Stale version tested; non-IN_REVIEW state not separately tested through REST |
| API-NEG-08 | `test_16_revocation_midflight_denies_commit` | LAB_COVERED | Grant revoked during simulated provider call prevents append |
| API-NEG-09 | `test_12_wrong_sha_returns_checked_fail` | PARTIAL | Wrong SHA via REST mock; repo/workflow/attempt mismatches tested at provider R1A, not this REST |
| API-NEG-10 | `test_11_provider_failure_is_inconclusive` | PARTIAL | HTTP 403 via simulated transport; redirect/pending/timeout not tested via REST |
| API-NEG-11 | `test_10_replay_does_not_refetch` | LAB_COVERED | Same idempotency key returns one record, one fetch |
| API-NEG-12 | `test_13_reusing_idem_with_different_policy_409` | PARTIAL | Different policy checked; evidence and task-version variants not REST-tested |
| API-NEG-13 | `test_14_caller_identity_override_rejected_422` | PARTIAL | Actor override blocked; other forbidden fields not individually REST-tested |
| API-NEG-14 | `NOT_IMPLEMENTED` | BLOCKED | Policy expiry/disable/supersede lifecycle not implemented |
| API-NEG-15 | `test_09_synthetic_success_is_append_only_no_done` | LAB_COVERED | Mock success stored as SIMULATED_TRANSPORT, no DONE |
| API-NEG-16 | `NOT_EXECUTED` | OPEN | PostgreSQL unavailable/503 response and secret-free logs not exercised end-to-end |

Additionally, tests `test_01_flag_disabled_by_default` and `test_02_flag_rejects_non_lab_dsn` validated opt-in route absence and fail-closed startup when a non-laboratory DSN is supplied.

**Do not retroactively mutate** the 16 original SI-RD-03C JSONL test fixtures (`synthetic=true, executed=false`) or the original R2 R0 historical contract. Run-time evidence is reported separately, and the `API-NEG` catalogue is not fully closed.

## Security status and next gate

**VERIFIED LAB ONLY:** opt-in FastAPI endpoint; initial bearer identity derived server-side; SERVICE-type scoped verification; exact `evidence_id`↔policy binding checked before provider call and under transaction; append-only verification attempt; idempotency and mid-call revocation in synthetic lab; no DONE. Main/JARVIS/PULSE/Mem0 vendor unchanged.

**NOT READY FOR PRODUCTION:** provider authorization/allowlist lifecycle per tenant, expiry/disable/supersede, production OIDC/workload identity and key management, source-level ACL/consent/retention, rate limits and abuse controls, RLS/least-privilege DB audit, external-effect outbox/reconciliation, independent reviewer, release configuration, backup/restore, and UC-CORE-01 M01–M18 full acceptance. SEC-R1C-01..04 are ratified as security **principles**, not proven production implementations.

**NEXT proposed gate:** R2 R1D-R0 — close the API-NEG-02/03/06/07/09/10/12/13/16 lab gaps, design and ratify policy expiry/disable (API-NEG-14), formalize R2 provider/identity/privacy decisions, and require a real GitHub API-through-REST smoke in a disposable isolated environment (safe credential handling). Do **not** enable production or independent review/DONE by inference.

This evidence report is committed in a documentation-only SI-MH-0035 alongside MASTER append-only checkpoint and CURRENT handoff. Its own CI is a separate future run; the above SUCCESS belongs **only** to implementation SHA `f4732da8de086c9f869b3833a66f168a35e82a40`.
