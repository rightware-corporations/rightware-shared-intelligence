# RIGHTWARE — SI-RD-03A A0-GLOBAL-02 v0.8, sealed challenge and pre-registered comparison

**Date:** 2026-11-14 (Africa/Maputo). **Classification:** RESEARCH EXPERIMENT / EVALUATOR-SEALED CHALLENGE — **PROPOSAL NOT OFFICIAL PRODUCT DECISION, NOT VENDOR SELECTION, NOT IMPLEMENTED IN CORE.**  
**Baseline HEAD (read-only before adding artefacts):** `develop@60f8e51a0df4d5be0b25246eb30f7d741207711a`, latest visible CI run at preparation: `43609135330 completed/success`.  
**Unchanged:** Core R1/R2 engineering, R2 G01/G04 security and privacy decisions, main, JARVIS, PULSE, migrations, CI workloads and production infrastructure.

## 1. V07 is frozen as historical evidence
The independently audited [A0 v0.7 Kaggle results](SI_RD_03A_A0_V07_KAGGLE_EVIDENCE_AUDIT_2026-11-14.md) reported PostgreSQL 18.3/PGlite 0.5.8 WebAssembly, 49 documents, 40 questions, no oracle-derived case filter, and 0 foreign-scope source IDs in a fixed-scope synthetic experiment. The best observed Portuguese + OR had **hit@2=19/31 (61.29%)**; it was **post-hoc** (originally designed after v0.6) and suffers distractors, weak EN recovery and candidate generation for unanswerable questions. Do not extrapolate this to production server or a model comparison.

## 2. Frozen candidate challenge — A0-GLOBAL-02
Archive: [A0-GLOBAL-02 synthetic public package](RIGHTWARE_SI_RD03A_A0_GLOBAL02_PUBLIC_v08.zip) (stored in `docs/research/bundles/RIGHTWARE_SI_RD03A_A0_GLOBAL02_PUBLIC_v08.zip`).  
**Git blob:** `16ece24ee29d4c336a28f742f0139bb0cfc451eb`; **archive SHA256:** `c946ef45f97d932796e6ddc80c453da797f2523b0c06b19ae7dfecb38dcc1707`. The remote blob SHA was independently checked against `git hash-object` of the local ZIP; ZIP CRC PASS. No private key is stored in GitHub.  
**Contents:** 82 **synthetic-only** sources (70 fixed authorized scope `lab:rw:alpha`, 12 foreign `lab:rw:beta`), 56 public PT/EN queries **without gold identifiers or tracks**, README, common submission contract, locked manifest, engine-independent evaluator, 10 public contract tests and AES-GCM encrypted scoring oracle. Corpus SHA-256 `79d864eec2fd046f3102ca29dd94f61758f9d6d7db04048fd62b36579997d3e0`; query SHA-256 `d6b6cd11c091968ecf35ce34ec0d5eb7bc152d1d9b3f880d13f9f9f8983e4402`; ciphertext file SHA-256 `b82610b1a0197d03baa27829431a0c765bb4a87037d15e9e3bee36b3ae120ff2`; oracle plaintext commitment SHA-256 `585494484292f8c92eea9961174f63fae9cb8295beacaadc48842d8a4e772694`. 
Evaluator key is retained privately by the operator as `RIGHTWARE_SI_RD03A_A0_GLOBAL02_EVALUATOR_KEY_PRIVATE_v08.zip`, SHA256 `f3903e8892e17d5a2f0d806b7e8db6a4c0e9c728d000b2c1d2241d6211f5270c`, **NOT COMMITTED TO GITHUB, NOT TO KAGGLE OR PROVIDER**.

