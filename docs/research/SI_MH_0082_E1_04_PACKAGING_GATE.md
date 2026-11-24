# SI-MH-0082 — ENG-E1-04 local packaging and human-input gate

**2026-11-24 Africa/Maputo. BASE:** develop@d0a13f571aa12595d954ef258914f11fbda7945b. SI-MH-0081 official continuity policy preserved; own CI [45353879662](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45353879662) in_progress/null. SI-MH-0080 [CI 45348458409](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45348458409) completed/success, 356/356 confirmed in SI-MH-0081. This is local operator tooling, not a new model, human review or benchmark. Initial publishing attempt stopped on concurrent HEAD advance; reconciled without overwriting.

## Delivery and observed verification
`scripts/e1_04_prepare_review.py` wraps the existing v2 exporter, refuses dirty checkout/wrong branch/unignored .runtime, creates a unique batch, validates blank packet integrity, archives four allowlisted files per reviewer, checks ZIP CRC/SHA256 and avoids overwrite; receipt and reverse map remain CUSTODY_ONLY. No recursive archive or network dispatch. .runtime and Unix directory mode are NOT encryption, Windows ACL management or verified custody.

Five actual local Python smoke checks on MOCK records passed: exact archive allowlist/CRC/hash and secret file exclusion, wrong slot rejection, nonblank grade rejection, bad packet hash rejection, exclusive ZIP creation. No real corpus export or human submission here. Browser sandbox has Chromium but exact remote form retrieval failed DNS/raw GitHub access; browser E2E NOT_RUN. Local helper SHA256 77d813126dc7f684eb938c2cf8d78a24f0b9d1ab130417835be795ee1a4cc301. New CI pending.

## Operator action (after checking new CI)
On clean develop, appropriately access-controlled and encrypted storage:
```powershell
git fetch origin
git switch develop
git pull --ff-only origin develop
python -m pip install -e .
python scripts/e1_04_prepare_review.py
```
PACKAGING_PASS identifies batch directory. Before dispatch, open the HTML locally using test copies of packet/blank; check 24 queries, blank submission refused, draft save/reload. Never count test drafts/submissions as human evidence. Share separate REVIEWER_A.zip and REVIEWER_B.zip only after verifying human independence and private custody. Never share CUSTODY_ONLY or full batch. Follow [runbook](e1_04/OPERATOR_RUNBOOK.md).

## Gate
0 documented human reviewers/submissions; adjudication and reserved holdout absent. E1_DATA_READY REVIEW_REQUIRED; BLOCKED_HUMAN_REVIEW until humans available. No actual exports or dispatch, no Core/API/SQL/G04/main/JARVIS/PULSE/vendor or sealed A0 changes. Next: local execution and independent reviewers; avoid further infrastructure churn absent a concrete issue. If humans unavailable, operator must explicitly decide on a separate provisional research scope; no silent bypass of E1 scientific gate.
