# Architecture v0.1 — proposal and lab implementation

**State:** WORK-00 experimental code. The only executable RIGHTWARE component is a Python Mem0 HTTP client and its deterministic fake-backed tests. No MCP server, database migration, production authentication, orchestrator or integration with Jarvis/PULSE is implemented.

## Boundaries

- vendor/mem0: unmodified upstream gitlink, pinned to a reviewed commit. This is Mem0's code; license and development history remain upstream.
- rightware_si: RIGHTWARE-authored, dependency-free, project-scoped Python adapter.
- The adapter calls Mem0 self-hosted REST POST /memories (infer=false) and POST /search using the supplied service account key.
- Mem0 self-hosted provides its own persistence/auth. The current upstream server uses PostgreSQL/pgvector, but defaults to hosted LLM and embedding APIs unless configured otherwise. The adapter does not make this free or offline.
- project scope rw:<organization>:<project> is a naming convention only. It is NOT secure tenant authorization.

## Trust and state

A model-written handoff is a claim, not verified completion. Upstream Mem0 stores/searches notes; it is NOT authoritative for task state, approvals, evidence validation, or audit trails.

Future event system must be append-only and transactional in a RIGHTWARE-controlled PostgreSQL schema. Only a trusted verifier may mark an action verified. Do not infer approval from a memory record.

## Integration target (not implemented)

App / Claude / n8n / Jarvis
→ authenticated RIGHTWARE REST or MCP gateway (not yet built)
→ access policy / event log / memory adapter
→ local/remote Mem0 self-hosted service
→ its configured Postgres and LLM/embedder providers

No direct production exposure of the Mem0 REST API or this helper client.

## Quick test

python -m unittest discover -s tests -v

Test descriptions explicitly say FAKE. They test serialization, isolation filter, input validation, and fail-closed handling of cross-project results. They do not test Mem0 itself, PostgreSQL, Ollama, MCP, or external apps.