| Track | Questions | Expected |
|---|---:|---|
| EXACT_ID | 12 | Exact reference/source identity |
| MULTILINGUAL | 18 | Language-separated PT/EN source recovery |
| AUTHORITY | 8 | Contradictory unverified agent vs official ledger source |
| TEMPORAL | 6 | Current/as-of source selection |
| UNANSWERABLE | 6 | No factual source; gateway may ABSTAIN |
| FORBIDDEN_SCOPE | 6 | Requested fact exists only in foreign scope; gateway must DENY |

**44** queries have at least one source oracle; **12** negative queries do not. Runners have only corpus, public queries and a **trusted fixed scope assigned out-of-band**; no `case_id`, track, oracle, expected source or key may enter a provider runner. The encrypted oracle is a commitment, not a source of input facts.

## 3. Evaluation tiers & pre-registered metrics
- **R — Engine-only retrieval:** same corpus/source granularity/source IDs, same externally enforced scope, each of 56 queries once per fixed config, top_k=5. Score hit@1, hit@2, hit@5 over **44** scored queries; candidate coverage, per-language and per-track denominators; scope source IDs = **zero forbidden**.
- **G — Identical common gateway, separate score:** exact ID routing, source trust/authority, temporal validity and `ANSWER/ABSTAIN/DENY`. The gateway may cite only a source returned by retrieval; correctness based on separate oracle. Never call this engine-native success.
- **E — Human-validated response quality:** optional distinct future gate; NO automated answer truth has been measured or authorized here.
- **Hard gates:** 56/56 unique queries, no unknown sources, no duplicates in Top 5, no oracle-guided query filtering, checksum integrity, pinned runtime identity, 0 cross-scope source IDs. A failing gate = `INVALID/BLOCKED`, never averaged into positive hit@k.
- **Comparability:** provider native R only compared to native R. Memory components lacking a comparable source ID or metadata contract are marked `NOT_COMPARABLE`, not mis-scored at zero. PostgreSQL Server is not PGlite WebAssembly. Record CPU/RAM/embedding model and hash, ingestion/latency and pinning for Mem0 and Hindsight.

## 4. Test evidence and warnings
Local deterministic contract tests: **10/10 public + 18/18 evaluator-private PASS** on 2026-11-14 (synthetic fake outputs are contract unit tests, not vendor query results); ZIP CRC PASS; sha256 and Git object ID confirmed. The scoring script **has not scored a real provider run**. PostgreSQL Server, Mem0, Hindsight = **NOT_RUN on A0-GLOBAL-02**. No runtime code or dependency added to RIGHTWARE Core.
- This challenge is **evaluator-sealed**, NOT independently authored/blinded; the synthetic documents and evaluator were built by the research team. A truly independent blind set and human adjudication are required before any external/general performance claim.
- The static scope ID is synthetic; does NOT validate real user permissions, OIDC, RLS, tenant consent, retention/deletion or G04 control design.
- Authority and temporal judgments belong to the common gateway and verified source-of-truth, not lexical/vector ranking alone.
- This new dataset must NOT be compared numerically with v0.7 or tuned after observing early supplier results without publishing a new benchmark version.

## 5. Next gates (planned, not run)
1. Verify this archive and two handoffs on `develop` and observe its own CI.
2. Provision a **disposable isolated** PostgreSQL Server baseline with source IDs, exact-ID and FTS, consistent scopes and metrics. Do NOT touch live R2/production DBs.
3. Re-verify exact Mem0 OSS and Hindsight pinned SHA/config at experiment time and prepare separate adapters in identical source/scope/evidence conditions, with local model budget recorded.
4. Freeze run configs before the first provider; obtain **immutable raw outputs** from each; only the offline evaluator opens the sealed oracle key. Manual review all authority/temporal/negative cases.
5. Publish raw/scorecard hashes and a decision matrix (retrieval, operational cost, privacy/security, interoperability); **NO_VENDOR_SELECTION** until validated.

**Source package** includes `bench/PROTOCOL_GLOBAL_02.md` (full 8-section procedural protocol) and `bench/CONTRACT_SUBMISSION_V1.md` (submission JSON schema/instructions).
