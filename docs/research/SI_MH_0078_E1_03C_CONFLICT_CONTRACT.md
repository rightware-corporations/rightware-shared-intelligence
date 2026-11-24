# SI-MH-0078 — ENG-E1-03C: separate contradiction annotation from authoritative support

2026-11-24 Africa/Maputo. Base `develop@a09cd71413c559380de8cffd0f5b992a1cb62581`. CI SI-MH-0077 [45346421772](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45346421772): completed/success. **Implementation, new CI pending; no human submissions.**

## Problem and contract
P1 from SI-MH-0076: v1 required two grade>=2 official sources for AUTHORITY_CONFLICT and prohibited positive grades on UNVERIFIED_CLAIM. Typical official-versus-unverified contradictions could not be represented. Newly issued opaque A/B packets use review schema v2 and custody map v2. Legacy v1 remains readable only for historical isolated tests; old packet/custody versions are rejected by current opaque comparison. Do not distribute earlier packets.

Each v2 judgment adds `conflict_claims: []`. Ratings remain *authoritative answer-support grades* (0–3); an unverified source must remain grade 0, even when relevant as a contradiction. A human who selects AUTHORITY_CONFLICT must explicitly identify a current, same-scope eligible official anchor graded 2–3, a distinct current same-scope opposing source, its literal quote and rationale. An opposing official source needs grade 2–3; an unverified opponent remains 0. Foreign/project-mismatched, stale/future, fabricated spans, duplicates, wrong schema and conflicts on non-conflict classes are rejected. No semantic verification of contradiction is claimed: the annotator's rationale requires human adjudication.

## Reconciliation
Private crosswalk canonicalizes both source aliases and conflict pairs across A/B. Comparison reports number of queries with differing conflict pairs separately from authority-grade agreement. It remains a technical schema check, not proof of independent humans or approved gold. No change to corpus/hashes or any held-out/ sealed labels.

## Verification
15 new unit tests use explicitly MOCK submissions, including real fixture-shaped official/unverified pair, no unauthorized positive grade, missing/foreign/expired/cross-project/forged/duplicate pairs and A/B agreement. Existing 341-test suite expected +15 = 356 tests, conditional on previous CI success; **not executed locally** (container cannot resolve github.com; connector can commit and inspect CI). No scientific metrics or human reviews executed. New CI must be checked before distributing packages.

## Operator procedure (after CI success)
Use a fresh local output directory; never reuse or overwrite old reviewer forms. 
```powershell
python scripts/e1_03_review.py --mode self-check
python scripts/e1_03_review.py --mode export --output-dir .runtime/e1_03_v2
```
Share reviewer_A and reviewer_B separately only with independent humans who did not author or inspect provisional labels. Keep CUSTODY_ONLY and all completed submissions private; distinct pseudonyms are not proof of identity. Reviewers should distinguish official support from unverified contradicting claim and provide rationale. Public train/dev text is discoverable; independent evaluator must author/hold a new genuinely reserved holdout. Third human adjudicator resolves conflicts; record independence, evidence spans, agreement and unresolved items.

**Gate:** E1_DATA_READY REVIEW_REQUIRED; no actual reviewer, adjudicator, independent gold or E1.2–E1.5 run. G04 real identity/RLS, private/client data and production remain separate blocked gates. No SQL/API, runtime integration, main, JARVIS/PULSE, vendor Mem0 or sealed A0-GLOBAL-02 edits. Rollback: revert this bounded offline research change via new commit and both handoffs; do not distribute v1 packets.
