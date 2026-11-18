# SI-MH-0065 — E1 scientific priority and execution sequence clarified

**2026-11-18 Africa/Maputo · Type:** OFFICIAL REAFFIRMATION OF ENGINE PRIORITY + RECOMMENDED GATED EXECUTION ORDER; documentation-only. **New CI PENDING.**

Verified basis: `develop@9461e8c8cc4ab506ad9441ea2910c058cd1b26b7`, [Actions 44314535706](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/44314535706) **SUCCESS 259 tests/8 migrations**, R2 G01 GitHub LIVE native restore, MCP/Mem0/Ollama. E0 standalone research is tested but no ML model is trained.

The operator explicitly corrected the plan so **E1 means Learning AND Evaluation as a whole**, not only data preparation: independent training/validation, **first trainable RIGHTWARE ranker**, fair comparisons with BM25 and actual external vendors, and **confidence/abstention calibration**, using BEIR/LongMemEval/RAGAS as scientific methodology. No unmeasured superiority or completed scientific gate is implied.

New [E1 execution order R1](RIGHTWARE_ENGINE_E1_EXECUTION_ORDER_R1.md) freezes:
- E1.1 ENG-E1-01 dataset + license/labels + leak-free splits, evaluation runner;
- E1.2 BM25/dense/hybrid reproducible baselines;
- E1.3 RW-R1 trainable reranker, actual learned weights/model card;
- E1.4 calibrated risk–coverage/abstention/conflict;
- E1.5 held-out, PT/EN, temporal/authority, blind vendor comparison, costs/confidence intervals.
G04 IAM/tenant remains a parallel **independent** security workstream. Synthetic E1 does not need production identity, but private source, deployment and customer integration are blocked by G04-A1/A2 and privacy requirements. All five E1 gates are **NOT_IMPLEMENTED**, 28 G04 real acceptance oracles also NOT_IMPLEMENTED. Sealed SI-RD A0-GLOBAL-02 oracle remains untouched. No new code, migrations, API, production or private data.

This SI-MH-0065 has only execution-plan document and two handoffs, with new CI pending. Next actual mission: E1.1/ENG-E1-01; do not declare E1 complete until E1.5 and independent review.
