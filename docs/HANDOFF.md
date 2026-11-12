# RIGHTWARE Shared Intelligence — CURRENT HANDOFF

**Refreshed:** 2026-11-12 (Africa/Maputo); checkpoint SI-MH-0014 · **Source of historical truth:** [HANDOFF_MASTER.md](HANDOFF_MASTER.md) · **Policy:** [HANDOFF_POLICY.md](HANDOFF_POLICY.md)

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
- **SI-FG-01 commit `12ea7c3b299b5a84b0d1a96d59a4c78401cbe40b` validado:** [Actions 43151016529](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43151016529) SUCCESS: HANDOFF_POLICY_PASS, **55/55 testes PASS e E2E sintético real PASS**. A documentação evidencia as lacunas; não entrega funcionalidades ausentes.

## SI-RD-02E — Triagem da investigação externa Perplexity (PDF, 11 páginas)
- [Dossier da triagem](research/SI_RD_02_EXTERNAL_PERPLEXITY_TRIAGE_2026-11-12.md): fonte externa PARCIAL, sem acesso ao repo RIGHTWARE; fact-check GitHub/arxiv, confronto SI-RD-02/SI-FG-01, 3 erros de aritmética no top-10, Kuzu arquivado, SoMem/DBOS e caminhos experimentais.
- **Nenhuma tecnologia adoptada, dependência alterada ou benchmark executado.** Documento é investigação, não decisão oficial de produto.
- Hipótese principal permanece UC-CORE-01 (transferência entre dois agentes com contexto autorizado, evidência independente e recuperação sem efeitos externos duplicados); manter WORK-03B R0 antes de produção, SI-RD-03 como laboratório isolado.
- Parent anterior `develop@7b719f7411cc7da042faae70c3f5198c4d8a0fc3` tem CI SUCCESS run 43151308140; CI deste novo commit documental PENDENTE. MASTER checkpoint SI-MH-0010.

## WORK-03B R0 — Functional Contract Closure (DRAFT / CI PENDENTE)
- [Functional contract](work03b/WORK03B_R0_FUNCTIONAL_CONTRACT.md), [machine-readable contract](work03b/UC_CORE_01_CONTRACT.json), [M01-M18 acceptance crosswalk](work03b/UC_CORE_01_ACCEPTANCE.md), `tests/test_work03b_contract.py`.
- UC-CORE-01: Agent A context-write/checkpoint -> release/handoff -> Agent B independent new-process `resume` -> `IN_REVIEW` evidence -> external verifier + authorized reviewer DONE; separated permissions and revoked-scope checks.
- Inventariados **10 endpoints protegidos existentes** e **7 endpoints propostos**, sem reivindicar novas APIs funcionais. **14 passos de cenário** e **18 critérios originais**, todos PENDING_FULL_E2E, sem produto completo.
- Os 5 testes estáticos novos verificam inventário API real por AST, IDs e oráculos, distinção de rotas não implementadas, sequenciamento, protecções/semântica 409 de segredo. Não demonstram execução da jornada.
- Base `develop@4c6f90feccccb30fa7a6aadb83512f18f50dfdac`: CI 43152798777 SUCCESS para código existente. CI novo após o commit **PENDENTE**.
- Sem mudanças de backend, DB, Mem0/vendor, model inference, Jarvis/PULSE, `main`, PRs ou deployment.
- Ratificação do operador para schema, direitos, MCP-write e política de recuperação de leases continua ABERTA antes do R1.

## WORK-03B R0 — CI REAL VALIDADO
- [Evidence](work03b/EVIDENCE_R0.md) para `develop@c32ab1e7f4b72a27da6c005d04e6825bed62f76e`: Actions [43154026213](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43154026213) SUCCESS; **60/60 testes PASS**, cinco novos testes estáticos do contrato e E2E real **existente** MCP/REST/PostgreSQL/Mem0/Ollama PASS com dados sintéticos.
- R0 contract/schema, M01–M18, 14 passos continuam DRAFT/propósitos, não implementações completas; R1/R2 e ratificação OPEN. Entrada MASTER SI-MH-0012; novo commit de evidência tem CI PENDENTE.

## WORK-03B R0B — Princípio operacional da visão (PROPOSTA)
- Dossier [Blueprint produto](product/work03b/README.md): 7 documentos sobre funcionamento, bounded contexts, autoridade PostgreSQL, Mem0 substituível, Observations/Checkpoint/ContinuationPackage, handoff, resume, verificação, privacidade, risco e research reuse.
- **O contrato canónico continua em `docs/work03b/UC_CORE_01_CONTRACT.json`** (10 APIs actuais, 7 candidatas, 14 passos, 18 aceitação M01–M18); os restantes endpoints e passos UX do blueprint são backlog, não duas especificações concorrentes.
- Referência em `docs/ARCHITECTURE.md`; nenhum novo backend/migration/teste de produto foi implementado. Estado: R0B conceptual, não aprovado para produção.
- **WORK-03B R0B commit `387d489b26a1363ec017b9b8eadb3b572008aa2d` validado:** [Actions 43154792920](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43154792920) SUCCESS — handoff gate, 3 migrations, 60/60 testes e E2E real sintético MCP/REST/PostgreSQL/Mem0/Ollama PASS. O blueprint é só arquitetura, não novo código de produto. Esta adenda documental precisará do próprio CI.
- Próximo trabalho proposto: rever/ratificar ownership e permissões; iniciar WORK-03B R1A autorizado (Observation/AgentRun/SourceRef); depois checkpoint/resume em dois processos. Não tocar no Jarvis em produção.

## Next exact work
**Próximo gate: ratificar o contrato UC-CORE-01 e o blueprint R0B; iniciar WORK-03B R1A delimitado**, com fontes/observações/runs autorizados e testes; depois checkpoints e resume entre dois processos sem alterar Jarvis. Não implementar Jarvis em produção. SI-RD-03 benchmark isolado em paralelo; reconciliar antigos PRs e proteger main/develop sem reescrever histórico.

## Recovery protocol
1. Read develop HEAD and docs/HANDOFF_MASTER.md last entry.
2. Read docs/HANDOFF_POLICY.md and matching checkpoint.
3. Review last GitHub Actions result + diff and any open blockers.
4. Execute limited work; commit output and both handoffs atomically; review actual CI and append follow-up if outcome arrives later.

