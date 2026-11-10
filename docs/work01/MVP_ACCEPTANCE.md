# MVP acceptance contract — WORK-01 specification

**Status:** future acceptance plan; **no live Mem0 / PostgreSQL / MCP tests were executed in WORK-01.**

## 1. Core question
Can two independently running authorized agents or client programs share project context, exchange a controlled handoff, recover accurately after interruptions, and prove which results are observed versus verified — without unauthorized access to a second project?

## 2. Test environment proposal
- One RIGHTWARE server process with PostgreSQL and Mem0 self-hosted in a private isolated environment.
- Two separate client identities (Agent A, Agent B) in Project Alpha.
- A third unauthorized principal and a separate Project Beta to test access boundaries.
- Synthetic tasks and source documents only; no private project information.
- A deterministic evidence verifier fixture simulating GitHub external results; a real GitHub read-only check is a later optional gate.
- Reproducible database migrations, seeded fixtures, explicit server/client versions and captured test evidence.
- No default paid external LLM APIs or embeddings unless separately approved and recorded.

## 3. Acceptance matrix

| ID | Scenario | Pass criterion |
|---|---|---|
| M01 | Create/publish/claim task | Correct task versions and one exclusive lease |
| M02 | Agent A appends observation + source | Stored as ASSERTED; cannot mark task DONE |
| M03 | A offers handoff and releases lease | Handoff OFFERED; task BLOCKED; event history complete |
| M04 | B accepts handoff | Exactly one live lease for B; A's old lease rejected |
| M05 | B retrieves project context | Approved scoped refs, task state and source labels are correct |
| M06 | B submits result | Task IN_REVIEW, not DONE |
| M07 | Independent verifier and reviewer | Verification records specific check; DONE only with authorized acceptance |
| M08 | Stale version update | 409 with no lost update, version unchanged |
| M09 | Replayed/duplicate request | Same key/body idempotent; same key/different body 409 |
| M10 | Cross-project queries, reads, writes | 100% denied for unauthorized principal (including MCP) |
| M11 | Concurrent handoff acceptance | At most one accepted transfer/lease, deterministic conflict for loser |
| M12 | Mem0 unavailable | Authoritative task and audit read still work; semantic search explicitly unavailable |
| M13 | Stale/revoked context | Revoked resource is not returned, even with old snapshot |
| M14 | Model-injected instruction in memory | Treated as data; no unauthorized tool or status transition |
| M15 | Source/evidence mismatch | Verification FAIL/INCONCLUSIVE; no implicit success |
| M16 | Restart & replay | All authoritative state and event history persist; pending outbox replay recovers |
| M17 | Python REST and compatible MCP client | Same server policy/state; no alternate permission bypass |
| M18 | Event and idempotency traces | Every mutation traceable by principal, time, correlation and resource version |

## 4. Minimum exit conditions
- All M01–M18 pass in an isolated reproducible run; evidence includes command, SHA, environment, results and known limitations.
- Zero unauthorized cross-project reads/writes and zero false claims of verified/approved completion in the test set.
- Repeated concurrent lease/handoff tests reproduce the single-writer invariant.
- CI/automated tests must not be conflated with a production security certification.
- A manual review inspects the evidence of at least one complete two-agent run.
- No hard-coded customer names, proprietary documents or credentials in the fixtures.

## 5. Metrics to record, not promise
- Handoff completion success rate across deterministic scenarios.
- Conflict and error rate, including expected 409 responses.
- Retrieval precision/recall on an approved synthetic gold set.
- End-to-end context retrieval latency p50/p95 and cost per indexed memory.
- Index projection lag between authoritative event and Mem0 availability.
- Backup/restart and recovery evidence.

No performance SLA is set yet; choose thresholds after hardware/runtime baseline to avoid invented claims.

## 6. Distinct acceptance scopes
- **Core acceptance:** PostgreSQL transactions, policy, tasks and handoffs without any model.
- **Memory acceptance:** actual Mem0 backend, local model/embedding behavior, source/relevance.
- **Protocol acceptance:** REST and MCP against identical policy, clients in separate processes.
- **Integration acceptance:** optional n8n, Jarvis and PULSE, each with project-specific authorization and its own evidence.

A passing FAKE test validates its harness, not real inference, Mem0, Docker, GPU, Windows, external GitHub integrations or client MCP compatibility.

## 7. NEXT implementation work (not authorized by this document)
1. Create domain SQL migrations and deterministic transaction tests.
2. Build a minimal authenticated FastAPI domain API over PostgreSQL.
3. Set up Mem0 self-hosted under a pinned profile; verify provider costs and outbound network settings.
4. Add outbox projection and fail-closed context retrieval.
5. Add MCP adapter and run two-process handoff demonstration.
