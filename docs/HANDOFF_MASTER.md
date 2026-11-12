# RIGHTWARE Shared Intelligence — MASTER HANDOFF

> REGISTO CRONOLÓGICO CUMULATIVO. Não reescrever nem apagar entradas históricas. Correções e revisões entram como nova adenda identificada. O Git preserva versões; proteção contra force-push ainda precisa de configuração.

**Repositório:** https://github.com/rightware-corporations/rightware-shared-intelligence
**Política:** docs/HANDOFF_POLICY.md · **Estado atual:** docs/HANDOFF.md · **Recuperação histórica:** docs/handoffs/BASELINE_WORK00_WORK02D.md
**Confidencialidade:** este repositório é público. Registar resumos técnicos, referências verificáveis e hashes; nunca chats completos privados, tokens, dados pessoais ou segredos.

## Convenções vinculativas
- Cada entrega técnica, investigação que altere decisões, implementação, correção, teste, falha ou checkpoint deve incluir uma NOVA entrada nesta cronologia e atualizar o HANDOFF atual no MESMO commit.
- Cada entrada inclui: data, WORK, classificação (DECISÃO / PROPOSTA / IMPLEMENTADO / VALIDADO / FALHOU / BLOQUEADO), objetivo, alterações, ficheiros, evidência real, riscos, próximo passo e referência Git.
- Nunca transformar um resultado anunciado num resultado testado. Se ainda não houver CI, escrever PENDENTE e acrescentar adenda depois da execução.
- Nunca apagar uma falha histórica. Corrigir com uma nova entrada referenciando o incidente. Nunca expor segredos em diffs ou logs.
- O operador definiu apenas duas branches de trabalho futuro: develop (construção) e main (release aprovado). As antigas seis branches continuam temporariamente preservadas porque contêm PRs Draft e evidências; limpeza requer reconciliação cuidadosa.

---

## SI-MH-0001 — Recuperação histórica WORK-00 → WORK-02D
**Registado:** 2026-11-12 · **Tipo:** BACKFILL RETROSPECTIVO · **Autor institucional:** RIGHTWARE · **Base do código:** 6345fb4f6238ecea2d376e82b659238d4684f30f
**Objetivo:** recuperar num documento durável todo o progresso material comprovado anteriormente, sem declarar que trabalho histórico foi reexecutado neste checkpoint.

### WORK-00 — Fundação OSS Mem0
- Draft PR #1: https://github.com/rightware-corporations/rightware-shared-intelligence/pull/1
- Último commit WORK-00: ba59cecc67c3fb1c5340b5b9471f1b1d25d110ee.
- Mem0 original ligado em vendor/mem0 como submódulo, commit f1791daa86d469249c9b002f62644d58a1eb96a0 (Apache-2.0). Código upstream não se tornou propriedade exclusiva da RIGHTWARE.
- Criado adaptador Python inicial de memória por escopo, documentação de segurança/licenciamento e 8 testes determinísticos. CI com submódulo real verificado: runs 42803825893 e 42803815468 (SUCCESS).
- **Limite:** os testes iniciais usavam memória simulada; não provaram serviço Mem0 em execução.

### WORK-01 — Estratégia, domínio e arquitetura
- Draft PR #2: https://github.com/rightware-corporations/rightware-shared-intelligence/pull/2
- Último commit WORK-01: 3f54278d1f5c8d04138696813a847e9d7d91c682.
- Nove documentos: produto/MVP, entidades, tarefas e handoffs, arquitetura, REST/MCP, segurança e matriz de aceitação.
- **Classificação:** RECOMENDAÇÕES ARQUITETURAIS; criação de documentos não equivale a validação de implementação ou decisão oficial sobre todos os detalhes.

### WORK-02A — Núcleo transacional
- Draft PR #3: https://github.com/rightware-corporations/rightware-shared-intelligence/pull/3
- Último commit WORK-02A: 9310245559743ab9f51bf88fba91b22d64b36db9.
- Implementados PostgreSQL schema, organizações, projetos, principals, grants, tasks com optimistic versions, lease exclusivo, handoff e eventos.
- Integração real PostgreSQL 16, testes determinísticos e concorrência: CI run 43055391551 — **16/16 PASS**.
- **Limite:** nessa fase não havia autenticação HTTP nem aprovação de resultados como DONE.

### WORK-02B — REST autenticada e MCP de leitura
- Draft PR #4: https://github.com/rightware-corporations/rightware-shared-intelligence/pull/4
- Último commit WORK-02B: 4f721f4d10fccccd2f2fef495223e91e79a4ef49.
- Adicionados FastAPI, bearer keys com hash/expiração/revogação, issuer offline, MCP stdio read-only e testes de isolamento.
- CI run 43067218210 — **29/29 PASS**.
- **Limite:** MCP ainda era testado principalmente in-memory; sem integração Jarvis produtiva.

### WORK-02C — Contexto por projeto e Mem0/Ollama reais
- Draft PR #5: https://github.com/rightware-corporations/rightware-shared-intelligence/pull/5
- Último commit WORK-02C: f82147d49cfe65560462acff420974f56684e09a.
- ContextReader com verificação PostgreSQL, isolamento, Mem0 como memória contextual UNVERIFIED, graceful degradation quando motor está offline, ferramenta MCP de contexto e probe cliente somente leitura.
- CI de contrato PostgreSQL/FastAPI/MCP com Mem0 FAKE: run 43072256626 — **45 testes PASS**.
- Smoke real: Mem0 OSS pinned + PostgreSQL 17/pgvector + Ollama 0.40.15/all-minilm embeddings; CI final 43072249164 — **SUCCESS**. Escreveu/recuperou memória sintética Alpha sem devolver Beta.
- Falha inicial em run 43071128516 (empacotamento/import no script); corrigida. Credencial sintética efémera passou a ser mascarada nos logs.
- **Limite:** modelo Qwen não executado em inferência de texto; infer=false e embeddings locais. Não foi usada API paga obrigatória.

### WORK-02D — Segurança de leases + cadeia E2E real
- Draft PR #6: https://github.com/rightware-corporations/rightware-shared-intelligence/pull/6
- Último commit validado com documentação: 6345fb4f6238ecea2d376e82b659238d4684f30f.
- Migração 0003 remove credenciais lease_token de respostas antigas na tabela si_idempotency; novas gravações não persistem token recuperável. Duplicados claim/accept devolvem conflito explícito; recuperação de resposta perdida continua PENDENTE.
- Cliente MCP v2 executado como subprocesso externo -> REST FastAPI autenticada -> PostgreSQL grants/tasks -> Mem0 real -> Ollama local -> pgvector. Negativos: Beta negado, agente não autorizado negado, token revogado negado.
- Runs 43107788463 FAILED (fixture com configuração Mem0 herdada), 43108113909 FAILED (colisão de fixture sintética, embora 48 testes tivessem passado), corrigidos.
- Run FINAL 43109095085 — **SUCCESS: 48/48 testes PASS + WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS**.
- **Limites:** dados sintéticos, sem PII, sem auditoria independente de segurança, sem deploy, sem alterações Jarvis ou PULSE, sem aprovação de produção.

### Estado transversal recuperado
- Arquitetura em código: pacote Python rightware_si, SQL migrations, Mem0 submódulo, SDK/MCP adapter, testes e workflows CI. FRONTEND ainda NÃO IMPLEMENTADO.
- Main contém só o README de inicialização (SHA 87c3351055aaf58d37f233dbc96eaa8f0b749c5c). Todo o desenvolvimento está na ancestralidade da branch WORK-02D.
- PRs #1-#6 continuam DRAFT, não mesclados. Nenhum deployment Shared Intelligence no Jarvis.
- Pendências: reposição segura de lease após resposta perdida, identidade de workloads, rate limits/TLS, direitos mínimos PostgreSQL, outbox, consentimento/retention/deletion, benchmark embeddings, staging Jarvis opt-in.

### Evidência e reconstrução
- PRs, Git history e Actions são a fonte de detalhes. Não copiar transcrições privadas para este repositório público.
- Documento retrospectivo: docs/handoffs/BASELINE_WORK00_WORK02D.md.
- **Próximo passo proposto:** consolidar a estrutura do repositório no WORK-03, mantendo a lógica existente e repetindo regressões. Não executar Jarvis staging antes de gate de segurança.

---

## SI-MH-0002 — Política de handoffs e adoção de develop/main
**Registado:** 2026-11-12 · **Classificação:** DECISÃO EXPLÍCITA DO OPERADOR + IMPLEMENTAÇÃO DE DOCUMENTAÇÃO.
**Decisão:** develop é a única branch de desenvolvimento futuro; main recebe apenas releases aprovados. Regra obrigatória de checkpoint em cada entrega técnica: atualizar docs/HANDOFF.md, anexar nova entrada neste MASTER, e preservar o output com commits e evidência.
**Execução factual neste checkpoint:** criado develop a partir do WORK-02D HEAD 6345fb4f6238ecea2d376e82b659238d4684f30f; os outros ramos ainda existem como arquivo histórico, sem limpeza ou merge. Documentação de governança criada em docs/HANDOFF_POLICY.md.
**Validação desta entrada:** a criação de develop foi confirmada no GitHub; CI de develop e proteção de branches ainda devem ser verificados após o commit.
**Próximo passo:** validar HEAD/CI de develop, registar o resultado em nova adenda; só então consolidar a árvore de pastas.

---

## SI-MH-0003 — DEVELOP baseline CI verified
**Registado:** 2026-11-12 · **Classificação:** VALIDADO · **Alteração validada:** commit fb59750191a50c605ef828c1d726f4bad29c811c.
**Contexto:** confirmação da política do MASTER e da branch develop após migração do HEAD WORK-02D, sem mudança na lógica existente.
**Evidência:** [GitHub Actions 43119271001](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43119271001) SUCCESS.
**Resultados observados nos logs:** HANDOFF_POLICY_PASS audited_commits=1; **51/51 testes PASS** (48 anteriores + 3 testes da política); WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS (real MCP subprocess, REST auth, PostgreSQL, Mem0 OSS, Ollama/pgvector e negativas de acesso). Credencial efémera não apareceu em claro nos logs.
**Escopo:** somente provas sintéticas de laboratório; nenhuma alteração ou deployment Jarvis/PULSE, nenhum merge para main. Este novo commit de atualização de evidência altera só os dois documentos de handoff; requer verificação própria do CI, que não deve ser presumida.
**Próximo passo:** WORK-03A reorganizar pastas/packaging sem alterar comportamento; comparar tree e repetir CI. Antes de encerrar as antigas branches, reconciliar os seis PRs e preservar links SHA/CI.

---
---

