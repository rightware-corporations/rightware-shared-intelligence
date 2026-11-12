# WORK-03B R2 R1D-G02 — Negative HTTP tests and sanitized PostgreSQL outages

**Date:** 2026-11-12 Africa/Maputo. **Scope:** LAB IMPLEMENTATION, CI PENDING, NOT R1D-G01/G03/G04/G05 RATIFICATION OR PRODUCTION.

## Baseline and verified prerequisites

- Baseline `develop@1cc93652669e1ff8d7377bd5f1474229a971980e`.
- SI-MH-0036 [Actions 43252805427](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43252805427) **SUCCESS** (confirmed via GitHub Actions run metadata; exact new test count of this run not independently extracted here).
- SI-MH-0035 158/158 verified at [43252042999](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43252042999).
- R2 R1C is an opt-in, disposable localhost PostgreSQL lab endpoint only. No OIDC, policy lifecycle or production enablement.

## Scope implemented here

- Added **16 named R2 R1D-G02 negative HTTP/PostgreSQL tests** to `tests/test_r2_r1c_api_lab.py`, numbered 17–32. Together with earlier 158 distinct tests, **174 tests expected** on the new CI; no claim of PASS until the run has completed.
- **API-NEG-02:** HUMAN with both granted permissions is still rejected; SERVICE-only is not grant-only.
- **API-NEG-03:** removing `task:read` independently blocks a SERVICE, in addition to the earlier `evidence:verify` missing-grant test.
- **API-NEG-06/07:** another task's evidence ID cannot borrow the first policy; an existing task switched to `BLOCKED` is not verifiable.
- **API-NEG-09:** wrong repository ID, workflow ID or run attempt return CHECKED_FAIL (mocked provider source).
- **API-NEG-10:** pending workflow, redirect response and network timeout return INCONCLUSIVE (mocked provider source).
- **API-NEG-12/13:** stale-version idempotency replay conflicts; all additional forbidden caller-controlled body fields rejected 422; invalid idempotency key rejected without provider calls.
- **API-NEG-16:** simulated ledger OperationalError and bearer-resolution OperationalError must both respond with sanitized 503 and no secrets in HTTP body. Introduced a generic FastAPI `psycopg.OperationalError` exception handler to cover dependency failures outside the route; R2 R1C route's own 503 handling remains.
- Independent policy-author/verifier separation also exercised through HTTP. All simulated provider checks carry `SIMULATED_TRANSPORT`, and no task DONE/reviewer is created.

## Not closed by these tests

- API-NEG-14 expiry/disable/supersede: **BLOCKED** until operator approves policy management model, lifecycle and migration. Do not add fields or permissions silently.
- G03 real GitHub provider-through-new-HTTP not yet implemented in this checkpoint; prior R1B LIVE is separate.
- Production auth identity/OIDC, source-level access/consent/retention, rate-limits, tenant DB RLS, branch protection, backup/restore, independent reviewer and release not implemented.
- No modifications to `main`, JARVIS/PULSE or vendor Mem0; no new migrations, dependencies or deployments.

## CI acceptance

Check new Git SHA's Actions job: migration 0001–0007, `Ran 174 tests` / `OK`, internal GitHub LIVE regressions, R1C two agents, real Mem0/Ollama. If failing, record precise testcase/step and repair with a follow-on checkpoint. Nothing claimed LIVE for new negative endpoint tests.
