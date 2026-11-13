# RIGHTWARE Shared Intelligence — CURRENT HANDOFF

**Refreshed:** 2026-11-13 (Africa/Maputo); checkpoint SI-MH-0044 · **Source of historical truth:** [HANDOFF_MASTER.md](HANDOFF_MASTER.md) · **Policy:** [HANDOFF_POLICY.md](HANDOFF_POLICY.md)

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

## WORK-03B R1A — Operational Continuity Foundation (IMPLEMENTADO; CI PENDENTE)
- Base de código: `develop@ad1bc5dcf604bf3fed58846a5fed29ca8fa39917` validada anteriormente em [Actions 43155153394](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43155153394): 60/60 testes e real Mem0/MCP smoke PASS (dados sintéticos).
- **Neste novo commit:** SQL 0004; backend `continuity.py`; 4 rotas REST autenticadas para run/source/observation/list; 8 testes reais novos + 1 gate de contrato; CI migra 0004. O task.version continua inalterado nos asserts; si_continuity_events guarda referências e sequência independente.
- **Novo contrato:** 14 rotas implementadas, 6 propostas, M02 R1A_LAB_PARTIAL; M01–M18 todos PENDING_FULL_E2E. Ver [R1A_IMPLEMENTATION.md](work03b/R1A_IMPLEMENTATION.md).
- **R1A validado em laboratório:** `develop@538eb1b67628e8a0905b6511da9fddf9f0d1313c`, [Actions 43157921966](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43157921966) **SUCCESS** — SQL 0001–0004 MIGRATION_PASS, **69/69 testes PASS**, E2E anterior real MCP/REST/PostgreSQL/Mem0/Ollama PASS (synthetic). Documento detalhado [R1A_EVIDENCE.md](work03b/R1A_EVIDENCE.md). Este commit documental requer validação CI própria.
- Sem alterações a `main`, Jarvis/PULSE, vendor Mem0, produção, deployment ou MCP write tools. Não foram implementados checkpoint/resume, memória persistente por outbox, verificador, decisão DONE ou consentimento/retention.
- Segurança: 30-min task lease, grant scoped e idempotência; falhas 409 em stale/lease ou replay secreto, 403 em permissões; observações são ASSERTED, nunca verificadas.
- Próximo: validar CI desta mudança; se falhar, corrigir e registar. Depois **WORK-03B R1B — TaskCheckpoint + scoped read-only Resume em novo processo** e controlos de revogação.
## WORK-03B R1B — Checkpoint & Resume Engine (CÓDIGO PRONTO / CI PENDENTE)
- Base original validada `develop@9080bbe1d73b91fe752159354000e39e20eb2234`: [CI 43158313613](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43158313613) SUCCESS, 69/69 + E2E real Mem0/MCP/Ollama em laboratório.
- **R1B neste commit:** `0005_work03b_r1b_checkpoints.sql` com checkpoints imutáveis (DB triggers), CAS por seq, FKs mesmo task, eventos auditáveis; métodos `ContinuityCore.record_checkpoint` e `resume_task` (PostgreSQL repeatable read, read-only e project grants).
- REST POST checkpoint + GET resume e MCP `resume_task` apenas de leitura. **16 rotas implementadas / 4 rotas futuras** em `docs/work03b/UC_CORE_01_CONTRACT.json`.
- **R1B CI validado:** [Actions 43160672177](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43160672177) SUCCESS para `develop@5c98e9f42a481709762550d9d451cb64f7d65b31`: cinco migrations, **81/81 testes PASS**, E2E A/B processos independentes com Mem0 offline, e E2E Mem0/Ollama/MCP real PASS. Provas em [R1B_EVIDENCE.md](work03b/R1B_EVIDENCE.md). A adenda documental necessita CI própria.
- `docs/work03b/R1B_IMPLEMENTATION.md` explica a mecânica, limitações e os riscos. Snapshot de observações **ASSERTED**, não VERIFIED. Não emite lease nem executa next_actions; apresenta `checkpoint_binding=NOT_IMPLEMENTED_R1B`.
- `main`, Jarvis/PULSE, pinned vendor Mem0 inalterados. Nenhum release, deploy, dado privado ou inferência de modelo neste trabalho.
- Progresso UC-CORE-01 **PARCIAL**. Sem checkpoint-bound handoff (R1C), lease lost-response recovery, outbox/ingest, per-source consent, independent reviewer e DONE.
- Próximo passo: R1C handoff vinculado ao checkpoint, fencing e recuperação segura de lease; sem declarar o UC-CORE-01 concluído.

