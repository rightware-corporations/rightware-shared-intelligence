# SI-MH-0084 — E1-X01: isolated provisional trainable ranking experiment
**Date:** 2026-11-24 Africa/Maputo. **Classification:** operator-authorized provisional experiment; NOT formal E1.2/E1.3 or scientific approval. Base develop@91da42178ceabe9ea73e464d7c71792b2bd71b6e, CI 45354460769 completed/failure. SI-MH-0082 CI 45354167631 success. Observed SI-MH-0083 CI 45354460769 failure in isolated browser job dependency installation; real-mcp-mem0 job success. This experiment does not repair or override browser smoke gate.

## Frozen protocol
Standalone [notebook](notebooks/RIGHTWARE_SIC_E1_X01_KAGGLE.ipynb), SHA256 069cf9e71fb66c51be6e781bc29f3a7356ec81e6e6c56406c21b217e34af678b, exact Git blob bd8475a477d38b12256917da8c1518cdaa44f91c. Seed 20261124. CPU, Python/Numpy/scikit-learn/Matplotlib preinstalled; no network, external data, GPU, APIs, or paid model. New synthetic corpus 288 documents, 192 queries, 48 disjoint entity groups split 28/10/10 train/dev/diagnostic. 56 positive training pairs among 15,680 scoped pairs. Rule labels public and generated, no human review, no independent holdout. No read/use of E1.1B eval or A0-GLOBAL-02. All seven methods scope-filter before ranking; no gold group restriction. BM25, char TF-IDF, train-fit LSA32 (not pretrained dense semantic model), fixed hybrid, hybrid + hard authority/validity filter, two train-only logistic ranking models (text vs text+metadata). Scores indicate support candidates, not answer correctness. Threshold selected solely on dev by maximum coverage with zero observed wrong acceptances, with fail-closed option 1.01. Fixed configuration, no diagnostic tuning.

## Local real execution (not Kaggle)
nbconvert execute all 14 cells passed, Python 3.13.5, NumPy 2.3.5, sklearn 1.8.0. 1,344 rankings; ZIP CRC and all 10 manifest hashes/lengths verified. Evidence local ZIP RIGHTWARE_SIC_E1_X01_EVIDENCE.zip SHA256 d26bfbb249fa38a5c033457128b4e1d73e5e8be51bb355335f89538c3ce97d4e. Diagnostic n=40 queries (20 answerable):
| method | nDCG@5 | Hit@1 |
|---|---:|---:|
| BM25 | .496 | .350 |
| CharTFIDF | .375 | .250 |
| LSA32 | .295 | .200 |
| Hybrid | .513 | .350 |
| Hybrid-Authority | .758 | .500 |
| RW-R1-X01-text | .222 | .050 |
| RW-R1-X01-meta | .385 | .150 |

The trained prototypes UNDERPERFORM baseline; do not promote. Dev abstention selects 1.01, accepts 0/40, diagnostic 0/40, risk undefined (not zero demonstrated). Zero scope violations in fixed synthetic eligibility, not production authorization. Public templated dataset and deterministic labels, class imbalance, no independent reviews, no external providers, no production decisions. Weights JSON is diagnostic, not a packaged inference pipeline. No cross-dataset generalization or vendor comparison. Kaggle execution remains NOT_RUN until operator returns ZIP; no assertion of exact numeric reproduction across library versions.

## Next
Operator imports notebook, CPU/None, Internet Off, Run All; return ZIP for independent audit. Only then propose further experimental feature work. Formal E1_DATA_READY REVIEW_REQUIRED, human adjudication and genuinely reserved holdout still required; official E1.2–E1.5 unchanged. G04 separate. No SQL/API/CI workflow/runtime/main/JARVIS/PULSE changes, no sealed labels or keys exposed.