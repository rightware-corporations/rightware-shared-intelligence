# WORK-02B — Authenticated FastAPI + read-only MCP 2.x adapter

**Status:** ISOLATED ENGINEERING PROTOTYPE. NOT PRODUCTION-READY. No changes to Jarvis or PULSE; nothing deployed or merged.

## 1. What this phase adds
- A FastAPI gateway exposing the existing WORK-02A PostgreSQL transactional task/handoff functions.
- A new PostgreSQL table holding **SHA-256 hashes of high-entropy random bearer tokens**, associated with existing Principals; tokens may expire and be revoked.
- A trusted local offline CLI to issue/revoke tokens, with one-time plaintext display.
- A **read-only MCP v2 stdio bridge**, whose tools call this exact REST gateway as a separately authorized principal: \`get_task\`, \`get_task_events\`.
- Repeatable integration suite against a disposable PostgreSQL 16 database, including REST, bearer auth, and an in-memory MCP protocol dispatch test.

## 2. Separation of concerns
\`\`\`text
                              +----- FastAPI /work02b -----+
Python REST client ---------->| Bearer authentication      |
MCP host -> stdio MCP bridge->| same REST HTTP endpoint    |
                              | Project-grant checks      |
                              +------------+--------------+
                                           |
                           WORK-02A PostgreSQL WorkCore
                             tasks / version / lease / events

                    Mem0: NOT INTEGRATED IN THIS PHASE
                    Jarvis: NOT MODIFIED IN THIS PHASE
\`\`\`

The MCP bridge *does not* open a public MCP network port, authenticate arbitrary remote MCP users, or provide mutation tools. It runs under one controlled client process with one scoped API token. If the host cannot securely retain the token, do not connect the bridge.

## 3. API paths (experimental)
- \`GET /healthz\` — service process status only, not a full dependency readiness check.
- \`POST /v1/projects/{project}/tasks\` — draft creation, requires task:create.
- \`GET /v1/projects/{project}/tasks/{task_id}\` — authoritative task read, requires task:read.
- \`GET /v1/projects/{project}/tasks/{task_id}/events\` — events, requires audit:read.
- \`POST .../tasks/{task_id}/publish\` — DRAFT → READY.
- \`POST .../tasks/{task_id}/claim\` — READY → IN_PROGRESS; returns temporary lease token.
- \`POST .../tasks/{task_id}/handoffs\` — IN_PROGRESS → BLOCKED with offered handoff.
- \`POST .../handoffs/{handoff_id}/accept\` — BLOCKED → IN_PROGRESS for target agent.
- \`POST .../tasks/{task_id}/submit\` — IN_PROGRESS → IN_REVIEW with UNVERIFIED evidence reference.

Every route except \`/healthz\` requires a bearer token; the actor is **never** read from request JSON. All mutations require \`Idempotency-Key\` and \`expected_version\` for state transitions. Client submissions CANNOT set DONE, APPROVED or evidence PASS.

## 4. Safe local exploratory setup (only on dedicated database)
Preconditions: Python 3.12, PostgreSQL 16, a brand-new empty database \`rw_test\`, and a trusted local operator. The steps below must never run against an existing Jarvis, PULSE, Mem0, business or personal database.

\`\`\`sh
python -m pip install -r requirements-work02.txt -r requirements-work02b.txt
# Set the DSN through your shell/environment secrets; do not commit it.
# RW_SI_DATABASE_URL=postgresql://.../rw_test
python -c "import os, pathlib, psycopg; db=os.environ['RW_SI_DATABASE_URL']; assert db.endswith('/rw_test'); c=psycopg.connect(db,autocommit=True); [c.execute(pathlib.Path(p).read_text()) for p in ('db/migrations/0001_work02_core.sql','db/migrations/0002_work02b_api_credentials.sql')]; c.close()"
\`\`\`

A system administrator must create organization, project, principal and project grants explicitly in the isolated test DB before issuing a key (see \`tests/test_http_api.py\` for **synthetic** examples). This phase intentionally provides **no remote privileged provisioning endpoints**.

\`\`\`sh
python -m rightware_si.token_admin issue --principal agent-a --ttl-hours 24
# Capture token only in a secret store; it will not be displayed again.
# Start local API (loopback only):
uvicorn rightware_si.http_api:app --host 127.0.0.1 --port 8890
\`\`\`

For local stdio MCP, provide a distinct least-privilege read token via \`RW_SI_API_TOKEN\` and \`RW_SI_API_URL=http://127.0.0.1:8890\`, then have a trusted MCP host launch \`python -m rightware_si.mcp_bridge\`. Never paste tokens into shared transcripts.

## 5. Production Jarvis policy
Jarvis is a production consumer. **Do not modify, redeploy or hot-patch it as part of WORK-02B.**
- First integration phase may only use read-only task/context operations under an explicit project-scoped token and user permission.
- Enable via a feature flag disabled by default, with short timeouts and fail-open-to-local-behaviour (not fail-open-to-auth).
- No copying personal Jarvis context to Shared Intelligence automatically.
- Roll back by disabling the integration, not by altering Jarvis's core inference.
- Offline Jarvis flows must not require this API.
- Never use Shared Intelligence's admin/DB identity as Jarvis's MCP token.

## 6. Known production blockers
1. **No enterprise-grade identity management**: local high-entropy bearer tokens are a test authentication baseline, not OAuth/OIDC, short-lived workload credentials, SSO or dynamic delegated authorization.
2. **Lease token persisted in idempotency replay response** in WORK-02A; readable by the DB account. Before production, encrypt or redesign idempotent lease recovery, limit DB roles and add key rotation.
3. No rate limiting, HTTPS termination, WAF or network segmentation in code; bind to localhost only.
4. No request tracing/redacted structured audit for credential issuance and access denial.
5. No resource-level grants beyond project/action; no human approval/verification or DONE workflow.
6. No proper server-side cleanup of expired leases, graceful redispatch, cancellation or outbox projection.
7. No independent production penetration test, tenant-isolation analysis, backup/retention policy.
8. MCP stdio is only one transport, not a remotely authenticated Streamable HTTP MCP service; compatibility is not proven in any vendor-specific Jarvis/GPT/Claude host.
9. No real Mem0, embedding inference, external AI calls or semantic retrieval.
10. Tests exercise a synthetic lab and do not establish Jarvis production readiness.

## 7. Evidence / verification
The WORK-02B workflow starts PostgreSQL 16, applies both migrations and runs all unit/integration tests. Inspect its actual recorded outcome before claiming success. In-memory MCP tests validate SDK tool invocation; REST tests use FastAPI TestClient + real PostgreSQL; full vendor-client-to-MCP-to-network-REST tests remain future work.

WORK-02C should first resolve blockers around authorization and lease token handling, then connect self-hosted Mem0 and a read-only Jarvis pilot behind a feature flag.
