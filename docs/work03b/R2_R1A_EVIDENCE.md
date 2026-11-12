# WORK-03B R2 R1A — Verified Lab Evidence: GitHub Workflow Run

**Date:** 2026-11-12 Africa/Maputo
**Code SHA tested:** `1aa40c0d54c96d7c59bb7118326700a974cbb46e` on `develop`.
**GitHub Actions run:** [43214573166](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43214573166) — **SUCCESS**.
**Classification:** real GitHub provider checks + synthetic adapter tests, **not** a production trusted verifier, R2 approval/DONE or full UC-CORE-01 acceptance.

## Exact observed CI

- `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`.
- PostgreSQL migrations 0001–0006 applied; `MIGRATION_PASS 0006_work03b_r1c_handoff_fencing.sql`.
- `Ran 115 tests in 16.344s`, `OK`. Baseline 100/100 + **15 new tests** of actual GitHub-checker logic with mocked/synthetic provider records.
- `R2_R1A_EV-01_LIVE_PASS observed=CHECKED_PASS task_approved=false provider=github_workflow_run`
- `R2_R1A_EV-02_LIVE_PASS observed=CHECKED_FAIL task_approved=false provider=github_workflow_run`
- `R2_R1A_EV-03_LIVE_PASS observed=CHECKED_FAIL task_approved=false provider=github_workflow_run`
- `R2_R1A_EV-04_LIVE_PASS observed=CHECKED_FAIL task_approved=false provider=github_workflow_run`
- `WORK03B_R2_R1A_GITHUB_LIVE_PASS run_id=43202560651 repo_id=1452533938 workflow_id=415280241 attempt=1 provider_live=true task_done=false evidence_records_persisted=false review_not_implemented=true`
- `WORK03B_R1B_RESUME_E2E_PASS`: two processes, authorized canonical PostgreSQL checkpoint with Mem0 offline and negative authorization checks.
- `WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS`: bound handoff, monotonic generation/rekey, no secret replay.
- `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS`: real MCP stdio/REST/PostgreSQL/Mem0 OSS/Ollama/pgvector, scoped grants/denials.
- No unmasked ephemeral internal Mem0 key was observed in these logs. Postgres expected negative-test trigger exceptions appeared in container shutdown logs, not test failures.

## What EV-01..EV-16 actually mean after this run

| Case set | Execution method | Actual outcome / confidence |
|---|---|---|
| EV-01 | **LIVE** authenticated GitHub REST GET of pinned previous completed run | CHECKED_PASS for exact **GitHub run fields** only; no DONE |
| EV-02 | **LIVE** GitHub REST GET with deliberately wrong expected SHA | CHECKED_FAIL/WRONG_SHA, no DONE |
| EV-03 | **LIVE** GitHub REST GET with deliberately wrong stable repository ID | CHECKED_FAIL/WRONG_REPOSITORY, no DONE |
| EV-04 | **LIVE** GitHub REST GET with deliberately wrong expected workflow ID | CHECKED_FAIL/WRONG_WORKFLOW, no DONE |
| EV-05 | MOCKED provider response (in_progress, no conclusion) in real adapter unit test | INCONCLUSIVE, no DONE; no live pending workflow tested |
| EV-06 | MOCKED connection error in actual adapter unit test | INCONCLUSIVE, no DONE; no live GitHub outage tested |
| EV-07 | UNTRUSTED_MEDIA screenshot representation in actual adapter unit test | INCONCLUSIVE, no DONE; no image manipulation investigation |
| EV-08..EV-16 | **NOT EXECUTED**, no actual signed bundle/reviewer/effect/revoked context | Keep expected oracles only; no result |

**Original SI-RD-03C source fixture remains unchanged** with `synthetic=true`, `executed=false` for all 16. It is a frozen research specification. The above table describes the **new implementation's actual CI runs** and intentionally does not falsify historical specification metadata.

## Scope of genuine GitHub proof

- Real GitHub provider check (GitHub API, token read-only) confirmed stable repository ID/name, workflow ID, exact 40-char SHA, run ID/attempt/event, status completed, conclusion success and matching head repository. The negative live checks mutate expected fields only, not GitHub data.
- Adapter does **not** accept arbitrary URLs, follow redirects, consult model-generated text or render screenshots as proof. HTTP errors, rate limits, missing/invalid JSON, pending workflows are INCONCLUSIVE, not automatic PASS. It returns only bounded metadata, reason and trust result.
- No independent verifier service principal or PostgreSQL scope policy is enforced here. `CHECKED_PASS` from this lab cannot be attached to a multi-tenant task, used for signed attestation, or promoted to reviewer-approved DONE.
- Attestation/SLSA/Sigstore verification, source-level consent/revocation, provider webhook verification, append-only VerificationAttempt records, workflow criteria coverage and authorized reviewer decision are **not implemented**.
- The verified result is limited to this completed known run; it does not assert that other workflows, providers or customer criteria would pass. This is an integration test, not a code security audit.

## Controls not yet approved

SEC-R1C-01..04 **still PENDING OPERATOR RATIFICATION**. R2-R0 contract **still draft**, `implemented_r2_routes=0`; UC-CORE-01 remains 18 lab REST routes, three proposed routes and M01–M18 `PENDING_FULL_E2E`. No new migration, API route, runtime deployment, extra dependency, main/Jarvis/PULSE changes, or Mem0 pin modifications.

## Next action

Request explicit operator ratification/revision of R1C security defaults and first provider policy (supported criterion and evidence scope) before building **R2 R1B**: append-only VerificationAttempt + independent authenticated evidence verifier endpoint and project grant enforcement, source/privacy policy, rerun/revocation checks and tests. Do **not** build reviewer/DONE yet.

This evidence-documentation checkpoint must update both handoffs in the same commit and its own CI must be verified separately.