## SI-MH-0004 — SI-RD-01 investigação técnica comparativa / feedback
**Registado:** 2026-11-12 (Africa/Maputo) · **Classificação:** PESQUISA DOCUMENTAL / HIPÓTESES / RECOMENDAÇÕES · **Branch de base:** develop@521961dd681d55b86cadef823f61243e176b15da.
**Objectivo:** aprender com outras infraestruturas de memória e continuidade de agentes, seus sucessos, issues de produção, resultados e repositórios, antes de ampliar o Shared Intelligence Core.
**Entregável:** [docs/research/SI_RD_01_TECH_LANDSCAPE_2026-11-12.md](research/SI_RD_01_TECH_LANDSCAPE_2026-11-12.md); referências primárias e propostas de comparação mantidas no dossier.
**Achados relevantes:** Mem0: issue histórico de dados ruidosos/realimentação, com soluções da comunidade e um relato de retorno ao Mem0 por usabilidade; issue TS P0 encerrado em Julho 2026; Graphiti: issues de duplicação e embeddings não finitos; Hindsight: resultados reportados e issue de timeout/mitigação; Letta: proposta archival consolidation encerrada; LangGraph/Temporal/A2A já fornecem primitivas de persistência e interoperabilidade, portanto não reinventar sem comparação.
**Hipóteses não aprovadas:** verified operational continuity, memory quality/temporal truth e private enterprise intelligence. Não existe benchmarking novo nem prova comercial neste checkpoint.
**Alterações:** dossier de investigação + actualização dos dois handoffs num commit; sem código, dependencies, DB, migrações, Git branches, PRs, Jarvis ou main alterados.
**Evidência anterior, não reexecutada:** develop@521961dd681d55b86cadef823f61243e176b15da; run 43119637429 SUCCESS, relativo ao núcleo já existente. Nenhum teste ou benchmark executado neste SI-RD-01. CI do commit documental deve ser inspecionado depois, sem antecipar PASS.
**Limites e segurança:** dados sintéticos apenas; não confundir relatos/benchmarks próprios de fornecedores com provas RIGHTWARE; issues podem ter sido corrigidos em versões recentes; actualizações de product-market fit dependem de entrevistas. Nenhum dado sensível publicado.
**Próximo passo:** SI-RD-02 matriz com código/versão/licenças e desenho de benchmark justo; escolher baseline antes de novas funcionalidades. WORK-03A só prossegue respeitando gate de arquitectura e investigação.

## SI-MH-0005 — WORK-03A R0: Consolidar pastas e arquitetura executável
**Data:** 2026-11-12 (Africa/Maputo) · **Classificação:** IMPLEMENTADO; CI DESTE COMMIT PENDENTE · **Base verificada:** develop@`6c257ff70b5ac961b455cc23fb96a6676e575939`.

**Objectivo:** reorganizar a árvore para futuro deployment e continuidade de engenharia sem alterar os 17 blobs existentes de código Python, SQL ou requirements, sem reescrever o núcleo e mantendo somente `develop`/`main` como branches de trabalho.

**Operações executadas na árvore Git:** `rightware_si/**` → `backend/rightware_si/**` (11 blobs), `db/migrations/**` → `database/migrations/**` (3), `requirements-work02*.txt` → `backend/requirements/{core,api,memory}.txt` (3). SHA de blobs de origem/destino conferido: **17/17 idênticos**. `pyproject.toml` ajustado para pacote editável em backend; testes com path atualizado e quatro testes novos de layout. Seis workflows históricos retirados da árvore actual de develop, preservados no Git, e um CI `.github/workflows/ci.yml` consolidado para develop/PR main, com validação de handoffs, build/editable import, PostgreSQL e Mem0/Ollama E2E.

**Artefactos documentais:** README e `docs/ARCHITECTURE.md` actualizados; `backend/README.md`, `database/README.md`, `frontend/README.md` e `infrastructure/README.md` criados. A frontend e deployment continuam NÃO IMPLEMENTADOS. Inventário completo em `docs/work03a/RESTRUCTURE_MANIFEST.md`.

**Conflito concorrente tratado sem perda:** durante preparação, entrou em develop a pesquisa SI-RD-01 no commit `6c257ff70b5ac961b455cc23fb96a6676e575939` com entrada SI-MH-0004. Reconciliado o tree para preservar `docs/research/SI_RD_01_TECH_LANDSCAPE_2026-11-12.md` e a entrada SI-MH-0004. A pesquisa e hipótese de benchmark SI-RD-02 continuam abertas; não as confundimos com validação de produto.

**Evidência ANTES da alteração:** develop@`521961dd681d55b86cadef823f61243e176b15da`, Actions `43119637429`: 51/51 PASS + E2E real PASS. Pesquisa SI-RD-01@`6c257ff`, Actions `43120700147`: SUCCESS (documentação, sem novo benchmark). **Testes da árvore reorganizada NÃO comprovados no instante deste commit; devem ser anotados em nova adenda SI-MH-0006 após CI.**

**Não realizado:** nenhum merge, Jarvis/PULSE alterado, frontend implementado, serviço lançado, fornecedor trocado, modelo textual Qwen testado, branch antiga apagada ou dado privado publicado.

**Riscos:** localização do pacote setuptools, caminhos de migração, testes/imports em CI. **Rollback:** revert do commit por Git (sem force push). **Próxima acção:** CI de develop para novo HEAD; se falhar, corrigir e preservar log. Depois validar gate de arquitectura/benchmarks e staging Jarvis autorizado separadamente.

---

## SI-MH-0006 — WORK-03A R1: CI real validado após reorganização
**Data:** 2026-11-12 (Africa/Maputo) · **Estado:** VALIDADO · **Commit testado:** `54f3664359e884a90902dee3db2c238c26b622a8` · **Ramo:** `develop`.

**Evidência exacta:** GitHub Actions [43121657190](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43121657190), workflow `rightware-shared-intelligence-ci`, conclusão **SUCCESS**. Logs: `HANDOFF_POLICY_PASS audited_commits=1`; `PACKAGE_LAYOUT_PASS backend`; `MIGRATION_PASS` 0001, 0002, 0003 (PostgreSQL16); **55 testes executados, OK**; `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS` (cliente MCP stdio independente -> REST autenticada -> PostgreSQL scoped -> Mem0 OSS real + Ollama embeddings + pgvector). Chave efémera mascarada, não visível em claro no log.

**Comparação com base anterior:** 51 testes anteriores + 4 novos testes de árvore. A migração preservou **17/17 hashes dos blobs** de código/requisitos/SQL. O workflow consolidado instala `backend/requirements/` e o pacote em `backend/rightware_si/`, que foi confirmado por import editável. O CI não utilizou Qwen text generation e não é uma certificação de segurança em produção.

**Histórico preservado:** pesquisa SI-RD-01 do commit `6c257ff70b5ac961b455cc23fb96a6676e575939` (SI-MH-0004); seis Draft PRs históricos continuam disponíveis e `main` inalterada. Frontend e deployment ainda não implementados.

**Riscos e trabalho pendente:** CI cobre somente runtime de laboratório e dados sintéticos; restrições de produção (identidade OIDC/workload, política de retenção/apagamento, rate limits, TLS, backups, outbox e lease recovery). Reconciliar PRs/branches históricos antes de encerrar, sem remover referências sem prova. Avançar com a investigação SI-RD-02 de alternativas/benchmarks e o desenho operacional do deployment de forma autónoma, sem afetar o Jarvis em produção.

**Handoff pós-verificação:** este commit actualiza MASTER e HANDOFF actual; próprio CI deste commit de documentação ainda precisa de verificação separada (não antecipar resultado).

---


---

## SI-MH-0007 — SI-RD-02: Reverse analysis & benchmark contract
**Data:** 2026-11-12 (Africa/Maputo) · **Classificação:** INVESTIGAÇÃO DOCUMENTAL / RECOMENDAÇÃO, NÃO TESTADO como benchmark · **Parent:** `develop@a357e636f3accb73d8214ede7946b4e6e518142d`.

**Objectivo:** implementar a regra RESEARCH FIRST da RIGHTWARE na próxima etapa do Shared Intelligence; estudar código, licenças, decisões de arquitectura e adaptar, sem reinventar Mem0/Hindsight/Graphiti/Letta/LangGraph/Temporal/A2A.
**Ficheiros criados:** `docs/research/SI_RD_02_SOURCE_CODE_MATRIX_2026-11-12.md` (matriz com SHA de sete repos e anchors de código), `docs/research/SI_RD_02_BENCHMARK_CONTRACT.md` (tracks e métricas), `docs/research/fixtures/SI_RD_02_cases_v1.jsonl` (18 oracles sintéticos; validados estruturalmente: 6 memory, 6 continuity, 6 security).
**Achados:** Mem0 ADD-only/hybrid e graph retirado do OSS; Hindsight já tem mecanismos de memory defense, validator e tenant hooks; Graphiti timestamps episódicos/temporal e retrieval híbrida; Letta Code Git-backed memory; LangGraph e Temporal têm persistência/workflows; A2A requer persistência separada para eventos críticos. Critérios de diferenciação **ainda são hipóteses**, não reivindicações comerciais.
**Método de validação desta entrega:** repositórios analisados por API GitHub com SHA explicitado; fixture JSONL montada e validada sintacticamente com JSON.stringify sobre 18 objectos únicos e oracles. **Nenhum LLM, motor externo, pentest, CI novo, benchmark nem deploy executado por SI-RD-02**; testes anteriores do projecto continuam distintos.
**Evidência histórica do núcleo:** WORK-03A CI 43121657190 SUCCESS (55 testes + E2E); este commit documental precisa do seu próprio CI. `develop` apenas; `main` intocada; nenhum novo branch/PR, migration, código, vendor pin, Jarvis/PULSE ou dado privado alterado.
**Decisão oficial:** nenhuma decisão de produto; apenas recomendação de manter Mem0 enquanto se benchmarka baseline PostgreSQL, Hindsight e Graphiti; workflow engines num track independente.
**Riscos e limitações:** não auditadas dependências/transitive licenses; implementação dos vendors não executada; avaliação funcional e dados de mercado NÃO VALIDADA. Próximo gate SI-RD-03: harness isolado de avaliação com os fixtures; validação dos oracles por humano, pin de ambientes, repetição e resultados reprodutíveis; segurança com critério zero falhas críticas. Responsável: coordenação técnica RIGHTWARE.

## SI-MH-0008 — SI-FG-01: Auditoria de lacunas funcionais

**Data:** 2026-11-12 Africa/Maputo · **Estado:** AUDITORIA DOCUMENTAL, RECOMENDAÇÃO (NÃO implementar código) · **Base:** `develop@5787579f3b2b936e049d386488bb9671778bae52`.

**Objetivo:** confrontar a visão original do Shared Intelligence com as funções reais do backend para determinar se WORK-03B deve ser deployment ou fecho funcional. A pedido do operador, desafiar a suposição de que CI verde implica produto completo.

**Resultado:** núcleo PostgreSQL+FastAPI+MCP(read-only)+Mem0/Ollama está comprovado no laboratório (Actions 43122815508 success, 55 testes + E2E). Mas faltam observação e escrita de memória via API autorizada, handoff contextual estruturado/snapshot, recuperação após crash, verificação de evidências e decisão/review a DONE, gestão da memória/retention/erasure, outbox, integrações reais Jarvis/PULSE e frontend. Não confundir demonstração E2E com os 18 critérios MVP originais.

**Ficheiro criado:** `docs/product/SI_FG_01_FUNCTIONAL_GAP_AUDIT_2026-11-12.md` com inventário de código, cobertura conservadora de M01–M18, jornada mínima demonstrável, sequência recomendada, riscos e fontes. Handoff actual actualizado simultaneamente.

**RECOMENDAÇÃO (ainda não aprovada):** alterar próximo passo para WORK-03B R0 Functional Contract Closure → R1 Context/Handoff/Resume vertical slice → R2 Evidência/Decisões/Lifecycle; só depois deployment/operacionalização e staging Jarvis. Continuar SI-RD-03 como investigação e benchmark separado. Não substituir motor sem comparações.

**Não realizado:** nenhum código, DB schema, CI workflow, benchmark, branch, merge, deployment, Jarvis/PULSE, API externa ou testes novos. A execução CI do commit documental fica PENDENTE até ser consultada.

**Próxima ação:** rever/ratificar o escopo funcional e começar os contratos + critérios de aceitação em `develop` com novos checkpoints MASTER/CURRENT. `main` intocada.

---

## SI-MH-0009 — SI-FG-01 CI verified (document-only checkpoint)

**Data:** 2026-11-12 Africa/Maputo · **Tipo:** VALIDADO · **Tested commit:** `12ea7c3b299b5a84b0d1a96d59a4c78401cbe40b` (SI-FG-01 audit + both handoffs).

