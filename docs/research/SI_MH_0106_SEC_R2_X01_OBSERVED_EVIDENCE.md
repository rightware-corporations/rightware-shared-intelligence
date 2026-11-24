# SI-MH-0106 — SEC-R2-X01 observed baseline evidence

**2026-11-24 Africa/Maputo. Classification:** EXPERIMENT EXECUTED / TWO LAB HYPOTHESES REPRODUCED / NO CORRECTION AUTHORIZED. Operator authorization SI-MH-0104, frozen protocol SI-MH-0105, executed commit 054869d0fe134a6f25cdd45d97b9f60c612c8a9b. [CI 45439599363](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45439599363) / [DB diagnostic job 138606696905](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45439599363/job/138606696905). PostgreSQL 16.16, disposable marker passed. 32 tests in 5.789s, OK (29 baseline + 3 diagnostics). Nine observed trials. CI success means valid diagnostic instrumentation, not that stronger security properties passed.

## Observations
| Finding | Condition | Trials | Observed result | Classification |
|---|---|---:|---|---|
| SR-F01 | committed synthetic external identity deletion | 3 | signed reader DENY 3/3; existing restricted DB connection ALLOW 3/3; fresh restricted DB connection ALLOW 3/3 | REPRODUCED boundary divergence |
| SR-F02 early | grant revocation after first read | 3 | in-flight DENY 3/3; new request DENY 3/3 | PASS revalidation for tested ordering |
| SR-F02 late | grant revocation after final SQL fetch | 3 | in-flight ALLOW 3/3; new request DENY 3/3 | REPRODUCED delivery window |

F01 requires already provisioned restricted lab login credentials, not forged identity or acquired external credentials. Revocation of external identity is not revocation of that independent database authority. No cross-tenant data exposure, real account breach or production exploit demonstrated. F02 uses deterministic event ordering with a separately committed grant update, real SQL results and READ COMMITTED; not a measured temporal SLA or exploit against a deployed endpoint. All six F02 requests begun after committed revocation denied. In-flight reads were initiated and authorized earlier; the late window is a design finding, not a violation of an approved strict delivery cutoff (none yet adopted). Mutation/commit race NOT_RUN, read-only gateway. No independent human review. All experiments reported fixture restoration and unchanged payload baseline; F01 unrelated positive control passed. No randomized or stress test; three repetitions per condition are not a statistical guarantee.

## Sanitized raw CI markers
```
2026-11-24T16:39:32.4536876Z G04_A2_GUARD_PASS postgres_version_num=160016
2026-11-24T16:39:35.6817581Z SEC_R2_X01_F01 trial=1 signed=DENY existing_db=ALLOW fresh_db=ALLOW unrelated_control=PASS committed=true
2026-11-24T16:39:35.9064885Z SEC_R2_X01_F01 trial=2 signed=DENY existing_db=ALLOW fresh_db=ALLOW unrelated_control=PASS committed=true
2026-11-24T16:39:36.2355536Z SEC_R2_X01_F01 trial=3 signed=DENY existing_db=ALLOW fresh_db=ALLOW unrelated_control=PASS committed=true
2026-11-24T16:39:36.2686056Z SEC_R2_X01_F01_SUMMARY trials=3 divergence=3 fixture_restored=true
2026-11-24T16:39:36.5026660Z SEC_R2_X01_F02 trial=1 barrier=1 in_flight=DENY new_request=DENY committed=true isolation=read_committed queries=2
2026-11-24T16:39:36.7670353Z SEC_R2_X01_F02 trial=2 barrier=1 in_flight=DENY new_request=DENY committed=true isolation=read_committed queries=2
2026-11-24T16:39:37.0950382Z SEC_R2_X01_F02 trial=3 barrier=1 in_flight=DENY new_request=DENY committed=true isolation=read_committed queries=2
2026-11-24T16:39:37.1257770Z SEC_R2_X01_F02_SUMMARY barrier=1 trials=3 in_flight_allow=0 new_request_allow=0 fixture_restored=true
2026-11-24T16:39:37.4710048Z SEC_R2_X01_F02 trial=1 barrier=2 in_flight=ALLOW new_request=DENY committed=true isolation=read_committed queries=2
2026-11-24T16:39:37.8905025Z SEC_R2_X01_F02 trial=2 barrier=2 in_flight=ALLOW new_request=DENY committed=true isolation=read_committed queries=2
2026-11-24T16:39:38.2022878Z SEC_R2_X01_F02 trial=3 barrier=2 in_flight=ALLOW new_request=DENY committed=true isolation=read_committed queries=2
2026-11-24T16:39:38.2333586Z SEC_R2_X01_F02_SUMMARY barrier=2 trials=3 in_flight_allow=3 new_request_allow=0 fixture_restored=true
2026-11-24T16:39:38.2358930Z Ran 32 tests in 5.789s
2026-11-24T16:39:38.2359301Z OK
```

## Regression status at publication
synthetic-signed-credentials (138606696798): completed/success; g04-a2-real-postgres-isolation (138606696905): completed/success; real-mcp-mem0 (138606697064): in_progress/PENDING; e1-04-offline-browser-smoke (138606697235): completed/success.
```
2026-11-24T16:39:27.1643767Z Ran 98 tests in 0.711s
2026-11-24T16:39:56.9424872Z E1_04_BROWSER_SMOKE_PASS synthetic_only=true actual_humans=0 submitted=0 adjudicated=0 operator_dispatch=false science_gate=REVIEW_REQUIRED
```
Prior verified full CI 45378895388 at functional baseline SI-MH-0102: 356 Core + 98 A1 + 29 A2 and browser/integration PASS. This experiment run full workflow status must be checked separately; evidence commit does not alter previous observations.

## Baseline preservation and decisions
Verified remote diff SI-MH-0105: only appended three diagnostics to test_isolation.py, new test helper and docs. signed_reader.py, A1 module, schema.sql and ci.yml verified identical to SI-MH-0104. Existing migrations, backend runtime, main and LEARN unchanged. No corrective code, MCP or public deployment. Evidence publication is documentation-only. Original 28 G04 acceptance oracles unchanged; E1_DATA_READY REVIEW_REQUIRED. No production promotion.

## Next: operator analysis, not implementation
F01: define complete principal revocation semantics across credential, login binding, sessions and data-plane access; compare coordinated revocation and compartmentalized credential broker designs; no solution chosen. F02: decide explicit read authorization linearization point and whether in-flight read delivery is permitted or bounded/cancelled; separately define mutation commit semantics. No promise to retract previously disclosed data. Compare alternatives and measure operational tradeoffs before corrective scope; do not fix these findings or advance to MCP until operator reviews evidence. Record later full CI evidence without retroactively editing this checkpoint. Rollback only diagnostic additions if separately requested; preserve results. No release.
