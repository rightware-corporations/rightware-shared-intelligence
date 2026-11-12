# SI-RD-02E — External Perplexity report: validation, gap analysis and research intake
**Date:** 2026-11-12 (Africa/Maputo) · **Checkpoint:** SI-MH-0010 · **Classification:** EXTERNAL RESEARCH TRIAGE / FACT-CHECK / RECOMMENDATIONS, not a product decision, external benchmark, or integration.
**Source artifact:** user-supplied *SI-RD-02-RESEARCH-REPORT.pdf*, 11 pages, Perplexity; report status `SI_RD_02_PARTIAL`. Do not publish the full PDF to the public GitHub; this is an original derived summary with externally auditable direct URLs.
**Repository baseline read for this triage:** `develop@7b719f7411cc7da042faae70c3f5198c4d8a0fc3`; SI-RD-01, SI-RD-02, SI-FG-01 and HANDOFF_MASTER read. No third-party code run.

## 1. What the PDF actually supports
The Perplexity report offers (a) C1-C10 capability taxonomy, (b) broad candidate landscape beyond seven named systems, (c) public papers and product claims, (d) preliminary community experience, (e) ten scored hypotheses and (f) proposals for validating them. It explicitly says it **did not access RIGHTWARE's internal documents or inspect external code at line/commit granularity**, and much of the list is `NOT VERIFIED`/E0-E1; named Hindsight, Temporal and MCP are among its gaps.
**Use as discovery and citation lead, NOT proof of new invention, source-level behaviour, comparative quality or market demand.** The earlier RIGHTWARE SI-RD-02 *did* inspect source trees and code for the seven core technologies with commit pins, so do not downgrade existing independent evidence to the Perplexity document's weaker evidence level.

