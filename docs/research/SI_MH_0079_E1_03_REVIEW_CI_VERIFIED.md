# SI-MH-0079 — E1.1C reviewer opaque IDs and contradiction annotation CI VERIFIED

**2026-11-24 Africa/Maputo · STATE: VERIFIED OFFLINE SOFTWARE CONTRACT; E1_DATA_READY REVIEW_REQUIRED.**

## Verified CI provenance

1. **P0 alias patch:** `develop@a09cd71413c559380de8cffd0f5b992a1cb62581`, [Actions 45346421772](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45346421772), job 138281973103, completed **SUCCESS**, `Ran 341 tests in 31.105s / OK`, `E1_03B_OPAQUE_IDS_PASS reviewer_A_B_independent=true original_ids_exposed=false crosswalk_private=true eval_gold_exported=false actual_reviewers=0`, eight migrations and R2 GitHub LIVE/PostgreSQL native restore, Mem0/Ollama E2E PASS.
2. **P1 contradiction v2:** source `develop@65c2e8b0315af898e5b0771beed123001665775b`, [Actions 45346784374](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45346784374), job 138283161244, completed **SUCCESS**. Observed `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`, migrations 0001–0008 PASS, `Ran 356 tests in 33.764s / OK`, `E1_03B_OPAQUE_IDS_PASS`, `E1_03_SCIENCE_GATE REVIEW_REQUIRED public_corpus_is_not_blind=true human_reviews=0`, `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS`. The 15 new tests (341→356) exercise v2 `conflict_claims` and alias reconciliation.
3. Original E1.1C source SI-MH-0073 [Actions 45344586199](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45344586199) had **FAILED (1 error of 328 tests)** from absent `.runtime/`; SI-MH-0074 fixed it; SI-MH-0075 code CI [45344939725](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45344939725) SUCCESS 328/328. Never reinterpret failed run as PASS.

## Engineering result vs scientific gate

- Two reviewer-specific packets now use random opaque aliases; original predictable q1/d1 patterns are not distributed; reverse crosswalk and agreement remain under Git-ignored `.runtime/CUSTODY_ONLY` with no public labels/eval.
- A versioned v2 reviewer contract separates **authority support grade** from cited contradiction, including unverified opposing claims, while refusing to treat them as eligible positive proof. This is structural validation; code cannot semantically verify that two factual claims actually contradict each other.
- **No actual independent human reviewers; no third-party adjudication; no real blinded evaluator-only gold.** The E1.1B source texts and provisional labels remain public and searchable. These aliasing tests do not make them blind. `E1_DATA_READY=REVIEW_REQUIRED`.
- The synthetic data and all sealed SI-RD A0-GLOBAL-02 oracle keys remain unchanged; no new trained RW-R1, E1.2 fair baselines, E1.4 calibration or E1.5 scientific comparison.
- G04 real HUMAN OIDC/SERVICE identity, tenant membership/ACL/RLS, legal consent/deletion and private data deployment are separate OPEN gates. No SQL migrations/API/client sources/production, reviewer/DONE, main, JARVIS/PULSE or vendor Mem0 changes.

## Exact next action

**ENG-E1-04 — Human annotation and evaluator custody:** nominate two truly independent domain reviewers and a third adjudicator; authenticate reviewer identity outside the software, deliver only **new v2** A/B packets separately, never old v1; store raw reviews and private crosswalk outside Git, record agreement and adjudicate conflicts. Commission a separate hidden externally curated dataset with legally permitted sources and evaluator-only gold. Do not claim E1_DATA_READY until independent oversight actually signs off.

**This SI-MH-0079:** evidence report + two handoffs only. Own documentation CI separate and initially PENDING.
