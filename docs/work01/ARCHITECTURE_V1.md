# Architecture v1 — Independent Shared Intelligence

**Status: architecture proposal; WORK-00 adapter is the only implemented connection code.**

## 1. Functional view

```text
Authorized clients: Jarvis | PULSE | coding agents | n8n | independent apps
    |
    +-- REST/HTTPS ----------------------------------------------------+
    |                                                               |
    +-- MCP client -> RIGHTWARE MCP adapter -------------------------+
                                                                    |
                                                     RIGHTS + API GATEWAY
                                                     principal authn/authz
                                                     project boundaries
                                                                    |
                                              RIGHTWARE CORE (modular monolith)
                                     +----------------------+------------------+
                                     | task/handoff/decision| context/memory    |
                                     | transactional       | projection/recall |
                                     +----------------------+------------------+
                                                |                         |
                                       PostgreSQL (authoritative)    Mem0 adapter
                                                |                         |
                                         transactional outbox     Mem0 self-hosted
                                                |                         |
                                       workers/projection sync     vector index
                                                |
                                      GitHub verifier / future n8n
```

MCP, REST, and n8n use identical core policies; no bypass routes. Raw Mem0 API is private and never exposed as the trusted organization API.

## 2. Deployable shape
**Start as a modular monolith in Python**, not a fleet of microservices:
- FastAPI gateway and domain services in one application process.
- PostgreSQL transactional DB with scoped tables and append-only event history.
- Mem0 self-hosted as a separately pinned dependency/service behind a `MemoryProvider` interface.
- A small background worker for transactional-outbox projection and optional evidence checks.
- Optional MCP endpoint/package that invokes the same application service as REST.
- n8n is **optional** and may call REST or MCP; it is not required for storing or reading memory.
- SDKs call the public gateway; Java/TypeScript can use OpenAPI-generated clients.

WORK-00 `rightware_si/memory.py` is a *trusted-only experimental Mem0 transport adapter*. It is NOT an externally accessible API, auth service or production tenancy system.

## 3. Why two storage responsibilities?
- **PostgreSQL:** who has authority, task state, versions, decisions, events, evidence, idempotency, leases and durable source records.
- **Mem0:** derived contextual memories and semantic retrieval.
- If both use PostgreSQL, prefer separate schemas/DB roles and independent migration control; do not assume Mem0's vector tables are valid domain event stores.
- The authoritative record must be queryable without Mem0.

## 4. Consistency contract
1. On a domain write, a **single PostgreSQL transaction** commits state, Event and OutboxEvent.
2. A worker consumes OutboxEvent and updates Mem0's derived index asynchronously.
3. Each ContextSnapshot records a `projection_watermark` and source refs; context API can report `fresh`, `stale`, or `unavailable`.
4. Task read-after-write MUST use PostgreSQL; no domain state inferred solely from a stale Mem0 response.
5. Projection retry is at-least-once, requiring idempotent writes or de-duplication. Do not claim exactly-once cross-system delivery.
6. If Mem0 or its embedder is unavailable, domain transactions remain available and semantic search fails explicitly; never fabricate context.

## 5. Context retrieval order
1. Identify authenticated principal, project and purpose.
2. Resolve applicable project grants and resource-level restrictions.
3. Load authoritative state and relevant decision/evidence refs from PostgreSQL.
4. Retrieve candidate Mem0 memories **under server-enforced scope**; do not trust a client-supplied `user_id` as access control.
5. Re-check candidate authorization; remove quarantined or revoked data.
6. Return context with provenance, trust/verification markers, timestamp and watermark, not a raw unlabelled prompt.
7. Client chooses how to use returned data; model-facing text is untrusted data, not instructions.

## 6. Integrations
- **Jarvis:** opt-in Python adapter calling REST; personal/local memory remains separate; no dependency on cloud connectivity for local functions.
- **PULSE:** service-to-service client with explicit organization/project grants; PULSE retains its own business records as authoritative.
- **Coding agents:** MCP tools for context, observation and handoff; cannot turn a self-report into approved task completion.
- **GitHub:** independent verifier reads exact repository/commit/CI refs when authorized; no GitHub credentials in memory text.
- **n8n:** webhook or scheduled actor with least-privilege project permissions; workflow failure does not corrupt authoritative state.

## 7. Implementation milestones
- **M1** SQL schema, domain transitions, privileges, Event/Outbox transaction, no Mem0 dependency.
- **M2** work from WORK-00 adapter toward a local Mem0 integration with explicit LLM/embedder config and no unintended cloud calls.
- **M3** server-side retrieval scope plus REST contract; two independent synthetic clients.
- **M4** MCP adapter on same services, real client compatibility test.
- **M5** evidence checker for immutable GitHub refs and one real (non-sensitive) handoff.
- **M6** Jarvis/PULSE/n8n integration only after acceptance gates, with no forced coupling.

## 8. Technical open questions
- Whether Mem0 self-hosted can run fully with an approved local embedding+extraction stack in the exact pinned version; its bundled server provider list is limited.
- HTTP MCP transport choice and authentication design for deployed clients.
- Whether a single PostgreSQL instance with separate schemas is operationally simpler than independent DBs.
- Which subset of domain grants belongs in a local auth service versus existing identity provider.
- Backups, key management, erasure policies and hosting costs.
