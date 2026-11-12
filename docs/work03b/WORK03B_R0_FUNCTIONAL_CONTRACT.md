# WORK-03B R0 — UC-CORE-01 Functional Contract Closure

**Status:** DRAFT / engineering specification ready for operator ratification; **NOT** implementation approval.  
**Date:** 2026-11-12 (Africa/Maputo) · **Repository:** RIGHTWARE Shared Intelligence · **Branch:** `develop`.  
**Source of current implementation truth:** `backend/rightware_si/core/postgres.py`, `backend/rightware_si/http_api.py`, `backend/rightware_si/context_service.py`, `database/migrations/0001_work02_core.sql`, `docs/product/SI_FG_01_FUNCTIONAL_GAP_AUDIT_2026-11-12.md`.  
**Machine-readable draft:** [UC_CORE_01_CONTRACT.json](UC_CORE_01_CONTRACT.json) · **Acceptance matrix:** [UC_CORE_01_ACCEPTANCE.md](UC_CORE_01_ACCEPTANCE.md).

## 1. Product job and scope boundary
**UC-CORE-01:** Two different authorized agent principals on the same synthetic project must continue one versioned task between **independent processes**, without requiring the original conversation. A can write an unverified observation and a lease-bound checkpoint, offer a handoff, and lose its exclusive write lease. B atomically accepts, retrieves a freshly authorized continuation snapshot, resumes work, submits an evidence reference, and stays `IN_REVIEW` until an independent verifier checks the specific external fact and a different authorized reviewer accepts the result. Unauthorized project access is denied.

