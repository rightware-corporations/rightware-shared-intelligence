# SI-FG-01 — Functional Gap Audit vs Product Vision

**Date:** 2026-11-12 (Africa/Maputo)
**Classification:** PRODUCT AUDIT / RECOMMENDATION (not an official product approval)
**Audited source:** `develop@5787579f3b2b936e049d386488bb9671778bae52`
**Code changed by this audit:** NONE

## 1. Conclusion

RIGHTWARE Shared Intelligence **does not yet deliver the complete envisioned product**. The verified CI (`43122815508`, success) establishes a reliable *narrow laboratory path*: REST-authenticated scoped task read, independent stdio MCP bridge, real Mem0 OSS contextual retrieval with local Ollama embeddings and pgvector, plus deterministic PostgreSQL task/lease/handoff operations.

A successful E2E smoke is not the same as: durable human/agent context continuity, automatic resume of interrupted work, evidenced result completion, operational decision approval, controlled memory lifecycle, external integrations and production-ready isolation.

**Architecture consequence:** immediate production deployment work is premature as a product-completeness milestone. Keep infrastructure discovery/security constraints, but prioritize a contract-driven functional closure and tests of a complete **two-agent handoff and resume**.

## 2. Source inspection

Inspected these current code paths, not only proposals:
- `backend/rightware_si/core/postgres.py`: actual WorkCore methods: `create_task`, `publish_task`, `claim_task`, `offer_handoff`, `accept_handoff`, `submit_result`, `get_task`, `task_events`. No implementation for DONE approval, evidence verification, decision authorization, lease renewal, resume after crashed agent or transactional outbox.
- `backend/rightware_si/http_api.py`: task REST operations, context GET, memory-search POST; **no public authenticated memory-write, memory-delete, evidence-review/decision API**.
- `backend/rightware_si/context_service.py`: server-derived project scope, memory candidate filtering, UNVERIFIED trust and backend-down degradation; **no persistent context snapshot or provenance resolution against independently validated sources**.
- `backend/rightware_si/mcp_bridge.py`: **read-only** MCP tools `get_task`, `get_task_events`, `get_project_context` through HTTP; no generic agent write/structured handoff tools.
- `database/migrations/0001_work02_core.sql`: organizations/projects/principals/grants/tasks/leases/handoffs/evidence references/events/idempotency. **No** decision tables, verification records, context snapshots, source audit of memories, outbox or consent/erasure lifecycle.
- `docs/work01/PRODUCT_VISION.md`, `docs/work01/MVP_ACCEPTANCE.md`: originally proposed scope and 18 acceptance cases; those 18 **have NOT all been demonstrated**.
- `docs/research/SI_RD_02_BENCHMARK_CONTRACT.md`: comparison methodology and 18 **synthetic fixtures**, not executed benchmark or product tests.
- `docs/HANDOFF.md`, `docs/HANDOFF_MASTER.md`, `docs/ARCHITECTURE.md`: history and implementation boundaries.

## 3. Functional coverage, conservative classification

| Capability | Status | Specific reality / gap |
|---|---|---|
| PostgreSQL versioned tasks, basic grants and exclusive lease handoff | IMPLEMENTED / lab verified | Actual WorkCore and PostgreSQL tests; only subset of whole workflow |
| REST authentication + read-only MCP | IMPLEMENTED / lab verified | No full model-agent write interface; no external vendor host interoperability claim |
| Scoped Mem0 retrieval with Ollama embeddings | IMPLEMENTED / lab verified | Synthetic actual Mem0; no production ingestion, consent/deletion or retrieval quality benchmark |
| Create/record trusted contextual memories via public RIGHTWARE API | MISSING | Internal Mem0 lab supports add; not an authenticated product write operation |
| Structured handoff payload (task checkpoint, artefacts, blockers, objectives, context references, next actor) | PARTIAL | Handoff contains summary/recipient; context snapshot not assembled, versioned, reauthorized or made resumable |
| Recovery after agent restart/crash without rebuilding the chat manually | UNPROVEN / MISSING | E2E does not simulate process restart + state reconstruction + tool side-effects |
| Independently verified Git/CI/test evidence and approval to DONE | MISSING | Evidence references are unverified; no verifier/reviewer transition to DONE |
| Decisions, authority, supersession and organizational approval | MISSING | No decision aggregate/tables/routes |
| Memory lifecycle: provenance, correction, invalidation, consent, delete, retention, privacy | MISSING | Metadata/scope only; no governed lifecycle |
| Event/outbox index synchronization and replay | MISSING | Domain event table exists; no transactional outbox or projection reconciliation |
| Tenant isolation for hostile multi-customer production | PARTIAL / UNVERIFIED | Project grants and synthetic negative tests; no production workload OIDC, resource-level ACL, formal adversarial audit |
| Jarvis/PULSE/Claude/ChatGPT/n8n actual integrations | MISSING | Read-only *independent probe* exists; no modifications of Jarvis production, no native ChatGPT/Claude memory sync |
| Admin UI + monitoring + deployment operations | MISSING | frontend and infrastructure contain README only |
| Reproducible synthetic E2E path | VERIFIED | Prior CI run 43122815508 SUCCESS (55 tests + real MCP/REST/PostgreSQL/Mem0/Ollama smoke); narrower than production functionality |

