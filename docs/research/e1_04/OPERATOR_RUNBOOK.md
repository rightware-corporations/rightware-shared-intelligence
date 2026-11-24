# ENG-E1-04 — Human execution runbook (2026-11-24)
**State: PREPARED / AWAITING REAL HUMANS.** E1.1C P0/P1 CI [45346784374](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45346784374) verified 356 tests at SI-MH-0079; own SI-MH-0079 docs run [45347242669](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45347242669) success. No reviewer has been recruited or submitted a real review by this checkpoint.

## Operator — execute on local Windows clone
Use a private encrypted disk and a controlled account. Review data is synthetic only. First recover current develop HEAD and inspect its CI. If local edits exist, reconcile instead of reset. The commands use the **existing validated v2 Python exporter**, not the superseded v1 commands.
```powershell
git fetch origin
git switch develop
git pull --ff-only origin develop
git rev-parse HEAD
python -m pip install -e .
python scripts/e1_03_review.py --mode self-check
$root = ".runtime/e1_04_v2_" + (Get-Date -Format "yyyyMMdd_HHmmss")
python scripts/e1_03_review.py --mode export --output-dir $root
if ($LASTEXITCODE -ne 0) { throw "Export failed" }
foreach ($slot in @("A","B")) {
    $dest = Join-Path $root ("reviewer_" + $slot)
    Copy-Item docs/research/e1_04/REVIEWER_OFFLINE.html $dest
    Copy-Item docs/research/e1_04/REVIEWER_GUIDE_PT_EN.md $dest
    Compress-Archive -Path (Join-Path $dest "*") -DestinationPath (Join-Path $root ("REVIEWER_" + $slot + ".zip"))
}
Get-ChildItem $root
Get-FileHash (Join-Path $root "REVIEWER_A.zip"),(Join-Path $root "REVIEWER_B.zip") -Algorithm SHA256
```
Never share the root directory or CUSTODY_ONLY. Use two separate approved private channels; archive hashes locally. Retain the exact original packet and mapping; do not regenerate after distribution. The HTML is a convenience form, not the authoritative Python validator. Browser smoke must be performed locally before sending (open each package, select matching files, check 24 questions, save a draft and reload it; blank must not export as completed). Verify no external network access; if form fails, use the original blank JSON with a local editor and the same rubric. Do not use a public form service.
 
## People
- Reviewer A: independent PT/EN competent person, preferably domain/operations.
- Reviewer B: independent PT/EN competent person, preferably retrieval/data evaluation. No shared review sessions, author involvement, prior gold access or AI-generated annotations.
- Adjudicator: third independent qualified person, reviews disagreements, not model predictions.
- Curator: independent of development, controls fresh holdout and secret gold; may coincide with adjudicator only if independence and separation are documented. Do not claim anonymity as proof of independence.

Check competence and prior exposure before assignment; give different pseudonyms. Keep real identities, permissions, consent, assignments and dates in private storage. Assign only when verified; do not post names publicly. Send guide and one respective ZIP. Both annotate 560 ratings (1,120 in total) and all 24 classes, independently. Receive exact completed SUBMITTED.json through approved private route. Do not alter reviewer originals.

## Compare only after both return
Save submissions in their own folders beneath the same original $root; do not overwrite BLANK or mapping. Run:
```powershell
python scripts/e1_03_review.py --mode compare --output-dir $root --a "$root/reviewer_A/SUBMITTED.json" --b "$root/reviewer_B/SUBMITTED.json"
```
This creates private agreement_PRIVATE.json; validate actual identities separately. No repeat selection based on high kappa; report class/rating exact agreement, Cohen kappa and weighted kappa (null when undefined), denominators, class/language distribution and conflict pair disagreement. Preserve raw submissions/hashes. Resolve disagreements with independent adjudicator, document rationale and remaining ambiguity. No fabricated signatures, revisions or consensus. Use private copy of the blank receipt template, not GitHub.

## External test: independent reserved holdout
See INDEPENDENT_HOLDOUT_PROTOCOL.md. Existing public E1.1B text/labels, even opaque IDs, are not a secret independent test. Do not use sealed A0-GLOBAL-02 for tuning. Obtain independent fresh evaluation data, isolate curator-held gold and run only after frozen experiment contract. Scope/authority/temporal and negative classes must be represented. No client data or live tenant credentials.

## Exit gate
E1_DATA_READY remains REVIEW_REQUIRED until two verified humans actually return independent reviews, adjudication and semantic leakage audit are complete, curator holds genuinely reserved gold with license/provenance/split commitments, and authorized scientific review accepts quality and limits. If humans are unavailable, record BLOCKED_HUMAN_REVIEW, not PASS. Until then E1.2–E1.5 and proprietary trained model remain pending. Keep G04 real identity/ACL/RLS and SI-RD v0.8 provider runs separate.