## SI-RD-03C — Investigação de evidências importada para futuro R2
- [Dossier técnico](research/SI_RD_03C_EVIDENCE_RESEARCH_2026-11-12.md) e [16 casos sintéticos](research/fixtures/SI_RD_03C_EVIDENCE_CASES_v1.jsonl) documentados e versionados em `develop`. Não são implementações, benchmarks ou decisões aprovadas; todos os 16 oracles foram validados estruturalmente mas **NÃO EXECUTADOS**.
- Áreas: in-toto/Test Result, SLSA, Sigstore/GitHub attestations, W3C PROV, OpenTelemetry e autorização de verificador/revisor. Preservar `ASSERTED` vs `CHECKED_PASS` vs `REVIEW_ACCEPTED`, e não atribuir DONE por CI simples.
- A importação SI-MH-0019 foi verificada no HEAD `9233f8afefa5877e2eec27a5f90ca0a4a00322ad`: [CI 43161674536](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43161674536) SUCCESS, 81/81 testes + E2E R1B e regressão Mem0 PASS. Nenhum dos 16 oráculos EV foi executado. Nenhum runtime/DB/JARVIS/MAIN alterado; **R1C mantém prioridade**.

## SI-RD-03C → WORK-03B R2 — Integração e gates (RECOMENDAÇÃO, NÃO CÓDIGO)
- **Checkpoint SI-MH-0020:** documento [R2_SI_RD_03C_INTEGRATION_REVIEW.md](work03b/R2_SI_RD_03C_INTEGRATION_REVIEW.md). Referências oficiais preservadas: [dossier SI-RD-03C](research/SI_RD_03C_EVIDENCE_RESEARCH_2026-11-12.md) e [fixture EV-01..EV-16](research/fixtures/SI_RD_03C_EVIDENCE_CASES_v1.jsonl), sem edições.
- **Verificação estática de ingestão:** 16 JSONL válidos, IDs EV-01..EV-16 únicos, todas entradas `synthetic=true`, `executed=false`; oráculos NÃO executados. CI do HEAD de origem `9233f8afefa5877e2eec27a5f90ca0a4a00322ad` SUCCESS [43161674536](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43161674536) com **81/81 testes anteriores**, não um teste de verificador R2.
- **Reuse antes de Build:** R1A/R1B PostgreSQL grants, `si_evidence_refs`, `si_source_records`, `si_observations ASSERTED`, `si_continuity_events`, task `IN_REVIEW`, MCP REST auth; in-toto/Test Result + W3C PROV vocabulário; SLSA/GitHub Attestations/Sigstore opcionais em builds, OTel como correlação sem prompts. OPA e novas dependências adiados.
- **Trust invariants:** `ASSERTED != CHECKED_PASS != REVIEW_ACCEPTED`; CI verde, URL, assinatura ou LLM não autorizam `DONE`. Executor, verificador e reviewer devem ser distintos sob grants atuais. R2 contratual e a fixture exigem gates pós-R1C.
- **CI verificado para a integração:** `develop@2db9cd40e1701639434dc0c00cca8cf5282adead` [Actions 43182746837](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43182746837) SUCCESS: handoff gate, cinco migrations, **81/81 testes**, R1B A/B E2E com Mem0 desligado e regressão MCP/REST/Mem0/Ollama PASS. **Nenhum EV-01..EV-16 foi executado**. SI-MH-0021 adiciona evidência; o seu commit é apenas documental e precisará de CI própria.
- **Prioridade inalterada:** WORK-03B R1C (checkpoint-bound handoff, fencing, lease recovery) → avaliação/ratificação R2 → EV-01..EV-16 tests reais com logs/SHAs.

## WORK-03B R1C — Checkpoint Bound Handoff & Lease Fencing (VALIDADO EM LABORATÓRIO, 94/94)
- Base `develop@5fa303487fb4df92d5938c1c84ae2384fd3f882e` e CI [43183197724](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43183197724) SUCCESS (81/81, R1B A→B e Mem0/Ollama real E2E).
- **Novo código:** migration `0006_work03b_r1c_handoff_fencing.sql`; `si_handoffs` checkpoint id/seq/task.version com FK/trigger; `si_lease_fences` garante geração persistente monotónica. Oferta ligada a checkpoint *exato e do writer* quando tarefa já tem checkpoint; nenhuma auto-substituição de estado. Sem checkpoint, modo histórico `LEGACY_UNBOUND`, não é handoff verificável.
- **Leases:** aceitação revê checkpoint/grants, fencing generation crescente; holder autenticado e com `task:recover` consulta nonsecret generation e roda token one-time por `expected_generation`. Replays 409; sem usurpação de outro holder nem armazenamento de segredo bruto no audit/idempotency.
- **API:** 2 rotas novas GET `lease-status` / POST `lease-recovery`; resume inclui id do checkpoint bound/historical sem emitir lease. Contrato canónico 18 rotas atuais de laboratório + 3 R2 futuras.
- **CI R1C comprovado:** [Actions 43196082372](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43196082372) SUCCESS no `develop@0eb985a02d34a55db2cafe721978bd96abbbeac2`: 0001–0006 MIGRATION_PASS, **94/94 testes PASS**, R1C B recovered lease in separate subprocess/without Mem0, replay denied, R1B e Mem0/Ollama E2E regressão PASS. Evidência [R1C_EVIDENCE.md](work03b/R1C_EVIDENCE.md). O commit documental desta adenda requer nova validação CI.
- [R1C_IMPLEMENTATION.md](work03b/R1C_IMPLEMENTATION.md) documenta contratos e limites. Nenhum R2 verifier implementado; EV-01..EV-16 `executed=false`, decisões `ASSERTED` não `CHECKED_PASS` nem `REVIEW_ACCEPTED`.
- Não mexer `main`, JARVIS/PULSE, Mem0 pinned, deploy, frontend. Riscos: modo LEGACY_UNBOUND, token recovery de holder com bearer privilegiado, nenhum fencing sobre efeitos externos, sem consent/retention/verified DONE. **R1C CI e adenda documental já validados em 43196082372 / 43196692278 (94/94)**.
- Próximo: decidir política R1C LEGACY_UNBOUND, grant holder-only recovery/step-up e fencing de side-effects externos; depois **R2 design/contrato**, usando SI-RD-03C sem executar os 16 EV até ao gate aprovado.

