# WORK-03B R2 R1C — SERVICE-only REST Verification Adapter (LAB)

**2026-11-12 · Code checkpoint SI-MH-0032 (CI PENDING)**

Baseline `develop@3567c99dfa620f3bf23eaf8fa0b1b030c42f131c`. This is an experimental lab-only adapter over already verified `EvidenceLedger`, NOT a production API. The four SEC-R1C conservative principles are ratified in [SEC_R1C_POLICY_RATIFICATION_R1.md](SEC_R1C_POLICY_RATIFICATION_R1.md); their production enforcement remains incomplete.

## Changes

- `EvidenceLedger._load` now accepts `expected_evidence_id`, compare policy evidence UUID **before network** and again **under task row lock** before insert. Existing R1B internal caller remains compatible with optional keyword argument.
- `http_api.create_app`: registers `POST /v1/projects/{project_id}/evidence/{evidence_id}/verify` only when **both** `RW_SI_ENVIRONMENT=lab` and `RW_SI_ENABLE_R2_R1C_LAB_API=1`, and PostgreSQL is disposable loopback `/rw_test` on port 5432. Otherwise the route is absent or the app refuses startup. No endpoint from normal `uvicorn` setup.
- Request body limited to `policy_id` UUID and strict positive `expected_task_version`, plus `Idempotency-Key`; principal from bearer dependency, no request-supplied actor/token/provider/URL/client.
- Existing provider HTTPS protections, SERVICE separation, project grants, idempotency, observation provenance and append-only PostgreSQL storage reused. `psycopg.OperationalError` mapped to sanitized 503 at the new route.
- Existing review/DONE behaviour remains absent. No migration, paid service or production key added.

## Test contract

- `tests/test_r2_r1c_api_lab.py`: **16 actual HTTP-to-PostgreSQL integration test definitions** (CI still pending) for disabled feature gate, startup refusal on production DSN, 401, 403 principal, missing grant, path mismatch, unknown policy, stale version, simulated success, replay, provider error, wrong SHA, idempotency conflicts, forbidden actor overrides, cross-project, and mid-call grant revocation. `httpx.MockTransport` injected by test harness only and marked `SIMULATED_TRANSPORT`.
- `tests/test_r2_r1c_contract.py` updated to preserve 11 static checks, now expecting opt-in route and explicit `expected_evidence_id`.
- Existing R2 R1B 131 tests remain mandatory. Expected total **158** (131 previous +11 contract +16 new HTTP tests), unverified until real CI logs. All 16 API-NEG oracles in the original JSON remain `NOT_EXECUTED` until each is individually mapped to a passing CI case; some such as policy expiry/disable remain BLOCKED by missing lifecycle.
- Production workload identity/OIDC, tenant policy lifecycle/disable/expiry, RLS/source privacy consent/retention, rate-limits, reviewer/DONE, external-effect outbox and full M01–M18 E2E are still missing. CI green cannot close these.

## Rollback

Only three existing files are changed (`http_api.py`, `verification_ledger.py`, static contract + JSON) plus new tests/docs/handoffs. The feature flag is OFF by default. If CI fails or security bug appears, retain failure logs, disable the lab flag and revert this new feature via non-destructive correction commit; do not alter historical checkpoints, `main`, JARVIS or PULSE.
