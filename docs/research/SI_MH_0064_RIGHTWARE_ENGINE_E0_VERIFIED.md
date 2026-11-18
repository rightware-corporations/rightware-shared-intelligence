# SI-MH-0064 — RIGHTWARE Intelligence Engine E0: verified 259-test lab baseline

**Date:** 2026-11-18 Africa/Maputo. **Classification:** VERIFIED RESEARCH PROTOTYPE; NOT PRODUCTION, NOT A TRAINED FOUNDATION OR SPECIALIZED ML MODEL.

## Observed upstream source

- Source commit `develop@7aa7ae0749d6f0606eba65fa2d3dc0249a53ff87` (SI-MH-0063) contains research-only `experimental_engine_e0.py`, 22 new unit tests, strategy and scientific protocol. Research was explicitly requested to establish the RIGHTWARE-ownable intelligence motor independently of simply wrapping vendor memory/LLM products.
- [GitHub Actions 44313829879](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/44313829879), job `134834575340`: **completed SUCCESS**; `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`; migrations 0001..0008 `MIGRATION_PASS`; `Ran 259 tests in 32.131s / OK`.
- R2 GitHub LIVE independent SERVICE/G01 two HUMAN approvals/revocation marker `WORK03B_R2_R1D_G01_LAB_POLICY_LIVE_PASS`, native PostgreSQL `WORK03B_R2_R1D_G01_NATIVE_RESTORE_PASS`, bound two-agent recovery and `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS` were all observed in the same successful run.

## What the 22 engine E0 tests establish — and do NOT establish

E0 tests use **synthetic fake records, fake pre-authorized scope, offline BM25** and in-memory provenance markers. They demonstrate deterministic candidate ordering, scope-before-rank, time validity, no future evidence, refusal of unverified-only answers, conflict detection in authoritative synthetic claims even beyond top-k, no foreign source ID leakage, no public runtime import, and Portuguese lexical normalization. **No engine retrieval accuracy benchmark, human factual correctness, learned weights, confidence calibration, multi-tenant authorization or external model comparison was run.**

BM25 is open established science, not proprietary IP. The user-facing phrase *motor próprio* is a **strategic design direction** to create own future learning/ranking/confidence/provenance methods and datasets under license; an ML-trained RIGHTWARE ranking model **does not yet exist**. `EVIDENCE_CANDIDATE` means a candidate requiring verification, not proven answer or task DONE.

The sealed [SI-RD-03A A0-GLOBAL-02 v0.8 package](SI_RD_03A_A0_GLOBAL_02_PREREG_2026-11-14.md) (82 sources, 56 PT/EN queries, hidden evaluator oracle) remains unmodified and must never be used for feature tuning/training/threshold selection. Vendor PostgreSQL Server, Mem0, Hindsight comparison remains unrun for that pre-registered challenge at this checkpoint.

G04-A0 limited synthetic policy remains, but **real G04-A1 OIDC/workload identity, G04-A2 resource ACL/RLS and all 28 original G04 DB/E2E oracles remain NOT IMPLEMENTED**. No production/client data/private source, migrations/HTTP/MCP changes, JARVIS/PULSE integration, main/vendor Mem0 edits, reviewer/DONE or source selection.

## Next research and security gates

1. Define independent licensed/synthetic E1 train/dev dataset and annotation QA; freeze splits and exact baselines before model fit.
2. Implement feature-extracting E1 ranker interface and model card; evaluate supervised features in held-out data, calibration, ablation and bootstrap confidence intervals; do not tune on sealed A0-GLOBAL-02.
3. Separately choose real identity issuer/workload technology G04-A1; develop DB-enforced G04-A2 tenant ACL and RLS only after the respective approval. The engine's fake scope flag is not authorization.
4. Keep branch protection and D06–D11 open until actually ratified and configured.

This checkpoint itself changes only this evidence document and BOTH handoffs. Its own docs-only CI is separately pending.
