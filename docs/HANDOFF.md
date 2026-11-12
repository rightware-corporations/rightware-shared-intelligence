# RIGHTWARE Shared Intelligence — CURRENT HANDOFF

**Refreshed:** 2026-11-12 (Africa/Maputo); checkpoint SI-MH-0008 · **Source of historical truth:** [HANDOFF_MASTER.md](HANDOFF_MASTER.md) · **Policy:** [HANDOFF_POLICY.md](HANDOFF_POLICY.md)

## Immediate recovery
- Repository: https://github.com/rightware-corporations/rightware-shared-intelligence
- Active development branch: **develop**. Created from verified WORK-02D code+docs commit **6345fb4f6238ecea2d376e82b659238d4684f30f**; current branch head must always be fetched at the start of a new task.
- Stable release branch: **main**, SHA **87c3351055aaf58d37f233dbc96eaa8f0b749c5c** (only initial README). main is NOT a tested deployment/release of the shared intelligence service.
- All new work directly in develop; main only receives an explicitly approved release. Historical feat/docs branches and six Draft PRs are retained as forensic anchors until safely reconciled. **Do not delete them or merge automatically.**
- MASTER entry SI-MH-0001 reconstructs WORK-00 -> WORK-02D. SI-MH-0002 records the operator's two-branch + per-output handoff decisions.

## Current implemented scope
- Python package em `backend/rightware_si/` (import `rightware_si`): PostgreSQL task/handoff lifecycle, project grants, bearer auth FastAPI, MCP stdio, Mem0 contextual e integração de laboratório.
- Database em `database/migrations/`: SQL 0001 tarefas/grants, 0002 API credentials, 0003 limpeza de lease tokens (bytes preservados nesta mudança).
- Memory engine: Mem0 OSS pinned submodule vendor/mem0 SHA f1791daa86d469249c9b002f62644d58a1eb96a0, Ollama local all-minilm embeddings + pgvector in test.
- NO frontend application or deployment infrastructure ready yet. NO Jarvis/PULSE production integration. NO model training, no global approved-decision engine.

## Last verified tests and status
- WORK-02D code base SHA 6345fb4f6238ecea2d376e82b659238d4684f30f: Actions https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43109095085 **SUCCESS**.
- 48/48 unit+PostgreSQL/REST/MCP tests PASS; separate real MCP subprocess -> REST auth -> PostgreSQL task/grants -> real Mem0 OSS -> Ollama local embeddings -> pgvector E2E PASS. Synthetic data only.
- Corrected fail runs: 43107788463 and 43108113909. Preserve these failures and fixes in evidence, not delete history.
- Primeira execução de DEVELOP para a política e base WORK-02D: [Actions run 43119271001](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43119271001) **SUCCESS**: HANDOFF_POLICY_PASS (ambos os docs editados no commit), **51/51 testes PASS** e E2E real MCP/REST/PostgreSQL/Mem0/Ollama PASS. Código+docs verificados em commit fb59750191a50c605ef828c1d726f4bad29c811c.

## Official operator decisions (2026-11-12)
1. Only develop (building/testing) and main (approved stable release) as ongoing working branches.
2. Every technical output/checkpoint must be durable: append MASTER, refresh CURRENT HANDOFF and commit alongside output. Research conclusions, blocked work and test failures count as outputs.
3. Preserving future work in docs is mandatory to survive loss of the chat. Use history and SHA, not chat session as the source of truth.

## Unresolved risks
- Repository is public; no private memories, keys, tokens, personal data or CI secrets may be committed.
- Lease-token idempotency secrecy improved in WORK-02D, but a lost response still requires recovery/reassignment policy.
- Workload identity/OIDC, TLS for remote clients, rate limits, resource-level grants, memory retention/deletion, event outbox and independent security review remain unimplemented.
- Embedding model tag not immutable; vendor MCP hosts and actual Jarvis staging require separate test; no production readiness claim.
- Existing six Draft PRs + historical branches need careful inventory/archival before deletion. GitHub branch protections and separate backup/restore remain unconfigured.

## WORK-03A R1 — Reestruturação validada em laboratório
- Parent HEAD actual de `develop`: `6c257ff70b5ac961b455cc23fb96a6676e575939`. A pesquisa SI-RD-01 e SI-MH-0004 estão preservados.
- 11 blobs Python movidos para `backend/rightware_si/`, 3 SQL para `database/migrations/`, 3 requisitos para `backend/requirements/`, **17/17 hashes de blob iguais**.
- `pyproject.toml` ajustado; `.github/workflows/ci.yml` único workflow actual; testes de layout novos. `frontend/` e `infrastructure/` contêm documentação, **não** aplicações/deployments.
- `docs/ARCHITECTURE.md`, `README.md` e `docs/work03a/RESTRUCTURE_MANIFEST.md` descrevem o estado actual. **CI 43121657190 SUCCESS (55/55 testes + E2E real)** para o código reorganizado; evidência completa em `docs/work03a/EVIDENCE.md`.
- `main`, vendor Mem0, Jarvis, PULSE e seis Draft PRs não alterados. Continuar a investigação SI-RD-02 sem transformar hipóteses em decisões oficiais.

