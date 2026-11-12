# RIGHTWARE Shared Intelligence — Architecture baseline (WORK-03A)

**Status:** actual repository-backed architecture after layout consolidation. **Experimental code only**; no production deployment or Jarvis/PULSE integration. Historical WORK-00 proposal was replaced here because it did not describe the implemented WORK-02D system; original history remains in Git and `docs/work01/`.

## One repository, one Python application, private memory service

```text
Proposed future Admin UI (NOT built)        External clients (Jarvis / PULSE / MCP SDK)
             |                                         |
             +-----------------------------------------+
                         AUTHENTICATED REST API
                         backend/rightware_si/http_api.py
                                     |
                      backend/rightware_si/api_auth.py
                                     |
         +---------------------------+--------------------------+
         |                                                      |
    WorkCore (PostgreSQL)                             ScopedContextReader
    backend/rightware_si/core/postgres.py               backend/rightware_si/context_service.py
         |                                                      |
    PostgreSQL 16 operational store                     Memory adapter / internal Mem0
    database/migrations/0001–0003                         |
                                                         Mem0 OSS + Ollama local embeddings
                                                         PostgreSQL 17 / pgvector (LAB)
```

MCP uses `backend/rightware_si/mcp_bridge.py` as a **read-only stdio bridge**, and calls the **same REST API** with a project-scoped bearer token; it cannot skip REST authentication.

### Backend — implemented
- `backend/rightware_si/http_api.py`: FastAPI routes for tasks, events, handoffs, context and semantic search; no public write-memory endpoint.
- `api_auth.py`, `token_admin.py`: bearer token verifier and offline lab token issuance/revocation; no OAuth/OIDC.
- `core/postgres.py`: task lifecycle, versions, exclusive lease transfer, append-only task events, scoped grants and idempotency.
- `context_service.py`: derives organization/project scope from PostgreSQL, reads canonical tasks and obtains Mem0 candidates; rejects cross-project metadata, labels memory UNVERIFIED; degrades when Mem0 is down.
- `memory.py`: pinned Mem0 HTTP adapter, scope convention, no identity authority.
- `mem0_local_service.py`: **isolated lab** wrapper around pinned OSS Mem0 with Ollama embedding and pgvector; private loopback and test key, not exposed to the internet.
- `mcp_bridge.py`: stdio, read-only get_task/get_task_events/get_project_context.
- `client_readonly.py`: standalone probe only, **not** integrated into Jarvis.

### Database — implemented
- `database/migrations/0001_work02_core.sql`: organizations, projects, principals, permissions, tasks, leases, handoffs, evidence references, task events, idempotency.
- `0002_work02b_api_credentials.sql`: hashed bearer keys / expiration / revocation.
- `0003_work02d_scrub_lease_replays.sql`: scrubs historical one-time lease secrets from saved idempotency JSON.
- The lab uses PostgreSQL 16 for authoritative task state, a **separate** PostgreSQL 17+pgvector instance for Mem0 embeddings. Production database topology **is not yet decided**.
- No migration framework such as Flyway/Alembic is installed; SQL files are explicitly applied in the CI lab.

### Memory — implemented laboratory path
- Upstream Mem0 is a Git submodule under `vendor/mem0/`, pinned to `f1791daa86d469249c9b002f62644d58a1eb96a0` (Apache-2.0).
- Ollama `0.40.15` and `all-minilm:latest` embeddings validated in CI. Tags are not immutable model hashes.
- No text-generation success claimed: real smoke uses `infer=false`, no Qwen generation.
- Retrieval filtering is not a replacement for RIGHTWARE authorization.

### Frontend — future
`frontend/README.md` is only a placeholder explaining a possible React/TypeScript administrative console. There are no frontend dependencies, build commands, pages, screens or working application. Frontend is not a prerequisite for agent-to-agent memory.

### Infrastructure — planned, not deployed
`infrastructure/README.md` captures isolation, credentials, runtime dependencies and proposed deployment boundary. There is **no tested Docker Compose or production deploy** in WORK-03A.

### Tests and CI
- Root `tests/`: synthetic deterministic tests plus real disposable PostgreSQL auth/transaction tests, layout guard and MCP in-memory contract.
- `scripts/work02d_real_mcp_e2e.py`: real external MCP subprocess -> REST auth -> PostgreSQL project scope -> Mem0 OSS -> Ollama embeddings -> pgvector with synthetic Alpha/Beta.
- `.github/workflows/ci.yml`: single current workflow for develop plus release PR to main. Enforces BOTH handoff files in each new commit, installs `backend/` editable distribution, migrates disposable PostgreSQL, runs unit/integration suite and real E2E.
- Historial CI from WORK-00 to WORK-02D remains visible in Git history, PRs and GitHub Actions.