## SEC-R1C + WORK-03B R2 R0 — DECISIONS/CONTRACT (NÃO IMPLEMENTAÇÃO)

- **Checkpoint SI-MH-0024:** [R1C_SECURITY_POLICY_GATE_R0.md](work03b/R1C_SECURITY_POLICY_GATE_R0.md) apresenta SEC-R1C-01..04 como **RECOMENDAÇÕES, NÃO DECISÕES OFICIAIS**: migração de LEGACY_UNBOUND, ausência de titular/takeover, efeitos externos e recovery grant/step-up. O código R1C lab não foi alterado.
- **R2 R0 desenhado apenas:** [R2_TRUST_CONTRACT_R0.md](work03b/R2_TRUST_CONTRACT_R0.md) e [R2_TRUST_CONTRACT_R0.json](work03b/R2_TRUST_CONTRACT_R0.json). R2-00..R2-05 gates; `si_observations ASSERTED` continua separado de futuro `VerificationAttempt CHECKED_*`, e `ReviewDecision` requer revisor autorizado e policy/version CAS. Não há aprovação DONE por CI.
- **CI de contrato R2 R0 VERIFICADO:** `develop@22d71632caa6f7e442af5964561b42b1b4ea8693` [Actions 43201981635](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43201981635) SUCCESS: seis migrations, **100/100 testes PASS** (94 anteriores + seis estáticos), R1B/R1C A→B + rekey com Mem0 OFF, MCP/REST/Mem0/Ollama real PASS. Isto é somente **CONTRACT-LINT**, não EV-01..EV-16 execução; `executed=false` e `observed_decision=null` em todos. Evidência [R2_R0_CONTRACT_EVIDENCE.md](work03b/R2_R0_CONTRACT_EVIDENCE.md). A adenda documental exige CI própria.
- Contrato original UC-CORE-01 preservado com 18 rotas laboratório / 3 futuras, M01–M18 `PENDING_FULL_E2E`. Não instaladas dependências nem alterados backend/SQL/workflow/vendor, `main`, JARVIS/PULSE.
- **Próximo gate:** ratificar/rever SEC-R1C-01..04 e definir provider GitHub Actions/critério exacto para um futuro verificador R2 R1. Não há R2 verifier, review endpoint ou decisão DONE implementados.

## WORK-03B R2 R1A — GitHub Evidence Verifier (VALIDADO EM LABORATÓRIO, 115/115)

- Baseline validada `develop@0c63b2f2d3d4cf00926752ab2c58d42ccbd64901`, [Actions 43202560651](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43202560651) SUCCESS, 100/100 testes PostgreSQL/R1C e Mem0/Ollama real.
- **Novo** `backend/rightware_si/evidence_github.py`: check limitadíssimo da API de GitHub Workflow Run, vínculo exacto de repo ID/nome, workflow ID, SHA 40 hex, run ID, attempt, event e conclusão; falhas `CHECKED_FAIL/INCONCLUSIVE` sem aprovação de tarefa. Sem endpoints, DB, credenciais persistidas ou chamadas arbitrárias.
- **Testes:** `tests/test_r2_r1a_github_lab.py` = 15 testes reais da lógica com respostas MOCK, incluindo EV-01..07 como casos de laboratório; `scripts/work03b_r2_r1a_github_live.py` usa provider API GitHub real com pinned historical CI 43202560651 e EV-01..04; workflow read-only `actions:read`. **115 testes ESPERADOS; live smoke ainda PENDENTE até run comprovar**.
- [R2_R1A_GITHUB_VERIFIER_LAB.md](work03b/R2_R1A_GITHUB_VERIFIER_LAB.md) lista identidade exacta, boundaries, benefícios e limites. 16 oráculos da pesquisa preservados com `executed=false`, pois o input continua uma especificação; se EV-01..04 forem executados, provas reais devem ser registadas **separadamente** no CI. EV-08..16 NÃO EXECUTADOS.
- **NÃO implementado:** API `evidence:verify`, tables VerificationAttempt, produtor confiável/reviewer separado, `task:review`, DONE, attestation/signature, per-resource privacy/consent, tool effect outbox, frontend, Jarvis. R2 R0 JSON continua 0 rotas R2 operacionais e UC-CORE-01 conserva 18/3 e M01–M18 PENDING_FULL_E2E.
- **Governança:** SEC-R1C-01..04 mantidos **PENDENTES DE RATIFICAÇÃO**; protótipo não altera essas políticas nem concede poderes. `main`, vendor Mem0, JARVIS/PULSE e produção inalterados.
- **Próxima ação:** ler CI real e acrescentar SI-MH-0027 com 115-test e os 4 live outcomes se verificados; investigar falhas sem ocultá-las, depois pedir ratificação das políticas de identidade/evidência para a fase R2 R1B.