## Investigation checkpoint SI-RD-01 (documentation only)
- [Research dossier](research/SI_RD_01_TECH_LANDSCAPE_2026-11-12.md): review of Mem0, Hindsight, Graphiti/Zep, Letta, LangGraph, Temporal, A2A, simple PostgreSQL/FTS baseline; verified issue statuses vs vendor claims; community success/failure patterns; proposed differential hypotheses.
- No new benchmarks run, no runtime/DB/Jarvis changes, no commercial advantage validated. Source URLs and experimental method in dossier.
- Baseline used for this research checkpoint: develop@521961dd681d55b86cadef823f61243e176b15da; CI run 43119637429 SUCCESS (pre-existing runtime), new documentation CI PENDING after commit.
- Proposed next research task: **SI-RD-02**, inspect source/license/versions per technology, then build synthetic memory+continuity benchmark with identical conditions.

## SI-RD-02 — Pesquisa de engenharia concluída documentalmente (sem benchmark executado)
- Dossier [SOURCE_CODE_MATRIX](research/SI_RD_02_SOURCE_CODE_MATRIX_2026-11-12.md), [BENCHMARK_CONTRACT](research/SI_RD_02_BENCHMARK_CONTRACT.md) e [18 fixtures sintéticas](research/fixtures/SI_RD_02_cases_v1.jsonl). Checkpoint SI-MH-0007.
- Código/documentação de sete fornecedores lidos com SHA e licença principal identificados; classificação REUSE/EVALUATE/LEARN. Matriz não constitui aprovação de licenças transitivas ou desempenho.
- A investigação indica que Hindsight já possui memory defense/validação, Graphiti temporal edges, Letta Git-backed memory; Mem0 pinned é ADD-only/hybrid e não inclui graph OSS. Diferença comercial ainda HIPÓTESE.
- Fixture validada estruturalmente: 18 JSONL objectos (6 memory, 6 continuity, 6 security), IDs únicos, oracles. Nenhum benchmark foi executado, nenhuma integração mudou.
- CI do commit SI-RD-02: PENDENTE, deve ser consultado e registado em checkpoint posterior; último CI consolidado verificado foi WORK-03A 43121657190 SUCCESS (55 testes + E2E).
- Próximo gate recomendado: SI-RD-03 isolated benchmark harness (baseline PostgreSQL vs Mem0/Hindsight, Graphiti temporal depois), sem alterar o runtime/ produção.

## SI-FG-01 — Auditoria de fecho funcional (documental)
- Relatório: [SI_FG_01_FUNCTIONAL_GAP_AUDIT_2026-11-12.md](product/SI_FG_01_FUNCTIONAL_GAP_AUDIT_2026-11-12.md). Base de auditoria `develop@5787579f3b2b936e049d386488bb9671778bae52`; não houve alteração de runtime.
- Prova actual de laboratório: PostgreSQL/REST/MCP/Mem0/Ollama sintéticos PASS; **não é o produto integral da visão**.
- Lacunas prioritárias: observação e memória autorizadas, context snapshot, `resume` após crash/restart, handoffs com artefactos, verificação/decisão/approval, memory lifecycle, outbox, Jarvis staging.
- **RECOMENDAÇÃO:** WORK-03B R0 Functional Contract Closure **antes** do deployment; R1 jornada real de continuidade, R2 trust/lifecycle e só depois staging/infra. A aprovação formal desse roadmap ainda cabe ao operador.
- A pesquisa SI-RD-02 continua documental (18 oracles sintéticos; nenhum benchmark concluído); SI-RD-03 permanece avaliação de fornecedores separada.
- CI do novo commit documental PENDENTE; último CI observado para código anterior foi 43122815508 SUCCESS.

## Next exact work
**Proposta prioritária: WORK-03B R0 Functional Contract Closure** — formalizar lacunas e a jornada de continuidade entre dois agentes antes de avançar para deployment. Não implementar Jarvis em produção. SI-RD-03 benchmark isolado em paralelo; reconciliar antigos PRs e proteger main/develop sem reescrever histórico.

## Recovery protocol
1. Read develop HEAD and docs/HANDOFF_MASTER.md last entry.
2. Read docs/HANDOFF_POLICY.md and matching checkpoint.
3. Review last GitHub Actions result + diff and any open blockers.
4. Execute limited work; commit output and both handoffs atomically; review actual CI and append follow-up if outcome arrives later.

