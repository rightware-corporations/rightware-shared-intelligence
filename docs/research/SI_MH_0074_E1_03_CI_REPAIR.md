# SI-MH-0074 — ENG-E1-03 CI failure and narrow local-workflow repair

**24/11/2026 Africa/Maputo. STATE: FAILURE DOCUMENTED + FIX IMPLEMENTED; NEW CI PENDING.**

## Initial run: FAILED, do not report as PASS

- Source `develop@249f82d0c70003e71e9d6bae298907e8a8eeefb9` SI-MH-0073.
- [GitHub Actions 45344586199](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45344586199), job 138275989859: **FAILED** in `Full deterministic/real PostgreSQL test suite`. Actual log: `Ran 328 tests in 33.746s`, `FAILED (errors=1)`. The only E1.1C regression error was `test_24_private_file_exclusive_create_prevents_overwrite`: `FileNotFoundError` because the CI checkout has no `.runtime/` directory before `TemporaryDirectory(dir=ROOT/".runtime")`. All other 24 E1.1C unit cases passed.
- The CI stopped before the new `E1.1C independent reviewer packet contract and no-gold gate` step, so `E1_03_REVIEW_CONTRACT_PASS` **was NOT observed** on the failed run. An unrelated `UnexpectedToolError` trace in test logs was part of earlier expected negative tests and not the one observed test-suite error.

## Repair and additional preventive fix

1. In `tests/test_e1_03_review_process.py`, create `.runtime/` explicitly before making a temporary test directory. This folder remains Git-ignored; no real review submissions are written or committed. Preserve the exclusive-create no-overwrite assertion.
2. In `e1_03_review_protocol.make_packet`, only include the SHA256 of **documents and queries**. The first draft also included `labels_provisional` as a hash-key; while no gold *values* were exported, the CLI self-check conservatively rejects that label metadata key. Omit the label key without weakening integrity: `read_data` already verifies SHA256 for all three original JSONL inputs and `audit` checks the dataset before packet creation.
3. Extend existing `test_02_packet_does_not_expose_rule_labels_or_roles` to ensure the string `labels_provisional` does not occur anywhere in the exported packet. No completed or fake human reviews and no evaluator gold.

**Test count:** same 25 new E1.1C tests; 328 expected total under new CI, not yet PASS. All 56 E1.1B synthetic documents, 32 queries, 24 provisional train/dev labels and the 8 unlabeled eval questions stay unchanged with original hashes. Test-only mock pseudonyms are not independent reviewers. `E1_DATA_READY` remains REVIEW_REQUIRED.

No product APIs, real IAM, DB migrations, private credentials, JARVIS, PULSE, vendor Mem0, branch main, production or automated task DONE changes.

**NEXT:** Verify new CI is completed SUCCESS with 328/328, `E1_03_REVIEW_CONTRACT_PASS`, migrations and G01/Mem0 regressions. Append new evidence checkpoint; never rewrite previous FAIL.