**Evidência:** [Actions run 43151016529](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43151016529) **SUCCESS**. Logs: HANDOFF_POLICY_PASS audited_commits=1; 55/55 existing tests PASS; real independent MCP/REST/PostgreSQL/Mem0/Ollama synthetic E2E PASS.

**Escopo da validação:** regressão do código previamente testado enquanto foram acrescentados documentos. **Não** é validação de features ausentes, de todos os M01–M18, de benchmark SI-RD-03 ou de Jarvis em produção.

**Avaliação inalterada:** SI-FG-01 identifica lacunas funcionais e recomenda WORK-03B R0 Functional Contract Closure antes de deployment. Não houve alterações a runtime, vendor, DB, main ou Jarvis/PULSE.

**Próxima ação proposta:** definir e ratificar jornada única UC-CORE-01 entre dois agentes (context-write -> checkpoint/handoff -> new-session resume -> evidence -> independent review); delimitar o MVP e especificar esquema/API/testes. Novo commit de documentação desta adenda exige verificação CI própria; não presumir resultado.

---


---

## SI-MH-0010 — SI-RD-02E: Perplexity external report triage
**Data:** 2026-11-12 (Africa/Maputo) · **Classificação:** INVESTIGAÇÃO DOCUMENTAL / FACT-CHECK / RECOMENDAÇÃO · **Base:** `develop@7b719f7411cc7da042faae70c3f5198c4d8a0fc3`.
**Material de entrada:** PDF Perplexity de 11 páginas fornecido pelo operador; identificado pelo próprio fornecedor como SI_RD_02_PARTIAL. O PDF não continha estado de código interno RIGHTWARE nem tinha inspecção robusta dos principais candidatos. Não publicar PDF original no repo público.
**Entrega:** [docs/research/SI_RD_02_EXTERNAL_PERPLEXITY_TRIAGE_2026-11-12.md](research/SI_RD_02_EXTERNAL_PERPLEXITY_TRIAGE_2026-11-12.md): confronto com SI-RD-01, SI-RD-02 e SI-FG-01, validações externas directas, oportunidades de reúso, limites comerciais e sequência de experiências.
**Resultados importantes:** Kuzu arquivado (não escolher como nova dependência activa; avaliar LadybugDB); SoMem paper 2026-11-09 + código MIT relevante para memória documental; DBOS Python activo como benchmark de durabilidade; XTDB MPL-2.0; Restate/Langfuse/Phoenix licença principal não classificada via GitHub, requer revisão. PDF pontuou incorrectamente três oportunidades: #3 4.40→4.35, #6 4.05→4.15, #9 4.10→4.05; ranking proposto não está ordenado. Não afirmar `exactly once` de efeitos externos apenas por receipts.
**Classificação:** NENHUMA NOVA DECISÃO DE PRODUTO; hipóteses/recomendações permanecem não aprovadas. Seguir WORK-03B R0 para contrato `UC-CORE-01` e SI-RD-03 para benchmark isolado, sem trocar Mem0/WorkCore sem evidência.
**Mudanças:** dossier externo + ambos handoffs no mesmo commit, sem alterar código, dependências, migrações, vendor, CI workflow, JARVIS, PULSE ou `main`.
**Verificação:** aritmética recomputada dos scores conforme pesos do PDF, fontes GitHub/arxiv verificadas; não houve execução de benchmarks nem novos testes. Último CI do projecto no parent `develop@7b719f7411cc7da042faae70c3f5198c4d8a0fc3` SUCCESS (run 43151308140). CI do commit documental PENDENTE até observação posterior.
**Próximo passo:** reler CI deste commit, adicionar adenda se necessário; programa SI-RD-03A/B e WORK-03B R0, mantendo dados sintéticos e critérios de segurança.


---

## SI-MH-0011 — WORK-03B R0: Functional Contract Closure
**Data:** 2026-11-12 (Africa/Maputo) · **Classificação:** IMPLEMENTAÇÃO DE ESPECIFICAÇÃO E TESTES ESTÁTICOS / PROPOSTA FUNCIONAL (NÃO HOMOLOGADA) · **Parent:** `develop@4c6f90feccccb30fa7a6aadb83512f18f50dfdac`.
**Objectivo:** fechar ambiguidades da jornada sintética UC-CORE-01 (dois agentes, duas sessões, observação + checkpoint + transferência + resume + evidência + revisão independente) sem construir novas features antes dos contratos.
**Ficheiros:** `docs/work03b/WORK03B_R0_FUNCTIONAL_CONTRACT.md`, `docs/work03b/UC_CORE_01_CONTRACT.json`, `docs/work03b/UC_CORE_01_ACCEPTANCE.md`, `tests/test_work03b_contract.py` + ambos HANDOFFs no mesmo commit.
**Implementado:** contratos de 10 endpoints existentes vs 7 futuros, 14 passos da jornada, matriz M01–M18 sem falsos PASS, papéis e grants propostos, SourceRecord/Observation/AgentRun/ContextSnapshot/Checkpoint/Verification/Review/Outbox, semântica de restart/fail-closed e gates de autoridade.
**Segurança:** M09 ajustado à segurança WORK-02D: claim/accept com lease secreto devolve 409 ao repetir; não reemitir secret/idempotency response. DONE exige autorização independente, não agent claim. Não prometer exatamente uma execução externa fora de reconciliação.
**Verificação local do conteúdo:** JSON serializado de objectos estruturados e invariantes checadas na autoria (M01–M18, 14 passos únicos, 10 rotas live, 7 propostas); cinco novos testes `unittest` estáticos aguardam execução de CI; não representam cobertura funcional R1/R2.
**Evidência preexistente:** GitHub Actions 43152798777 `SUCCESS` na base `4c6f90feccccb30fa7a6aadb83512f18f50dfdac` (55 testes + E2E sintético real); este novo commit CI PENDENTE até observar logs, contagem esperada 60 testes se 5 novos rodarem.
**Não realizado:** nenhuma migração, API/authorization runtime, provider/LLM, benchmark SI-RD-03, produção, Jarvis/PULSE, main, merge ou branch nova. Direitos e entidades propostos ainda exigem ratificação do operador antes de R1.
**Próximo passo:** confirmar CI do presente HEAD; corrigir se falhar, criar checkpoint; aprovar UC-CORE-01/R0 e implementar WORK-03B R1 mínimo sem quebrar a política de segredo/lease e com teste de processo independente.


---

## SI-MH-0012 — WORK-03B R0 GitHub CI verified
**Data:** 2026-11-12 Africa/Maputo · **Classificação:** VERIFICADO · **Commit testado:** `c32ab1e7f4b72a27da6c005d04e6825bed62f76e` · **Ramo:** `develop`.
**Evidência factual:** [Actions 43154026213](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43154026213) `SUCCESS`, job 130969666674. Logs: `HANDOFF_POLICY_PASS`; `PACKAGE_LAYOUT_PASS`; três `MIGRATION_PASS`; **60 testes OK (55 anteriores + cinco testes estáticos do contrato WORK-03B)**; `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS` (synthetic only, MCP real + REST auth + PostgreSQL + Mem0 OSS + Ollama embeddings + negativas).
**Entrega desta adenda:** [docs/work03b/EVIDENCE_R0.md](work03b/EVIDENCE_R0.md) com marcadores exactos e limitações; actualização simultânea de CURRENT+MASTER. **Sem alterações a runtime/DB/frontend/vendor/main/Jarvis/PULSE**.
**Interpretação:** contrato R0 documentalmente consistente e regressão do núcleo existente aprovada. Não prova novas operações de observação, checkpoint, resume independente, verifier, DONE, ciclo de vida ou benchmark. Ratificação de schema/roles ainda necessária.
**Próximo passo:** WORK-03B R1 implementação limitada da jornada, depois de ratificar contrato e garantir matriz de autorização; SI-RD-03 benchmark isolado prossegue como investigação. O CI deste novo checkpoint documental será PENDENTE até consulta.

## SI-MH-0013 — WORK-03B R0B: Arquitectura do princípio de funcionamento do produto

**Data:** 2026-11-12 (Africa/Maputo) · **Classificação:** ARQUITECTURA FUNCIONAL / RECOMENDAÇÕES, **NÃO IMPLEMENTAÇÃO** · **Base:** `develop@ac9bcc813b75c6dfe3fb820c72a4316f4b5dd53b`.

**Objectivo:** traduzir a visão RIGHTWARE em funcionamento end-to-end: agente A autenticado cria observação e checkpoint com fontes; handoff com lease/version; agente B em novo processo recebe continuação autorizada sem chat original; verificador confirma checks delimitados; revisor aprova apenas após critérios. O Mem0 é projecção semântica e pode estar indisponível sem tornar estado canónico falso.

**Investigação reutilizada:** SI-RD-01 landscape; SI-RD-02 source code/license; SI-RD-02E Perplexity externa com correcções; SI-FG-01 lacunas; WORK-01 domínio; A2A task/message/artifact, Temporal retries/idempotência, W3C PROV e MCP Authorization. Os relatórios de fornecedor não equivalem a benchmark RIGHTWARE ou decisão oficial.

**Documentos criados:** `docs/product/work03b/README.md`; `00_PRODUCT_OPERATING_PRINCIPLE.md`; `01_COMPONENT_DOMAINS_BOUNDARIES.md`; `02_DOMAIN_PROTOCOL_SECURITY_CONTRACTS.md`; `03_UC_CORE_01_ACCEPTANCE_AND_EXECUTION.md`; `04_RESEARCH_TO_ARCHITECTURE_DECISIONS.md`; `05_CANONICAL_CONTRACT_ALIGNMENT.md`. Referência adicionada ao `docs/ARCHITECTURE.md`.

**Reconciliado com trabalho concorrente:** `docs/work03b/UC_CORE_01_CONTRACT.json`, `WORK03B_R0_FUNCTIONAL_CONTRACT.md`, `UC_CORE_01_ACCEPTANCE.md` e `tests/test_work03b_contract.py` mantêm-se **contrato canónico R0 DRAFT**: 10 rotas existentes, 7 futuras, 14 passos e M01–M18. Os 20 passos UX e endpoints adicionais do blueprint são **horizonte conceptual, não outra API aprovada**. Um Observation não tem necessariamente de aumentar task.version; seguir o contrato canónico. M09 lease secret replay retorna 409 conforme WORK-02D.

**Evidência anterior:** run [43154026213](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43154026213) SUCCESS no commit `c32ab1e7f4b72a27da6c005d04e6825bed62f76e`: 60 testes e E2E sintético Mem0/MCP PASS, cinco testes novos apenas de contrato estático. A documentação do SI-MH-0012 foi preservada. **A criação deste blueprint não adiciona novas funcionalidades nem novos testes executados. CI deste commit PENDENTE.**

**Não alterado:** backend, SQL, vendor Mem0 pin, Jarvis/PULSE, frontend executável, deployments, `main`, branches antigas/PRs. Sem dados privados ou segredos no repo público.

**Status decisão:** propostas de ownership PULSE, RBAC, source/consent, lease recovery, verificação humana e expansão MCP requerem ratificação antes de R1; não transformar visão em aprovação automática.

**Próximo gate recomendado:** ratificar o contrato UC-CORE-01 e executar R1A mínimo (AgentRun + SourceRecord + Observation, ACL/CAS e testes) seguido de checkpoint/resume em nova sessão; SI-RD-03 benchmark permanece independente. Guardar handoffs a cada checkpoint.

---

## SI-MH-0014 — WORK-03B R0B: CI do blueprint validado

**Data:** 2026-11-12 Africa/Maputo · **Classificação:** VALIDADO (REGRESSÃO), **NÃO** ACEITAÇÃO FUNCIONAL DE UC-CORE-01 · **Tested SHA:** `387d489b26a1363ec017b9b8eadb3b572008aa2d` em `develop`.

