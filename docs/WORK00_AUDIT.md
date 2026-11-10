# WORK-00 — preliminary findings

Status: source inspection + deterministic integration contract; not a deployment or full code-security audit.

| Candidate | License | Language | Assessment |
|---|---|---|---|
| mem0ai/mem0 | Apache-2.0 | Python | Chosen for pinned *evaluation*: self-hosted API, memory engine, Postgres/pgvector support |
| getzep/graphiti | Apache-2.0 | Python | Temporal graph substrate, more infrastructure; revisit if relationship/time queries justify |
| letta-ai/letta-code | Apache-2.0 | TypeScript | Strong persistent-agent model, but larger agent runtime than a universal memory component |
| mem0ai/mem0-mcp | Apache-2.0 | Python | ARCHIVED; not recommended as required self-hosted MCP |

Key gap: memory is not an authoritative operational event store. Need structured task state, evidence, revisioning, ACL, tenant isolation, retention and deletion policy.

Security issues to test before any external deployment:
1. API key scoping per organization/project, enforced on server, not via client-supplied user_id.
2. Prompt injection and memory poisoning, including an agent fabricating successful work.
3. Concurrent updates, contradictory facts, idempotency, versioning, replay.
4. Privacy and retention: no silent ingestion of personal chats; opt-in and deletion.
5. Model / embedding provider routing: upstream default can trigger paid APIs.
6. Public repo: never commit secrets, personal data, private business content.

Next acceptance gate: in an isolated environment start pinned Mem0 self-hosted with an explicit approved local model configuration and fake/synthetic data, verify two independent clients and confirm no unapproved external requests. No claim of those results yet.
