# Domain Model — v0.1

**Status: RECOMMENDATION.** This defines a logical model, not committed SQL migrations.

## 1. Ubiquitous language and source of truth

| Entity | Meaning | Authoritative store |
|---|---|---|
| Organization | Security/ownership tenant | RIGHTWARE PostgreSQL |
| Project | Authorized work boundary belonging to one organization | RIGHTWARE PostgreSQL |
| Principal | Authenticated user, agent service identity or application | RIGHTWARE PostgreSQL / identity provider |
| Agent | Registered logical actor, linked to a principal and capabilities | RIGHTWARE PostgreSQL |
| ProjectGrant | Explicit allow for principal, project, action and conditions | RIGHTWARE PostgreSQL |
| Task | Unit of assigned work, objective and acceptance requirements | RIGHTWARE PostgreSQL |
| TaskLease | Time-limited right to actively operate on a task | RIGHTWARE PostgreSQL |
| Handoff | Explicit offer/acceptance to transfer work/context | RIGHTWARE PostgreSQL |
| AgentRun | Bounded execution attempt with correlation and agent/version metadata | RIGHTWARE PostgreSQL |
| Assertion | Untrusted statement made by an agent, human or external source | RIGHTWARE PostgreSQL |
| Evidence | Immutable reference and independently observed validation | RIGHTWARE PostgreSQL + external source |
| Verification | Reproducible check result by a specified verifier | RIGHTWARE PostgreSQL |
| Decision | Proposed, approved, rejected or superseded organizational choice | RIGHTWARE PostgreSQL |
| ContextSnapshot | Versioned set of references assembled for a particular access decision | RIGHTWARE PostgreSQL (manifest) |
| MemoryItem | Contextual fact or extracted memory with its provenance | Mem0 index, backed by source records |
| Event | Append-only state transition and actor, time, reason | RIGHTWARE PostgreSQL |
| OutboxEvent | Transactional intent to update derived indices or notify systems | RIGHTWARE PostgreSQL |

Identifiers are stable opaque IDs (recommended UUID/ULID); public request IDs must not be accepted as proof of access.

## 2. Relationships
- One Organization owns many Projects; one Project owns many Tasks, Handoffs, Decisions, Assertions and MemoryItems.
- A Principal may be granted rights in multiple Projects; permissions are project-specific and action-specific.
- One Task may have many AgentRuns, Handoffs, Assertions, Evidence and Verification records.
- A Handoff references **one Task** and identifies from-agent, intended to-agent, offer state, expected task version, and optional evidence/context-snapshot references.
- A Decision belongs to one Project, has a proposed author and separately recorded approving principal where approval is required.
- A MemoryItem may point to one or more source Assertions, Events, Decisions or Evidence records; search results never replace those records.
- Each authoritative mutation appends an Event atomically, plus OutboxEvent if a projection must be updated.

## 3. Core invariants
1. **Tenant scope:** every resource belongs to exactly one organization; project ownership cannot be changed by client-supplied metadata.
2. **Authorization:** an authenticated actor and a project grant must permit every read/write; `rw:org:project` string filters are **not** authorization.
3. **No authority by assertion:** agent-written memories/claims cannot set Task=DONE, Evidence=VERIFIED, or Decision=APPROVED.
4. **Versioned transitions:** Task state changes require `expected_version`; stale updates return a conflict without losing either event.
5. **Single active lease:** at most one exclusive active lease per task in MVP; expiry and renewals are server-time controlled. Parallel read-only work is possible.
6. **Handoff atomicity:** accepting a handoff must acquire the target lease and record acceptance in a single transaction; if version/lease has changed, reject or retry explicitly.
7. **Evidence independence:** an external identifier is only a reference until a verifier records status and what was checked; a commit hash alone does not prove requirements were fulfilled.
8. **Immutable history:** no destructive rewriting of Events or Verification results; corrective Events supersede earlier claims. Privacy deletion/redaction requirements need a specific policy.
9. **Idempotency:** every mutating API operation accepts a client idempotency key, scoped to principal/project/operation; same key+body returns same result, same key+different body is conflict.
10. **Degraded search:** if Mem0 is offline, authoritative tasks and permissions remain readable; semantic context may be marked stale/unavailable, never silently fabricated.

## 4. Trust model (not a numerical truth score)
- `ASSERTED`: statement received from an actor; unverified.
- `SOURCE_LINKED`: linked to a source reference but not independently checked.
- `CHECKED_PASS`: deterministic verifier confirmed the **declared check**; not global truth.
- `CHECKED_FAIL` / `INCONCLUSIVE`: evidence did not establish the claim.
- `APPROVED`: authorized decision/acceptance actor approved via policy, distinct from checks.

These are distinct attributes for different entities; they are not a single universal `trust` boolean. A successful CI job may warrant CHECKED_PASS for "CI job succeeded" but not automatically for "feature is correct".

## 5. Minimal logical fields
- `tasks`: id, organization_id, project_id, title, objective, acceptance_criteria_json, status, version, created_by, created_at, updated_at.
- `task_leases`: id, task_id, principal_id, expires_at, lease_token_hash, created_at, released_at.
- `handoffs`: id, task_id, from_agent_id, to_agent_id, state, expected_task_version, context_snapshot_id, offered_at, resolved_at.
- `assertions`: id, project_id, task_id nullable, author_principal_id, content, source_ref, observed_at, claim_kind.
- `evidence`: id, task_id, kind, uri, external_ref, captured_at, digest nullable, verifier_status.
- `verifications`: id, evidence_id, verifier_id, criteria_version, result, checked_at, details_json.
- `decisions`: id, project_id, subject, proposal, state, proposer_id, reviewer_id nullable, approved_at nullable.
- `events`: id, organization_id, project_id, aggregate_type, aggregate_id, aggregate_version, actor_id, event_type, occurred_at, payload_json, correlation_id.
- `outbox_events`: id, event_id, type, payload_json, created_at, delivered_at nullable, retries.
- `context_snapshots`: id, project_id, subject_task_id nullable, refs_json, projection_watermark, created_for_principal_id, created_at.

Index candidates: `(organization_id, project_id)` on all scoped tables, `(aggregate_id, aggregate_version)` UNIQUE, lease expiry, external evidence ID, outbox undelivered timestamp. Choose exact keys and row-level-security strategy after the DB threat model.

## 6. Open choice
A single PostgreSQL instance with distinct schemas/roles is initially recommended. Mem0's own migrations and schema ownership must be audited before sharing the same physical instance; independent instances remain a valid alternative. There is no approval of cross-service table writes.