**Evidência:** [Actions run 43154792920](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43154792920) **SUCCESS**; job `real-mcp-mem0`. Logs observados: `HANDOFF_POLICY_PASS audited_commits=1`, três `MIGRATION_PASS`, **60 tests, OK**, e `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS` com MCP stdio em processo separado, REST auth, PostgreSQL, Mem0 OSS+Ollama local embeddings, negative scopes e revogação. Key efémera mascarada.

**Verificação de escopo:** diff do commit `387d489b26a1363ec017b9b8eadb3b572008aa2d` contém exclusivamente os 7 documentos `docs/product/work03b/`, `docs/ARCHITECTURE.md` e ambos handoffs. Nenhum código, migração, API, fornecedor, modelo ou deploy mudado; `main` e Jarvis/PULSE não alterados.

**Interpretação correcta:** 60 testes existentes incluindo cinco estáticos do contrato R0; sucesso de regressão no laboratório. Não demonstra Observations, checkpoint, `resume` entre dois agentes com handoff de conteúdo, evidence verifier, DONE review, memory lifecycle, benchmarking comparativo, Jarvis staging ou produção. Esses itens continuam a executar em R1/R2 após ratificação.

**Próximo passo:** revisão de arquitectura e ratificação do contrato canónico `docs/work03b/UC_CORE_01_CONTRACT.json`, respeitando harmonização `docs/product/work03b/05_CANONICAL_CONTRACT_ALIGNMENT.md`. Se autorizado, implementar o **primeiro vertical R1A** (AgentRun + SourceRecord + Observation com ACL, provenance, eventos e testes reais) em `develop`, antes de checkpoint/resume. O CI de documentação desta adenda está pendente até observação.

---

## SI-MH-0015 — WORK-03B R1A: Operational Continuity Foundation implementation

**Data:** 2026-11-12 Africa/Maputo · **Tipo:** IMPLEMENTADO no Git / CI AINDA PENDENTE · **Base de trabalho:** `develop@ad1bc5dcf604bf3fed58846a5fed29ca8fa39917` (Actions 43155153394 SUCCESS, 60/60 testes + E2E sintético real).

**Autorização/âmbito:** após definição da visão e pedido explícito de avançar para R1A, executar somente infraestrutura funcional de AgentRun, SourceRecord e ASSERTED Observation em laboratório. Mantidas as decisões oficiais: trabalhar só em `develop`, `main` para release aprovado, dois handoffs por output, Jarvis e PULSE de produção intactos.

**Implementação:**
- `database/migrations/0004_work03b_r1a_continuity.sql`: si_agent_runs com actor/correlation/task_version, si_source_records revisionados com FK do mesmo task/run, si_observations ASSERTED, si_observation_sources FK composta para impedir cross-task, si_continuity_events separado de si_events(task_id,task_version). Nenhum índice Mem0 ou migração de dados privados.
- `backend/rightware_si/continuity.py`: operações transacionais autenticadas pelo gateway, autorização por grant, task-lock/expected_version, lease vigente, idempotência, fonte segura (GitHub HTTPS ou urn:rw: de receipt), source-linked assertion, leitura restrita a task:read+context:read; conteúdo não verificado e sem incremento de task.version.
- `backend/rightware_si/http_api.py`: 4 operações REST — start_run, register_source, record_observation, list_task_observations. Identidade efetiva do bearer, não de campos do request.
- `.github/workflows/ci.yml`: aplica migração 0004 antes dos testes; `tests/test_work03b_r1a.py` acrescenta 8 testes reais PostgreSQL/TestClient de autorização, proveniência, grants, isolamento, no-stale-lease, handoff, idempotência, falhas e revogação.
- Atualizados `tests/test_repository_layout.py`, teste estático canónico `tests/test_work03b_contract.py` (+1 teste), contrato machine-readable `docs/work03b/UC_CORE_01_CONTRACT.json` (14 routes live / 6 future), matriz M02 LAB_PARTIAL, documentação da arquitectura e `docs/work03b/R1A_IMPLEMENTATION.md`. Os 18 critérios M01–M18 continuam PENDING_FULL_E2E.

**Fonte de prova anterior:** Actions 43155153394 SUCCESS na base. **R1A pós-commit NÃO foi executado ao registar esta entrada**. O total esperado é cerca de 69 testes (60 baseline +8 novos de integração +1 novo teste do contrato); somente logs da nova run podem confirmar.

**Limites / riscos expressos:** nenhuma API de checkpoint/resume, outbox/MemoryWrite, source-level ACL/consent, verificador, DONE reviewer ou Jarvis staging. Source URIs são meros pointers e não prova; `run` não tem heartbeats nem close-on-handoff. Retenção/PII e OAuth/OIDC não implementados. Não executar dados reais no CI ou em serviço exposto. Falha CI deve criar adenda e fix em `develop` sem apagar entradas antigas.

**Próxima ação:** inspecionar execução GitHub Actions para o commit R1A; reportar PASS/FAIL com evidências em nova entrada; depois WORK-03B R1B (checkpoint versionado + resume canónico sob ACL), sem alterar o Jarvis.

---
## SI-MH-0016 — WORK-03B R1A CI verified
**Data:** 2026-11-12 Africa/Maputo · **Estado:** VALIDADO EM LABORATÓRIO, NÃO PRODUÇÃO · **Tested SHA:** `538eb1b67628e8a0905b6511da9fddf9f0d1313c`.

**Evidência:** [Actions 43157921966](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43157921966) **SUCCESS**. Logs observados: HANDOFF_POLICY_PASS, MIGRATION_PASS SQL 0001/0002/0003/0004, **69 testes OK** (60 anteriores + 8 R1A reais + 1 teste estático de contrato), e WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS (MCP stdio/REST/PostgreSQL/Mem0/Ollama/pgvector reais com dados sintéticos e casos negativos). Nenhum segredo interno efémero em claro foi observado no log.

**Resultado R1A:** AgentRun, SourceRecord e Observations ASSERTED com task lease ativa, grants por project, identidade do bearer, idempotência e isolamento por task; SQL com FK composta, evento de continuidade independente e claim sem autopromoção a DONE. O commit manteve o Mem0 e MCP read-only existentes. A evidência detalhada está em `docs/work03b/R1A_EVIDENCE.md`.

**Não implica:** UC-CORE-01 completo, checkpoints, nova sessão resume, verified evidence, reviewer DONE, governança de memória, privacy consent, comparação de providers, Jarvis staging, deployment ou certificação empresarial. M02 R1A_LAB_PARTIAL, M01–M18 PENDING_FULL_E2E.

**Escopo desta adenda:** anexar resultado realmente observado ao MASTER e HANDOFF atual; não modificar runtime/DB/CI/vendor ou main. O próprio commit documental terá novo CI, cujo resultado não foi antecipado.

**Próxima ação:** WORK-03B R1B — checkpoint versionado e recuperação de contexto canónico após interrupção em novo processo, sempre com ACL revalidada, Mem0 down fallback e sem expor segredo de lease.

---
## SI-MH-0017 — WORK-03B R1B: Checkpoint & Resume Engine (implementation)

**Data:** 2026-11-12 Africa/Maputo · **Classificação:** IMPLEMENTADO NO GIT; CI **PENDENTE** no momento do commit · **Base:** `develop@9080bbe1d73b91fe752159354000e39e20eb2234`. CI anterior: [43158313613](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43158313613) SUCCESS (69/69 + real MCP/Mem0/Ollama E2E, dados sintéticos).

**Objetivo:** permitir checkpoint versionado, imutável e recuperável para continuação de tarefa por outro agente em sessão separada, sem depender de conversa original nem de Mem0. O handoff continua a ser um mecanismo de lease independente; binding a um checkpoint ainda não implementado (R1C).

**Implementação deste checkpoint:**
- `database/migrations/0005_work03b_r1b_checkpoints.sql`: tabela de checkpoints com sequência por tarefa, referência ao AgentRun, resumo/ações/bloqueios JSONB, trust=ASSERTED, observações cross-task proibidas por composite FK e triggers PostgreSQL de imutabilidade UPDATE/DELETE; estende event_type de continuidade para CHECKPOINT_RECORDED.
- `backend/rightware_si/continuity.py`: `record_checkpoint` transacional e CAS `expected_checkpoint_seq` sob lock de task, lease atual, task version, run ownership e grants `checkpoint:write` + `task:execute` + `context:read`; `resume_task` com snapshot PostgreSQL REPEATABLE READ READ ONLY, reautorização `task:read` + `context:read`, latest checkpoint/refs/handoff, nenhuma nova lease, no verified/DONE, sem chamada Mem0.
- `backend/rightware_si/http_api.py`: POST `/v1/projects/{project_id}/tasks/{task_id}/checkpoints`, GET `.../resume`; modelos estritos Pydantic. `backend/rightware_si/mcp_bridge.py`: somente nova ferramenta read-only `resume_task` via REST autenticada (nenhuma tool de escrita).
- `tests/test_work03b_r1b.py`: 9 cenários PostgreSQL/TestClient reais; `tests/test_work03b_r1b_mcp.py`: 2 cenários do SDK MCP. `scripts/work03b_r1b_real_resume_e2e.py`: teste isolado com processos A/B separados; B recebe apenas token seu e handoff ID, nunca chat/lease/DB creds de A, consulta API real sem Mem0/Ollama ativo; teste de revogação e intruder.
- Workflow CI migra SQL 0005, executa 81 testes esperados (69 anteriores +9+2+1 gate de contrato), novo E2E sem Mem0 antes do E2E existente Mem0/Ollama. Resultado CI fica pendente até logs.
- Contrato canónico `docs/work03b/UC_CORE_01_CONTRACT.json`: **16 REST routes implementadas / 4 propostas**; S05/S09 apenas R1B_LAB_PARTIAL, M05/M12/M16/M17 parciais. M01–M18 continuam PENDING_FULL_E2E. Teste AST e matriz de aceitação atualizados.
- README do repo/backend/database, `docs/ARCHITECTURE.md`, `docs/work03b/WORK03B_R0_FUNCTIONAL_CONTRACT.md` e novo `docs/work03b/R1B_IMPLEMENTATION.md` documentam o escopo.

**O que NÃO foi feito:** não foi modificado `main`, Jarvis/PULSE de produção, vendor Mem0, deploy ou serviços pagos. Não há checkpoint binding no handoff (R1C), recuperação de lease perdido, outbox/ingestão Mem0 das observações, consent/PII/retention, evidência verificada por terceiro, aprovação DONE, UI ou preparação enterprise.

**Riscos e política:** checkpoint e next_actions são dados de agente não confiáveis, nunca instruções a executar; nenhuma fonte externa é verificada por registrar um URL. A trigger de imutabilidade não substitui privilégios mínimos da role DB e backups. Mem0 disabled não permite reivindicar memória semântica válida.

**Próxima ação exata:** analisar o CI do novo SHA; se falhar, corrigir em `develop` e registar o FAILED em adenda. Se passar, acrescentar SI-MH-0018 com resultados concretos e atualizar HANDOFF. Depois iniciar WORK-03B R1C, com handoff atomicamente vinculado ao checkpoint, fencing e recovery da lease sob autorização.

---

## SI-MH-0018 — WORK-03B R1B CI e continuação multi-processo validados

**Data:** 2026-11-12 Africa/Maputo · **Estado:** VALIDADO EM LABORATÓRIO · **SHA testado:** `5c98e9f42a481709762550d9d451cb64f7d65b31`.

