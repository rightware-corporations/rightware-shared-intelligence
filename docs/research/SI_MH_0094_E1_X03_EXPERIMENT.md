# SI-MH-0094 — LEARN E1-X03: evidence support and answerability (LOCAL EXECUTED)
**2026-11-24 Africa/Maputo.** Operator-authorized provisional research, no formal E1.2/E1.3 approval. Base develop@14d4327ad0bf887826f452cfcf89b81b22540e51; CI 45368557908 completed/success. Preserve TRUST work; SI-MH-0090 audited X02. 

## Frozen experimental protocol
[Notebook](notebooks/RIGHTWARE_SIC_E1_X03_KAGGLE.ipynb), SHA256 679fc4ad5e61d099f4f957d30e444ac189315221c853ad35ef16375567735c3c, exact Git blob 64e53b464a841ec11a458f6bc133156340b6455c. CPU, Internet Off, no installs/API/private data. Seed 20261126; 72 entity groups, 40/16/16 train/dev/diagnostic, 792 docs, 648 queries (nine per group). Two answerable queries (literal ID and alias), six negatives/ambiguity (missing, negated, uncertain, foreign-only, expired-only, ambiguous), one official contradiction. PT/EN, same-author synthetic grammar and shared dictionary; diagnostic sentence order and uncertainty wording varied. Exact token aliases are not natural entity resolution. Rule labels separate from public records; source and query IDs random, group/role/gold not used as features. Scope-only BM25 is separate control; six other methods use common official/current/scoped pool. TF-IDF and BM25 statistics fitted on scoped train docs only. Three fitted logistic models: query-balanced pointwise, pairwise (6 hard + 6 random eligible negatives per support), support verifier adds clause identity/property/value/connector/negation/uncertainty features. X02-style controls refit, not old X02 weights; no cross-corpus direct performance comparison.
 
Decision policies share explicit top-five shortlist. MentionTop1 can propose source without span and is penalized. AssertionRule and LearnedVerifier require literal typed span, matching entity/property and positive assertion cues; distinct values from different parsed sources trigger conflict. Ambiguity abstains. Gold exact source+property+value+offsets+quote is required for correct acceptance. Conflict scored separately, not included as accepted answers. Fixed grid 0..1 plus 1.01, maximize correct dev accepts with zero wrong, ties higher threshold; freeze before diagnostic predictions. Learned scores not calibrated probabilities. No diagnostic tuning. 

## Execution and verification
All 17 notebook cells (8 code) executed successfully via nbconvert, Python 3.13.5/NumPy 2.3.5/sklearn 1.8.0. Local evidence ZIP SHA256 e8b7b61b3fb052bd881eec0866292d12119406e596224d6183cadd5bf39c6163; 20 manifest entries with CRC/hash/size verified. Separate Python audit checked 4,536 unique ranking rows, exact scope/eligible candidate counts, distinct ordered top-five IDs, 105 retrieval metric rows, 99 decision metric rows, 306 dev threshold entries and selected thresholds, 1,944 decision inputs/final actions and literal spans, 57,600 training rows (160 positives and per-query weights), 1,920 pair records (3,840 symmetric directions). Verified six synthetic parser probes in run; no independent retraining or re-extraction of every feature claimed. Inspected three rendered plots. Zero observed scope violations in synthetic filter, NOT real IAM/RLS proof.

## Diagnostic retrieval (48 support-bearing queries: 32 answerable and 16 conflict)
| Method | Hit@1 | Hit@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|---:|
|BM25-Scope|0.2292|0.3750|0.2837|0.2798|
|BM25|0.2708|0.5208|0.3399|0.3462|
|Hybrid|0.2708|0.6250|0.3618|0.3780|
|Explicit|0.6042|1.0000|0.7882|0.8385|
|Pointwise|0.4583|1.0000|0.7049|0.7834|
|Pairwise|0.5208|1.0000|0.7108|0.7684|
|SupportVerifier|1.0000|1.0000|1.0000|1.0000|
SupportVerifier ranked all gold support sources ideally (including both conflict sources) on this particular diagnostic, nDCG 1.000, descriptive group bootstrap effect vs Explicit +.161510 [.110089,.218284], 16 groups. This does not establish external generalization; shared templates, metadata and feature engineering are strong. Scope-only control has different eligibility and is not matched. Full ranked verifier not used to generate the common decision shortlist. 

## Critical negative result: answerability NOT solved
| Policy | Dev-selected threshold | Diagnostic accepted | Correct | Wrong | Exact conflicts | Abstain | Selective risk |
|---|---:|---:|---:|---:|---:|---:|---:|
| MentionTop1 |1.01|0|0|0|0|144|undefined|
| AssertionRule |1.00|35|24|11|7|102|31.43%|
| LearnedVerifier |.99|35|24|11|7|102|31.43%|
Both assertion-based policies have identical final aggregate outcomes; no demonstrated added decision value of learned verifier over assertion rule. Learned dev 32/32 correct acceptances, 16/16 correct conflict flags and 96 abstentions; diagnostic 24/32 answerables accepted correctly, 8 abstain. 5/16 uncertain queries accepted incorrectly (unseen phrases “cenário de estudo”/“planning scenario”). 6/16 conflict cases incorrectly accepted one source as answer, 7/16 exact conflict signals, 3/16 abstain. No wrong accept in other negative classes. No false conflict signals. 35/144 coverage 24.31%; 11/35 incorrect, despite zero observed dev acceptance errors. Conflict detection depends on parsed spans; missing the second assertion can make incomplete conflict appear unambiguous. Do not equate perfect retrieval with valid evidence or confidence calibration. No promotion, no safety/production claim. 

## Next
Operator imports frozen notebook, CPU/None Internet Off Run All and returns RIGHTWARE_SIC_E1_X03_EVIDENCE.zip. Kaggle NOT_RUN. Independently audit reproduction before proposing X04. Investigate conflict completeness, generalization to novel uncertainty and semantic assertions, verified retrieval-to-decision handoff; no post-hoc retuning this diagnostic. E1_DATA_READY REVIEW_REQUIRED; independent humans and reserved gold still required, formal E1.2–E1.5 unchanged. No G04/Core/SQL/API/CI workflow/main/JARVIS/PULSE/vendor or sealed A0 changes. Local raw ZIP external custody, notebook/report/scorecard registered. Own CI PENDING.