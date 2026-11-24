# SI-MH-0075 — ENG-E1-03 independent review tooling verified in CI

**2026-11-24 Africa/Maputo. STATUS: VERIFIED OFFLINE REVIEW INFRASTRUCTURE; E1_DATA_READY SCIENCE GATE REVIEW_REQUIRED.**

## Observed actual CI proof

- Source `develop@d160ad7aa3c5cd8554c10bc26d2a6caacdd72b40`, SI-MH-0074 narrow repair.
- [GitHub Actions 45344939725](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45344939725), job 138277116787, **completed SUCCESS**.
- Actual logs: `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`; eight `MIGRATION_PASS` for 0001–0008; `Ran 328 tests in 36.135s / OK` (303 existing + 25 new E1.1C).
- `E1_01_DATA_INTEGRITY_PASS records=84 queries=60 ... no_model_trained=true` and `E1_02_QUALITY_AUDIT_PASS documents=56 queries=32 provisional_labels=24 eval_unlabeled=8 ...` both PASS.
- New `E1_03_REVIEW_CONTRACT_PASS source_docs=42 questions=24 provisional_gold_exported=false eval_exported=false real_reviewers=0 adjudicated_gold=false`.
- `E1_03_SCIENCE_GATE REVIEW_REQUIRED independent_human_reviews=0 evaluator_gold=uncollected no_model_trained=true`.
- G01 real GitHub two-human authorization & append-only revocation `WORK03B_R2_R1D_G01_LAB_POLICY_LIVE_PASS`; actual PostgreSQL native logical restore `WORK03B_R2_R1D_G01_NATIVE_RESTORE_PASS`; two-agent lease and `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS` all PASS.

## Failure and fix provenance

[Initial run 45344586199](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45344586199) on SI-MH-0073 **FAILED**: 328 tests ran with one `FileNotFoundError` because `.runtime/` was absent during one test, and CI self-check had not run. SI-MH-0074 corrected scratch folder creation and omitted the provisional-label hash **key** from the exported packet, without removing integrity verification of all original dataset files. The 25-test suite and E1_03 marker now PASS.

## What exists and what still does NOT exist

- Offline export/validation tooling `backend/rightware_si/e1_03_review_protocol.py` and `scripts/e1_03_review.py`, with two **blank** local-review templates and strict 42-source/24-query train/dev coverage.
- Format for independently self-attested reviewer submissions plus exact evidence quotes, per-source grades, class agreement (Cohen's kappa), weighted ordinal agreement. Does not authenticate human identity, prove reviewer independence, prevent deception or adjudicate correct gold.
- All filled submissions restricted to Git-ignored `.runtime/`; this is not encryption, official retention policy or secure identity service. `E1_REVIEW_INFRA_READY` passes as a **software gate only**.
- **Independent human reviewers: 0**. **Adjudication: not performed**. **Evaluator-controlled independent held-out gold: not collected**. E1.1B's eight eval questions remain public and unlabeled, not a true blind benchmark. E1_DATA_READY stays **REVIEW_REQUIRED**.
- E1.2 BM25/dense/hybrid comparison, E1.3 trainable RIGHTWARE RW-R1, E1.4 calibrated abstention and E1.5 independent evaluation still NOT_STARTED. G04 real IAM/RLS and privacy/legal approval still OPEN.
- The A0-GLOBAL-02 sealed evaluator oracle remains untouched; no private customer data, public product API, SQL migration, main/JARVIS/PULSE/vendor Mem0 or task DONE changes.

## Next engineering handoff — explicit external dependency

**ENG-E1-04 / Human scientific review:** Operator must arrange **two real independent reviewers**, validate identities out-of-band, independently review train/dev without seeing rule-authored labels, then arrange a third adjudicator. Collect and encrypt submissions outside public Git, run local compare tool, investigate disagreements and manual semantic near-duplicate cases. Curator must establish a separate blinded evaluator-only dataset under access controls. Do not manufacture submissions, treat synthetically generated mock attestations as reviews, or start training as if E1_DATA_READY passed.

This SI-MH-0075 only appends this verified evidence and updates both handoffs. Its **own documentation CI is separately PENDING**.