## R2 R1A verified evidence — SI-MH-0027

- **CI real:** [Actions 43214573166](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43214573166) SUCCESS para `develop@1aa40c0d54c96d7c59bb7118326700a974cbb46e`: **115/115 testes PASS**, migrations 0001–0006, independent R1B/R1C A→B and lease-recovery E2E PASS, full MCP/REST/Postgres/Mem0 OSS/Ollama PASS. `HANDOFF_POLICY_PASS` confirmado.
- **GitHub live provider checks:** EV-01 `CHECKED_PASS` para ID/commit/workflow/run corretos; EV-02/03/04 `CHECKED_FAIL` nos mismatches esperados. **EV-05/06/07 só MOCK HTTP/inputs simulados** em testes do código. EV-08..16 NÃO EXECUTADOS. Todos `task_approved=false`; nenhum SQL/evento de verificação, review ou DONE.
- [R2_R1A_EVIDENCE.md](work03b/R2_R1A_EVIDENCE.md) conserva logs, fonte LIVE vs MOCK, identidade exata do run e limites. Original fixture SI-RD-03C `executed=false` inalterado (spec, não journal de testes).
- **Contratos de segurança ainda abertos:** SEC-R1C-01..04 sem ratificação; R2 R0 DRAFT, sem VerificationAttempt, `evidence:verify` service principal, resource grants/retention, endpoint ou reviewer; M01–M18 pendentes.
- **Este commit documental:** apenas reporte + dois handoffs; CI separada deve ser observada. Próximo: ratificar políticas de GitHub provider e R1C release; depois R2 R1B persistência/autorização controladas, sem alterar Jarvis, main ou vendor Mem0.

## WORK-03B R2 R1B — Internal VerificationAttempt Ledger (VALIDADO EM LABORATÓRIO, 131/131)

- Baseline develop@7e38f617c851d8c70911e15001aec945eac5ebda, [Actions 43215546691](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43215546691) 115/115 SUCCESS, GitHub API EV-01..04 live e R1C/Mem0/Ollama E2E reais.
- **Migration 0007:** si_evidence_verification_policies e si_verification_attempts scoped por project/task/evidence, imutáveis/append-only e geração de evento EVIDENCE_CHECKED. Campo observation_channel LIVE_HTTPS vs SIMULATED_TRANSPORT diferencia prova real de mock.
- **Serviço interno:** verification_ledger.EvidenceLedger exige actor SERVICE autenticado, evidence:verify+task:read, separação do criador/submeter/policy owner; policy exact GitHub URL+repo/workflow/run SHA, estado IN_REVIEW e expected_version; chamada de rede fora de lock, revalidação de grants/versão antes do commit. Leitura apenas com evidence:read + task:read. Replays idempotentes. NENHUM endpoint público R2 ou decisão DONE.
- **CI R2 R1B REAL VERIFICADO:** [Actions 43237504677](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43237504677) **SUCCESS**, migrações 0001–0007, **131/131 testes PASS** (115+16 PG), R2 R1B **GitHub LIVE API → SERVICE bearer autorizado → PostgreSQL append-only CHECKED_PASS**; idempotência e read revocation, task IN_REVIEW e evidence REFERENCED, no DONE. Regressões R1C e Mem0/Ollama PASS. Evidência [R2_R1B_EVIDENCE.md](work03b/R2_R1B_EVIDENCE.md). Esta adenda documental requer CI própria.
- [R2_R1B_VERIFICATION_LEDGER.md](work03b/R2_R1B_VERIFICATION_LEDGER.md) contém schema, boundary de autoridade, lista de testes e limitações. Original SI-RD-03C fixture ainda investigação; R2 R0 JSON mantém 0 REST rotas R2 operacionais; UC-CORE-01 18 lab/3 futuras, M01–M18 PENDING_FULL_E2E.
- **Gates pendentes:** SEC-R1C-01..04 sem ratificação, critérios/provider por cliente, consent/privacy/source ACL, OIDC, rate limits, policy lifecycle, REST/MCP verify e revisor independente. Sem main/JARVIS/PULSE/vendor changes, sem paid services/deploy.
- Próximo: ratificar/rever SEC-R1C-01..04, política de GitHub/provider/criteria por cliente, perfis de SERVICE/consent/retention antes de API operacional. CHECKED_PASS do run não constitui revisão ou DONE.

## Next exact work
**Próximo gate: ratificar SEC-R1C-01..04 e políticas de provider/identity/consent/criteria para R2 operacional, após R2 R1B laboratório 131/131 PASS; só posteriormente considerar API REST evidence:verify e um reviewer independente; nunca auto-DONE** com checkpoints imutáveis, ContextSnapshot e resume controlado, teste em dois processos sem o chat original. Ratificações de privacy/recovery e separação de revisão continuam abertas. Não implementar Jarvis em produção. SI-RD-03 benchmark isolado em paralelo; reconciliar antigos PRs e proteger main/develop sem reescrever histórico.

