# Candidate REST & MCP Contract — v0.1

**Status: DRAFT, not implemented.** All routes and tool names below are provisional.

## 1. Common rules
- Base `/v1`. JSON request/response, UTF-8; timestamps UTC ISO-8601, stable resource IDs.
- Authentication: short-lived service/user credentials. Organization and project access resolved from token + server-side grants.
- Mutations require `Idempotency-Key`; state transitions additionally require `expected_version`.
- Responses expose `request_id`, `resource_version`, `actor` and authoritative timestamps where applicable.
- Server must not forward a project-wide Mem0 admin key to any consumer.
- Fail closed on denied scope, invalid tool parameters, expired leases, unknown provenance and incompatible versions.
- No endpoints that allow an agent to set `verified=true` or `approved=true` merely by passing a boolean.

## 2. REST endpoints (proposed)

| Method | Path | Meaning | Minimum permission |
|---|---|---|---|
| GET | `/v1/projects/{project_id}/context` | Authorized contextual snapshot, with source refs and freshness | context:read |
| POST | `/v1/projects/{project_id}/observations` | Append a sourced **unverified assertion** | observation:write |
| POST | `/v1/projects/{project_id}/memories/search` | Semantic candidates, filtered by server grants | memory:read |
| POST | `/v1/projects/{project_id}/tasks` | Create draft task | task:create |
| GET | `/v1/projects/{project_id}/tasks/{task_id}` | Read authoritative task state | task:read |
| POST | `/v1/projects/{project_id}/tasks/{task_id}/publish` | DRAFT → READY | task:manage |
| POST | `/v1/projects/{project_id}/tasks/{task_id}/claim` | Acquire exclusive lease and start | task:execute |
| POST | `/v1/projects/{project_id}/tasks/{task_id}/submit` | IN_PROGRESS → IN_REVIEW | task:execute |
| POST | `/v1/projects/{project_id}/tasks/{task_id}/review` | Accept or request changes (policy checked) | task:review |
| POST | `/v1/projects/{project_id}/tasks/{task_id}/handoffs` | Offer handoff, block/release task lease | handoff:offer |
| POST | `/v1/projects/{project_id}/handoffs/{handoff_id}/accept` | Accept offer + acquire lease atomically | handoff:accept |
| POST | `/v1/projects/{project_id}/evidence` | Register external evidence reference | evidence:submit |
| GET | `/v1/projects/{project_id}/events` | Read scoped append-only activity | audit:read |

Not all clients need all endpoints; MFA/approval requirements may restrict sensitive operations even for permissioned principals.

## 3. Example: create a handoff offer (synthetic)

```http
POST /v1/projects/PRJ123/tasks/TASK123/handoffs
Authorization: Bearer <service-token>
Idempotency-Key: 6a2715d9-2fc2-4a7f-873b-fac17ba9ef3f
Content-Type: application/json
```

```json
{
  "to_agent_id": "agent-b",
  "expected_version": 4,
  "summary": "Changed implementation; integration test remains pending.",
  "evidence_refs": ["EVID123"],
  "context_refs": ["CTX123"]
}
```

Server returns `201` with `state=OFFERED`, `task_status=BLOCKED`, `handoff_id`, `task_version=5`, timestamps and correlation IDs. No promise of approval or verification.

Agent B calls `accept` with latest `expected_version=5`; server either returns `200` with a new exclusive lease/fencing generation or `409` if the task changed. Stale source credentials cannot continue to mutate.

## 4. API error conventions
- `400` malformed input, `401` missing/invalid authentication, `403` authenticated but forbidden.
- `404` when a scoped resource does not exist; for sensitive deployments return 404 instead of 403 where revealing existence leaks data.
- `409` stale version, lease contention or conflicting idempotency reuse.
- `422` valid JSON but failed domain invariants (or align with FastAPI's validation semantics before final contract).
- `429` rate-limited; `503` semantic memory temporarily unavailable (authoritative tasks still accessible).
- Never echo API keys, full untrusted prompts, or private records into error messages/logs.

## 5. MCP tools (projection of the SAME service rules)
- `get_project_context(project_id, task_id?, purpose?)`: read-only, bounded retrieval.
- `search_memories(project_id, query, limit)`: read-only, scoped and capped.
- `write_observation(project_id, task_id?, content, source_ref?)`: unverified append, no status transition.
- `get_task(project_id, task_id)`: read authoritative state.
- `offer_handoff(project_id, task_id, to_agent_id, expected_version, summary, evidence_refs)`: change with explicit policy.
- `accept_handoff(project_id, handoff_id, expected_version)`: change with explicit policy.
- `submit_result(project_id, task_id, expected_version, evidence_refs)`: transitions to review only.

`approve_decision` and `accept_result` are **not exposed to generic model-agent MCP clients** in MVP. They remain protected human/reviewer workflows or separately trusted automated policies.

MCP is **not** a transport-security or auth substitute. Its tools must call the same domain service and policy as REST, with individually verified caller identities.

## 6. Operational safeguards
- Hard cap results (top_k), payload lengths, tool call rate and request duration.
- Include source IDs and trust labels in read results.
- Authoritative tasks are never read from Mem0's semantic index.
- Re-check permissions at context retrieval even if an older ContextSnapshot was valid.
- Clients must acknowledge freshness flags and not silently treat stale search as complete.
- Add pagination and streaming only after basic semantics and limits are accepted.

## 7. Client interoperability acceptance
A Python client, an MCP test client and an n8n HTTP workflow must observe the **same** task/handoff states for the same grant set, and all must receive denial for cross-project operations. This is a specification goal, not a tested outcome.
