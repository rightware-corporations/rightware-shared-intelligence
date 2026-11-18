# SI-MH-0068 — E1.1 dataset audit failure and narrow repair

**2026-11-18 Africa/Maputo. STATE: REPAIR PUBLISHED, NEW CI PENDING; PRIOR FAILURE PRESERVED.**

## Initial source and actual failure

- `develop@f027a1fdde4d6cda7cb4a8fc186d6d7b96931531`, SI-MH-0067.
- [Actions 44322381727](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/44322381727), job 134864432467 **FAILED** in `Full deterministic/real PostgreSQL test suite`. Full log: `ERROR: setUpClass (test_e1_01_data_eval.E101DatasetTests)`, `DataIntegrityError: non-synthetic document identifier`, `Ran 259 tests ... FAILED (errors=1)`. New E1.1 tests did not execute because setUpClass failed; do NOT report 283/283 on this run. Core migrations and handoff gate passed before failure.
- Root cause: dataset intentionally creates a synthetic `other-project` decoy in the **same organization but different project** `syn-other-project-<family>`. The new global identifier guard incorrectly demanded every document project begin with `syn-e1-project-`, rejecting a synthetic negative sample that is supposed to be outside the authorized project.
- Repair: global guard requires the safe `syn-` namespace; the **existing role-aware group validation** remains strict: authorized roles must exactly match group's official project, `other-project` must differ only in project, `foreign` must differ only in organization. This enforces the intended separation without admitting client identifiers or foreign source outputs.

## Retest required

- Same 84 documents, 60 queries, SHA256 manifest and 24 new tests **unchanged**. Total 283 expected (259+24) under new CI; do not claim PASS pending logs.
- Runner new CI step should output `E1_01_DATA_INTEGRITY_PASS` and `E1_01_E0_OFFLINE_DIAGNOSTIC` after full test suite and before real G01 GitHub smoke. If this step or unit tests fail, repeat exact evidence/fix checkpoint.
- E1.1 **SCIENCE_GATE REVIEW_REQUIRED** remains due shared templates, public rule-authored gold and lack of independent annotation; no `E1_DATA_READY`, trained RW-R1, external vendor comparison or calibration.

No dataset/regression deletion, no SQL migration/API/production/private source/JARVIS/PULSE/vendor changes. G04 real OIDC/RLS still OPEN, A0-GLOBAL-02 sealed challenge untouched.