**Evidência:** [Actions run 43160672177](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43160672177) **SUCCESS**. Logs: HANDOFF_POLICY_PASS, 0001–0005 MIGRATION_PASS, **81/81 testes PASS**, `WORK03B_R1B_RESUME_E2E_PASS` com A terminado/B novo processo, REST autenticada, checkpoint PostgreSQL, Mem0 desligado, lease antigo negado, intruso negado e revogação de grant efectiva; `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS` com Mem0 OSS/Ollama/pgvector real. Nenhum segredo efémero em claro observado.

**Entrega técnica:** checkpoint sequencial imutável, CAS, ligação a Observations e leitura resume transacional/autorizada. MCP read-only encaminha pela mesma REST API. O segundo processo recuperou informação canónica sem a conversa de A. `memory_status=NOT_QUERIED`, `checkpoint_binding=NOT_IMPLEMENTED_R1B`, `verified_completion=false` para impedir falsas garantias.

**Detalhes e limitações:** `docs/work03b/R1B_EVIDENCE.md`. Handoff ainda não está vinculado atomicamente a checkpoint; não há recuperação segura de lease, outbox/memória consentida, verificador independente, revisão DONE, UI nem produção. UC-CORE-01 e M01–M18 continuam incompletos.

**Integridade:** este commit de evidências só modifica `docs/` e ambos os handoffs; `main`, Jarvis/PULSE e submódulo Mem0 inalterados. O seu CI deve ser verificado separadamente.

**Próximo passo:** WORK-03B R1C — binding do handoff à versão do checkpoint, fencing e recuperação segura sob autoridade, com testes de restart e negativos.

---


---

## SI-MH-0019 — SI-RD-03C — Evidence verification external research intake
**Data:** 2026-11-12 Africa/Maputo · **Classificação:** INVESTIGAÇÃO INDEPENDENTE / RECOMENDAÇÃO, SEM DECISÃO DE PRODUTO OU EXECUÇÃO DE TESTES DE VERIFICADOR · **Base real:** `develop@ea7cd5f6d9c01a3298ed204fd5b25cbfe8de18f0`.

**Objetivo:** arquivar na branch de desenvolvimento o dossier previamente criado fora do GitHub enquanto outra sessão implementa WORK-03B R1B/R1C. Disponibilizar ao próximo implementador R2 a engenharia reversa de in-toto, Test Result Predicate, SLSA, GitHub attestations, Sigstore, W3C PROV, OpenTelemetry GenAI e OPA, sem copiar código de fornecedores nem introduzir dependências.
**Ficheiros entregues:** [docs/research/SI_RD_03C_EVIDENCE_RESEARCH_2026-11-12.md](../research/SI_RD_03C_EVIDENCE_RESEARCH_2026-11-12.md) e [docs/research/fixtures/SI_RD_03C_EVIDENCE_CASES_v1.jsonl](../research/fixtures/SI_RD_03C_EVIDENCE_CASES_v1.jsonl); 16 casos JSONL (`EV-01..EV-16`) com IDs únicos, todos `synthetic=true` e `executed=false`.
**Recomendação, ainda não aprovada:** R2 separar `ASSERTED -> SOURCE_RESOLVED -> CHECKED_* -> REVIEW_ACCEPTED/REJECTED`; verificadores independentes read-only, matching exacto de repositório/commit/workflow/run attempt, autorização de reviewer distinta do executor; manter `IN_REVIEW` até prova e aceitação efectiva. `exactly-once` externo não decorre de CI verde nem recibos.
**Verificações feitas:** leitura integral dos 2 ficheiros, validação JSON estrutural/IDs/campos sintéticos; o restante dossier é investigação documental, não execução de 16 cenários contra backend/fornecedor. O CI existente da branch `develop@ea7cd5f6d9c01a3298ed204fd5b25cbfe8de18f0` é SUCCESS (run 43161267399), mas testa outro âmbito; o CI deste commit novo fica PENDENTE.
**Isolamento de trabalho:** somente dois documentos de investigação + `docs/HANDOFF.md` e `docs/HANDOFF_MASTER.md`. Nada em backend, DB/migrations, tests, workflows, Mem0, main, Jarvis/PULSE, R1C ou PRs antigos. Não implementar R2 automaticamente nem alterar o contrato canónico antes do gate de design.
**Próximo passo:** depois de estabilizar R1C, a outra sessão deverá ler o dossier/fixture, rever os oracles com fonte e dono de política, confrontar com `docs/work03b/UC_CORE_01_CONTRACT.json` e preparar R2 design/validação, com novo checkpoint de handoff quando houver alterações.

## SI-MH-0020 — SI-RD-03C → R2: referência integrada, 16 oráculos classificados e R1C preservado

**Data:** 2026-11-12 Africa/Maputo · **Classificação:** REVISÃO DE INVESTIGAÇÃO / RECOMENDAÇÃO; NÃO IMPLEMENTAÇÃO R2. **HEAD lido e preservado:** `develop@9233f8afefa5877e2eec27a5f90ca0a4a00322ad` (SI-MH-0019), `main@87c3351055aaf58d37f233dbc96eaa8f0b749c5c`; `vendor/mem0@f1791daa86d469249c9b002f62644d58a1eb96a0`.

**Consulta prévia:** `docs/HANDOFF.md`, última entrada SI-MH-0019 de `docs/HANDOFF_MASTER.md`, contrato canónico `docs/work03b/UC_CORE_01_CONTRACT.json`, código do WorkCore (submit_result/offer_handoff/accept_handoff) e CI [43161674536](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43161674536). **CI do SHA base SUCCESS:** HANDOFF_POLICY_PASS, migrações 0001–0005, 81/81 testes PASS, E2E R1B A→B em processos separados (sem Mem0), E2E anterior Mem0/MCP/Ollama PASS. A suíte não executa oráculos EV-01..EV-16.

**Fontes R2 incorporadas por referência, sem modificação:** `docs/research/SI_RD_03C_EVIDENCE_RESEARCH_2026-11-12.md` e `docs/research/fixtures/SI_RD_03C_EVIDENCE_CASES_v1.jsonl`. Lidos e analisados. Verificação estática de ingestão: **16 objectos JSONL**, IDs EV-01..EV-16 únicos e sequenciais, campos presentes, `synthetic=true` e `executed=false` em todos. Isto NÃO é execução de verificador, benchmark, teste de segurança ou gate de produto.

**Novo artefacto:** `docs/work03b/R2_SI_RD_03C_INTEGRATION_REVIEW.md` — matriz completa dos 16 casos com oráculo/UC-CORE-01/risco, CROSSWALK para recursos RIGHTWARE já construídos, decisão REUSE/BUILD/DEFER para in-toto, SLSA, Sigstore, GitHub Attestations, W3C PROV, OpenTelemetry/OPA e gates futuros R2-00..R2-05. Referências oficiais de standards consultadas para nuances: in-toto v1.2 (Test Result v0.1 independente), SLSA versões e OTel conteúdo sensível.

**Separação de confiança mandatória:** `ASSERTED` continua claim do agente; `CHECKED_PASS/FAIL/INCONCLUSIVE` é resultado futuro de verificador separado e limitado ao teste exacto; `REVIEW_ACCEPTED/REJECTED` pertence a actor/política com `task:review`, sujeito a CAS/ACL. Nem URL, screenshot, assinatura, CI verde ou memória semântica promovem automaticamente a DONE. Não existe ainda endpoint/verificador/revisor R2 implementado. M07/M13/M14/M15 e UC-CORE-01 final continuam pendentes.

**Implementação e isolamento:** documentação apenas; não alterar código, migrations, requirements, testes, workflow, contratos canónicos, GitHub fixture, runtime, `main`, JARVIS/PULSE, Mem0 ou branches. Não instalar in-toto/Cosign/OPA/OTel agora. `develop` recebe único commit fast-forward com ambos handoffs. Resultado da CI do novo commit será verificado separadamente; até lá PENDENTE.

**Próximo passo:** **WORK-03B R1C continua prioritário**: handoff atomicamente vinculado ao checkpoint, lease fencing e recuperação segura; só depois ratificar contratos de R2 e transformar EV-01..EV-16 em execução com evidência real. Não marcar nenhum dos 16 PASS sem implementação e logs.

---

## SI-MH-0021 — CI da integração SI-RD-03C comprovado

**Data:** 2026-11-12 Africa/Maputo · **Classificação:** CI VALIDADO PARA DOCUMENTAÇÃO/REGRESSÃO; **NÃO VERIFICADOR R2** · **SHA realmente testado:** `2db9cd40e1701639434dc0c00cca8cf5282adead` em `develop`.

**Evidência GitHub Actions:** [run 43182746837](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43182746837) **SUCCESS**. Logs observados: `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`, 0001–0005 migrations, `Ran 81 tests` / `OK`, `WORK03B_R1B_RESUME_E2E_PASS` (A termina, B novo processo, PostgreSQL canónico, Mem0 offline, denies para stale lease/intruso/revogação), `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS` (MCP/REST/Postgres/Mem0 OSS/Ollama real). Nenhum segredo efémero em claro observado nos logs. Nenhum teste EV-01..EV-16 foi invocado pelo CI.

**O que este resultado prova:** a integração documental do dossier/fixture SI-RD-03C, `docs/work03b/R2_SI_RD_03C_INTEGRATION_REVIEW.md`, os dois handoffs e as regressões anteriores não quebraram o código R1B. **Não demonstra** verificador de evidências, 16 casos PASS, review/DONE, assinatura in-toto, Sigstore ou attestation; são apenas oráculos de investigação com `executed=false`.

**Escopo da adenda:** este commit actualiza **somente** `docs/HANDOFF_MASTER.md` (append-only) e `docs/HANDOFF.md`. Nenhum código, contrato canónico, CI, SQL, pacote, dependência, fixture, submódulo Mem0, branch `main` ou JARVIS/PULSE alterados. Novo commit documental necessita validação do seu próprio CI.

**Próxima ação:** **WORK-03B R1C** continua prioridade: checkpoint-bound handoff, fencing e lease recovery; R2 só após gates e ratificação do contrato/verificador.

---

## SI-MH-0022 — WORK-03B R1C: checkpoint-bound Handoff e lease fencing implementados

**Data:** 2026-11-12 Africa/Maputo · **Estado:** IMPLEMENTADO NO GITHUB / **CI PENDENTE** ao preparar este commit · **HEAD base verificado:** `develop@5fa303487fb4df92d5938c1c84ae2384fd3f882e`; `main@87c3351055aaf58d37f233dbc96eaa8f0b749c5c`. [CI base 43183197724](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43183197724) SUCCESS (81/81 testes + R1B A/B e Mem0 real E2E).

**Objetivo e autorização:** concluir R1C, antes do R2, sem alterações à produção JARVIS/PULSE, `main`, vendor Mem0 ou branched work. Reutilizar WorkCore/R1A/B, PostgreSQL e REST, sem novas dependências.

