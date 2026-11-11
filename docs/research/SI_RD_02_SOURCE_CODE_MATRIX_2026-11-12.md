# SI-RD-02 — Source-code reverse analysis, licensing and technical decision matrix

**Data:** 2026-11-12 (Africa/Maputo)  
**Classificação:** INVESTIGAÇÃO / RECOMENDAÇÃO TÉCNICA PROVISÓRIA, não aprovação comercial nem benchmark executado.  
**Fonte do projecto:** `rightware-corporations/rightware-shared-intelligence` em `develop`.  
**Âmbito:** leitura de implementação OSS, APIs públicas, documentação e feedback. Não executar código de fornecedores, não alterar runtime, não incorporar fontes externas nesta fase.

## 1. Decisão que esta investigação prepara
Determinar **REUSE / INTEGRATE / ADAPT / BUILD / REJECT**, por mecanismo, para um serviço independente de memória contextual e continuidade operacional verificável, sem confundir recordação com execução de acções nem autenticação com simples filtro vectorial.

Princípio: **não criar uma nova Mem0, Graphiti, Temporal ou A2A**. Testar primeiro a integração mínima e só desenvolver tecnologia própria onde existir lacuna demonstrável em desempenho, fiabilidade, evidências, segurança ou adequação ao cliente.

## 2. Evidência auditada
Foram consultadas árvores e ficheiros concretos nos commits fixados a seguir. Os SHAs são **refs de leitura da investigação**, não dependências aprovadas no produto. Licenças são a licença principal do repositório identificada via GitHub; pacote, modelo, dependências transitivas e eventuais termos comerciais exigem auditoria independente antes de redistribuir.

| Motor / componente | Licença principal | Ref de investigação | Evidência observada no código | Tratamento provisório |
|---|---|---|---|---|
| Mem0 OSS | Apache-2.0 | `f1791daa86d4` | ADD-only (one extraction pass), hybrid semantic/BM25/entity scoring; scope keys filtered; provider for semantic context | REUSE now; benchmark before upgrade or replacement |
| Hindsight | MIT | `7cec128b8fdb` | Retain/recall/reflect; memory defense, operation validator, temporal + BM25 + semantic + graph, RequestContext tenant hooks | EVALUATE as replaceable memory adapter |
| Graphiti | Apache-2.0 | `ebef986a0b23` | EntityEdge valid_at / invalid_at / episode links; graph + vector + text search, partition group_id | EVALUATE temporal cases if simpler baseline fails |
| Letta Code | Apache-2.0 | `67fc302873d2` | Git-backed MemFS, self-adjusting agent memory, identity and agent runtime | LEARN patterns; do not import entire agent harness into shared memory |
| LangGraph | MIT | `5ea88ecbcdb9` | Thread checkpointing, pending writes and store; configurable durability | COMPARE workflow-state track only; not memory retrieval benchmark peer |
| Temporal Python SDK | MIT | `4733537c4a1d` | Activities, workers, durable workflow execution, retries and replay semantics | EVALUATE as optional workflow backend after complexity warrants |
| A2A specification | Apache-2.0 | `d18aa92c911c` | Task/Context ids, task lifecycle, messages and artifacts; transient events are not durable by promise | ADOPT protocol alignment later; not source of truth |
| PostgreSQL full-text + exact lookup | PostgreSQL license (verify redistribution duties per component) | `RIGHTWARE lo` | Authoritative task state, exact ids and reproducible handoff; no LLM needed for exact facts | CONTROL baseline mandatory |

