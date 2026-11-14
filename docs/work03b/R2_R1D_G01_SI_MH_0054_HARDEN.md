# WORK-03B — SI-MH-0054 G01-HARDEN: process-race, mid-provider expiry, and lifecycle idempotency

**Date:** 2026-11-14 Africa/Maputo. **Status:** LAB-ONLY CODE + TESTS IMPLEMENTED; NEW CI NOT YET VERIFIED.

## Verified baseline

- `develop@690100e46d10a4b9c6d80b609c4cbac860dba795`, SI-MH-0053 independent research audit preserved (no product code changes in that research checkpoint).
- [Actions 43605297383](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43605297383) `SUCCESS`, `Ran 208 tests in 23.545s / OK`, 8 migrations including G01 0008; `WORK03B_R2_R1D_G01_LAB_POLICY_LIVE_PASS`, `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS`.
- The R2 G01 policy lifecycle is enabled only when lab environment + local `rw_test` + R1C verify route + separate G01 flag are explicitly configured.

## New verified-by-code safeguards (CI PENDING)

Existing `PolicyLifecycle._write` idempotency returned a previous event if policy id and type matched. It did **not** check the previous reason code, supersession successor or the expected previous policy generation; it also allowed an old PROPOSED idempotent retry after the policy was terminally DISABLED. This checkpoint makes replays require exact event payload, correct expected previous generation (per-policy predecessor sequence, not global sequence -1), and refuses replays of earlier proposal/approval after terminal disable/supersession. An identical DISABLED event retry remains idempotently readable.

Eight new tests `test_15`.. `test_22`, using only synthetic /rw_test:
- mismatched disable reason fails;
- mismatch supersession successor fails;
- changed approval expected generation fails;
- old proposal retry fails after disable;
- cross-org HUMAN cannot propose target policy;
- PostgreSQL-clock expiry **after** MockTransport provider fetch but before ledger append rejects without new attempt;
- **two genuinely separate spawned Python processes**, verifier and disabler with different PostgreSQL transactions: verifier pauses at MockTransport provider, disabler commits DISABLED, verifier resumes and must raise Conflict without attempt insertion; PID separation and child exit codes asserted;
- identical DISABLED idempotent retry succeeds without duplicate rows.

The provider used by these tests is `httpx.MockTransport`, NOT live GitHub; the pre-existing separate CI G03 runs live GitHub HTTPS and must still pass. **216 total tests expected (208+8), NOT VERIFIED** until the new commit's CI completes.

## Remaining gates

G01-12 **real PostgreSQL backup + restore remains OPEN**; this checkpoint does not pretend normal new-connection persistence equals restorable backup. Independent process race under one deterministic ordering does not prove all possible races, nor network attack resistance. Production tenant consent/source ACL/retention, OIDC identity, DB RLS, rate limiting, key management and G04/G05 production release remain BLOCKED. No public lifecycle route, no reviewer/DONE, no schema changes, and no modification to main, Jarvis, Pulse, or pinned Mem0.

Next: observe GitHub Actions for 216 tests + existing eight migrations + G03 real provider marker and Mem0/Ollama. If failure, publish exact diagnosis in following append-only checkpoint.