`MISSING` = not implemented as a product-facing service, even if low-level infrastructure or experiments exist; `UNPROVEN` = absence of an accepted end-to-end demonstration, not proof of impossibility.

## 4. WORK-01 acceptance contract gap grouping

| Acceptance IDs | Conservative position |
|---|---|
| M01, M08, M11 | Narrow core path exercised; verify contract-level criteria in targeted acceptance report |
| M03, M04, M06, M10, M12, M17 | Partial scope exercised by the existing laboratory tests (e.g. MCP read only; handoff without context snapshot) |
| M09 | Conditional: idempotency exists, but retry of lease-issuing commands deliberately returns 409 after WORK-02D, diverging from original generic "same key+body same result" wording |
| M02, M05, M07, M13, M14, M15, M16, M18 | Missing, insufficiently demonstrated or missing required trust/provenance/audit/recovery dimensions |

**Do not represent these classifications as new test executions.** Formal per-ID assertions must be implemented and reported separately.

## 5. Proposed minimum complete product journey (synthetic, not yet achieved)

1. A principal with explicit project grant starts a work session with a stable task/run ID.
2. Agent A reads an authorized context snapshot, executes work, creates a scoped observation with provenance and a checkpoint recording completed/remaining work.
3. The service persists the claim/observation/handoff as an authoritative, versioned event; optional memory projection is asynchronous and reversible.
4. Agent A offers handoff to B, atomically transfers task lease; A is no longer authorized for writes.
5. Agent B starts in a **new process/session** and requests `resume(task_id)`; receives task, validated decisions, accepted observations, evidence statuses and remaining steps without the original chat.
6. B executes a safe deterministic action, submits a result with a Git/CI evidence reference; status remains IN_REVIEW until independent validation and authorized reviewer approval.
7. The process is killed/restarted and the system reconstructs the same authority, pending state and next steps; no duplicate side effects.
8. Cross-project clients and revoked principals are denied at **every** read/write/retrieval edge. Bad model text remains untrusted data.
9. Memory correction/deletion events propagate to the searchable projection, without erasing the documented authoritative audit basis contrary to applicable policy.

This is the defining vertical slice for Shared Intelligence. **A memory-search demo alone does not pass it.**

## 6. Priorities / next execution proposals

**WORK-03B R0 — Functional Contract Closure (next, before production deployment):**
- Confirm the minimum customer job: work handoff/recovery between two independent authorized clients (first internal Jarvis-compatible use case).
- Adopt a bounded MVP scope and sign off acceptance criteria. Distinguish core tasks from PULSE ownership.
- Resolve schema/API contracts for SourceRecord/Observation, ContextSnapshot, MemoryLifecycle, Verification, Decision and AgentRun.
- Amend original M01–M18 tests with expected outcomes and explicit support/NOT_APPLICABLE flags.
- Reconcile SI-RD-02 and SI-RD-03 benchmark plan: evaluation informs memory-provider selection but need not indefinitely block deterministic product architecture.
- Produce executable test plan on synthetic data. No Jarvis prod code changes.

**WORK-03B R1 — Real semantic continuity slice:** authorized observation and memory-write, context snapshot, versioned handoff bundle, `resume` API/MCP, restart/replay tests.

**WORK-03B R2 — Trust and lifecycle:** evidence Git/CI verifier, independent approval to DONE, decision authority, consent/delete and outbox projection; isolation and adversarial tests.

**WORK-03C — Staging/Deployment gate:** only after functional minimum passes; deployable configuration, backups, TLS/workload identity, readiness/recovery and read-only Jarvis staging with rollback. Do not deploy immediately.

## 7. Decisions and risks

**OFFICIAL operator decisions unchanged:** develop/main as sole future work branches; both MASTER and CURRENT handoffs updated each technical output; Jarvis production untouched.

**RECOMMENDATION, NOT OFFICIAL DECISION:** choose WORK-03B R0 over immediate infrastructure/deployment build; the product's customer job is not yet end-to-end.

**Risk:** scope expansion to full task manager or all-agent chat-sync would postpone value. Keep PULSE as owner of its business workflow records and treat ChatGPT/Claude-native memory APIs as integration capabilities requiring independent availability/authorization checks. Do not promise automatic extraction of other vendor private conversations.

**Verification status:** document-only code audit; no new runtime functionality or tests implemented as part of SI-FG-01. Root latest checked HEAD was `5787579f3b2b936e049d386488bb9671778bae52`; GH Actions at that head showed success. The documentation commit must itself pass CI before being called validated.
