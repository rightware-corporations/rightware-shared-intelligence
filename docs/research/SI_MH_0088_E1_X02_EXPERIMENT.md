# SI-MH-0088 — LEARN E1-X02: provisional query-balanced pairwise ranking

**2026-11-24 Africa/Maputo. Classification:** operator-authorized provisional experiment; not formal E1.2/E1.3 or scientific approval. Base develop@965cff0861cda46d282bd22703822ba40db1d741; latest CI 45364884789 completed/success. TRUST work unchanged.

## Protocol and implementation
[Standalone notebook](notebooks/RIGHTWARE_SIC_E1_X02_KAGGLE.ipynb), SHA256 1aea1cf2007450ffc4353e7263a1d62bc0e344b5777a2de68b9935d3c0dbaf53, exact Git blob c83149c3eb5b29677912c284e3c401efd290494d. Seed 20261125. CPU/Internet Off, no external data/install/paid API. 72 random entity groups 42/15/15 train/dev/diagnostic, 576 documents, 432 queries, 2 positive and 4 negative per group. PT/EN templates differ by split, but same author and shared synthetic grammar; no independent holdout. Unknown attribute, missing reference, foreign-only, expired-only negative cases. Cross-mentions, alternative official properties, historical and unverified claims. Text reference (RW-/AX-) and fixed bilingual property dictionary are explicit signals, not learned semantic understanding. Gold IDs/groups/kind used for supervised labels and evaluation only, never candidate selection. Scope-only BM25 control and common official/current/scoped pool for all nine primary methods. Train-only TF-IDF, LSA32, IDF/scaling (eligible scope, not exclusively official docs); LSA is lexical latent representation, not pretrained dense. Refit X02 pointwise control, 14,112 rows, 84 positives, query/class weighting; pairwise logistic full, text and no-ID ablation, 1,344 positive-negative comparisons (8 hard/8 random per positive training query), 2,688 symmetric directions. X01 frozen as historical control, no application of X01 weights to X02 features; not a matched-corpus cross-version comparison. Fixed score and dev-only threshold selection; no diagnostic optimization.

## Local execution
All 14 cells (7 code) executed successfully by nbconvert; Python 3.13.5, NumPy 2.3.5, sklearn 1.8.0. Local evidence ZIP SHA256 d402655c1c50d15622dd449eb779bb96630a8b0bedc32a7d4e1ac667e3a432e7; 14 manifest files and CRC/hash/length checks passed. Separate Python verification independently recalculated 90 metrics rows and inspected 4,320 ranking records, scope/authority/time constraints and distinct top5 IDs. Both plots visually inspected. No local real service or vendor run. Kaggle NOT_RUN until operator supplies evidence.

Diagnostic: 30 positive/60 negative queries, 15 groups. Rounded metrics:
| Method | Hit@1 | Hit@2 | Hit@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|---:|---:|
|BM25-Scope|0.0000|0.0000|0.7333|0.1928|0.3232|
|BM25|0.0000|0.3667|1.0000|0.3667|0.5249|
|CharTFIDF|0.3333|0.6000|1.0000|0.5806|0.6854|
|LSA32|0.0333|0.0667|0.1333|0.0694|0.0854|
|Hybrid|0.2333|0.5667|1.0000|0.5333|0.6511|
|Hybrid-ID-Property|0.8333|0.9667|1.0000|0.9111|0.9341|
|Pointwise|0.8333|1.0000|1.0000|0.9167|0.9385|
|PairwiseText|0.0000|0.5000|1.0000|0.3944|0.5470|
|PairwiseNoID|0.0000|0.6333|1.0000|0.4250|0.5714|
|RW-R1-X02|0.7667|0.9333|1.0000|0.8722|0.9052|

All primary methods share identical eligible populations. Full pairwise hit1 23/30; explicit baseline and pointwise 25/30. Pairwise no-ID drops to .5714 nDCG; full .9052, but does NOT beat explicit .9341 or pointwise .9385. Full-minus-explicit group mean delta -0.028969; descriptive group-bootstrap percentiles [-0.082543,0.020240], 2,000 resamples; no population inference or claim of superiority. Diagnostic negative queries all retrieve candidates: retrieval is not answerability. Fixed confidence score chooses 1.01 on dev; accepts 0/90 dev and 0/90 diagnostic; risk null, not proof of accuracy/security. Zero observed forbidden IDs only in fixed synthetic lab scope. No generated answer metric, real authorization, timing comparison, probability calibration or human validation. Shared property dictionary and negative phrase feature are hand-engineered for synthetic grammar, so improvement within this dataset cannot establish generalization. No promotion.

## Next
Operator imports notebook CPU/None Internet Off Run All and returns RIGHTWARE_SIC_E1_X02_EVIDENCE.zip. Audit actual artifact; investigate answerability decision separate from ranker and evaluate harder alias/description cases beyond template matching. Do not tune X02 after diagnostic. E1_DATA_READY REVIEW_REQUIRED, humans=0, formal E1.2–E1.5 unchanged, no sealed A0 or E1.1B eval used, no provider/core/SQL/API/G04/main/JARVIS/PULSE/TRUST changes. New CI pending.