## Architecture decisions vs remaining proposals

**Official engineering workflow decision:** only `develop` and `main` as continuing work branches. Per-output MASTER + CURRENT Handoff documentation. No direct Jarvis production modifications.

**Recommended technical direction (not production approved):** keep simple Python modular monolith + REST/MCP and replaceable Mem0 library, postpone UI until needed.

**Production blockers:** OIDC/workload identity, per-resource authorization, rate limits, TLS, secrets management, history erasure, outbox/consent-aware memory ingestion, secure lease recovery, backups/restore, independent security assessment, real Jarvis staging.

See `docs/work01/` for the original domain model and acceptance hypotheses; implementation coverage is narrower than that proposal.


## Evolução funcional proposta (WORK-03B R0B — NÃO implementada)

A fonte da verdade da arquitectura **implementada** permanece nas secções anteriores. O produto de continuidade integral tem um desenho de próxima geração em [`docs/product/work03b/README.md`](product/work03b/README.md), incluindo princípio de funcionamento, read/write paths, entrega de `ContinuationPackage`, bounded contexts, fault/retry/security e pesquisa REUSE/BUILD.

**Contrato canónico machine-readable de MVP:** [`docs/work03b/UC_CORE_01_CONTRACT.json`](work03b/UC_CORE_01_CONTRACT.json) e [`docs/work03b/UC_CORE_01_ACCEPTANCE.md`](work03b/UC_CORE_01_ACCEPTANCE.md). Existem 10 rotas protegidas no laboratório e 7 rotas futuras DRAFT. Os endpoints adicionais do blueprint são ideias do horizonte, não APIs existentes nem aprovadas. Sem novos módulos, migrations, frontend ou produção neste R0B.

Princípio de autoridade: PostgreSQL para estado/eventos/checkpoints/decisões verificados; Mem0 apenas projecção recuperável e não confiável; REST/MCP reutilizam a mesma autorização e o `resume` requer revalidação de ACL/sources. Não confundir os 60 testes históricos com aceitação de UC-CORE-01 completa.


## WORK-03B R1A — Implemented experimental continuity primitives
- The new backend/rightware_si/continuity.py exposes lease-bound AgentRun, SourceRecord and ASSERTED Observation; source references are not verified, and task.version remains unchanged by observation writes.
- The 0004 migration adds immutable-by-app records with task-scoped composite FKs, plus a separate continuity event stream that does not conflict with task lifecycle version events.
- FastAPI has **14 implemented protected routes**; the canonical R0 contract now lists **6 future routes**. All R1A additions require existing server bearer authorization, correct task lease and project grants; observation reads require both task:read and context:read.
- Full checkpoint, resume across new process, review/DONE and source-level privacy remain **unimplemented**. See docs/work03b/R1A_IMPLEMENTATION.md. This is not production-ready.


## WORK-03B R1B — Implemented checkpoint/resume (experimental)

- PostgreSQL migration `0005_work03b_r1b_checkpoints.sql`: immutable `si_task_checkpoints` and `si_checkpoint_observations` (same-task FK), checkpoint_seq CAS, trigger rejects UPDATE/DELETE of checkpoint rows and associations. No historical task status/event schema replacement.
- `backend/rightware_si/continuity.py`: `record_checkpoint` requires active lease, current task version, owned AgentRun, `checkpoint:write` plus `task:execute` and `context:read`; validates observation references and records ASSERTED checkpoint without incrementing task.version.
- `resume_task` returns a **read-only fresh canonical PostgreSQL snapshot** under `REPEATABLE READ READ ONLY`, reauthorizes `task:read` and `context:read`, includes latest checkpoint/observations and task/handoff status, with `memory_status=NOT_QUERIED`. Does not mint a lease or promote assertions to verified.
- REST exposes POST task checkpoints and GET task resume; MCP adds a **read-only** `resume_task` tool delegating to the same REST authorization layer.
- Canonical contract: **16 implemented routes, 4 future**, 14-step UC-CORE-01 still **PENDING_FULL_E2E**. Proof is in `docs/work03b/R1B_IMPLEMENTATION.md` and CI evidence after execution.

**Limitation:** existing handoff is NOT tied to a specific checkpoint; target agent sees latest authorized checkpoint, and its `task_version_recorded` can differ from current task version after the handoff. R1C will bind handoff+checkpoint and address lost lease secrets. Production resource-level privacy/consent, outbox, external verification and DONE review remain missing.


## WORK-03B R1C — Checkpoint-bound Handoff and monotonic lease fencing (experimental)

