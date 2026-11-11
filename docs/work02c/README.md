# WORK-02C — scoped contextual retrieval + local Mem0 lab

**Status:** candidate implementation; not merged/deployed; not integrated with production Jarvis. This is a staged feature, not general availability.

## 1. Implemented
- \`ScopedContextReader\`: authenticated project grant checks from PostgreSQL, organization derived server-side, authoritative task state from PostgreSQL, semantic memory via private Mem0 HTTP client.
- \`GET /v1/projects/{project_id}/context?query=...\`: safe context with \`memory_status\`, source-of-truth marker, UNVERIFIED memory candidates. If Mem0 unavailable, returns authoritative task with empty memories + \`unavailable\` instead of inventing context.
- \`POST /v1/projects/{project_id}/memories/search\`: requires independent \`memory:read\` grant; Mem0 unconfigured/unavailable -> 503. Search results are minimized, never blindly forwarded.
- \`get_project_context\` MCP stdio read-only tool reuses the same REST gateway; no write/memory deletion/approval tools.
- \`mem0_local_service.py\`: *optional experimental Mem0 OSS library shim*, with explicit Ollama LLM + embedding providers, pgvector and a private X-API-Key. Only loopback (127.0.0.1) serving supported.
- \`client_readonly.py\`: standalone read-only compatibility probe, independent of Jarvis and OpenJarvis. **Not installed into Jarvis**.
- Real PostgreSQL/API tests plus deterministic fake memory/MCP protocol tests. The real Mem0 + Ollama smoke is a separate **manual acceptance gate**.

## 2. What Mem0 provides vs what RIGHTWARE provides
- Mem0: store/search semantically with local Ollama embeddings when configured and verified; original upstream code remains in \`vendor/mem0\`.
- RIGHTWARE: authenticated organization/project policy, domain tasks/handoffs/versions, source-of-truth distinction, trust labels, and integrated REST/MCP contracts.
- Mem0 memories remain **unverified contextual candidates**. A hallucinated "task done" note cannot mark task DONE or authorize actions.

## 3. Controlled real Mem0 lab — experimental, isolated
Preconditions: dedicated local PostgreSQL with pgvector extension installed, a **separate** memory database, local Ollama with an embedding model already pulled (e.g. \`all-minilm:latest\`) and an operator-approved local LLM (e.g. \`qwen3.5:2b\`); Python 3.12. **Do not run on Jarvis's production machine or database.**

Install from the pinned upstream source:
\`\`\`sh
git submodule update --init --recursive
python -m pip install -r requirements-work02.txt -r requirements-work02b.txt -r requirements-work02c.txt
python -m pip install -e vendor/mem0
\`\`\`

Configure the following *only in local environment/secret manager*, never git:
\`\`\`text
RW_SI_MEM0_API_KEY=<new-random-32+-character-secret>
RW_SI_MEM0_PG_DSN=postgresql://<dedicated-role>:<secret>@127.0.0.1:5432/<separate-pgvector-memory-db>
RW_SI_MEM0_HISTORY=<private-local-path>/mem0_history.db
RW_SI_OLLAMA_URL=http://127.0.0.1:11434
RW_SI_OLLAMA_EMBED_MODEL=all-minilm:latest
RW_SI_OLLAMA_EMBED_DIMS=384
RW_SI_OLLAMA_LLM_MODEL=qwen3.5:2b
MEM0_TELEMETRY=false
\`\`\`

Check that the requested embedding model already exists in Ollama. The code refuses startup if it is missing, to avoid silent auto-pull/network access. The pinned Mem0 library may otherwise auto-pull models on its own. Verify the actual model dimensions; changing models requires matching pgvector collection dimensions.

Start the isolated shim (loopback only):
\`\`\`sh
python -m rightware_si.mem0_local_service
\`\`\`

Separately start the RIGHTWARE FastAPI with \`RW_SI_DATABASE_URL\` (own test DB) and \`RW_SI_MEM0_URL=http://127.0.0.1:8891\` plus \`RW_SI_MEM0_API_KEY\`. Do **not** expose ports to the internet. Issue separate principal credentials and grants for \`context:read\`, \`memory:read\`, \`task:read\` using WORK-02B's offline provisioner.

Execute only synthetic-data smoke after the service is healthy:
\`\`\`sh
python scripts/work02c_real_mem0_smoke.py
\`\`\`

**As written, this command is not automatically run by GitHub Actions**. A passing FAKE-backend CI run is not proof of actual Mem0/pgvector/Ollama operation, embedding quality, model costs, security or Jarvis compatibility. Preserve real smoke logs, commit pins, model digests and environment manifests when executed.

## 4. Secure behavior and constraints
- A project ID string never grants access; \`context:read\`/\`memory:read\` is checked against the authenticated actor.
- Organization is resolved from \`si_projects\` rather than caller-supplied organization/user ID.
- Even a returned Mem0 \`approved:true\` metadata field is ignored; every semantic candidate is labeled UNVERIFIED.
- A missing Mem0 service does not corrupt PostgreSQL task state. Search fails 503; task + context reads remain available with empty memory and explicit status.
- The local Mem0 shim uses a single server secret. It **must remain internal** behind the RIGHTWARE gateway; it is not secure multi-tenant authentication by itself.
- Never blindly promote prompt-injected memory text into tool or system instructions.

## 5. Jarvis production integration plan
- Jarvis is already in production according to project context. Do not modify its runtime or pinned upstream until a separate staging and rollback test is approved.
- First bridge is opt-in, read-only, per-project scoped with a dedicated token, short timeout and fail-to-local behavior.
- No automatic transfer of Issa's private memories, no compulsory remote service and no dependency on paid cloud APIs.
- The standalone \`client_readonly.py\` proves only the HTTP contract in isolation; it does **not** mean Jarvis is deployed with Shared Intelligence.

## 6. Unresolved blockers and next gate
1. Run the **actual** Mem0+Ollama+pgvector smoke in a dedicated controlled environment. Resolve any version/embedding/backend incompatibilities with recorded evidence.
2. Enforce cross-project filtering independently at the RIGHTWARE gateway and memory backend. Add memory record lifecycle, deletion and revocation.
3. Build a transactional outbox and explicit, consented memory writes. The current feature is **read-only** from the external agent's perspective.
4. Complete workload identities, token protection, rate limits and HTTPS before production.
5. Remove or protect WORK-02A idempotency storage of recoverable lease secrets before exposing writes.
6. Run true end-to-end MCP-host → stdio bridge → HTTP REST → PostgreSQL/Mem0 acceptance, not just SDK in-memory dispatch.
7. Execute a staged Jarvis pilot, with independent approval and rollback plan, only after all gates.