## Recovery protocol
1. Read develop HEAD and docs/HANDOFF_MASTER.md last entry.
2. Read docs/HANDOFF_POLICY.md and matching checkpoint.
3. Review last GitHub Actions result + diff and any open blockers.
4. Execute limited work; commit output and both handoffs atomically; review actual CI and append follow-up if outcome arrives later.


## SI-MH-0030 — Estado para novo chat / gate R2 R1C (DOCUMENTAL)

- **Baseline remoto confirmado:** `develop@e43a653b3c5999028abe4571fb9730b7f9b25dea`; `main` continua com README inicial. [SI-MH-0029](HANDOFF_MASTER.md) e [R2 R1B evidence](work03b/R2_R1B_EVIDENCE.md) são a última implementação comprovada.
- **Última suite efectiva:** 131/131 PASS [43237504677](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43237504677), GitHub LIVE API → SERVICE → PostgreSQL append-only; regressão R1C e Mem0/Ollama. CI documental [43238519552](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43238519552) job success observado. CI deste SI-MH-0030 **PENDENTE DE VERIFICAÇÃO**.
- **Recuperação:** [R2 R1C DECISION AND API GATE R0](work03b/R2_R1C_DECISION_AND_API_GATE_R0.md) consolida progressos, recomendações SEC-R1C-01..04, provider GitHub por tenant, identity, criteria, privacy, autorização SERVICE e matriz de testes a exigir antes do endpoint R2 R1C. **Documento apenas; nada ratificado nem implementado.**
- **Próximo passo operacional:** ratificar/rever SEC-R1C-01..04 e política de fornecedor/critério/consentimento; consultar CI deste commit; só então autorizar API REST de `evidence:verify` (sem reviewer/DONE). Manter `ASSERTED != CHECKED_PASS != REVIEW_ACCEPTED != DONE`.
- **Preservado:** zero alterações a backend/migrations/workflows/runtime, `main`, JARVIS, PULSE e vendor Mem0. Não repetir commits nem aplicar PRs históricos destrutivamente.

## SI-MH-0031 — R2 R1C contract lint / evidence path safety (NÃO API)

- HEAD inicial conferido: `develop@0eb4e662490ffb22a18cdb5e21ac4c85c14066d4`. Novo [REST contract R0](work03b/R2_R1C_REST_VERIFY_CONTRACT_R0.md) e [JSON](work03b/R2_R1C_REST_VERIFY_CONTRACT_R0.json), 16 oráculos negativos API-NEG-01..16 **NÃO EXECUTADOS**.
- **Gap de código encontrado:** o path futuro usa `evidence_id`, mas `EvidenceLedger.verify_and_record` só usa `policy_id`. Exigir `expected_evidence_id` e binding/recheck transacional ANTES de implementação REST; não passar adiante um path ignorado.
- `tests/test_r2_r1c_contract.py` adiciona **11 static lint tests** sem PostgreSQL ou API E2E. Suite estimada 142 (131 baseline +11); **CI do novo commit pendente**, não declarar 142 PASS sem observação.
- SEC-R1C-01..04, R2-PROVIDER, R2-IDENTITY, R2-PRIVACY aguardam ratificação; nenhuma rota R2, review ou DONE disponível. `main`, JARVIS, PULSE e pinned Mem0 preservados.
- **Next:** verificar CI do SI-MH-0031; ratificar políticas; só depois autorizar endpoint SERVICE-only e executar API negative integration, revocation, concurrency e live provider tests.

## SI-MH-0032 — SEC-R1C conservador ratificado (PRINCÍPIOS) / REST R2 R1C LAB (CI PENDENTE)

- HEAD de origem `develop@3567c99dfa620f3bf23eaf8fa0b1b030c42f131c`, commit atómico de backend+testes+docs+ambos handoffs. [Registo oficial de princípios](work03b/SEC_R1C_POLICY_RATIFICATION_R1.md): SEC-R1C-01..04 aprovadas como DIREÇÃO DE SEGURANÇA; mecanismos de execução não implementados em produção. R2-PROVIDER/IDENTITY/PRIVACY para tenants reais **pendentes de ratificação**.
- [R2 R1C LAB](work03b/R2_R1C_LAB_IMPLEMENTATION_R0.md): nova rota FastAPI **apenas se** `RW_SI_ENABLE_R2_R1C_LAB_API=1`, `RW_SI_ENVIRONMENT=lab` e PostgreSQL loopback `/rw_test`; de resto desativada. `expected_evidence_id` validado antes e depois do provider. SERVICE-only com bearer e evidence:verify + task:read. Nenhuma rota de review/DONE.
- `tests/test_r2_r1c_api_lab.py`: 16 testes HTTP/DB sintéticos adicionados; contrato estático 11 atualizado; suíte estimada **158 = 131+11+16**, **CI pendente**. Não confundir simulados com LIVE; novo artefacto não comprovado até execução. Última baseline verificada: 131/131 [43237504677](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43237504677).
- Pendentes: CI deste checkpoint, mapping API-NEG por caso, identity OIDC, gestão da policy/pin/expiry/disable, privacidade por fonte, rate-limit, outbox, reviewer, DONE, M01–M18. Sem alterações a `main`, JARVIS/PULSE, Mem0 pinned.
- NEXT: confirmar CI real e corrigir falhas se existirem; depois checkpoint de evidência com SHA/logs, sem promover para produção.

