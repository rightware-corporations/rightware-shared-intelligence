# ENG-E1-01 / E1.1 — Data foundation for RIGHTWARE Intelligence Engine

**2026-11-18 (Africa/Maputo). Status: ENGINEERING DATASET + E0 EVALUATION PIPELINE IMPLEMENTED; OWN CI PENDING; SCIENTIFIC DATA GATE REVIEW_REQUIRED.**

## Baseline and priority

`develop@134739d4ae7a89ce01931a365d9ae045e21c49f6`, SI-MH-0066. [Actions 44320181640](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/44320181640) SUCCESS 259 existing tests, eight PostgreSQL migrations, G01 real GitHub / native PostgreSQL logical restore, MCP/Mem0/Ollama. Current SI-MH-0066 own documentation run 44320844769 was observed completed SUCCESS before this commit. The operator authorized **ENG-E1-01** as the sole main engineering task, part of E1.1 only; E1 as a whole still includes own RW-R1 training, fair comparisons and calibrated decision.

## Exact deliverables

- `docs/research/e1_01/documents.jsonl` — 84 versioned authored synthetic documents, 12 family/project groups (7 each: current primary + secondary, expired, unverified, general distractor, another organization and another project). These are NOT actual licensed customer documents.
- `docs/research/e1_01/queries.jsonl` — 60 labelled PT/EN questions, 5 per family: three answerable with explicit source-grade maps and two negatives (unanswerable, forbidden-source-only). 36 positive and 24 negative. Labels are **rule-authored from templates, not independently human reviewed**.
- `docs/research/e1_01/manifest.json` — SHA256 of both JSONL files, 6 families/30 queries train, 3/15 dev, 3/15 test; counts, authorship, known structural templating caveat and review status.
- `backend/rightware_si/e1_01_data_eval.py` — offline full-input SHA256 + schema/split/group/project/exact-content leakage audit, gold source active/official/authorized check, deterministic E0 BM25 retrieval diagnostic and correct per-query hit@1,@2,@5/MRR@5/nDCG@5, negative emission counts; fail closed if *any* foreign source ID appears.
- `scripts/e1_01_evaluate.py` — CLI: `python scripts/e1_01_evaluate.py --dataset docs/research/e1_01 --output /tmp/e1_01_metrics.json`. No GitHub token, external vendor, private sources, embeddings or LLMs.
- `tests/test_e1_01_data_eval.py` — 24 new unit tests: exact hashes, counts, isolation, expired/foreign/unverified labels, invalid timestamps, deterministic reproducibility, negative denominators, metric math, no production wiring.
- CI step executes runner and checks `E1_01_DATA_INTEGRITY_PASS` before external G01 lab smoke.

## Caveats / scientific gate

This is a **controlled engineering fixture**, not a blind benchmark or independently validated training corpus. The same author wrote the synthetic documents and labels, source patterns are structurally shared across splits, dataset is small and test labels are visible in Git; this prevents a defensible generalization claim. **Do not declare `E1_DATA_READY` or train/publish scientific RW-R1 performance** until independent human labeling, improved corpus diversity, source/time/task leakage review and suitable held-out evaluation are completed. The runner's scores describe only E0 on these controlled fixtures and are **not** vendor comparative results.

Sealed `SI-RD-03A A0-GLOBAL-02 v0.8` evaluator/challenge remains uninspected for tuning and must not enter model training or threshold selection. The E1.1 label audit does not validate G04 private-source authorization. OIDC/RLS and 28 real G04 acceptance tests remain unimplemented.

**Next:** Verify new CI and exact metrics; follow-up expand independent expert-reviewed annotation and data diversity, then E1.2 baselines. Do not skip own trained RW-R1 in E1.3 or decision calibration in E1.4. No new DB migrations/HTTP/MCP APIs, no production, no main/JARVIS/PULSE/vendor Mem0 modifications.
