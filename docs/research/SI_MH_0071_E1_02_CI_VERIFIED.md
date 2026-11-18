# SI-MH-0071 — ENG-E1-02 E1.1B CI verified, negative controls still weak

**2026-11-18 Africa/Maputo. Classification:** VERIFIED ENGINEERING AND DATA QUALITY AUDIT; SCIENTIFIC `E1_DATA_READY` STILL REVIEW_REQUIRED. Parent: `develop@6260fc220b7112382de80608cc1593c756b6af52` (SI-MH-0070).

## Actual GitHub Actions proof

[GitHub Actions 44327416091](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/44327416091), job 134882338189, **completed SUCCESS**. The actual job log confirms:
- `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`.
- Migrations 0001–0008: all `MIGRATION_PASS` (no new migration).
- `Ran 303 tests in 33.807s / OK`: 283 previous + 20 E1.1B negative-first quality tests.
- `E1_01_DATA_INTEGRITY_PASS records=84 queries=60 ...` previous corpus unchanged.
- `E1_02_QUALITY_AUDIT_PASS documents=56 queries=32 provisional_labels=24 eval_unlabeled=8 shared_projects=true cross_split_near_dup_checked=true`.
- `E1_02_SCIENCE_GATE REVIEW_REQUIRED reviewer_a=missing reviewer_b=missing adjudication=missing evaluation_gold=not_collected no_model_trained=true`.
- Actual R2 G01 GitHub policy LIVE, PostgreSQL native logical restore, R1C bound-agent recovery and `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS` confirmed in the same successful job.

## Actual E0 diagnosis — NOT scientific model performance

| Split | Answerable provisional | E0 hit@1 on positive | Negative queries | E0 negative candidate emissions | Out-of-scope sources |
|---|---:|---:|---:|---:|---:|
| train | 8 | 7 | 8 | 8 | 0 |
| dev | 4 | 3 | 4 | 3 | 0 |

This new corpus is more challenging than the former single-project family structure: distinct topics COMPETE inside a common authorized project per split, with current/adjacent, expired, unverified, foreign tenant, other-project and generic distractor sources. E0 hit@1 falls below 100% on synthetic labels, and candidate emission for negative questions remains high. These are diagnostic counts, **not independently adjudicated retrieval ground truth or proof of generated hallucination**; E0 only emits evidence candidate IDs. The 8 eval queries were **not scored** and have **no gold**.

## Scientific gate

**E1.1B engineering audit PASS.** **Scientific E1_DATA_READY NOT APPROVED.** Required:
1. Independent reviewer A and reviewer B, not the data author; separate source relevance and query-answerability labels and evidence spans.
2. Blind-ish adjudication, unresolved disagreements, inter-rater agreement and documented rubric adherence; true sealed evaluator labels kept outside public Git.
3. Domain and semantic near-duplicate leakage audit by humans and licensed-source provenance for any non-synthetic addition.
4. More realistic negative, temporal and authority-conflict cases with independently authored assessment.
5. Pre-registered acceptance metrics, train/dev/test treatment, and no use of the unrelated sealed SI-RD-03A A0-GLOBAL-02 oracle for tuning.

The E1.1B manifest and reviewers protocol explicitly note human reviewers **zero**; project-sharing and normalized four-token Jaccard threshold 0.65 check only structural/lexical leakage. No E1.2 vendor baselines, E1.3 trained RW-R1, E1.4 calibration or E1.5 blind scientific evaluation. The G04 real OIDC, tenant ACL/RLS, consent/privacy remain open. No product integration, private customer data, main/JARVIS/PULSE/vendor Mem0 or task DONE modifications.

## Next single execution item

**ENG-E1-03 / E1.1C — human annotation and evaluator isolation gate.** This requires *real independent reviewers*; ChatGPT cannot represent itself as two independent humans or manufacture adjudication. Prepare reviewer-ready packages and secure label custody, obtain actual reviews, check agreement and freeze dataset before proceeding to E1.2. The current public query files are **unlabeled, but not truly blind**.

This SI-MH-0071 commit changes only this evidence report and both handoffs. Its OWN documentation CI is separately PENDING.
