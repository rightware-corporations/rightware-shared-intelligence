# RIGHTWARE Shared Intelligence

Independent RIGHTWARE-owned platform for scoped contextual memory, verified operational continuity, and handoffs between authorized AI agents/applications.

**Status (2026-11-12): experimental, NOT deployed or production-ready.** The tested WORK-02D laboratory includes PostgreSQL tasks/handoffs, FastAPI authentication, read-only MCP, real Mem0 + local Ollama embeddings and a passing synthetic E2E. No production Jarvis/PULSE integration and no frontend application yet.

## Repository governance — operator decisions
- **develop:** the ONLY active construction/integration branch; all technical outputs require handoff logging in the same commit.
- **main:** stable approved release branch (currently only initial README; do not deploy as a product). No merge without explicit release approval.
- Historic six experimental branches and their Draft PRs are temporarily preserved as evidence; no new feature branches. Cleanup is a separate audited migration.
- [Current handoff](docs/HANDOFF.md) — resume here first.
- [MASTER HANDOFF](docs/HANDOFF_MASTER.md) — append-only technical history.
- [Handoff policy](docs/HANDOFF_POLICY.md) — mandatory per-output checkpoint procedure.
- [Historical recovery](docs/handoffs/BASELINE_WORK00_WORK02D.md) — PR/commit/CI evidence from WORK-00 to WORK-02D.

## Current source layout (pre-consolidation)
- `rightware_si/` — Python backend (REST, auth, tasks/leases, MCP, memory adapters).
- `db/migrations/` — authoritative PostgreSQL schema and security migrations.
- `vendor/mem0/` — Apache-2.0 original Mem0 pinned as Git submodule; attribution in THIRD_PARTY_NOTICES.md.
- `tests/`, `scripts/` and `.github/workflows/` — reproducible tests and real E2E lab.
- `docs/` — architecture, security, API contracts, evidence, current and historical handoffs.

**Next proposed milestone:** WORK-03A architecture/folder consolidation without functional rewrite. Proposed future layout: backend/, database/, infrastructure/, frontend/ (later), tests/, docs/, vendor/. Re-run all tests after moves.

## Safety
Never write secrets, unredacted CI tokens, private conversations or personal project memories to this PUBLIC repository. No production data or Jarvis deployment in the current proof. Model-generated contextual text is UNVERIFIED; PostgreSQL is source of truth for task state.

Read docs/HANDOFF.md, then docs/HANDOFF_MASTER.md and the latest CI run before continuing.