The Shared Intelligence Core owns **contextual source records, scoped task coordination, evidence status and continuation manifests**. The business workflow (PULSE, JARVIS's personal UX, Boane Conecta, etc.) remains owned by the corresponding application. This does **not** make Shared Intelligence a general task manager or grant it control of another agent.

**Non-goals for R0:** runtime changes, third-party engine adoption, PostgreSQL migrations, paid models, production/deployment, actual JARVIS modifications, UX screens, unscoped automatic chat ingestion, autonomous self-approval. `main` untouched.

## 2. Entities and the authority model (draft for R1/R2 implementation)
| Entity | Required ownership / fields | Trust and lifecycle |
|---|---|---|
| `AgentRun` | id, project_id, task_id, authenticated principal, runtime label, began_at, ended_at, correlation_id | Describes an attempt, NOT a successful result |
| `SourceRecord` | source_id, project_id, kind, source URI/internal ref, hash if obtained, observed_at, actor, provenance | A source pointer does not assert source truth |
| `Observation` | id, project_id, task_id?, agent_run_id, text, source_refs, asserted_at, `ASSERTED` | Append-only claim; not a task status, grant or decision |
| `TaskCheckpoint` | id, task_id, task_version, agent_run_id, completed_claims, pending_steps, blocker, external_action_refs, created_at | Lease-bound; claims are not verified effects; immutable history |
| `ContextSnapshot` | id, project_id, task_id, task_version, pointer refs + their observed version, projection watermark, created_for, issued_at | Versioned manifest; reauthorise on **every** resume/read; no secret credentials |
| `HandoffBundle` | handoff_id, task_id, from/to principals, snapshot_id, checkpoint_id, criteria refs, blockers, offered_version | Transfer references atomically with lease release; existing basic handoff table lacks bundle refs |
| `EvidenceReference` | id, task_id, artifact type/uri, digest when available, submitted_by, declared criterion | Starts `REFERENCED` only |
| `Verification` | id, evidence_id, verifier principal, declared exact check, observed outcome, provider response hash, checked_at | `PASS/FAIL/INCONCLUSIVE` apply only to that specific check |
| `Review` | id, task_id, independent reviewer, criteria decisions, justification, time | Permits `IN_REVIEW -> DONE` only by scoped policy |
| `MemoryProjection` | project/source ref, memory provider id, derived version, status, last indexed watermark | Unverified derived data, rebuildable from authoritative events and source records |
| `OutboxEvent` | event id, project, projection operation, attempts, delivery/retry status | Atomic intent; consumers at-least-once with idempotent processing and reconciliation |

Proposed SQL additions belong in a separate reviewed migration **after** this contract is ratified. A task version increment is **not** necessary for each Observation, but checkpoint acceptance must protect the active task version/lease and prevent concurrent writers; observation-specific revision/correlation sequencing needs separate evaluation.

## 3. Current code versus proposed interfaces
The following **already exist** in `http_api.py`: 10 scoped REST endpoints (plus unscoped `/healthz`), including GET task/events/context, POST memory-search, create/publish/claim/offer/accept/submit. MCP is **read-only** and delegates to the same REST auth. `submit` stores an unverified EvidenceReference and sets `IN_REVIEW`, **not DONE**.

The seven **proposed (not implemented)** operations are listed in the JSON contract:
1. `POST /v1/projects/{project_id}/observations`: strict text/source_ref, server-derived actor, project grant `observation:write`; `ASSERTED` only. R1.
2. `POST /v1/projects/{project_id}/tasks/{task_id}/checkpoints`: lease token + expected task version + structured pending/complete claims; append event + immutable checkpoint. R1.
3. `GET /v1/projects/{project_id}/tasks/{task_id}/resume`: B's authenticated, newly authorised read of task, snapshot/refs, outstanding work and verified facts; NO hidden lease issuance, no stale/unverified decision promotion. R1.
4. `POST /v1/projects/{project_id}/tasks/{task_id}/review`: independent reviewer + explicit criterion verdict; may accept `IN_REVIEW->DONE` or request changes. R2.
5. `POST /v1/projects/{project_id}/evidence/{evidence_id}/verify`: trusted verifier checks immutable ref, Git/CI results and exact claim; model-generated claims alone cannot drive PASS. R2.
6. `POST /v1/projects/{project_id}/memories/{memory_id}/invalidate`: authorized lifecycle event and projection deletion/invalidating old entries. R2.
7. `POST /v1/projects/{project_id}/tasks/{task_id}/lease-recovery`: **DEFERRED**, requires separate threat model for lost response; recovery must NEVER reveal/replay an old lease secret.

Every future mutation must validate scoped grants, actor from auth (not input), idempotency and event journaling. Raw SQL access to idempotency/leasing tables must remain privileged. Specific REST body/response JSON schemas require R1 contract testing; they are not approved public APIs in R0.

### Contract discrepancy already present
WORK-01 M09 described `same key+same body -> same result`. WORK-02D deliberately changed **lease-issuing** `claim_task` and `accept_handoff` to return **409** on replay instead of returning a raw lease token. R0 codifies this **security exception**, not a regression. If caller loses initial response, do NOT retry blindly, mint a new lease, read secret from response history, or claim success. Fail closed and use the future authorised recovery/reassignment procedure only after design and validation. Other mutations retain their own idempotency contracts.

## 4. Canonical UC-CORE-01 journey
The machine-readable `journey[]` lists 14 ordered steps. The expected *task-version milestones* are:
`create DRAFT v1 -> publish READY v2 -> A claim IN_PROGRESS v3 -> A observation/checkpoint v3 -> A offer BLOCKED v4 -> B accept IN_PROGRESS v5 -> B new-process resume (read) -> B submit IN_REVIEW v6 -> independent verifier remains v6 -> authorized reviewer DONE v7`. These are **target synthetic oracle values**; R1/R2 must first validate concurrency and exact DB implementation. Negative checks include A's revoked lease, cross-project C and snapshot reuse after revocation.

Important: after B accepts, lease credentials are returned **only at that transition** through the authorised channel; `resume` is read-only. A restarted B process which has lost its current lease secret must not silently regain write rights.

### Result and event verification
A Git commit SHA proves that a commit can be identified. A GitHub Actions success proves that a named run completed successfully. Neither proves an acceptance criterion or allows `DONE` automatically. Evidence check policy requires service-side fetched state and explicit scope: repository, SHA, workflow id, target criterion, verifier identity, checked_at, source digest.

### Crash and side-effect semantics
`agent process exit` and `external action completed` are different. Track intent id + external idempotency key + observed provider result. If the provider response is lost, mark `OUTCOME_UNKNOWN` and reconcile before retrying; never claim universal exactly-once for uncontrolled providers.

## 5. Permission contract
| Role | Allowed conceptual operations | Prohibited |
|---|---|---|
| MANAGER | create/publish/authorized reassignment | Does not automatically verify evidence or approve its own agent claims |
| AGENT_A | execute with active lease, scoped observation, checkpoint, offer handoff | Mutations with stale token after offer; evidence self-PASS |
| AGENT_B | accept handoff, new-session read/resume, execute with fresh lease, submit | Reuse previous agent lease or approve own result |
| VERIFIER | independent external artifact checks, append immutable Verification | Task DONE without separate approved review authority |
| REVIEWER | specific criterion review and explicit authorised accept/reject | Trust model text as verified CI without source check |
| UNAUTHORIZED_C | no access to Alpha's resources | Cross-project read/write, even through MCP or semantic memory |

Actual privileges **must be enforced by PostgreSQL server-side grants and authenticated principals**, not by strings in the example. Principal may hold several roles in reality; **separation-of-duty** must compare effective identity, not just role label.

## 6. Critical invariants and failure contract
- Task status, actor, permissions, lease and acceptance live in PostgreSQL. Mem0 may contribute **UNVERIFIED** memory candidates only.
- All context refs are filtered at issuance **and** independently reauthorised when read later. Revocation wins; inaccessible referenced material must be excluded or denied with explicit status.
- Task mutations with stale expected_version -> 409 and no event/side effect. Lease mismatch/expiry -> 403 or 409 per audited error map, never implicit permission.
- Handoff acceptance must reserve one active lease, prevent A/B double-writes and record handoff acceptance plus task version event atomically.
- Events and review decisions are append-only with correction/supersession; privacy erasure requires a dedicated retention/deletion policy without leaking content into audit logs.
- Semantic provider down -> authoritative state accessible where permitted with `memory_status=unavailable` and no fabricated fallback.
- Unsupported client, LLM injection, cross-tenant memory metadata or unverified status cannot approve tasks/decisions.
- External receipt means **evidence of what was observed**, not guarantee that a third-party effect happened once.
- REST, MCP and future A2A must enforce the same effective server policy; generic MCP mutation tools must not expose reviewer/approval rights.

## 7. Acceptance, implementation boundaries and gates
[UC_CORE_01_ACCEPTANCE.md](UC_CORE_01_ACCEPTANCE.md) maps WORK-01 M01–M18 to current conservative coverage and new tests. **None is claimed fully passed as a product end-to-end acceptance solely by this R0.**

**R1 (next candidate slice):** SQL migration for SourceRecord/Observation/TaskCheckpoint/ContextSnapshot references and minimal AgentRun; REST authorised observations/checkpoints/resume, append-only event and outbox, 2-process restart test, A/B lease and Beta isolation. Keep task review in R2; B's submit remains IN_REVIEW.

**R2 (trust & lifecycle):** external Git/CI verifier, criterion-bounded Verification, distinct reviewer transition to DONE, memory correction/expiry/erasure, projection reconciliation, crash-after-effect idempotency, stronger auth/resource policy tests. Lease recovery is a separate security gate; do not accelerate it via token replay.

**Gate to claim R0 complete:** docs + JSON contract + static validator tests committed and CI green; operator ratification for schema/permission choices remains OPEN. **Gate to claim full MVP:** M01–M18 pass under deterministic and isolated real PostgreSQL/Mem0 conditions with an independent two-client E2E, operator review and security sign-off.

## 8. Research alignment and open decisions
The comparison SI-RD-03 must not block deterministic authority. Keep Mem0 pinned and replaceable; investigate Hindsight, Graphiti, SoMem and durable-workflow frameworks in independent experiments. No provider claims `VERIFIED` by default.

**Requires explicit operator ratification before R1:** schema/migration names and retention model, whether R1 exposes write-observation over MCP or REST only (recommend REST first), exact reviewer vs verifier policies, partial snapshot failure behavior, lost-lease recovery and chosen initial customer use case. Recommended baseline: synthetic first user two coding agents, no external business/customer data.

**What was NOT done:** no migration, auth change, API added, runtime execution, Jarvis integration, SI-RD-03 benchmark, production CI pass assumption, client execution, commercial validation.


## R1A progress — later implementation (not R0 historical state)
The R0 baseline above documented 10 existing routes and 7 future proposals. The canonical JSON has since been updated to **14 implemented laboratory routes and 6 proposed routes**: new AgentRun start, SourceRecord register, Observation assertion and authorized observation read. M02 is R1A_LAB_PARTIAL, while M01-M18 full acceptance remains PENDING_FULL_E2E. See R1A_IMPLEMENTATION.md. No checkpoint/resume, independent verification, reviewer DONE or production deployment is implied.


## WORK-03B R1B — Execution update (experimental)
The original R0 10/7 route counts above are historical. After R1A and R1B the DRAFT machine contract describes **16 live experimental routes and 4 proposed routes**, including POST checkpoint and GET resume. S05 and S09 are **R1B_LAB_PARTIAL**; M05/M12/M16/M17 partial as detailed in the current acceptance matrix. Full UC-CORE-01 acceptance and model-independent evidence verification are **not implemented**.


## WORK-03B R1C — execution update (experimental)
The historical R0 and R1A/B route counts above are intentionally preserved as the history at those commits. Canonical JSON now describes **18 laboratory routes / 3 future R2 routes** (two R1C endpoints: lease-status and lease-recovery). Handoff operations share their original routes but bind exact checkpoint ID/sequence when a task contains checkpoints, prevent generation regression and allow authorized current-holder-only lost/expired secret rotation. Tasks without any checkpoint retain an explicitly `LEGACY_UNBOUND` path for historical compatibility. No full UC-CORE-01 acceptance or R2 verifier/reviewer was added.
