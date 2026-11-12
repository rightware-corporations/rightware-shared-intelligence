# RIGHTWARE Shared Intelligence

Independent RIGHTWARE infrastructure for authorized AI agents and applications to share **contextual memory**, **task continuity** and **evidence-aware handoffs**.

**Status:** experimental Python backend validated in synthetic lab. R1A adds source-linked, unverified observations; R1B checkpoint/resume read-only and R1C checkpoint-bound handoff/fenced holder-only rekey in synthetic lab; full verification remains unimplemented. **Not a production service.** Jarvis and PULSE unchanged; no frontend UI.

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
  migrations/               # 0001–0006 authoritative PostgreSQL schema
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

## WORK-03B R1A
- Six experimental continuity REST operations: R1A start AgentRun, register SourceRecord, append ASSERTED Observation, list observations; R1B record immutable checkpoint and read current scoped resume.
- See [R1A implementation scope](docs/work03b/R1A_IMPLEMENTATION.md), including migration 0004 and known limitations. No memory ingestion/outbox, independent verifier, approved DONE or production deployment. R1C exact checkpoint binding applies only when the task has checkpoints; zero-checkpoint legacy handoffs remain clearly UNBOUND.

## WORK-03B R1C
- Checkpointed task handoffs require explicit latest owned checkpoint ID/sequence; same-task immutable FK and PostgreSQL trigger prevent rebinding.
- Persistent lease fence generation never regresses across acceptance, removal or holder-only rekey. Authenticated current holder can inspect generation and obtain a new one-time token with a dedicated `task:recover` grant; raw lease secrets are never stored or replayed.
- See [R1C implementation](docs/work03b/R1C_IMPLEMENTATION.md). This is a lab capability only; external effects, multi-tenant resource ACL and Jarvis production are out of scope.

## Security review and future R2 (draft, not implementation)
- [R1C security decision register](docs/work03b/R1C_SECURITY_POLICY_GATE_R0.md): legacy unbound handoffs, administrative reassignment and external-effect reconciliation. **Recommendations only; operator ratification pending.**
- [R2 trust R0 contract](docs/work03b/R2_TRUST_CONTRACT_R0.md) and [machine-readable draft](docs/work03b/R2_TRUST_CONTRACT_R0.json): evidence verification, independent review and the 16 *unexecuted* synthetic oracles. Six new tests validate only documentation consistency; **no verifier, signed artifact validation or DONE approval exists.**

## R2 R1A — Isolated GitHub evidence-verifier experiment
- [R2 R1A adapter and limitations](docs/work03b/R2_R1A_GITHUB_VERIFIER_LAB.md): a bounded, read-only GitHub workflow-run checker validating exact repository/workflow/run/attempt/SHA/status. This is **not a production API, not a signed attestation and not task approval**.
- `backend/rightware_si/evidence_github.py` and `tests/test_r2_r1a_github_lab.py` test provider response logic with a fake transport, including EV-01..EV-07. The separate `scripts/work03b_r2_r1a_github_live.py` uses a real previously completed GitHub Actions run for limited EV-01..EV-04 provider checks.
- No verifier persistence, evidence API route, reviewer, DONE, or new dependency has been added. Original SI-RD-03C 16-oracle source fixture stays unmodified; EV-08..EV-16 remain unexecuted.

## R2 R1B — Internal append-only PostgreSQL verification lab

- [R2 R1B Evidence Ledger](docs/work03b/R2_R1B_VERIFICATION_LEDGER.md): pinned policy, independent SERVICE identity, project grants, PostgreSQL immutable VerificationAttempt records and re-authorization after real GitHub API response. Mocked responses are explicitly marked SIMULATED_TRANSPORT.
- No public verification API/MCP, no reviewer, no DONE, no policy ratification and no production deployment. The original source fixture SI-RD-03C remains unchanged. R2-R0 zero operational R2 routes remains correct.

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
