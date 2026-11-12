# WORK-03B R2 R1C — SI-MH-0034: GitHub CI Results and Test Discovery Repair

**2026-11-12, Africa/Maputo** · **SOURCE-BACKED EVIDENCE REVIEW + TEST HARNESS FIX** · Not production acceptance.

## Confirmed Actions runs / exact Git SHAs

| SI checkpoint | Commit | GitHub Actions | Observed result |
|---|---|---|---|
| SI-MH-0030 | `0eb4e662490ffb22a18cdb5e21ac4c85c14066d4` | [43244269984](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43244269984) | SUCCESS (documentation/handoffs) |
| SI-MH-0031 | `3567c99dfa620f3bf23eaf8fa0b1b030c42f131c` | [43247901257](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43247901257) | SUCCESS, **Ran 142 tests**, OK; 7 migrations, live GitHub and Mem0/Ollama E2E |
| SI-MH-0032 | `2cec2c26bdbf63f0ae4b33986ad087c8a70c30b9` | [43249446536](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43249446536) | **FAILURE**, Ran 174 tests, FAILED (failures=2), downstream external E2Es skipped |
| SI-MH-0033 | `9de64471980ad3826b31c92160072fc8a457bb17` | [43249997206](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43249997206) | **SUCCESS**, Ran 174 tests, OK, all seven migrations and E2Es passed |

## Failure explanation and repair actually proven

CI SI-MH-0032 failed in static contracts:
1. `test_r2_r0_contract.R2DraftIntegrityTests.test_04_future_r2_routes_not_in_actual_fastapi_decorators` — historical R2 R0 test falsely expected no FastAPI decorator for future verify endpoint. The R2 R1C LAB feature adds the decorator but only registers the route when explicitly enabled in isolated laboratory.
2. `test_work03b_contract.ContractR0Tests.test_future_routes_not_misrepresented_as_live` — same mistake in canonical route inventory.

SI-MH-0033 repaired both tests and marked the verification route `IMPLEMENTED_R2_R1C_LAB_FLAGGED_OFF_BY_DEFAULT`, preserving two unimplemented future routes and pending M01–M18. The next CI **43249997206 SUCCESS**, including `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`, migrations 0001–0007 PASS, and these explicit smoke markers:

- `WORK03B_R2_R1A_GITHUB_LIVE_PASS`: provider read-only GitHub run identity, no task DONE.
- `WORK03B_R2_R1B_LEDGER_LIVE_PASS`: GitHub real API → authenticated SERVICE → PostgreSQL append-only; task IN_REVIEW, evidence REFERENCED, no review/DONE.
- `WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS`: independent agents, checkpoint binding, monotonic fencing and replay denial, Mem0 off.
- `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS`: actual MCP stdio, REST, PostgreSQL, Mem0 OSS, Ollama embeddings, tenant denials and revocation on synthetic data.

These smokes are **existing R1A/R1B/R1C and WORK02D regression tests**. The new HTTP R2 R1C tests use `httpx.MockTransport`, not a new live GitHub-over-HTTP-endpoint smoke; they prove synthetic HTTP→PostgreSQL contract under a fixture, not a production-identity/consent/release gate.

## New evidence-integrity issue: 174 executions vs 158 distinct tests

The SI-MH-0032/SI-MH-0033 suites actually ran **174 tests**, but that number includes **16 duplicates**. `tests/test_r2_r1c_api_lab.py` imported the **unittest.TestCase class `VerificationLedgerLabTests`** directly from `test_r2_r1b_ledger.py`. `unittest discover` then collected those 16 tests once from the original R1B module **and again from the imported symbol in the R1C module**.

This checkpoint corrects that test harness error only: import `test_r2_r1b_ledger as r1b_fixture`, and instantiate `r1b_fixture.VerificationLedgerLabTests` without exposing the TestCase class name in R1C module's global namespace. Unique planned count: **131 baseline +11 R2 R1C static +16 R2 R1C REST = 158**. The fix is NOT called PASS before the CI of this new commit runs. Duplicate tests were real executions, not fake results, but do not represent independent additional coverage.

## Explicitly not established

- No R2 R1C **live provider invoked through new REST endpoint** was demonstrated; new HTTP tests injected a mock transport and must be labeled `SIMULATED_TRANSPORT`.
- No current production OIDC/workload attestation, per-source ACL/consent/retention, policy lifecycle/expiry/revocation, rate-limiting, independent human review, task DONE, or external-effect outbox.
- The 16 original SI-RD-03C scenarios stay investigation fixtures `executed=false`; only EV-01..04 were separately observed LIVE via GitHub run, EV-05..07 simulated. The R2 R1C API-NEG catalogue is not exhaustively fulfilled (expiry/disable and some privacy requirements blocked).
- No changes to main, JARVIS, PULSE, vendor Mem0, server deployment, provider integrations or DB schema in SI-MH-0034.

**Next:** verify CI for the new commit, observe **158 tests** and all gates, then append a follow-up SI-MH-0035 PASS/FAIL based solely on the actual run. If CI fails, preserve failure logs and correct instead of certifying.