**Âncoras de reprodução (paths):**
- Mem0 OSS: [repo@f1791daa86d4](https://github.com/mem0ai/mem0/tree/f1791daa86d469249c9b002f62644d58a1eb96a0) — `mem0/memory/main.py ; docs/migration/oss-v2-to-v3.mdx`.
- Hindsight: [repo@7cec128b8fdb](https://github.com/vectorize-io/hindsight/tree/7cec128b8fdb0a696366d888e63be71fe1d52338) — `hindsight-api-slim/hindsight_api/engine/retain/orchestrator.py ; engine/search/retrieval.py ; hindsight_api/models.py`.
- Graphiti: [repo@ebef986a0b23](https://github.com/getzep/graphiti/tree/ebef986a0b2360211b65751c111cacb4a7d790eb) — `graphiti_core/edges.py ; graphiti_core/search/search.py`.
- Letta Code: [repo@67fc302873d2](https://github.com/letta-ai/letta-code/tree/67fc302873d2f21c9ab07dad8b145785e4ac3377) — `src/agent/memory-filesystem.ts ; src/agent/memory-git.ts ; README.md`.
- LangGraph: [repo@5ea88ecbcdb9](https://github.com/langchain-ai/langgraph/tree/5ea88ecbcdb9fde713c3abd58850a5b7beaa24ec) — `libs/langgraph/langgraph/pregel/_loop.py ; persistence/checkpoint docs`.
- Temporal Python SDK: [repo@4733537c4a1d](https://github.com/temporalio/sdk-python/tree/4733537c4a1d523fa1f0081c18512d895f4f88b8) — `temporalio/activity.py ; temporalio/workflow/* ; README.md`.
- A2A specification: [repo@d18aa92c911c](https://github.com/a2aproject/A2A/tree/d18aa92c911c1b49f0d584c1ca0e9d8718391014) — `specification/a2a.proto ; docs/specification.md`.

### 2.1. Mem0 — importante sobre algoritmo e escopo
O Mem0 OSS actualmente fixado pela RIGHTWARE é exactamente `f1791daa86d469249c9b002f62644d58a1eb96a0`, o mesmo hash `main` observado nesta consulta. O código `mem0/memory/main.py` contém `_strip_identity_keys`, `ENTITY_PARAMS` e classificação explícita de campos de identidade. O guia de migração no mesmo pin descreve **extracção ADD-only**, procura híbrida semantic+BM25+entity e remoção de Graph Memory do OSS. ADD-only não remove automaticamente uma afirmação antiga; exige interpretação temporal ou fontes autoritativas para asserções contraditórias. O teste actual RIGHTWARE usa `infer=false` e embeddings locais; **não comprova qualidade de extracção por LLM**.
- https://github.com/mem0ai/mem0/blob/f1791daa86d469249c9b002f62644d58a1eb96a0/docs/migration/oss-v2-to-v3.mdx
- https://github.com/mem0ai/mem0/blob/f1791daa86d469249c9b002f62644d58a1eb96a0/mem0/memory/main.py

### 2.2. Hindsight — diferenciação já existente
O `engine/retain/orchestrator.py` referencia `MemoryDefenseExtension` e `OperationValidatorExtension` e coordena o pipeline retain. O `engine/search/retrieval.py` separa sinais semantic/BM25/graph/temporal. `models.py` tem `RequestContext` com `tenant_id`, `api_key_id` e atributos internos. Isto **não prova** isolamento em qualquer deploy; mostra mecanismos de arquitectura que já existem. Portanto, **memory defense, temporal retrieval, proveniência e tenant hooks não são hipóteses exclusivas da RIGHTWARE**. É necessário comparar com resultados operacionais e custos.
- https://github.com/vectorize-io/hindsight/blob/7cec128b8fdb0a696366d888e63be71fe1d52338/hindsight-api-slim/hindsight_api/engine/retain/orchestrator.py
- https://github.com/vectorize-io/hindsight/blob/7cec128b8fdb0a696366d888e63be71fe1d52338/hindsight-api-slim/hindsight_api/engine/search/retrieval.py
- https://github.com/vectorize-io/hindsight/blob/7cec128b8fdb0a696366d888e63be71fe1d52338/hindsight-api-slim/hindsight_api/models.py

### 2.3. Graphiti — temporal já é prioridade de concorrentes
`EntityEdge` guarda episódios e tempos `valid_at`, `invalid_at`, `expired_at`; `search/search.py` combina funções de full-text, similarity, BFS, MMR e reranking. `group_id` é partição lógica, não substitui autoridade de identidade multi-tenant da RIGHTWARE. Não propor construir grafo próprio antes de testar se o benchmark temporal demonstra benefício superior a PostgreSQL+eventos.
- https://github.com/getzep/graphiti/blob/ebef986a0b2360211b65751c111cacb4a7d790eb/graphiti_core/edges.py
- https://github.com/getzep/graphiti/blob/ebef986a0b2360211b65751c111cacb4a7d790eb/graphiti_core/search/search.py

### 2.4. Letta Code — Git-backed memory
`src/agent/memory-filesystem.ts` gere directórios por agente; `src/agent/memory-git.ts` trata sincronização/versionamento e redacção de material de autenticação. É uma referência valiosa para Handoff e memória como artefacto durável; trata-se de um agent harness, não de um substituto directo para autorização/estado empresarial partilhado. O repositório `letta-ai/letta` é histórico; analisar `letta-ai/letta-code` para o desenvolvimento activo.
- https://github.com/letta-ai/letta-code/blob/67fc302873d2f21c9ab07dad8b145785e4ac3377/src/agent/memory-git.ts

### 2.5. Durabilidade e protocolos são categorias próprias
**LangGraph** checkpoint/store, pending writes e modos de persistência. **Temporal** workflows/activities/retries. **A2A** Task, contextId, artifact e message; a especificação declara que mensagens de progresso podem não ser persistidas e não podem ser canal fiável de eventos críticos. Não misturar scores destes sistemas com recall de Mem0/Hindsight.
- https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/checkpointers.mdx
- https://github.com/temporalio/sdk-python/blob/4733537c4a1d523fa1f0081c18512d895f4f88b8/temporalio/activity.py
- https://github.com/a2aproject/A2A/blob/d18aa92c911c1b49f0d584c1ca0e9d8718391014/specification/a2a.proto
- https://a2a-protocol.org/dev/specification/

## 3. Como NÃO repetir trabalho dos outros
**Camada contextual:** manter `Mem0` como provider actual; estudar `Hindsight` e `Graphiti` como adapters substituíveis, nunca importar código do fork inteiro sem licença/compatibilidade.
**Camada de estado:** manter PostgreSQL e estados transaccionais da RIGHTWARE. Antes de acrescentar motor de workflows, medir limites do WorkCore vs checkpoint LangGraph/Temporal em cenários concretos.
**Camada de protocolo:** preservar REST+MCP de leitura; estudar A2A para integração entre agentes, não como substituto dos eventos de auditoria.
**Camada proprietária candidata:** verificar se a combinação autorização independente + evidência verificável + handoff atómico e versionado traz valor **adicional** ao que existe. Esta combinação é HIPÓTESE, não patente, exclusividade ou vantagem comprovada.

## 4. Achados que contrariam pressupostos
- Não podemos reivindicar `provenance` ou `memory-defense` como funcionalidade original: já existem mecanismos no Hindsight/Graphiti.
- Não devemos assumir que Mem0 OSS inclui o grafo da oferta Platform: o guia do pin actual diz o contrário.
- Não basta ser self-hosted: Hindsight e outras plataformas já suportam esse modo.
- Memória semântica não deve conseguir alterar estado oficial; a RIGHTWARE já separa `UNVERIFIED` do PostgreSQL em `backend/rightware_si/context_service.py`.
- Persistência de um workflow não garante `exactly once` de um efeito externo. Idempotência e reconciliação são responsabilidade explícita.
- A própria análise de custos deve contar ingestão, embeddings, LLM, memória, armazenamento, backup, administração, segurança e suporte — não apenas custo de API.

## 5. Gaps e avaliações pendentes
- **Código lido, não executado:** não há resultado comparativo de RAG/memory, latência ou recall RIGHTWARE para Hindsight/Graphiti/Letta.
- **Licenciamento:** verificar submódulos, pesos de modelos, dependências e termos de redistribuição numa fase separada.
- **Segurança:** não houve pentest, alteração do pinned Mem0, integração de dados privados, auditoria de produção nem validação de tenant auth sob carga.
- **Negócio:** não existem clientes entrevistados nem disposição a pagar comprovada.
- **CI:** o histórico de 55/55 e E2E WORK-03A mede exclusivamente o núcleo actual e dados sintéticos, não a qualidade dos fornecedores pesquisados.

## 6. Próxima decisão proposta: SI-RD-03
Implementar um *harness* de laboratório ISOLADO de produção com 18 casos sintéticos versionados; fase A comparar exact/FTS do PostgreSQL contra Mem0 e Hindsight no mesmo protocolo de consulta; fase B adicionar Graphiti em cenários temporais; fase C validar continuidade com WorkCore actual e comparação posterior com LangGraph/Temporal; fase D analisar compatibilidade A2A.
Critério P0: zero violação de autorização, zero promoção sem verificação, zero side-effect externo duplicado; performance com denominadores e intervalos, sem inventar scores.
Só então apresentar BUILD/INTEGRATE formal para aprovação.
