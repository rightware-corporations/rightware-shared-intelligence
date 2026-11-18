# RIGHTWARE ENG-E1-02 — Annotation protocol and independent-review gate R0

**2026-11-18. STATE:** PROPOSED REVIEW WORKFLOW; **NO HUMAN REVIEW CONDUCTED**. No person has been recorded as an annotator or adjudicator.

## Scope

The new corpus `e1_02` has 56 entirely authored/synthetic source documents and 32 queries across 8 topic groups in PT/EN. Four groups train, two dev, two unlabeled eval. It uses shared project scopes within each split so multiple topics compete for retrieval. `labels_provisional.jsonl` has 24 rule-authored training/development labels only, **NOT** expert gold. Evaluation's 8 queries have **NO labels recorded**, so no test/eval nDCG should be reported. Their questions/documents are public and hence *not truly blind*.

### Review process — NOT DONE

1. Recruit **two independent competent reviewers**, each given source documents, question, `as_of` time, tenant/project boundary and **without seeing rule-authored labels** or each other's responses.
2. For **each** train/dev query and each candidate authorized document, choose relevance grade 0/1/2/3 and cite verbatim supporting evidence span or an explanation why it does not answer. Use `0` for irrelevant/unsupported, `1` contextual but not an answer, `2` partially supports answer, `3` directly answers. For forbidden, expired, cross-project and unverified sources, relevance for authoritative answer is **0 regardless of lexical match**; record eligibility reason separately.
3. Classify query: `ANSWERABLE`, `UNANSWERABLE`, `FORBIDDEN_SCOPE`, `TEMPORAL_INVALID`, `AUTHORITY_CONFLICT`. The negative label means **no authorized and current source** can support the requested claim, not absence of matching words.
4. Require reviewer IDs to be distinct and decisions made before any reconciliation. Do not infer agreement merely from matching IDs. Store raw submissions in an approved private review workspace, never commit names, employee data or the evaluator-only adjudicated gold to this public repo.
5. Adjudicator resolves grade/class disagreement, with rationale, timestamp, and references. Record agreement per language and class, Cohen's kappa or weighted kappa as appropriate, label coverage, disagreements, revisions and remaining unresolved cases. **Do not invent a numeric acceptance threshold before reviewing label distribution and costs**.
6. Re-check near duplicates with human semantic review, not only normalized 4-token Jaccard. Record document/provenance/license for any future externally sourced text before reuse.
7. Create a separate **evaluator-only held-out gold set** once reviewed, with access controls and integrity hashes. Do not import sealed SI-RD-03A A0-GLOBAL-02 oracle or use evaluation labels in training/dev. A public unlabelled eval query file is not sufficient to claim blind external validation.
8. Approve an updated split manifest and review receipt before declaring `E1_DATA_READY`. A reviewer, not the synthetic data author, must independently sign off. If review remains absent, scientific gate is **REVIEW_REQUIRED**.

### Annotation record (schema example, NOT a submitted review)

```json
{
  "query_id": "syn-e1b-example-q1",
  "reviewer_pseudonym": "TO_BE_ASSIGNED",
  "review_round": "INDEPENDENT_NOT_STARTED",
  "as_of": "2026-11-18T12:00:00+00:00",
  "query_class": "TO_BE_ANNOTATED",
  "source_relevance": {},
  "justification": "TO_BE_ANNOTATED",
  "evidence_spans": [],
  "source_consent_check": "SYNTHETIC_ONLY",
  "review_status": "NOT_SUBMITTED"
}
```

The example uses placeholders and may **never** count as one of two independent reviews.

## Technical audit boundaries

- Exact SHA256 pin of all three JSONL files; schema/IDs/time/role/gold/source validity and split-family isolation.
- Normalized accent-insensitive **4-token-shingle Jaccard threshold 0.65** for cross-split source/query near duplicates. Passing this **does not** establish no semantic leakage.
- Two independent domains per split share one authorized project; foreign org and other project decoys must be excluded before scoring.
- The E0 diagnostic measures only **train/dev** rows with provisional labels; no evaluation query is scored or its intended answer disclosed. It is an engineering diagnostic, **not model comparison or scientific win**.

**Next:** obtain genuinely independent review and evaluator-only gold; run a human near-duplicate and leakage audit; update the dataset and red-team negative cases, then start E1.2 controlled retrieval baselines. RW-R1 training E1.3, calibration E1.4 and E1.5 blind comparison remain pending. G04 private source identity/RLS still unrelated and unimplemented.
