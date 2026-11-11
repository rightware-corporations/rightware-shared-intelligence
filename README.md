# RIGHTWARE Shared Intelligence

Independent RIGHTWARE infrastructure for authorized AI agents and applications to share **contextual memory**, **task continuity** and **evidence-aware handoffs**.

**Status:** experimental Python backend validated with synthetic end-to-end data. **Not a production service.** Jarvis and PULSE production remain unchanged. No working frontend UI exists.

## Start here
- [Current HANDOFF](docs/HANDOFF.md) — last state, evidence, blockers and next action.
- [MASTER HANDOFF](docs/HANDOFF_MASTER.md) — cumulative append-only engineering history.
- [Handoff policy](docs/HANDOFF_POLICY.md) — update BOTH in every technical commit.
- [Architecture — implemented vs proposed](docs/ARCHITECTURE.md).
- [WORK-03A restructuring manifest](docs/work03a/RESTRUCTURE_MANIFEST.md).
- [Mem0 upstream provenance](docs/UPSTREAM_PROVENANCE.md).

## Project layout

```text
backend/
  rightware_si/             # FastAPI, PostgreSQL core, contextual memory, MCP
  requirements/             # core.txt, api.txt, memory.txt
database/
  migrations/               # 0001–0003 authoritative PostgreSQL schema
frontend/
  README.md                 # FUTURE: admin panel, not implemented
infrastructure/
  README.md                 # deployment boundaries; no production stack
tests/                      # unit, PostgreSQL, REST, MCP and layout tests
scripts/                    # CI governance and real synthetic E2E
docs/                       # current + historical handoffs, architecture and evidence
vendor/mem0/                # pinned Apache-2.0 Git submodule
.github/workflows/ci.yml    # one active CI workflow on develop
pyproject.toml              # editable package at backend/rightware_si
```

## Git policy
- **develop:** all future engineering/checkpoints. Every technical commit updates `docs/HANDOFF_MASTER.md` and `docs/HANDOFF.md`.
- **main:** explicitly approved releases only. As of this checkpoint, `main` contains only initial README; it is not an installed/shared-intelligence release.
- Historic WORK-00 through WORK-02D branches and six Draft PRs are preserved temporarily for provenance; no new temporary work branches.

## Lab validation (not production instructions)

Test dependencies and editable package:

```sh
git submodule update --init --recursive
python -m pip install -r backend/requirements/core.txt -r backend/requirements/api.txt -r backend/requirements/memory.txt
python -m pip install -e vendor/mem0 -e .
```

The integration test harness requires **disposable** PostgreSQL database `rw_test`, configured through `RW_TEST_DATABASE_URL`. The real Mem0 smoke requires an additional isolated pgvector database, a local Ollama service and synthetic data. Do not point these scripts at customer, Jarvis, PULSE or production databases.

See [infrastructure/README.md](infrastructure/README.md) and the [CI workflow](.github/workflows/ci.yml) for the tested synthetic-lab configuration. No default hosted paid inference API is required for that embedding smoke; real self-hosting, security and capacity planning are still pending.

## Functional boundaries
- PostgreSQL task and authorization state is **authoritative**.
- Mem0 is a **replaceable semantic-memory component** and its content is **UNVERIFIED**.
- MCP stdio bridge shares the authenticated REST gateway's project-scoped policies.
- Model text never directly approves work or grants permissions.

Maintainer: RIGHTWARE. Mem0 is an independent upstream project and retains its own license and source history.
