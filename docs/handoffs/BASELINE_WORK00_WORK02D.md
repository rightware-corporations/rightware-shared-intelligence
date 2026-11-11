# Historical Recovery Dossier — WORK-00 through WORK-02D

**Created:** 2026-11-12. Reconstructed from existing GitHub commit history, PRs and completed Actions runs. Does not claim that past work was performed again today.

## Source repository and Git topology
- Repository: https://github.com/rightware-corporations/rightware-shared-intelligence (public).
- Original main: 87c3351055aaf58d37f233dbc96eaa8f0b749c5c. No shared-intelligence production build in main.
- Development base taken from validated WORK-02D SHA 6345fb4f6238ecea2d376e82b659238d4684f30f, now on develop.
- Historic branches are cumulatively stacked in commit ancestry: feat/work00 -> docs/work01 -> feat/work02a -> feat/work02b -> feat/work02c -> feat/work02d.
- Six Draft PRs remain open; no merges were performed. Each has the previous branch as base, so preserve references before closing or deleting branches.

## GitHub evidence map
| Phase | Draft PR | Full head SHA | Evidence |
|---|---|---|---|
| WORK-00 | [#1](https://github.com/rightware-corporations/rightware-shared-intelligence/pull/1) | ba59cecc67c3fb1c5340b5b9471f1b1d25d110ee | 8 fake tests; real upstream submodule clone CI [42803825893](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/42803825893) |
| WORK-01 | [#2](https://github.com/rightware-corporations/rightware-shared-intelligence/pull/2) | 3f54278d1f5c8d04138696813a847e9d7d91c682 | documentation-only review, nine work01 files |
| WORK-02A | [#3](https://github.com/rightware-corporations/rightware-shared-intelligence/pull/3) | 9310245559743ab9f51bf88fba91b22d64b36db9 | [43055391551](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43055391551), 16/16 tests including real PostgreSQL |
| WORK-02B | [#4](https://github.com/rightware-corporations/rightware-shared-intelligence/pull/4) | 4f721f4d10fccccd2f2fef495223e91e79a4ef49 | [43067218210](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43067218210), 29/29 tests |
| WORK-02C | [#5](https://github.com/rightware-corporations/rightware-shared-intelligence/pull/5) | f82147d49cfe65560462acff420974f56684e09a | [43072256626](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43072256626) 45/45 tests and [43072249164](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43072249164) real Mem0+Ollama PASS |
| WORK-02D | [#6](https://github.com/rightware-corporations/rightware-shared-intelligence/pull/6) | 6345fb4f6238ecea2d376e82b659238d4684f30f | [43109095085](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43109095085) 48/48 tests + real external MCP subprocess E2E PASS |

## What is really in the repository (pre-reorganization)
```text
rightware_si/          # FastAPI, auth, tasks, Mem0 integration, MCP bridge
  core/postgres.py     # transaction and task/handoff state machine
db/migrations/         # 0001/0002/0003 SQL
vendor/mem0/           # pinned upstream submodule
tests/                 # 8 Python test files
scripts/               # real Mem0 smoke and real MCP E2E
docs/                  # architecture, WORK-specific reports, handoffs
.github/workflows/     # historical CI workflows
pyproject.toml
requirements-work02*.txt
README.md
```

**Not present as working applications:** frontend; deployable production admin console; secure self-service customer onboarding; full human approval UI; verified Jarvis integration.

## Known failures and remediation history
- WORK-02B first CI: expired token fixture conflicted with PostgreSQL validity constraint; MCP v2 list-tools test used incorrect response field. Fixed; 29/29 verified.
- WORK-02C first real Mem0 CI 43071128516: RIGHTWARE package was not installed for standalone smoke. Fixed editable install; real smoke later PASS. A temporary synthetic secret appeared in early CI logs; later key generation and masking corrected.
- WORK-02D 43107788463: unconfigured-memory test accidentally inherited backend URL from CI environment; fixture isolated.
- WORK-02D 43108113909: 48 tests PASS but E2E collided with existing synthetic DB project fixtures; E2E now truncates ONLY disposable local /rw_test DB; final CI 43109095085 PASS.

## Technology and boundaries
- Python >=3.11; GitHub CI Python 3.12; FastAPI; psycopg; PostgreSQL16 core, PostgreSQL17/pgvector lab; Mem0 OSS gitlink SHA f1791daa86d469249c9b002f62644d58a1eb96a0; local Ollama 0.40.15 + all-minilm embeddings; MCP Python SDK 2.x stdio.
- Multi-tenant authorization is RIGHTWARE API responsibility, never Mem0 user_id naming or LLM assertions. Memory retrieval text is UNVERIFIED.
- Qwen text inference not verified; synthetic real smoke used infer=false. Jarvis/PULSE production never touched.

## Continuation decisions
OFFICIAL: ongoing branch names develop/main only; append-only MASTER + current HANDOFF every technical output.
PROPOSED: repository directories backend/, frontend/ (future), database/, infrastructure/, tests/, docs/, vendor/; simple Python modular monolith rather than microservices.
NOT DECIDED: licensing/pricing, cloud hosting, frontend timing, DB topology for deployment, production retention/OIDC details.

