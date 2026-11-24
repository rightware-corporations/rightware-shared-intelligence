# SI-MH-0073 — ENG-E1-03 E1.1C human review workflow, no fabricated reviews

**24/11/2026 Africa/Maputo. ESTADO: IMPLEMENTAÇÃO DE INFRAESTRUTURA DE REVISÃO, CI DESTE SHA PENDENTE.**

**Baseline real:** develop@8417dd163e0e55f3de0a80d6847f912449bfada2, SI-MH-0072 dossier SIC; [GitHub Actions 44335025606](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/44335025606) completed SUCCESS, 303-test E1.1B code baseline and eight migrations. Recovered both handoffs and existing rubric. No concurrent HEAD movement as of tree creation.

## Âmbito executado

- `backend/rightware_si/e1_03_review_protocol.py`: review packet builder omits **all** provisional labels and **all** eval records (42 synthetic documents and 24 train/dev queries); two entirely blank templates; validation of exact coverage, dataset/packet SHA256, scope, expiry, authority, evidence quote, reviewer pseudonyms, self-attestation; per-query class agreement (Cohen's kappa) and source grade weighted kappa, including undefined-case handling.
- `scripts/e1_03_review.py`: CLI `self-check/export/compare` operating with pinned synthetic E1.1B data. Sensitive output and submission inputs must be below ignored `.runtime/`; no overwrite. No public review report is created.
- `tests/test_e1_03_review_process.py`: 25 standalone security/quality tests using **fully fabricated, labelled MOCK attestations** which are not human reviews and are not committed as filled records. 303 + 25 = **328 expected tests** until actual CI logs. CI self-check audit marker `E1_03_REVIEW_CONTRACT_PASS` does not generate dummy gold.
- [Procedure](e1_03/REVIEW_CUSTODY_AND_GATE_R0.md): two human independent reviewers + third adjudicator, private custody, verified provenance and evaluator-only held-out science. No real reviews were made or scored; no evaluator gold, consent/retention policy or acceptance of `E1_DATA_READY`.

## Scientific and security gates

- `E1_REVIEW_INFRA_READY` may be technically verified in CI; **E1_DATA_READY scientific remains REVIEW_REQUIRED** until actual independent human review, true evaluator-controlled sealed holdout, adjudication and semantic leakage analysis.
- Self-declared distinct reviewer pseudonyms and flags **are not cryptographic proof of two distinct humans**. Scripts check structure/evidence, not truth of a human's expertise or independence.
- The eight public `eval` questions remain UNLABELED and NOT BLIND. Original E1.1 and E1.1B corpora/hashes unchanged. No trained RW-R1, no baselines E1.2, no calibrated E1.4, no external E1.5; sealed SI-RD-03A A0-GLOBAL-02 oracle untouched.
- G04 private IAM/RLS legal policies unresolved. No SQL/API/HTTP/MCP/Mem0 workflow, customer data, production, main/JARVIS/PULSE/vendor Mem0 or reviewer/DONE changes.

**Next:** confirm 328 tests plus E1_03 CI marker and regressions, append a new CI evidence checkpoint if green. Then coordinate actual reviewers and evaluator-only gold separately; never mark reviews complete based on schema tests.