- `database/migrations/0006_work03b_r1c_handoff_fencing.sql`: `si_handoffs.checkpoint_id/seq/task_version` with project/task FK and trigger that prevents metadata forgery/rebinding; `si_lease_fences` persists monotonic generation even when an active lease row is deleted. Existing legacy unbound handoffs remain readable.
- `WorkCore.offer_handoff` now requires explicit latest checkpoint ID+sequence whenever the task has any checkpoint, and checks recorded_by/expected task version/current lease/target read grants before changing task or releasing A's lease. Tasks with **no checkpoint** retain a clearly labelled `LEGACY_UNBOUND` compatibility path; it is not a proof of continuity.
- `WorkCore.accept_handoff` validates the bound checkpoint and target permissions again. New lease generation is monotonic across handoff and holder-only rekey. `get_lease_state` never returns a token; `recover_lease` rotates one-time secrets only for **the current holder** with `task:recover`, matching expected task version and lease generation. Replay of the secret-bearing result returns HTTP 409.
- `ContinuityCore.resume_task` includes the exact handoff checkpoint identity and a retained historical checkpoint view if the latest checkpoint has subsequently advanced; all remain ASSERTED, not independently checked. Resume is read-only, rechecks grants and has no Mem0 dependency.
- Two additional REST endpoints are implemented for lease-status/recovery, making **18 implemented routes and 3 proposed R2 routes** in the canonical contract. No MCP mutation tools were added; a restart after lost acceptance can be recovered by a holder-specific API call, not autonomously by another agent.
- R1C synthetic CI and security negative tests are documented in `docs/work03b/R1C_IMPLEMENTATION.md` and associated evidence once the run is observed.

**Remaining:** No administrator-driven take-over when owner gone, no token recovery without `task:recover` grant, no fencing enforced against external tools (they need protocol support), no source-level consent/retention, no outbox, independent evidence verification, reviewer DONE, production deployment or Jarvis modifications. CI success only validates the tested synthetic paths.


## Next security gates and R2 trust architecture (DESIGN ONLY; no runtime implementation)

- R1C lab success is established by [CI 43196692278](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43196692278) (94/94 plus A/B recovery and Mem0 E2E). Release gates for `LEGACY_UNBOUND`, absent-holder reassignment, rate-limited workload identity, external effects and DB isolation are **not approved**; see [R1C_SECURITY_POLICY_GATE_R0.md](work03b/R1C_SECURITY_POLICY_GATE_R0.md).
- Proposed R2 independent validation is a **three-stage authority boundary**: agent `ASSERTED` observations remain immutable; a separate append-only verification attempt records the particular checked provider/criterion; a distinct `task:review` principal accepts or rejects using current grants, policy version and task CAS. No automatic `DONE` from CI/attestation/LLM. See [R2_TRUST_CONTRACT_R0.md](work03b/R2_TRUST_CONTRACT_R0.md) and [R2_TRUST_CONTRACT_R0.json](work03b/R2_TRUST_CONTRACT_R0.json).
- Existing PostgreSQL task/grants/events, `si_evidence_refs`, R1A SourceRecords/Observations, and R1B/C checkpoint/fencing are reused by **future** R2. No R2 tables, routes, provider calls, dependencies, Sigstore/in-toto verification, OPA, OpenTelemetry, or production integration was added by the R0 contract.
- The 16 SI-RD-03C cases are **unexecuted proposed oracles**; the new contract tests assert only mapping/consistency. Actual independent verification/review, enterprise privacy and `M01–M18` full acceptance remain pending.


## WORK-03B R2 R1A — Experimental GitHub provider-read boundary
- The bounded `evidence_github.py` adapter (existing httpx dependency) compares pre-pinned GitHub stable repository ID/full owner/name, workflow ID, run ID/attempt, full SHA, event and completed success. It never follows redirects, arbitrary provided URLs or environment proxies. Fail-closed inconclusive on unavailable provider or malformed/absent data. `CHECKED_PASS` is **not** task approval.
- 15 synthetic provider-response tests exercise EV-01..EV-07 adapter code and negative/security cases. Separate real GitHub CI smoke checks EV-01..EV-04 against one previously completed public Actions run; these prove **only those exact provider fields** when live CI succeeds.
- This is **not yet integrated** with PostgreSQL `si_evidence_refs`, independent verifier service identity, resource-level policy/grants, new REST/MCP route, or `ReviewDecision`. The `R2_TRUST_CONTRACT_R0.json` still shows `implemented_r2_routes=0` for operational routes; 18 experimental REST routes and 3 future routes stay unchanged.
- Four SEC-R1C policy decisions are still **unratified**. The design/implementation gate for writable verified results and DONE remains blocked. No source fixture or historical handoff is overwritten.