**Implementação:**
- `database/migrations/0006_work03b_r1c_handoff_fencing.sql`: `si_handoffs` agora pode vincular exatamente `checkpoint_id,seq,task_version` sob FK do mesmo task e trigger de integridade/imutabilidade. `si_lease_fences` persiste geração monótona mesmo após eliminação da lease activa. `LEASE_REKEYED` entra nos eventos auditáveis, sem credenciais.
- `backend/rightware_si/core/postgres.py`: `offer_handoff` exige ID+seq do checkpoint mais recente e criado pelo writer se existirem checkpoints, compara versão e grants do destinatário antes da transição atómica. Handoff de tarefas sem checkpoint continua **LEGACY_UNBOUND**, identificado explicitamente. `accept_handoff` verifica novamente grants/ligação/versão e emite uma única lease com geração monotónica.
- Recuperação: `get_lease_state` oferece só generation/expiry ao holder autenticado com `task:recover/task:execute/task:read`; `recover_lease` reemite credencial one-time *somente ao próprio holder* com expected_version e expected_generation, até após expiração. Token bruto não persiste na idempotency/audit, replay 409, geração sempre incrementada. Não existe takeover automático de outro principal.
- `backend/rightware_si/http_api.py`: GET `.../lease-status` e POST `.../lease-recovery` sem aceitar principal_id do corpo, e extensão aditiva ao POST .../handoffs com checkpoint fields. `backend/rightware_si/continuity.py` devolve `last_handoff` e `handoff_checkpoint` explícitos, mesmo após B criar checkpoint mais recente; mantém `ASSERTED` e leitura apenas.
- Testes: novo `tests/test_work03b_r1c.py` (12 PostgreSQL/TestClient reais + concorrência), actualiza `tests/test_work03b_r1b.py` e `scripts/work03b_r1b_real_resume_e2e.py` (processos independentes A/B com binding real, B lost response e rekey sem Mem0); +1 teste estático em `tests/test_work03b_contract.py`. CI executa SQL 0006; **94 testes esperados** (81+12+1), A→B E2E e regressão real Mem0/Ollama. **Não foram declarados PASS antes da run nova**.
- Contrato `docs/work03b/UC_CORE_01_CONTRACT.json` passa a 18 rotas implementadas em laboratório / 3 rotas futuras (R2), mantendo M01–M18 `PENDING_FULL_E2E`, `M09 SPEC_CONFLICT` e prioridade R1C. Actualizadas matriz, tests/layout, README, documentação de arquitectura e `docs/work03b/R1C_IMPLEMENTATION.md`.

**Limites e riscos:** mono geração só dentro do Core; efeitos externos requerem idempotência e reconciliação. `task:recover` é altamente privilegiado; bearer comprometido pode usá-la: requer OIDC, rate-limit e step-up antes de produção. Handoffs LEGACY_UNBOUND (tarefa sem cp) ainda permitidos por compatibilidade. Não há takeover quando holder perdeu conta, source-level grants/consent, memory outbox, evidence verifier, review DONE, UI nem deployment. SI-RD-03C e 16 EV oráculos permanecem apenas investigação não executada.

**Integridade:** este commit é um fast-forward em `develop` com ficheiros de código/testes/docs e os dois handoffs actualizados; `main`, JARVIS/PULSE, `vendor/mem0` inalterados. Se CI falhar, acrescentar nova entrada MASTER com falha, corrigir sem reescrever entradas anteriores.

**Próxima acção:** consultar CI do novo SHA; validar 0006, 94 testes e E2E R1C; se tudo passar, adicionar evidência SI-MH-0023. Só então rever segurança R1C e abrir o desenho/ratificação R2 — não executar automaticamente EV-01..EV-16.

---

## SI-MH-0023 — WORK-03B R1C validado: 94 testes, binding e fencing E2E

**Data:** 2026-11-12 Africa/Maputo · **Estado:** VALIDADO EM LABORATÓRIO (não production-ready) · **SHA testado:** `0eb985a02d34a55db2cafe721978bd96abbbeac2`.

**Evidência:** [Actions 43196082372](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43196082372) **SUCCESS**. Logs: HANDOFF_POLICY_PASS; migrações 0001–0006, incluindo `MIGRATION_PASS 0006_work03b_r1c_handoff_fencing.sql`; **`Ran 94 tests`, `OK`**. `WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS` confirma B noutra sessão, vinculação exacta, geração crescente, recuperação one-time de token após perda de resposta, replay 409 com Mem0 desligado; R1B E2E e real MCP/REST/Postgres/Mem0/Ollama PASS. Sem chave efémera em claro nos logs observados.

**Resumo do produto validado:** checkpoint ligado ao handoff de tarefas com checkpoint; PostgreSQL FK/trigger e task CAS, lease fence persistente, holder-only `task:recover` com status nonsecret e rotação de credencial não recuperável da idempotency; reautorização B e resume que distingue estado corrente e checkpoint histórico do handoff. Testes negativos cobrem grants, cross-task, stale, concorrência e expiração. Contrato 18 rotas laboratório / 3 futuras, M01–M18 ainda PENDING_FULL_E2E.

**Registo de evidências:** `docs/work03b/R1C_EVIDENCE.md` (SHA, run, log markers e limitações), ambos handoffs actualizados no presente commit documental.

**Limites expressos:** `LEGACY_UNBOUND` continua permitido para tarefas sem cp; recovery apenas do próprio holder com grant privilegiado, nunca takeover de outro actor; fencing externo/idempotência de ferramentas, consent/PII, R2 verification/review e produção pendentes. CI verde não converte `ASSERTED` em `CHECKED_PASS` nem DONE. Os 16 EV-01..EV-16 do SI-RD-03C continuam não executados e sem implementador R2.

**Próxima decisão:** ratificar o encerramento da compatibilidade LEGACY_UNBOUND, políticas de recovery/step-up e boundary de efeitos externos; depois começar R2 design/contrato com o dossier SI-RD-03C (sem instalar dependências ou implementar verifier por impulso). Este commit de documentação requer sua própria confirmação CI.

---

## SI-MH-0024 — R1C security policy gate and R2 R0 trust contract authored

**Data:** 2026-11-12 Africa/Maputo · **Estado:** DESIGN / RECOMENDAÇÃO NÃO RATIFICADA, CONTRATO R2 R0 APENAS. **HEAD verificado antes das alterações:** `develop@30986f53ab2b0459f4ea9eb8a5f7874d5dbcbfc4`, `main@87c3351055aaf58d37f233dbc96eaa8f0b749c5c`, Mem0 pinned `f1791daa86d469249c9b002f62644d58a1eb96a0`.

**Evidência da base:** [GitHub Actions 43196692278](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43196692278) SUCCESS no HEAD `30986f53ab2b0459f4ea9eb8a5f7874d5dbcbfc4`; migrações 0001–0006, **94/94 testes PASS**, handoff-bound R1C E2E entre subprocessos com perda/rekey de lease e Mem0 desligado, e regressão real MCP/REST/Postgres/Mem0 OSS/Ollama PASS. Isto não é prova de R2, external side effects, OIDC ou produção.

**Análise do código existente:** `WorkCore.offer_handoff/accept_handoff` exigem checkpoint mais recente quando a tarefa tem checkpoint, mas o modo LEGACY_UNBOUND permite tarefas sem checkpoint; `recover_lease` é holder-only com `task:recover`, não transferência para titular ausente; `si_lease_fences` garante gerações de leases no PostgreSQL, mas não idempotência/provas de efeitos externos. Os 16 oráculos SI-RD-03C são `synthetic=true` e `executed=false` (confirmado novamente), com três rotas futuras no contrato UC-CORE-01.

**Artefactos deste output:**
- `docs/work03b/R1C_SECURITY_POLICY_GATE_R0.md`: decisões **SEC-R1C-01** (descontinuação controlada de LEGACY_UNBOUND), **SEC-R1C-02** (ausência do titular, não permitir takeover automático), **SEC-R1C-03** (outbox/receipts/reconciliação para ações externas), **SEC-R1C-04** (limites de grant, identidade/step-up/rate-limit), com alternativas, risco, gate e roteiro. **Todos como RECOMENDAÇÃO / PENDENTE DE DECISÃO**, não escolhas aprovadas.
- `docs/work03b/R2_TRUST_CONTRACT_R0.md`: contrato escrito de EvidenceVerification & Trust R2 R0, distinção ASSERTED → CHECKED_PASS/FAIL/INCONCLUSIVE → REVIEW_ACCEPTED/REJECTED com actor e autoridade distintos; integração por reutilização de PostgreSQL/si_evidence_refs/grants/checkpoints, mapeamento de EV-01..EV-16 e gates R2-00..R2-05; nenhum DONE automático.
- `docs/work03b/R2_TRUST_CONTRACT_R0.json`: contrato machine-readable, 2 rotas R2 propostas e **0 implementadas**, três boundaries, records candidatos, invariantes e 16 entradas com `observed_decision=null`, `executed=false`, oráculos copiados sem lhes atribuir PASS.
- `tests/test_r2_r0_contract.py`: **6 testes de consistência estática** de contrato/fixture/ausência de routes R2, sem invocar verifier, Sigstore, GitHub API, artefactos assinados, reviewer ou ações externas. Actualizados README, arquitectura e matriz de aceitação para ligar as referências.
- `docs/HANDOFF_MASTER.md` recebe esta entrada cumulativa e `docs/HANDOFF.md` estado corrente. `docs/research/SI_RD_03C_EVIDENCE_RESEARCH_2026-11-12.md` e fixture ficam intactos.

**Limites / integridade:** APENAS docs + testes estáticos; nenhuma alteração ao backend, SQL, requisitos, vendor Mem0, CI workflow, contrato original UC_CORE_01_CONTRACT.json, `main`, JARVIS/PULSE, deploy ou produção. Não instalado in-toto/Sigstore/SLSA/OPA/OTel. `M01–M18` continua `PENDING_FULL_E2E`; R2 verifier/reviewer não existe. **CI deste novo commit AINDA PENDENTE à data do registo; seis testes novos são EXPECTATIVA, não resultado.**

**Próxima ação:** verificar CI real e persistir a evidência numa nova adenda SI-MH-0025 (sem reescrever esta); então apresentar a RIGHTWARE as quatro recomendações de R1C para ratificação/alteração e critérios/provedores da primeira versão de R2. Só após aprovação executar novas migrations/endpoints.

---

## SI-MH-0025 — R2 R0 contract consistency CI verified (100 tests)

**Data:** 2026-11-12 Africa/Maputo · **Estado:** DESIGN/CONTRACT-LINT VALIDADO EM CI; **R2 VERIFIER NÃO IMPLEMENTADO** · **SHA testado:** `22d71632caa6f7e442af5964561b42b1b4ea8693`.

**Evidência:** [Actions 43201981635](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43201981635) **SUCCESS**: HANDOFF_POLICY_PASS, migrações 0001–0006, **100/100 testes OK** (94 existentes + seis novos testes estáticos de consistência), R1B A/B e R1C rekey/fencing E2E com Mem0 OFF, regressão real MCP/REST/Postgres/Mem0/Ollama PASS. Nenhum segredo efémero exposto nos logs observados.

**Importante:** `tests/test_r2_r0_contract.py` validou somente integridade de documentos/JSON e a ausência de rotas R2. Os 16 casos EV-01..EV-16 permanecem **`synthetic=true, executed=false, observed_decision=null`**. Nenhum verificador GitHub/sigstore/in-toto, reviewer, decisão DONE, efeito externo ou análise criptográfica foi executado. CI verde não é prova R2.

**Documento de evidência:** `docs/work03b/R2_R0_CONTRACT_EVIDENCE.md`. Políticas SEC-R1C-01..04 em `R1C_SECURITY_POLICY_GATE_R0.md` permanecem **RECOMENDAÇÕES PENDENTES DE RATIFICAÇÃO**, não decisões oficiais; contrato `R2_TRUST_CONTRACT_R0` também DRAFT.

**Integridade:** documentação/handoffs apenas nesta adenda, sem alterar `main`, JARVIS/PULSE, vendor Mem0, contratos originais, SQL, APIs, CI ou pacotes. O próprio commit documental terá CI distinta, cujo resultado deve ser confirmado separadamente.

**Próximo passo:** apresentação das quatro decisões SEC-R1C à RIGHTWARE para ratificação; definir provedor GitHub workflow/identity/acceptance-criteria do MVP R2; depois WORK-03B R2 R1 *somente com autorização de implementação e critérios objectivos*. Nunca declarar M01–M18 full-E2E ou EV oracles PASS sem execução real e logs.

---