## SI-MH-0033 — R2 R1C contract route inventory corrected (CI pendente)

- Parent `develop@2cec2c26bdbf63f0ae4b33986ad087c8a70c30b9`; canonical `UC_CORE_01_CONTRACT.json` now separates 18 original regular routes, 1 `LAB_FLAGGED_OFF_BY_DEFAULT` verify decorator and 2 future unimplemented routes; M01–M18 unchanged.
- Tests `test_work03b_contract.py` + `test_r2_r0_contract.py` synchronized to preserve historical draft and avoid false negatives on code-added opt-in route. No runtime/backend/migration changes in this checkpoint.
- CI deste commit e do SI-MH-0032 não confirmado pelo conector disponível; **158 testes esperados, NÃO COMPROVADOS**. Legacy 131/131 verificado anteriormente. No main/JARVIS/PULSE/production changes.
- NEXT: observar CI com run+SHA, corrigir erros de teste/implementação, adicionar checkpoint SI-MH-0034 com resultados reais.

## SI-MH-0034 — CI real do SI-MH-0033 comprovado; teste duplicado corrigido

- HEAD de origem: `develop@9de64471980ad3826b31c92160072fc8a457bb17`. CI anterior do SI-MH-0033: [Actions 43249997206](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43249997206) **SUCCESS**, 174 execuções/OK, 7 migrações, live GitHub R1A/R1B + R1C A/B + MCP/REST/Mem0/Ollama E2E PASS.
- Falha histórica SI-MH-0032: [Actions 43249446536](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43249446536) **FAILURE 2 testes estáticos antigos**; corrigidos SI-MH-0033. SI-MH-0031: [Actions 43247901257](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43247901257) SUCCESS 142.
- **Atenção:** 174/174 inclui 16 testes R1B coletados duas vezes devido a import de TestCase no módulo R2 R1C. SI-MH-0034 corrige apenas o import; nova contagem prevista **158 casos distintos**, **CI pendente**. Não declarar 158 PASS antes de confirmação.
- Evidência [R2_R1C_SI_MH_0034_CI_EVIDENCE.md](work03b/R2_R1C_SI_MH_0034_CI_EVIDENCE.md), com graus LIVE vs MOCK, limitações, run IDs e próximo gate. R2 R1C HTTP testado com MockTransport; sem live provider via endpoint, OIDC/prod, policy lifecycle, consent ou DONE.
- Próximo: ler CI do novo HEAD, registar SI-MH-0035 com run+SHA e 158 teste PASS ou falhas reais, preservar `main`, Jarvis/PULSE e Mem0.

## SI-MH-0035 — R2 R1C laboratório: 158/158 testes e E2E validados

- Último código validado `develop@f4732da8de086c9f869b3833a66f168a35e82a40`: [Actions 43251091244](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43251091244) **SUCCESS**, `Ran 158 tests / OK`, sete migrations e smokes GitHub R1A/R1B live, R1C A/B sem Mem0 e E2E real MCP/REST/PostgreSQL/Mem0/Ollama. Correção de import SI-MH-0034 eliminou 16 execuções duplicadas.
- R2 R1C HTTP: **LAB ONLY FLAGGED OFF BY DEFAULT**; testes HTTP+PostgreSQL usam `SIMULATED_TRANSPORT`, não há prova LIVE GitHub chamada através da nova rota. Sem reviewer/DONE; a prova LIVE GitHub→ledger continua R1B.
- [Evidência e matriz API-NEG](work03b/R2_R1C_SI_MH_0035_VERIFIED_EVIDENCE.md): API-NEG parcialmente cobertos; expiração/revogação de policy por tenant, provider identity/OIDC/consent/retention e 503/secret-redaction ainda não fechados. Evitar marcação de aceitação integral.
- Este SI-MH-0035 altera apenas docs+handoffs; **seu próprio CI pendente**. `main`, JARVIS, PULSE, vendor Mem0 preservados.
- NEXT: R2 R1D-R0 — contratos policy/provider/identity/privacy, ampliar negativos, ensaio LIVE GitHub-through-REST isolado; sem produção.

## SI-MH-0036 — CI da adenda 0035 confirmado; R2 R1D-R0 apenas PROPOSTO

