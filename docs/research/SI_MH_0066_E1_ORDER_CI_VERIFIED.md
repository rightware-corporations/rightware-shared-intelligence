# SI-MH-0066 — E1 execution order R1 verified in repository CI

**2026-11-18 Africa/Maputo · VERIFIED DOCUMENTATION CI.** Parent `develop@5c618eb4080ed86500157d7a4275a5df54d07f7e`, SI-MH-0065.

GitHub [Actions 44320181640](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/44320181640), job 134856732253: **completed SUCCESS**. Observed log markers:
- `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`;
- PostgreSQL migrations 0001–0008, including `MIGRATION_PASS 0008`;
- `Ran 259 tests in 37.933s` and `OK`;
- `WORK03B_R2_R1D_G01_LAB_POLICY_LIVE_PASS`;
- `WORK03B_R2_R1D_G01_NATIVE_RESTORE_PASS`;
- `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS`.

## E1 operating decision

[Rightware E1 execution plan R1](RIGHTWARE_ENGINE_E1_EXECUTION_ORDER_R1.md) clarifies E1 as a complete **learning and evaluation phase** with five required internal milestones, not merely a dataset task:
E1.1 data/labels/splits/runner → E1.2 independent BM25/dense/hybrid baselines → E1.3 real learned RW-R1 reranker → E1.4 calibrated abstention/risk-coverage → E1.5 held-out scientific and vendor comparison under preregistered rules.

**This CI does not execute any E1 gates:** the 259 existing tests relate to E0 synthetic research and R2/G01/G04-A0 regressions. E1 train/dev/test corpus, trained weights, external vendor comparison and confidence calibration remain NOT_IMPLEMENTED. The sealed A0-GLOBAL-02 v0.8 private evaluation key and oracle have not been used for training or tuning.

**G04 separate parallel security line:** real OIDC, workload identity, PostgreSQL tenant memberships/ACL/RLS and private-source consent remain NOT IMPLEMENTED; offline synthetic scientific work can proceed, customer/private-data integration cannot. No G04 security development is implied by E1 plan approval.

No runtime code, schema, API, product, vendor Mem0, JARVIS, PULSE, main, task review/DONE or private source changes. This checkpoint records actual parent CI and both handoffs only. Its own documentation CI is separate, initially PENDING.

**Next exclusively active technical mission:** ENG-E1-01 (E1.1) independent licensed/synthetic dataset and leakage-audited splits plus reproducible evaluation runner, then E1.2–E1.5 without skipping training or calibration.