## SI-MH-0026 — WORK-03B R2 R1A: adaptador experimental de evidência GitHub

**Data:** 2026-11-12 Africa/Maputo · **Classificação:** EXPERIMENTO DE CÓDIGO R2 R1A, NÃO DECISÃO OFICIAL OU VERIFICADOR DE PRODUÇÃO · **Base verificada:** `develop@0c63b2f2d3d4cf00926752ab2c58d42ccbd64901`, `main@87c3351055aaf58d37f233dbc96eaa8f0b749c5c` e Mem0 pin `f1791daa86d469249c9b002f62644d58a1eb96a0`. CI base [43202560651](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43202560651) SUCCESS, 100/100 testes, E2E R1C A→B e Mem0/Ollama PASS.

**Objetivo e interpretação de autorização:** na continuidade solicitada para R2, criar **somente prova de conceito isolada, read-only, sem persistência, API pública, approval, revisão, effect execution ou mudança de decisões R1C**; não considerar o simples pedido 'vamos' como ratificação formal de SEC-R1C-01..04, política de providers para clientes ou DONE. R2_TRUST_CONTRACT_R0 continua **DRAFT_OPERATOR_RATIFICATION_REQUIRED_NOT_IMPLEMENTED** para operações externas.

**Código e testes desta entrega:**
- `backend/rightware_si/evidence_github.py`: política imutável `GithubRunPolicy`, `GithubCheck`, validação de ID estável de repositório 1452533938, workflow ID 415280241, run 43202560651 tentativa 1, SHA 0c63b2f2d3d4cf00926752ab2c58d42ccbd64901, event push, status completed e conclusion success. Resultados `CHECKED_PASS/CHECKED_FAIL/INCONCLUSIVE` com motivo explícito, sem permissões para DONE.
- Segurança: request apenas a `api.github.com/repos/{owner}/{repo}/actions/runs/{id}` usando slug validado, TLS, timeout 6s, no redirects, `trust_env=False`, resposta JSON limitada, sem URL fornecido por modelo, sem SSRF, sem output de token ou resposta bruta. HEAD repositório também validado, não apenas nome visível.
- `tests/test_r2_r1a_github_lab.py`: 15 testes **reais do código do verificador**, mas as respostas HTTP da unidade são MOCKED/SYNTHETIC. EV-01..EV-07 mapeados para oráculos JSONL sem alteração à fixture; negativos adicionais para run attempt, event, SHA, forks, repo/workflow, HTTP non-200, redirect, JSON corrupto, payload grande, inputs inseguros.
- `scripts/work03b_r2_r1a_github_live.py`: E2E de **consulta real à API GitHub**, fixado no run histórico concluído [43202560651](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43202560651) e 4 variantes EV-01..EV-04 (SHAs/repos/workflow trocados) com expected outcomes. A ação CI usa `GITHUB_TOKEN` temporário `actions:read`, nunca escreve em GitHub; não emite segredos ou JSON. **Ainda não executado no momento deste commit**, validar GitHub Actions.
- `.github/workflows/ci.yml` adiciona permissões mínimas `actions:read` e passo live, mantendo as seis migrations, testes PostgreSQL, R1B/R1C E2E sem Mem0 e E2E Mem0/Ollama reais.
- Novo `docs/work03b/R2_R1A_GITHUB_VERIFIER_LAB.md`, README, arquitectura e matriz UC-CORE-01 actualizados com os limites. **115 testes esperados** (100 anteriores + 15 de adaptador), não reportar PASS antes do CI. Contrato canónico mantém 18 rotas de laboratório / 3 futuras; o R2 R0 permanece 0 rotas implementadas.

**Limitações e separação:** `CHECKED_PASS` só representa campos exactos devolvidos por API GitHub para run específico, não comprova conteúdo do software, assinatura/attestation, critérios do produto, aprovação `REVIEW_ACCEPTED` ou DONE. Sem SQL `VerificationAttempt`, permissões `evidence:verify`, revisor, source-level ACL, consent/retention, workflows de cliente, deploy, API/MCP de escrita, tool execution ou outras dependências. EV-05..EV-07 em unittest usam mock; EV-08..EV-16 não executados. Ficheiro de investigação EV continua `executed=false` (representa proposta de oráculos, não relatório de CI). M01–M18 full E2E pendentes.

**Integridade:** `main`, JARVIS/PULSE, vendor Mem0 e produção inalterados. SEC-R1C-01..04 continuam recomendações pendentes. Sem branch adicional nem merge. CI do novo HEAD PENDENTE, anotar FAIL ou PASS real numa entrada posterior SI-MH-0027, nunca falsificar resultado histórico.

**Próximo:** verificar CI do commit experimental e registar exactamente quais EV checks eram LIVE vs MOCK; se passar, apresentar opções de ratificação SEC-R1C e política do primeiro provedor/critério R2 R1B antes de schema/endpoint/review.

---

## SI-MH-0027 — WORK-03B R2 R1A GitHub verifier: 115 testes e EV-01..04 LIVE validados

**Data:** 2026-11-12 Africa/Maputo · **Estado:** EXPERIMENTO EM LABORATÓRIO VALIDADO EM CI; **NÃO PRODUÇÃO, NÃO APROVAÇÃO DE TAREFAS**. **SHA testado:** `1aa40c0d54c96d7c59bb7118326700a974cbb46e`; branch `develop`.

**Evidência:** [GitHub Actions 43214573166](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43214573166) **SUCCESS**. Logs reais observados: `HANDOFF_POLICY_PASS`, migrations 0001–0006 PASS, **`Ran 115 tests` / `OK`** (100 anteriores + 15 novos testes determinísticos do adaptador GitHub com transport MOCK); `WORK03B_R2_R1A_GITHUB_LIVE_PASS` para **quatro consultas reais** da API do GitHub usando runner `actions:read` ao run fixo 43202560651, repo 1452533938, workflow 415280241, SHA 0c63b2f2d3d4cf00926752ab2c58d42ccbd64901, attempt 1. Retornos: **EV-01 CHECKED_PASS**, **EV-02 CHECKED_FAIL (wrong SHA)**, **EV-03 CHECKED_FAIL (wrong repo ID)** e **EV-04 CHECKED_FAIL (wrong workflow ID)**, todos `task_approved=false`. R1B A→B Mem0 OFF e R1C bound lease E2E PASS, Mem0 OSS/Ollama/MCP/REST/PG real regression PASS. Não foi observada exposição da chave efémera nos logs.

**Distinguir graus de prova:** EV-01..04 LIVE API de GitHub ao run histórico fixo; EV-05 (workflow pending), EV-06 (external API down), EV-07 (screenshot) foram **simulações/testes reais do código com MockTransport**, não observações de casos reais externos. EV-08..16 **NÃO EXECUTADOS**. A fixture de investigação SI-RD-03C permanece sem alterações, `synthetic=true,executed=false` para todos, pois é definição original dos oráculos. Os resultados reais do código são registados separadamente em `docs/work03b/R2_R1A_EVIDENCE.md`, sem falsificar histórico.

**Componente validado:** `backend/rightware_si/evidence_github.py` consulta somente um endpoint GitHub API fixo construído com owner/repo/run id estritamente validados, HTTPS+TLS, timeout, sem redirects/proxies/URLs arbitrários; compara repo/head repo ID, nome, workflow, run/attempt, SHA, event e status/conclusion. Resultado representa condição concreta; não se atribui direito de DONE nem marca uma observação ASSERTED como verdade. No PostgreSQL não há VerificationAttempt nem permissões `evidence:verify`, nenhuma API REST/MCP do R2 ou serviço independente autorizável; zero writes. `docs/work03b/R2_R1A_GITHUB_VERIFIER_LAB.md` e matriz UC-CORE-01 atualizados após CI.

**Limitações / decisões pendentes:** SEC-R1C-01..04 continuam RECOMENDAÇÕES não ratificadas; R2_TRUST_CONTRACT_R0 permanece DRAFT, `implemented_r2_routes=0`; UC-CORE-01 mantém 18 rotas de laboratório, 3 propostas e M01–M18 PENDING_FULL_E2E. Não foram verificadas assinaturas/SLSA/in-toto, políticas de criteria de cliente, atestação criptográfica, fonte PII/consent, revisor ou DONE. Este commit documental não modifica `main`, JARVIS/PULSE, Mem0, backend, SQL, CI ou dependências, e terá CI própria a verificar.

**Próximo passo:** ratificar com operador o escopo de políticas SEC-R1C-01..04 e a política de GitHub Provider por cliente/critério/identity. Depois R2 R1B (design de VerificationAttempt append-only, autorização de serviço `evidence:verify`, grants/consent, idempotência, revogação) sem habilitar review/DONE automaticamente.

---

## SI-MH-0028 — WORK-03B R2 R1B: ledger de evidências append-only e SERVICE verifier em laboratório

**Data:** 2026-11-12 Africa/Maputo · **Classificação:** IMPLEMENTAÇÃO EXPERIMENTAL/ISOLADA, **CI PENDENTE** no momento deste commit; NÃO aprovação oficial de políticas R1C, não produção. **HEAD base:** develop@7e38f617c851d8c70911e15001aec945eac5ebda; main@87c3351055aaf58d37f233dbc96eaa8f0b749c5c e vendor Mem0 pin f1791daa86d469249c9b002f62644d58a1eb96a0 preservados.

**Baseline:** [CI 43215546691](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43215546691) SUCCESS 115/115 testes, EV-01..04 live provider, EV-05..07 simulados, R1C A→B e Mem0/Ollama real. Confirmação prévia do HEAD, HANDOFF e histórico SI-MH-0027.

**Âmbito implementado, sem endpoint público:**
- database/migrations/0007_work03b_r2_r1b_verification_ledger.sql: nova tabela si_evidence_verification_policies versionada, amarrada a project/task/evidence, critério, repo/workflow/run/full SHA e criador; nova si_verification_attempts append-only com idempotência project+SERVICE+key, resultado limitado CHECKED_PASS/CHECKED_FAIL/INCONCLUSIVE e campo de proveniência LIVE_HTTPS vs SIMULATED_TRANSPORT. Triggers PostgreSQL bloqueiam UPDATE/DELETE, FKs impedem referência entre projetos/tarefas, novo evento EVIDENCE_CHECKED. Históricos si_evidence_refs REFERENCED e si_observations ASSERTED permanecem intactos.
- backend/rightware_si/verification_ledger.py: EvidenceLedger de uso **interno e confiável** (não request público); autenticação do ator é pressuposto e testada via bearer/resolve_principal no CLI. Somente principal_kind SERVICE com project grant evidence:verify + task:read verifica; autor/criador/evidence submitter não pode auto-verificar. Preflight compara estado IN_REVIEW, expected task version, critério e URL exata pinada à política do operador, sem fetch URL arbitrário. Consulta GitHub API HTTPS limitada **fora da transação**; nova autorização/versão/policy/URL sob row lock antes do insert. Read de attempts exige task:read + evidence:read e projeto atual.
- tests/test_r2_r1b_ledger.py: **16 testes reais PostgreSQL + código** de resultado simulated PASS/FAIL/INCONCLUSIVE, grants, separação AGENT vs SERVICE, self-check, URL errada, versão obsoleta, revogação durante chamada externa, idempotência/replay, DB imutável, critérios, revogação na leitura e concorrência.
- scripts/work03b_r2_r1b_live_ledger.py: prova end-to-end isolada GitHub API real (run histórico 43202560651) → SERVICE autenticado → insert PostgreSQL append-only; recusa DB diferente de localhost:5432/rw_test, trunca somente DB efémera sintética. Inclui task WorkCore create/publish/claim/submit, policy operator-seeded, confirmação de idempotência, read revocation, task IN_REVIEW e si_evidence_refs REFERENCED. GitHub Actions GITHUB_TOKEN somente read.
- CI workflow aplica SQL 0007, corre **131 testes esperados** (115 anteriores +16) e script live ledger, depois R1C E2E/Mem0. Contagem PASS NÃO afirmada até logs.
- Docs R2_R1B_VERIFICATION_LEDGER.md, README, database/backend README, docs/ARCHITECTURE.md e UC_CORE_01_ACCEPTANCE.md atualizados.

