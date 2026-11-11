# WORK-02D — Verified Evidence Ledger

**Scope:** isolated laboratory, synthetic data; not a production approval.

## Final tested code checkpoint
- Repo: https://github.com/rightware-corporations/rightware-shared-intelligence
- Branch: feat/work02d-e2e-security-hardening.
- Tested code commit: `8d7f5234d375d29df774388529094708a4e0cb3c`.
- Stacked Draft PR #6: https://github.com/rightware-corporations/rightware-shared-intelligence/pull/6.
- GitHub Actions: https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43108517846 — **SUCCESS**.
- Unit/integration suite: **48 tests, all PASS**. Real PostgreSQL 16, including 0003 migration scrub of legacy secret and explicit 409 on lease credential replay.
- Real end-to-end: `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS` — **PASS**.

## Full E2E verified topology
An independent MCP v2 Client launched the stdio MCP bridge as a separate subprocess. The bridge called the real RIGHTWARE FastAPI over loopback HTTP with an ephemeral bearer token. The API authenticated principal and project grants in PostgreSQL16, read the authoritative task, and fetched an actual semantic memory via private Mem0 HTTP adapter. Mem0 OSS was backed by PostgreSQL17+pgvector and generated search embeddings with Ollama 0.40.15 `all-minilm:latest`.

## Assertions that passed
- Alpha authenticated client retrieved synthetic Alpha memory and UNVERIFIED label.
- It obtained the DRAFT task status from authoritative PostgreSQL.
- Request for Project Beta denied; no Beta memory was returned.
- Revocation of the API token caused subsequent MCP calls to be denied.
- A separate intruder token without project grants was denied.
- Model extraction/generation was not executed: `infer=false` uses local embedding, not Qwen generation.
- No paid external inference APIs, production secrets, personal memory or Jarvis deployment.

## Historical failures preserved
- `43107788463` — FAILED: test expected disabled Mem0 but inherited CI Mem0 URL. Corrected the test to clear its optional provider configuration explicitly.
- `43108113909` — 48/48 suite PASS; E2E FAILED with duplicate synthetic `si_projects` records from previous test suite. The E2E now resets only the verified local `/rw_test` disposable database before fixtures.
- `43108517846` — 48/48 suite and actual E2E PASS.

## Security change
- WORK-02A originally saved raw `lease_token` in `si_idempotency.response`; WORK-02D now removes it before storing future idempotency results.
- `db/migrations/0003_work02d_scrub_lease_replays.sql` deletes historical `lease_token` keys in stored JSON. Regression tests assert both future redaction and legacy scrub.
- Replaying a token-issuing claim or handoff now produces explicit Conflict (HTTP 409) rather than exposing a recoverable lease secret. Lost response recovery/reassignment must be implemented before production.

## Remaining blockers
1. Secure lease retry/recovery, lease expiry maintenance, operator intervention flow.
2. Workload/OIDC identities, rate limits, TLS for remote access, least-privilege DB roles and independent security testing.
3. Durable outbox, memory provenance/consent, erasure/retention, audit and data classification.
4. Immutable embedding model digest and resource/cost/latency benchmarks.
5. Vendor-specific MCP host and Jarvis staging pilot, with read-only feature flag and rollback.

No changes to production Jarvis or PULSE, no merges. PR remains Draft.