- **Develop before SI-MH-0036:** `5adb8165eddf54c5145c5aba983882a72dca4b43`, [Actions 43252042999](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43252042999) **SUCCESS** `Ran 158 tests / OK`; handoff policy, migrations 0001..0007, GitHub R1A/R1B LIVE, R1C A/B e Mem0/Ollama E2E PASS. Code checkpoint SI-MH-0034 também validado em 43251091244.
- **Plano R2 R1D-R0:** [R2_R1D_SECURITY_GATES_R0.md](work03b/R2_R1D_SECURITY_GATES_R0.md): Policy lifecycle/tenant ownership, completar negativos API-NEG, ensaio LIVE GitHub-through-REST em CI isolado, identity/OIDC/privacy/consent, release gates; **RECOMENDAÇÃO não ratificada, nada implementado em R1D**.
- Este checkpoint apenas documentos; CI dele **PENDENTE**. Endpoint R2 R1C continua opt-in só laboratório, nunca DONE, main/JARVIS/PULSE/vendor Mem0 preservados.
- NEXT: ratificação dos contratos de provider/identity/privacy por tenant; depois testes R1D negativos e LIVE REST em laboratório sem deploy.

## SI-MH-0037 — R2 R1D-G02 laboratory negative tests (CI pendente)

- Baseline `develop@1cc93652669e1ff8d7377bd5f1474229a971980e`. SI-MH-0036 [Actions 43252805427](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43252805427) **SUCCESS**. Último total certo 158/158 em [43252042999](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43252042999).
- `tests/test_r2_r1c_api_lab.py` recebeu +16 testes (17..32) em HTTP/PG testando gaps API-NEG-02/03/06/07/09/10/12/13/16, autorizacao de policy creator e validação de Idempotency-Key; `http_api.py` agora sanitiza falhas `psycopg.OperationalError` também em bearer dependency.
- Esperados **174 testes** (158+16), **NÃO VALIDADOS ATÉ CI**. Provider destes HTTP tests = MOCK, nunca LIVE. R2 R1D-G01 lifecycle e G03 LIVE REST continuam por implementar/ratificar, R1D-G04/G05 release bloqueados.
- Documento [R2_R1D_G02_NEGATIVE_TESTS_R0.md](work03b/R2_R1D_G02_NEGATIVE_TESTS_R0.md), MASTER append-only. Sem mudanças a SQL migrations, main, JARVIS, PULSE, vendor Mem0 ou produção.
- Próximo: CI real deste SHA e correções, depois G03 live REST smoke em laboratório.

## SI-MH-0038 — R2 R1D-G03 GitHub LIVE REST pipeline (CI PENDING)

- Baseline `develop@a3a29dfba16b2bcfca1c523ac7c1229b46c10735` [Actions 43256900860](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43256900860) **SUCCESS 174/174**, seven migrations and GitHub R1A/R1B live + R1C A/B + Mem0/Ollama PASS.
- [G03 live HTTP lab](work03b/R2_R1D_G03_LIVE_HTTP_R0.md): `http_api.py` now sources optional provider token only from SERVER env; new guarded `scripts/work03b_r2_r1d_live_http.py` exercises SERVICE REST → actual GitHub API → PostgreSQL append-only + replay/revocation/no-DONE. CI workflow adds a separate step with GitHub Actions token not visible to caller.
- **CI desse commit PENDENTE:** expected 174 tests plus unique G03 marker; do NOT claim G03 LIVE success without observing logs. LAB-only feature flag remains OFF by default, no prod.
- SEC-R1C principles ratified, policy lifecycle G01, identity/consent G04, release G05 and 16 original EV oracles not fully closed. No changes main/JARVIS/PULSE/vendor Mem0.
- NEXT: inspect G03 GitHub Actions logs, preserve evidence, rectify failure if needed, checkpoint SI-MH-0039.

## SI-MH-0039 — R2 R1D-G03 LIVE HTTP verified, 174/174 tests

- **Último código verificado** `develop@4086e9b62fa06c8c28b9af48c47fe56354e73b2d` — [Actions 43257931058](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43257931058) **SUCCESS**, `Ran 174 tests / OK`, 7 migrations e markers R1A/R1B/G03 GitHub LIVE, R1C A/B e Mem0/Ollama PASS.
- **G03 comprovado:** HTTP TestClient via SERVIÇO independente autenticado, provider GitHub HTTPS REAL com token só de servidor, PostgreSQL append-only `LIVE_HTTPS`, idempotência e revoked verify grant negado, IN_REVIEW/REFERENCED/no-DONE. Não é servidor público implantado. [Evidência do job](work03b/R2_R1D_G03_SI_MH_0039_VERIFIED.md).
- G02 negativos 174/174 incluídos, mas G01 policy lifecycle/tenant expiry/revocation ainda sem ratificação nem código; G04 identity/OIDC/privacy/consent/retention/rate limits e G05 release/M01..M18 bloqueados. Nenhum reviewer/DONE, prod, JARVIS/PULSE/main/vendor Mem0.
- Este checkpoint **só documentação**, CI próprio ainda PENDENTE. Próximo gate: G01 contract/decisões de autoridade para policy por tenant, depois migration/tests sob aprovação.

## SI-MH-0040 — G01 lifecycle decision packet prepared; G03 documentary CI confirmed

