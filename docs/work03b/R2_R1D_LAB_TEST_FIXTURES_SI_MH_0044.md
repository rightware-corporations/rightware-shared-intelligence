# SI-MH-0044 — Guard destructive PostgreSQL unittest fixtures at import and execution

**Date:** 2026-11-13 Africa/Maputo. **Classification:** LAB TEST-SAFETY IMPLEMENTATION, CI PENDING. **G01 remains NOT RATIFIED.**

## Evidence baseline

- `develop@bbd731d6e30640df5f35da95bf9db979456287db`, SI-MH-0043 [Actions 43402943623](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43402943623): completed SUCCESS, verified through GitHub Actions metadata. Last extracted 190-test logs came from SI-MH-0042 [Actions 43402401931](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43402401931).
- Existing `lab_boundary.py` validates local PostgreSQL `/rw_test` and rejects `hostaddr` URI or environment and `PGSERVICE` indirection. Its CI integration scripts passed 190 tests.

## New finding (independent of G01 policy decisions)

Seven PostgreSQL unittest modules still computed `_SAFE` by checking *only* `urlsplit` URI path, or path+hostname+port. They **TRUNCATE** PostgreSQL tables at each `setUp`. They missed `?hostaddr=` query and `PGHOSTADDR`/libpq service override. Also a one-time collection predicate can become stale if environment changes before the tests run. In R2 R1C REST tests, R1B's legacy fixture is reused, inheriting that risk.

## Implemented here

- Added `is_disposable_postgres` to `backend/rightware_si/lab_boundary.py` as a safe boolean collection predicate that delegates to the previously verified strict `require_disposable_postgres`. Unsafe DSNs yield False and do not connect to the DB.
- Replaced legacy `urlsplit` _SAFE checks in seven modules: `test_context_api.py`, `test_http_api.py`, `test_pg_core.py`, `test_r2_r1b_ledger.py`, `test_work03b_r1a.py`, `test_work03b_r1b.py`, `test_work03b_r1c.py`. They call `require_disposable_postgres(_DSN, expected_user="rw")` **at the beginning of each setUp**, before any database connection or `TRUNCATE`.
- `test_r2_r1c_api_lab.py` inherits the updated R1B fixture safety automatically; no duplicated R1B `unittest.TestCase` imports.
- Added four pure tests in `test_lab_db_boundary.py` checking valid/invalid predicate, environment override, use-time failure, and source audit of all seven guarded fixture modules.
- Prior CI baseline 190 tests +4 tests = **194 expected**, but **NOT PASS until verified on the new SHA**. No migrations, new grants, auth changes or G01 implementation.

## Security boundary and next gate

Guard correctness does not prove network egress isolation, production identity/OIDC, tenant policy approval/expiry/disable/supersede, source consent/retention or user-credential lifecycle. The R2 verify endpoint remains a flagged, default-disabled synthetic lab route, no reviewer/DONE. G01 pending explicit operator ratification; 14 lifecycle oracles still NOT_EXECUTED.

Acceptance: exact Git SHA/Actions run, `Ran 194 tests / OK`, handoff policy, all seven migrations, GitHub LIVE G03, R1C agent handoff and Mem0/Ollama E2E. If failure occurs, preserve and fix under a new append-only checkpoint. No modifications to `main`, JARVIS/PULSE or vendor Mem0.
