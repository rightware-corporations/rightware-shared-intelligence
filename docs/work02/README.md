# WORK-02A — PostgreSQL transactional core (experimental)

**Status:** implementation candidate; security and deployment NOT approved. Separate from Jarvis and PULSE. The WORK-01 domain docs remain proposed architecture.

## What was implemented
- Schema for organizations, projects, principals, explicit project grants, tasks, one exclusive lease per task, handoff offers, evidence references, versioned events and idempotency.
- Internal Python \`WorkCore\` using psycopg. Every mutation checks an authorized principal *as supplied by the trusted caller*, reserves a scoped idempotency key, performs versioned row-locked state changes, and appends one task event atomically.
- Transitions: \`DRAFT -> READY -> IN_PROGRESS -> BLOCKED -> IN_PROGRESS -> IN_REVIEW\`.
- Handoff requires an active lease; acceptance targets a named principal and issues a new exclusive lease. Source lease becomes invalid.
- Submitted GitHub evidence references remain \`REFERENCED\`; no URL check equates to verification.
- Real PostgreSQL integration tests on a disposable database through GitHub Actions.

## What is deliberately NOT present
- No public REST API, auth gateway, identity verification or MCP endpoint.
- No human-review / DONE transition; cannot call unverified results complete.
- No Mem0 integration, semantic memory, local embeddings, n8n or Jarvis runtime changes.
- No enterprise deployment, secret distribution, service identity onboarding or production-grade PII retention.
- No lease renewal, expiry sweep, cancellation or outbox worker; WORK-02B+ must address these before relying on sustained tasks.
- The included PostgreSQL roles/grants represent **project authorization checks**, not real principal authentication. Callers MUST authenticate and map identities outside \`WorkCore\`.
- No production claim from green CI; this is a small isolated integration proof.

## Test contract
GitHub Actions starts PostgreSQL 16 with DB \`rw_test\`, applies \`db/migrations/0001_work02_core.sql\` and executes \`python -m unittest discover -s tests -v\`.
The integration test file refuses to run unless \`RW_TEST_DATABASE_URL\` ends in \`/rw_test\`, then truncates only this dedicated disposable database between tests. Never point it at existing Mem0, Jarvis, PULSE or user databases.

## Read in order
1. \`docs/work01/DOMAIN_MODEL.md\`
2. \`docs/work01/TASK_LIFECYCLE.md\`
3. \`docs/work01/SECURITY_MODEL.md\`
4. \`docs/work01/MVP_ACCEPTANCE.md\`
5. \`db/migrations/0001_work02_core.sql\`
6. \`rightware_si/core/postgres.py\`

## Next work — WORK-02B
Build a proper authenticated FastAPI boundary and shared REST/MCP service policy over these transaction functions; introduce evidence verification and approval as separate authorities. The Jarvis production integration should be **opt-in, read-only first**, with independent rollout and a rollback switch.

Do not merge or deploy this PR as a Jarvis dependency.