- **Baseline `b101aa8f64970524aab496e62e3032862fcf4b6c`**, [Actions 43258863694](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43258863694) **SUCCESS, 174/174 tests**, 7 migrations and LIVE GitHub via R1D SERVICE REST TestClient + existing R1A/R1B/R1C/Mem0/Ollama regressions PASS. No reviewer/DONE.
- **G01 proposal:** [R2_R1D_G01_POLICY_LIFECYCLE_DECISION_R0.md](work03b/R2_R1D_G01_POLICY_LIFECYCLE_DECISION_R0.md). Append-only activation/disable/supersede, DB-clock expiry, shared task row lock, 14 future negative cases **NOT EXECUTED**. Proposed ONLY; no ratification/SQL implementation.
- Pending explicit choices: activation authority/quorum, first internal tenant, expiry, disable/revocation, named legacy lab exceptions, source ACL/consent/retention; G04/G05 production still blocked.
- Docs+two handoffs only in SI-MH-0040, own CI pending; no code/new privileges/main/JARVIS/PULSE/vendor Mem0 changes. R2 R1C lab flag remains OFF by default.
- NEXT: ratify G01 then implement lifecycle transactionally with tests; do not advance production/DONE.

## SI-MH-0041 — Safety of disposable synthetic PostgreSQL DB (CI PENDING)

- Prior `develop@099b5e9d405bb16660a2b565bf221db33e689638` [Actions 43259970366](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43259970366) PASS 174/174 + R2 R1D G03 LIVE + Mem0/Ollama.
- `urlsplit` hostname-only check missed libpq `hostaddr` URI/env redirection; dangerous in synthetic scripts calling TRUNCATE. New `lab_boundary.py` validates query/env/host resolution, explicit user and /rw_test port 5432. R2 experimental API + four destructive CI scripts now call it.
- New `test_lab_db_boundary.py` 16 pure tests; 190 expected, **CI PENDING**. [Report](work03b/R2_R1D_LAB_DB_BOUNDARY_SI_MH_0041.md).
- G01 approval/expiry/tenant/consent NOT RATIFIED, G04/G05 blocked. No migrations/new production endpoints, main/JARVIS/PULSE/vendor Mem0 unchanged. Next observe run SI-MH-0041 and append actual results SI-MH-0042.

## SI-MH-0042 — Lab DB connection boundary VERIFIED 190/190

- Code baseline `d2c06290ec5593324b8c1b84ad96ef3bd335a05e`: [GitHub Actions 43401900930](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43401900930) SUCCESS, `Ran 190 tests / OK`, migrations 0001..0007, GitHub R1A/R1B/G03 LIVE, R1C independent agents and MCP/REST/PostgreSQL/Mem0/Ollama regressions PASS.
- New 16 `lab_boundary` tests validated rejection of DSN query hostaddr, env PGHOSTADDR/PGSERVICE/PGSERVICEFILE, unsafe hosts/database/port and injected redirects before database connection. Lab safety only, not production isolation guarantee.
- [Verified evidence report](work03b/R2_R1D_SI_MH_0042_CI_EVIDENCE.md). This checkpoint is docs-only, **new CI PENDING**, preserve previous proof run.
- G01 lifecycle/tenant authority expiry/disable/retention NOT RATIFIED; no policy schema changes, review/DONE or production route, main/JARVIS/PULSE/vendor Mem0 untouched.
- NEXT: obtain explicit G01 authority/quorum/expiry/tenant/consent decisions; then implement lifecycle with migrations and 14 tests and full regressions.

## SI-MH-0043 — CI SI-MH-0042 verified, 190/190

- `develop@bea6dd3ed4cc27ed841e3fc3d3c8fd6a469c5d27`: [Actions 43402401931](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43402401931) SUCCESS; 190 tests OK, migrations 0001..0007 PASS, GitHub LIVE R1B/G03 and R1C two-agent/MCP/Mem0/Ollama E2Es PASS. Implementation SI-MH-0041 also SUCCESS [43401900930](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43401900930).
- [Verified CI report](work03b/R2_R1D_SI_MH_0043_CI_EVIDENCE.md) appended; SI-MH-0043 itself docs-only; its CI separate.
- G01 activation/expiry/disable/supersession, actor authority, tenant consent and retention still DRAFT NOT RATIFIED; no code/migrations for G01, no reviewer/DONE or production access. Continue only after explicit operator decision.

## SI-MH-0044 — Seven destructive PostgreSQL test fixtures secured (CI pending)

- Last HEAD `develop@bbd731d6e30640df5f35da95bf9db979456287db`, [Actions 43402943623](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43402943623) SUCCESS by GitHub metadata; last exact test log 190 PASS [43402401931](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43402401931).
- Found 7 PostgreSQL unittest modules using stale URI-only `_SAFE` checks before `TRUNCATE`, including the R1B fixture reused in R1C REST tests. Replaced all with `lab_boundary.is_disposable_postgres` and use-time `require_disposable_postgres` before any DB connection. Four pure tests added to guard behavior and fixture source completeness.
- [Implementation audit](work03b/R2_R1D_LAB_TEST_FIXTURES_SI_MH_0044.md). **194 tests expected, CI pending**; no G01 ratification, G04/G05 approval, new SQL migrations or production route, reviewer/DONE, main/JARVIS/PULSE/vendor Mem0 changes.
- NEXT: inspect SI-MH-0044 Actions and append exact evidence in SI-MH-0045. G01 requires approval of tenant authority/quorum/expiry/retention first.
