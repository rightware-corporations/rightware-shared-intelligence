# Security, Authority and Privacy — WORK-01

**Status: proposed controls, NOT implemented or certified.** Public repository — no personal/enterprise secrets.

## 1. Threat surfaces
1. Untrusted LLM text, prompt-injected documents or model fabricated success.
2. Unauthorized project reads/writes; cross-organization data leakage.
3. Spoofed agent IDs or client-supplied tenant IDs; borrowed API keys.
4. Conflicting concurrent task updates; replayed handoffs; expired leases.
5. Retrieval poisoning, sensitive information reflected in context or logs.
6. External service outage, delayed Mem0 projections and stale context.
7. Compromised GitHub/n8n/MCP integrations, leaked credentials, excessive tool grants.
8. Data retention conflicts, deletion requests, hidden copies and backups.

## 2. Authentication and authority
- Every request resolves an authenticated Principal (human, service, registered agent).
- Server derives/validates allowed organization and project memberships; never trusts the `rw:org:project` Mem0 naming convention for permissions.
- Each API/tool action requires least-privilege grant, checked at use, not inferred from the model's identity statement or prompt.
- `agent_id` is descriptive metadata; cryptographic identity belongs to an authenticated Principal with registered agent delegation.
- Separate authorities: `task:execute`, `task:review`, `decision:approve`, `memory:write`, `memory:read`, `audit:read`.
- No generic model MCP tool with unrestricted admin access or organization-wide Mem0 service key.
- Token credentials short-lived, stored in secrets manager, not logs/context; TLS remote traffic, loopback exceptions only for isolated development.
- Permission revocations must take effect before new context or task actions, including old snapshots and cached results.

## 3. Proposed role capability map
Roles are convenience templates; grants still enforce organization/project/action conditions.

| Role template | Typical capabilities | Critical restrictions |
|---|---|---|
| ORG_OWNER | organization membership/roles, oversight | Requires high-risk confirmation; no implicit override of audit history |
| PROJECT_MANAGER | create/publish/cancel tasks, assign reviewers | Must not bypass evidence requirements by default |
| AGENT_WORKER | read authorized context, claim/submit task, offer handoff, write observations | Cannot approve own work or decisions |
| REVIEWER | verify/accept work, annotate decisions | Must satisfy separation-of-duties policy |
| READER | project context and task read only | Cannot write or claim leases |
| AUTOMATION_SERVICE | explicitly scoped events and updates | No cross-project wildcard grant |

Pilot can start with one organization and two projects, but security tests must already cover multiple principals and forbidden access.

## 4. Trust and memory poisoning
- All model output is untrusted data even if originated from a known agent.
- A `save_memory` action yields an ASSERTED record, not VERIFIED/APPROVED authority.
- Prompt-injected text in memory must be labeled as data; tools are selected/executed only by the trusted policy layer.
- Evidence references must be validated with allowlisted provider APIs, repository identity, commit SHA, expected workflow and immutable run IDs.
- Verifier records what it checked, expected values, timestamps, failures and limitations.
- Content promoted into context is checked for the requester's grants, quarantine status, source validity and retention policy; do not rely only on the vector index's filter.
- Privileged transitions require a separate authenticated actor/policy; agent self-attestation cannot satisfy a critical review.

## 5. Concurrency and integrity
- Optimistic task versions + exclusive fenced leases.
- Handoff acceptance and lease transfer in one PostgreSQL transaction.
- Idempotency keys plus payload hashes prevent duplicate writes or conflicting reuse.
- Event history with actor/correlation IDs; append-only ledger semantics for application changes.
- Derived memory index updated by transactional outbox, at-least-once; repairable on failures.
- No silent acceptance of stale or cross-project memory responses.
- Rate limiting, maximum input sizes, timeouts and request cancellation safety.

## 6. Data handling
- Default to synthetic data until security and retention controls are verified.
- Explicit consent and project scope before storing personal conversations.
- Classification: PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED (provisional).
- Define retention per data category, export and deletion flows, backup policies and legal hold exceptions before production.
- Store references/hashes rather than full raw secret-bearing artifacts whenever possible.
- Access logs record operation metadata and outcome, not raw conversations or credentials.
- If deletion/redaction is approved, propagate to Mem0 derived indices, source records according to law/policy, caches and backups per documented schedule; immutable audit metadata must not override applicable privacy requirements.

## 7. External integrations
- **Mem0:** hosted behind RIGHTWARE gateway; own service credentials never exposed to clients. Upstream default external LLM/embedder config must be replaced/approved. Telemetry settings audited.
- **MCP:** tool schema validation, caller auth, per-tool grants, bounded outputs, no unsafe generic command execution.
- **GitHub:** read-only evidence checks at first; privileged repo writes separate scope and human confirmation.
- **n8n:** workflow credentials scoped to one purpose and project; nodes cannot write approved decisions without reviewer policy.
- **Jarvis/PULSE:** separate integration tokens, independent release cadence, no automatic cross-app data sharing.

## 8. Required security tests before any deployment
- Cross-project read, search, write and handoff denied on REST **and** MCP.
- Untrusted memory cannot influence authorization or cause tool execution.
- Stale `expected_version`, duplicate idempotency key, replayed handoff, expired lease denied.
- Two concurrent handoff acceptances never create two active leases.
- Expired, revoked, deleted, quarantined or stale data cannot leak through context.
- Mem0 unavailable → authoritative task status remains reliable; no false-success response.
- CI evidence is independently fetched; mismatched repository/SHA/job is rejected.
- Secrets absent from logs, responses, Git history and telemetry.

## 9. Release gate
No external multi-tenant production use, external customer data, public Mem0 endpoint, or unreviewed agent execution until controls are implemented and independently tested.
