# SI-MH-0051 — G01 lifecycle enforcement across GitHub HTTP verification (LAB)

**2026-11-14 Africa/Maputo. BASE `develop@ac0512a731207b9d2b521b33e0041108f45c1127`. New code CI PENDING.**

## Verified prior state

- G01 event journal migration 0008 and internal bearer/HUMAN-separated activation passed [Actions 43602557496](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43602557496): **SUCCESS, Ran 202 tests in 17.124s / OK**, all eight migrations, R1A/R1B/G03 GitHub LIVE and WORK02D real Mem0/Ollama PASS.
- Its first failed CI [43602331541](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43602331541) remains recorded; fixed only dict row test and migration allowlist in SI-MH-0050.
- Pilot authorized only for internal RIGHTWARE synthetic data, two independent HUMAN bearers, seven-day database-clock policy validity, SERVICE verification, explicit revoke and no private client source/production.

## Implemented now

- `verification_ledger._load` has a `enforce_lifecycle` flag: in opt-in G01 mode, checks ACTIVE and DB-time expiry. Preflight holds the same task row lock even when an older idempotency key is replayed; no stale CHECKED_PASS returned after disable. After the bounded GitHub GET, the ledger re-locks task and checks policy state again before writing an attempt. A concurrent revocation wins and yields Conflict/HTTP409 and **no new attempt**.
- `http_api.create_app` refuses enabling G01 without R2 lab route. No policy administration routes exposed; existing verifier HTTP path remains opt-in lab and SERVER-sourced GitHub credential.
- Six new real PostgreSQL tests, provider inputs via `httpx.MockTransport` **SIMULATED_TRANSPORT**: inactive denies before network; ACTIVE verifies with idempotent replay; DISABLED denies already stored replay; midflight disable aborts commit; DB-clock expired denies before network; synthetic legacy path is accessible only with flag explicitly OFF. **202+6=208 tests EXPECTED, not yet validated.**
- Existing [G03 LIVE-through-REST script](../../scripts/work03b_r2_r1d_live_http.py) now seeds separate HUMAN proposer/approver bearer identities, activates the policy for seven days, verifies the actual public pinned GitHub workflow run via authenticated SERVICE REST, replays idempotently, disables via HUMAN, demands **409** on stale replay, revokes verifier grant demanding **403**; no task DONE. CI enables G01 flag only for this explicit G03 step and prints distinct `WORK03B_R2_R1D_G01_LAB_POLICY_LIVE_PASS` marker. No private repository/customer data.
- Existing R1B/G03 LIVE and Mem0/Ollama regression steps must remain PASS; no G01 policy event permission is inherited by the production or other tests.

## Limits / NOT CLOSED

- No actual two-process DB backup-and-restore test (G01-12 OPEN), no production tenant consent/source ACL or private source verification, OIDC/workload identity, key rotation, RLS or rate limits; G04/G05 BLOCKED.
- No complete user-level review/DONE or commercial readiness. Default feature flag OFF and LAB local rw_test only.
- Nothing in `main`, JARVIS/PULSE, vendor Mem0 or previous policy rows modified.

**NEXT:** check GitHub Actions on this SHA. Do not call G01 LIVE through policy PASS until exact log marker and SUCCESS confirmed. Repair any failures under next append-only SI-MH checkpoint.
