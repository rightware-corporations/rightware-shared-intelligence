# SI-MH-0070 — ENG-E1-02: hardening E1.1B data quality and independence

**2026-11-18 Africa/Maputo. STATE:** ENGINEERING IMPLEMENTATION / NEW CI PENDING; scientific readiness REVIEW_REQUIRED.

**Verified baseline:** `develop@0ccfa21b8650a95d9cff0ac6cdd918556f5542cb` SI-MH-0069, [Actions 44323888002](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/44323888002) completed **SUCCESS 283 tests**, eight migrations, E1_01 integrity, G01 GitHub real/natively restored PostgreSQL, MCP/Mem0/Ollama. E1.1 previous dataset 84 docs/60 queries remains unchanged.

## New implementation

- `docs/research/e1_02/documents.jsonl`: **56 original synthetic documents, eight distinct domain groups**, seven roles per group (current valid official, adjacent valid official, superseded expired, unverified, restricted foreign tenant, other project, generic distractor).
- `docs/research/e1_02/queries.jsonl`: **32 PT/EN queries** including open-ended, negative and foreign-only questions, but query files do not encode gold result classes.
- `docs/research/e1_02/labels_provisional.jsonl`: **24 rule-derived provisional labels for train/dev only**; **8 eval queries UNLABELED**. No evaluator gold is present and none has been reviewed by humans.
- `docs/research/e1_02/manifest.json`: SHA256 pins for all JSONL files, split counts (train 4 groups/28 documents/16 queries; dev 2/14/8; eval 2/14/8), original-license declaration and explicit science REVIEW_REQUIRED.
- `backend/rightware_si/e1_02_quality.py`: schema, split, scope/tenant/project, validity, gold eligibility, 4-token normalized cross-split near-duplicate audit, shared-project design and strict prohibition on eval gold. E0 diagnostics on train/dev **only**, not evaluation.
- `scripts/e1_02_audit.py`: reproducible CLI, prints E1_02_QUALITY_AUDIT_PASS and E1_02_SCIENCE_GATE REVIEW_REQUIRED.
- `tests/test_e1_02_quality.py`: **20** negative-first tests including exact/near-dupe, eval-label injection, foreign/source/expired/unverified gold, non-production import and reproducibility; expected suite **303 tests (283+20), NOT PASS until CI**.
- [Annotation and review protocol](e1_02/ANNOTATION_RUBRIC_R0.md): two truly independent reviewers, evidence spans, negative-case taxonomy, adjudication and evaluator-only held-out gold. **No reviewer was appointed, no review done, no gate accepted**.

## Methodological limitations

8 eval questions are *unlabeled* and unscored, not independently blind (documents and questions are in a public Git repository). Existing version E1.1 and sealed A0-GLOBAL-02 benchmark remain unchanged. A 4-gram Jaccard filter catches some copied paraphrases but cannot detect semantic overlap without further human review. All texts are authored synthetic samples, so the corpus is not yet sufficiently independent for generalization or vendor benchmarking. It intentionally reuses projects within splits to prevent trivial group-by-project selection; real tenant access continues to be governed by G04, not this code.

Do not call E1_DATA_READY until independent annotations, inter-rater checks, human semantic leakage audit, provenance and held-out evaluator gold are validated. E1.2 baselines, E1.3 learned RW-R1, E1.4 calibrated abstention and E1.5 blind comparative evaluation **remain NOT_STARTED**. No runtime database/API/G04/OIDC/private source, main/JARVIS/PULSE/vendor Mem0 changes, no DONE.

**Next:** Verify new CI; if PASS, keep science gate open and arrange independent reviewer submission before E1.2. Retain any failure and append a repair checkpoint.