## 2. External fact-check and important corrections
| PDF item | Independently checked state | Action |
|---|---|---|
| Kuzu as potentially suitable embedded graph DB | OFFICIAL repository `kuzudb/kuzu` shows `archived=true` since 2025-10-10. This is not an actively maintained new dependency. | Avoid Kuzu as default; study architecture. Investigate active fork `LadybugDB/ladybug` (MIT, active as of this inspection) on its own merits. |
| DBOS durable workflows | `dbos-inc/dbos-transact-py` (MIT) is active and PostgreSQL-backed. | Add to continuity comparison shortlist beside Temporal/LangGraph only if current WorkCore fails target requirements; do not assume drop-in compatibility. |
| Restate durable workflow | `restatedev/restate` is active, but GitHub repository license metadata is `NOASSERTION`. | Technical candidate; explicit licensing and deployment-cost review before embedding. |
| SoMem research paper | [arXiv 2611.11929](https://arxiv.org/abs/2611.11929) dated 2026-11-09; [Qi202/SoMem](https://github.com/Qi202/SoMem) public code (MIT) and active. Its model organizes linked documents with original evidence and temporal views. | HIGH PRIORITY code review / research comparison for document-backed long-term memory, but not production validation. |
| XTDB | `xtdb/xtdb` active with **MPL-2.0** repo license, bitemporal SQL DB. | Interesting temporal data reference, not automatic integration; license implications need review. |
| Cognee, MemOS, LangMem, sqlite-vec, LanceDB | Repositories active in GitHub snapshots; main licenses Apache-2.0/Apache-2.0/MIT/Apache-2.0/Apache-2.0 respectively. | Narrow code studies only if core comparison exposes a relevant unmet need. |
| LangGraph duplicated long tool calls | Open community issue [#7417](https://github.com/langchain-ai/langgraph/issues/7417) recounts re-dispatch; not a reproducible project-wide failure rate. | Include synthetic retry/reconciliation contract in continuity lab. |
| LangGraph checkpoint bloat 85% | Community issue [#7714](https://github.com/langchain-ai/langgraph/issues/7714) is **CLOSED** (2026-10-16); individual configuration report. | Do not publish the percentage as general current performance; benchmark own workload if relevant. |
| A2A/Temporal and exactly-once | Contract is not proof that an external API/physical action happened exactly once; durable execution must use idempotency keys, receipts, reconciliation. | Replace unconditional guarantee with *verifiable attempts, attested results, and bounded duplicate side-effects under tested conditions*. |
| Observation tools Langfuse/Phoenix | GitHub repo license metadata `NOASSERTION` for `langfuse/langfuse`, `Arize-ai/phoenix`; may have additional terms. | Do not interpret labels as permission for unrestricted commercial redistribution; use OTel and review licensing first. |
| Self-hosted/local-first constraint | PDF assumed Windows/local-model constraints for the full SIC, but RIGHTWARE product vision is independent deployment with optional model-local choices. | Do not force desktop SQLite as server authoritative database; keep PostgreSQL and a replaceable Mem0 adapter. |

**Verification sources:**
- https://github.com/kuzudb/kuzu (archived flag); https://github.com/LadybugDB/ladybug
- https://github.com/dbos-inc/dbos-transact-py ; https://github.com/restatedev/restate
- https://arxiv.org/abs/2611.11929 ; https://github.com/Qi202/SoMem
- https://github.com/xtdb/xtdb ; https://github.com/langchain-ai/langgraph/issues/7417 ; https://github.com/langchain-ai/langgraph/issues/7714
- https://github.com/langfuse/langfuse ; https://github.com/Arize-ai/phoenix

## 3. Arithmetic audit: PDF page 8 weighted opportunity scores
Published weights: severity 0.25, market gap 0.20, defensibility 0.20, RIGHTWARE feasibility 0.15, time-to-value 0.10, fit 0.10. Recalculated directly from the PDF's six integers:
| Original position | Hypothesis | Reported | Corrected |
|---:|---|---:|---:|
| 1 | Verifiable continuity receipts | 4.55 | **4.55** |
| 2 | Tamper-evident ledger | 4.45 | **4.45** |
| 3 | Evidence-backed task execution | 4.40 | **4.35** |
| 4 | Small-local-model extraction | 4.40 | **4.40** |
| 5 | Cross-vendor handoff fidelity | 4.00 | **4.00** |
| 6 | Memory poisoning resistance | 4.05 | **4.15** |
| 7 | Local-first temporal knowledge | 3.95 | **3.95** |
| 8 | Multi-agent concurrent consistency | 3.65 | **3.65** |
| 9 | Memory regression in CI | 4.10 | **4.05** |
| 10 | Privacy-preserving shared context | 4.00 | **4.00** |
**Corrections:** #3 4.40 -> **4.35**; #6 4.05 -> **4.15**; #9 4.10 -> **4.05**. The PDF ranks were not sorted by its own weighted values. The weighting and input scores are **subjective author judgements**, not market research, effect sizes, quantitative benchmarking or official RIGHTWARE priority approvals.

**Correct numerical order** (ties stable by original row): #1 4.55 > #2 4.45 > #4 4.40 > #3 4.35 > #6 4.15 > #9 4.05 > #5 4.00 > #10 4.00 > #7 3.95 > #8 3.65.

## 4. Crosswalk with RIGHTWARE functional gap audit SI-FG-01
The existing `docs/product/SI_FG_01_FUNCTIONAL_GAP_AUDIT_2026-11-12.md` is the controlling internal implementation inspection:
- **Already tested narrow functionality:** PostgreSQL WorkCore transaction/version/leases/handoffs; project grants; FastAPI authenticated reads, MCP read-only, scoped Mem0 + Ollama/pgvector synthetic E2E. CI 43151308140 SUCCESS at inspected HEAD.
- **Not yet functional product:** authorized memory-write, versioned ContextSnapshot, two-process `resume`, independently verified Git/CI action receipts and reviewer approval to DONE, memory correction/deletion/retention and outbox, real external client staging.
- PDF `BUILD` recommendations overlap with these gaps, but are NOT a licence to rebuild framework components. Keep existing authorization/WorkCore rather than migrating to unbenchmarked CRDT/SQLite.
- The **first user outcome to prove** is `UC-CORE-01`: agent A -> authorized observation -> versioned checkpoint -> handoff -> agent B new process `resume` -> independently validated artifact -> authorized review -> no duplicated side effect. Align `WORK-03B R0` contract before adding new runtime features.
- Handoff formats can learn from Git-backed memory at Letta; use W3C PROV for naming Agent/Activity/Entity and OpenTelemetry conventions for trace attributes, but neither standard independently validates facts.

## 5. Separate next research streams (recommendations, not approved changes)
**A / SI-RD-03A controlled memory retrieval:** PostgreSQL exact/FTS baseline, pinned Mem0 and Hindsight, then Graphiti where time semantics justify. Existing 18 synthetic fixtures are a **contract smoke**, not statistical evidence. Fix the model/input/embedding/source budget; flag `NOT_APPLICABLE` where provider is out of track.

**B / SI-RD-03B memory-document study:** inspect SoMem's evidence-backed linked documents and compare with Rightware Git handoffs plus SQLite/PostgreSQL simple versioned facts; follow the publication with code-level checks (no paper score accepted without same benchmark).

**C / WORK-03B R0 functional contract:** freeze UC-CORE-01 schema and state/evidence boundaries before production/deployment. Compare LangGraph, Temporal and DBOS only in durability/retry scenarios; refuse overclaim exactly-once for uncontrolled external side effects.

**D / Evaluation and market:** after smoke, extend corpus to Portuguese/PT-MZ and English scenarios with human-derived oracle; include source-trust, poisoning, contradictory updates, token/latency/cost/recovery metrics; interview customers before ranking monetizable gaps. Test small local Qwen extraction later, separately from infer=false embedding-only smoke.

## 6. Decision register
- **OFFICIAL unchanged:** only `develop` working and `main` release; all research/technical outputs committed to current + master handoff; no unauthorized main merge, vendor upgrade, Jarvis/PULSE modification or live data.
- **RECOMMENDATION:** accept external PDF as discovery input, **do not accept its numeric priority order or BUILD directives as approval**; preserve Mem0 pinned and current PostgreSQL authority; first prove one end-to-end two-agent journey and benchmark memory fairly.
- **EXPERIMENTS NOT DONE:** no new code, data migration, evaluation engines, model inference, security exploitation, customer interviews, commercial licensing audit or own benchmark. No raw PDF published.
- **Next checkpoint:** validate document-only CI for this commit; then converge WORK-03B R0 + SI-RD-03A/B. On any new substantive output append MASTER and refresh CURRENT in the same commit.