**Separação de estados obrigatória:** check independente e append-only NÃO altera status IN_REVIEW, task.version, trust_state ASSERTED, evidence REFERENCED, nem autoriza REVIEW_ACCEPTED/DONE. SIMULATED_TRANSPORT não é assinatura nem fonte live. Prova externa limita-se aos campos de workflow do GitHub, não aos critérios empresariais completos.

**Não alterado / bloqueios:** sem nova rota POST verify/review pública, sem MCP de escrita, sem app UI, sem R2 reviewer/DONE, sem OIDC/produção/consent/retention/reconciliação de efeitos, sem Sigstore/SLSA/attestation. Contrato R2 R0 continua histórico DRAFT com 0 rotas operacionais; UC-CORE-01 18 lab/3 futuras e M01–M18 PENDING_FULL_E2E. SEC-R1C-01..04 ainda pendentes de ratificação. main/Jarvis/PULSE/vendor Mem0 inalterados; sem novas dependências e sem branch temporária.

**Próximo:** acompanhar CI do SHA de implementação, registrar FAILs de forma append-only ou, se passar, SI-MH-0029 com prova live GitHub→PostgreSQL, 131 testes e regressões reais. Posteriormente ratificar provider/client policy, segurança e privacidade antes de qualquer API/reviewer público.

---

## SI-MH-0029 — WORK-03B R2 R1B: CI 131 testes e verificador LIVE→PostgreSQL validados

**Data:** 2026-11-12 Africa/Maputo · **Estado:** VALIDAÇÃO EXPERIMENTAL REAL EM LABORATÓRIO, NÃO PRODUTO/PRODUÇÃO. **SHA real testado:** develop@cfa6153c4e8bbebd27d30f629e1681966312663f.

**Fonte primária:** [Actions run 43237504677](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43237504677) **SUCCESS**: HANDOFF_POLICY_PASS, migrações 0001–0007 MIGRATION_PASS, **Ran 131 tests / OK** (115 prévios +16 reais PostgreSQL/adapter com fonte mock), R2 R1A EV-01 live CHECKED_PASS e EV-02..04 live CHECKED_FAIL esperado, **WORK03B_R2_R1B_LEDGER_LIVE_PASS** com GitHub API real + SERVICE autorizado por bearer + PostgreSQL append-only; confirmou idempotência, current grant/revoked read negado, task=IN_REVIEW, evidence=REFERENCED, no_review=true, no_done=true. R1C two-process bound handoff/lease recovery E2E PASS, Mem0 OSS/Ollama/MCP/REST/PostgreSQL real E2E PASS. Nenhuma chave efémera detectada em claro nos logs observados.

**O que efectivamente ficou verificado:** tabela de políticas imutáveis pre-seeded em laboratório e tentativas append-only, FKs de project/task/evidence, razão e canal LIVE_HTTPS vs SIMULATED_TRANSPORT, separação SERVICE de criador/agente, duas validações de grants/versão antes/depois de consulta externa, idempotência, leitura autorizada, preservação de estado independente de revisão. Registos de verificação não promovem ASSERTED nem automaticamente DONE.

**Hierarquia de provas:** EV-01..04 live GitHub contra run fixo; EV-05..07 simulados em testes do R1A; R2 R1B inclui uma nova prova separada LIVE API→SERVICE→PostgreSQL mais 16 testes PostgreSQL com respostas provider simuladas. EV-08..16 não executados. Original fixture SI-RD-03C permanece synthetic=true/executed=false como contrato de investigação, não é jornal de resultados de implementação.

**Documentos:** [R2_R1B_EVIDENCE.md](work03b/R2_R1B_EVIDENCE.md) contém run, SHA, observações exatas, métodos/live/mock/limites; [R2_R1B_VERIFICATION_LEDGER.md](work03b/R2_R1B_VERIFICATION_LEDGER.md) e UC_CORE_01_ACCEPTANCE actualizados. Ambos os handoffs preservados no mesmo commit.

**Bloqueios / integridade:** R2 R0 DRAFT (zero endpoints operacionais R2); SEC-R1C-01..04 recomendações NÃO RATIFICADAS; nenhum endpoint POST verify ou review, nenhuma aprovação independente/DONE, sem policy/admin UI, OIDC, source-level consent/privacy, retention, RLS prod, Sigstore/in-toto ou external-effect outbox. M01–M18 PENDING_FULL_E2E. main, JARVIS, PULSE e vendor Mem0 inalterados. Este commit de evidências é apenas documentação, e necessita CI própria antes de se declarar validado.

**Próximo passo:** ratificar políticas de autorização/persistência e critérios do primeiro provider por projecto; depois planear rota REST verificadora operacional com serviço credenciado e revisão separada. Não abrir DONE automático. Guardar CI desta adenda como run de documentação separada.

---


---

## SI-MH-0030 — Recuperação do chat e gate R2 R1C preparado (somente documentação)

**Data:** 2026-11-12 (Africa/Maputo). **Classe:** CONTINUIDADE / RECOMENDAÇÃO / DECISION PACKET; nenhuma ratificação ou implementação de R2 R1C. **HEAD inicial verificado:** `develop@e43a653b3c5999028abe4571fb9730b7f9b25dea`. Comparação inicial `develop` vs baseline: identical.

**Motivo:** atingido limite do chat anterior. O operador forneceu o registo histórico e pediu preservação em handoffs e continuação sem perder o progresso. Handoff oficial e GitHub foram usados como fonte de verdade; texto do chat não foi copiado integralmente para o repo público.

**Evidências pré-existentes confirmadas:** WORK-03B R1C 94/94 PASS [43196082372](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43196082372); R2 R0 contrato 100/100 PASS [43201981635](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43201981635); R2 R1A 115/115 PASS [43214573166](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43214573166); R2 R1B 131/131 PASS [43237504677](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43237504677). Job do [CI documental SI-MH-0029](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43238519552) observado como success. EV-01..04 LIVE; EV-05..07 transport MOCK; EV-08..16 não executados. `main` segue README inicial; sem produto pronto para produção.

**Ficheiros no mesmo commit deste checkpoint:** novo [decision packet R2 R1C](work03b/R2_R1C_DECISION_AND_API_GATE_R0.md), [HANDOFF.md](HANDOFF.md) e este MASTER. Nenhum código SQL, backend, provider, policy de runtime, workflow, teste, PR, dependência, JARVIS/PULSE, Mem0 ou `main` alterado. Novo CI deste commit: **PENDENTE DE OBSERVAÇÃO**, não afirmar PASS até logs reais.

**Decisões oficiais preservadas:** dois ramos de trabalho `develop/main` e handoffs obrigatórios por checkpoint; nenhuma decisão SEC-R1C-01..04 ou política R2 de provider/tenant/consent foi aprovada por este documento. `ASSERTED`, `CHECKED_*`, `REVIEW_*` e `DONE` continuam rigorosamente separados.

**Riscos/gates:** lease takeover e external-effect reconciliation não resolvidos; workload identity/OIDC, RLS/PII/source-level ACL, retenção, reviewer, review/DONE, endpoints R2 e full UC-CORE-01 pendentes. O novo pacote contém opções a ratificar, especificação de negative tests e critérios para uma API SERVICE-only restrita (sem autorizar a implementação).

**Próxima ação:** consultar CI deste commit; ratificar ou corrigir SEC-R1C-01..04 e as escolhas de provider/criteria/identity/retention. Só depois autorizar e implementar R2 R1C REST verifier; reviewer/DONE em gate separado. Nunca trocar uma recomendação por decisão automática.


---

## SI-MH-0031 — R2 R1C contract lint and evidence/path identity safety gate (sem API)

**Data:** 2026-11-12 Africa/Maputo. **Classificação:** INVESTIGAÇÃO / ESPECIFICAÇÃO TÉCNICA / TESTES ESTÁTICOS; **SEM aprovação de política, SEM rota operacional.** HEAD antes: `develop@0eb4e662490ffb22a18cdb5e21ac4c85c14066d4`; última implementação validada permanece R2 R1B 131/131 no [Actions 43237504677](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43237504677).

**Descoberta por leitura do código real:** `backend/rightware_si/http_api.py` possui 18 rotas laboratoriais mas não uma rota de verificação/review; `verification_ledger.py::verify_and_record` aceita policy_id mas não evidence_id, por isso o futuro `/evidence/{evidence_id}/verify` precisa de binding explícito na fronteira do ledger e revalidação sob lock antes de registrar tentativa; caso contrário o path pode ser ignorado. As regras de SERVICE/evidence:verify+task:read, separação de autoria, API fixa GitHub, provenance LIVE_HTTPS/SIMULATED_TRANSPORT, idempotência e revogação já existem internamente, não se duplicam.

**Artefactos deste checkpoint:** [R2_R1C_REST_VERIFY_CONTRACT_R0.md](work03b/R2_R1C_REST_VERIFY_CONTRACT_R0.md), JSON homólogo, 16 cenários negativos API-NEG-01..16 definidos (NÃO EXECUTADOS) e `tests/test_r2_r1c_contract.py` com **11 testes de consistência estática**. O script não tem dependência externa e não valida HTTP/DB nem autoria de operador. Código funcional, migrations, tokens, credenciais, CI workflow e branches de release intactos. Contagem de suíte completa: 131 anteriores +11 propostos = **142 ESPERADOS, NÃO COMPROVADOS** antes de CI. Não confundir lint com prova do endpoint.

**Governança:** SEC-R1C-01..04 e R2-PROVIDER/IDENTITY/PRIVACY continuam NÃO RATIFICADOS. `ASSERTED != CHECKED_PASS != REVIEW_ACCEPTED != DONE`. Nenhum REST verification endpoint, reviewer, DONE, policy admin, OIDC, source-level consent/retention, external-effect outbox ou produção implementado. `main`, JARVIS, PULSE, Mem0 pinned sem alterações.

**CI deste commit:** PENDENTE DE OBSERVAÇÃO. Validar HEAD, static test, suite 142 prevista, migrations e E2E anteriores, registar resultado real em novo checkpoint. Se falhar, corrigir e preservar evidências sem declarar aprovação. Não afirmar execução dos 16 API-NEG, EV-08..EV-16 ou M01–M18 completos.

**Próximo gate:** ratificação explícita das políticas e de condições por projecto/tenant; depois implementação mínima de binding `expected_evidence_id` + FastAPI SERVICE-only em checkpoint de engenharia separado com real negative tests. DONE e reviewer continuam separados.

## Modelo para cada NOVA entrada
### SI-MH-XXXX — [WORK / checkpoint]
- Data UTC e Africa/Maputo; estado declarado: DECISÃO, PROPOSTA, IMPLEMENTADO, VALIDADO, FALHOU ou BLOQUEADO.
- Objetivo / motivo / âmbito.
- Antes: branch e HEAD verificado.
- Alterações: ficheiros, migrations, testes, mudanças funcionais, documentação e restrições.
- Evidências: commit(s), PR, CI run(s), comandos (sem segredos), PASS/FAIL/SKIP e ambiente.
- Decisões oficiais distintas de recomendações e hipóteses.
- Riscos/limites, não alterado, rollback e próximo passo exato.
- Se uma execução ainda estiver pendente, nova adenda SI-MH-XXXX registra resultado; nunca editar o registro antigo como se fosse originalmente PASS.

