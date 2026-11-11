# WORK-02D — Experimental security and E2E acceptance

**Status:** engineering change on `feat/work02d-e2e-security-hardening`. No merge, no Jarvis production changes.

## Scope

1. Remove recoverable bearer-capable task lease tokens from `si_idempotency.response`. The original lease hash remains in `si_task_leases`; new responses reveal the secret once to the authenticated caller.
2. Scrub any previously created idempotency JSON objects with a `lease_token` key using migration `0003_work02d_scrub_lease_replays.sql`.
3. Reject a repeated `claim_task` / `accept_handoff` idempotency request with a clear 409, rather than silently returning a response that cannot include the one-time credential. This is a **deliberate behavior change**; if a client loses its initial response, a trusted operator must recover or expire/reassign the lease. Lease recovery is not implemented.
4. Run full service interoperability: an independent MCP stdio client calls MCP bridge → authenticated REST FastAPI → server-side project grants in PostgreSQL 16 → actual Mem0 OSS → local Ollama embedding → PostgreSQL 17/pgvector. Use synthetic Alpha/Beta records and independent credentials only.
5. Test denied cross-project reads and token revocation at the complete MCP interface boundary.

## Preconditions

- Never deploy this prototype to Jarvis or connect personal/user memory.
- Never start with a production PostgreSQL DSN. Tests use disposable databases named `rw_test` and `mem0_lab`.
- API and Mem0 bind 127.0.0.1 on the ephemeral runner. Key is generated and masked for the job.
- Docker model download is limited to a free embedding model; no paid inference APIs.
- Source-of-truth is PostgreSQL; all contextual memory remains UNVERIFIED.

## Remaining blockers

- Short-lived workload credentials/OIDC, request rates, least-privilege DB roles, TLS for remote use, memory deletion policy.
- Correct restoration for lost lease-token replies (a new `resume`/reassign policy) and persistent distributed outbox.
- Threat-model hostile/poisoned memory and multi-tenant data leakage across all future integration paths.
- External MCP host compatibility on a real user environment and Jarvis staging tests with opt-in flags.
- No current approval for merging any stacked Draft PR.

## Acceptance evidence

See `docs/work02d/EVIDENCE.md`. Record actual test counts and CI run IDs there; do not claim PASS before reading the workflow result.
