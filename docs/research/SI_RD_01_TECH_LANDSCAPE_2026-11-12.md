# SI-RD-01 — Landscape, feedback and differentiation intelligence
**Data:** 2026-11-12 (Africa/Maputo)
**Estado:** INVESTIGAÇÃO DOCUMENTAL INICIAL / PROPOSTAS, não decisão de produto, benchmark próprio ou produção.
**Âmbito:** RIGHTWARE Shared Intelligence, independência do Jarvis e PULSE. Zero execução de código externo nesta investigação.

## Questão de decisão
Que capacidades da memória e continuidade de agentes devemos **reutilizar, integrar ou construir**, para obter vantagem verificável em continuidade operacional entre agentes com isolamento, proveniência e evidência?

## Método
Método RIGHTWARE: descoberta -> engenharia reversa -> comparação reproduzível -> síntese de problemas e êxitos reais -> diferenciação -> decisão -> implementação limitada.
Hierarquia de evidência: (1) código/versionamento + testes reprodutíveis, (2) documentação técnica oficial, (3) benchmark externo reproduzível, (4) resultados publicados pelos próprios fornecedores, (5) relatos e issues da comunidade. Um issue aberto ou fechado não prova sozinho a existência actual ou resolução da falha no pin da RIGHTWARE.

## Radar técnico — o que já existe
| Solução | Capacidade a aprender/reutilizar | O que não devemos assumir |
|---|---|---|
| Mem0 OSS | Extracção/armazenamento/recuperação semântica; adapter já integrado no laboratório RIGHTWARE | Não confundir OSS com oferta comercial/Graph Memory; o seu escopo não substitui autorização empresarial |
| Hindsight | Retain/Recall/Reflect; consolidação; avaliação de custo de correcções humanas | Scores publicados pelo fornecedor não são benchmark RIGHTWARE; operação exige tuning e medições de latência |
| Graphiti (Zep) | Grafo temporal, proveniência por episódios, factos com validade temporal, retrieval híbrido | Graphiti OSS != Zep comercial; requer operar armazenamento e políticas; deduplicação não é infalível |
| Letta | Agentes com estado persistente, memória gerida, evolução de contexto | Persistir contexto não é provar conclusão de uma operação |
| LangGraph | Checkpointing, durabilidade por modo, stores inter-thread, intervenção humana | Persistência de execução não equivale a autorização/aceitação de evidência |
| Temporal | Workflows duráveis, retries, actividades, compensação e idempotência | Efeitos externos podem repetir; não prometer exactly-once externo |
| A2A | Identidade de tarefa/contexto, mensagens, artefactos e estados entre agentes | Protocolo de comunicação não garante que toda mensagem transitória fique guardada |
| PostgreSQL + texto/BM25/pgvector + handoffs Git | Baseline simples, auditável e potencialmente eficiente | Não assumir que pesquisa vectorial ganha de pesquisa exacta sem medir |

Fontes:
- Mem0 OSS vs Platform: https://github.com/mem0ai/mem0/blob/main/docs/core-concepts/how-it-works.mdx
- Hindsight benchmarks, dados *reportados pela empresa*: https://vectorize.io/benchmarks
- Hindsight consolidação: https://github.com/vectorize-io/hindsight/blob/main/hindsight-docs/blog/2026-05-21-agent-memory-consolidation.md
- Graphiti OSS: https://github.com/getzep/graphiti
- LangGraph durabilidade: https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/checkpointers.mdx
- Temporal retries: https://github.com/temporalio/documentation/blob/main/docs/encyclopedia/activities/activity-definition.mdx
- A2A: https://github.com/a2aproject/A2A/blob/main/docs/specification.md

## Aprendizagens positivas e negativas de utilizadores
1. **Mem0, memória ruidosa — relato único, não taxa de falha geral.** Utilizador auditou 10.134 registos e descreveu duplicados e inferências inventadas; resposta da comunidade apontou para evitar realimentar memória recuperada como entrada de extracção, preservar roles de origem, filtrar ruído antes da extracção, provenance e confirmação condicional. Uma implementação comunitária relatou regressar ao Mem0 self-hosted após explorar outras opções por critérios práticos de usabilidade, velocidade e rastreabilidade; as afirmações são relatos, não testes independentes.
  - Issue e discussão: https://github.com/mem0ai/mem0/issues/4573
  - Exemplos comunitários para estudo sem adopção cega: https://github.com/farrrr/mem0-stack-oss e https://github.com/jamebobob/mem0-vigil-recall
2. **Mem0 TS, identidade alterável — issue histórico P0.** Foi reportado que updates de metadata podiam alterar user_id/agent_id/run_id. Issue #6342 foi FECHADO em 2026-07-21; sem auditoria do patch/pin, não afirmar que a versão actualmente usada tem a falha. Mesmo assim, manter identidade e grants fora do LLM/memory engine.
  - https://github.com/mem0ai/mem0/issues/6342
3. **Graphiti, problemas de robustez reportados.** Issues sobre embeddings NaN/Inf e deduplicação de acrónimos por similaridade mostram por que validar embeddings, combinar match exacto com semântico e instrumentar ingestão. O estado verificado em 2026-11-12 era OPEN nos issues #1505 e #1734; não generalizar para todas as versões.
  - https://github.com/getzep/graphiti/issues/1505
  - https://github.com/getzep/graphiti/issues/1734
4. **Hindsight, ganhos e trade-off de configuração.** O fornecedor reporta 94,6% LongMemEval-S e 92,0% LoCoMo, e redução de correcções humanas nos agentes de programação sem ganho evidente na taxa de tarefas resolvidas nesse dataset. Issue #4568 descreve timeouts de reflect após upgrade, com resposta de maintainer e mitigação por configuração, fechado em 2026-09-28. Medir tempo/custo e qualidade por tarefa, não apenas fact recall.
  - https://vectorize.io/benchmarks
  - https://github.com/vectorize-io/hindsight/issues/4568
5. **Letta, custo de acumular passagens.** Pedido de deduplicação/consolidação archival #3116 foi encerrado como não planeado; investigar capacidade real nas versões actuais antes de interpretar como limitação permanente.
  - https://github.com/letta-ai/letta/issues/3116

## Cuidados com benchmarks públicos
- Scores entre fornecedores não são comparáveis sem manter **o mesmo dataset, modelo de resposta, juiz, budget de retrieval, prompts, hardware e condição de execução**.
- O benchmark comunitário de Setembro 2026 demonstra variação considerável numa configuração comum e mostra um baseline de desempenho distinto do marketing; há limitações de amostra e avaliação.
  - https://github.com/hamza-dev-tech/agent-memory-bench
- STATE-Bench (Microsoft, Maio 2026) propõe medir conclusão consistente de tarefas empresariais em vez de só recordação; incluir como referência do laboratório.
  - https://opensource.microsoft.com/blog/2026/05/19/introducing-state-bench-a-benchmark-for-ai-agent-memory/
- Linhas de avaliação que sugerimos: `recall_all@k`, precisão e `abstain`, validade temporal/contradição, controlo inter-tenant, continuação após falha, custo por tarefa, tempo p50/p95, custo de ingestão, proveniência, intervenção humana e replay sem duplicação de efeito externo.

## Hipóteses de diferenciação (NÃO VALIDADAS)
- H1 **Verified Operational Continuity**: task/handoff/evidence que distingue claims de fatos verificados e autoridade, independentemente do modelo/agent runtime.
- H2 **Memory Quality & Temporal Truth**: proveniência, consolidação, invalidação temporal, confiança sustentada em fonte, prevenção de feedback loops e recuperação de decisões revogadas.
- H3 **Private Enterprise Intelligence**: implantação local com controlo inter-tenant seguro, políticas, auditoria e custos rastreáveis.
As três têm concorrência parcial, logo vantagem só pode ser reivindicada após benchmarks e entrevistas com clientes.

## Design de investigação R2 (proposta, não executada)
**Matriz de soluções:** baseline handoff Markdown + PostgreSQL pesquisa exacta/FTS; Mem0 OSS pinned; Hindsight; Graphiti; Letta se tiver adapter compatível. Temporal/LangGraph/A2A avaliados em ensaios *de continuidade e interoperabilidade*, não no mesmo ranking de memória.
**Casos sintéticos:** factos simples, alterações de decisão ao longo do tempo, nomes exactos/IDs, informações contraditórias, fontes falsas, alteração de proprietário, permissões entre organizações, falha e recuperação de tarefas, lease expirado, duplicação de execução externa e recusa do desconhecido.
**Método justo:** modelos e prompts iguais na comparação de recuperação; separar memory ingest, retrieval, answer synthesis e decisão de execução; capturar hashes/configurações, tempos, tokens, custo e evidência de tool results. Controlo experimental e repetição; sem dados reais privados no repo público.
**Evidência:** métricas com amostra e denominador, tracing sanitizado por cenário, issues reproducíveis, scores recalculáveis e avaliação cega por humanos quando necessário.
**Benchmark ainda NÃO EXECUTADO** pela RIGHTWARE.

## Prioridades operacionais propostas
P0 — inventário de features+licenças+issues das 5 soluções (fonte e pin), reprodução controlada de 2 cenários de continuação e isolamento; reparar primeiro quaisquer P0 de segurança existentes no núcleo.
P1 — corpus sintético e baselines de memória; instrumentos de observabilidade e avaliação de erros em extração, consolidação, recuperação e resposta.
P2 — 5–10 entrevistas exploratórias com equipas que usam múltiplos agentes para validar procura e disposição para pagar; nenhuma afirmação de procura validada.
P3 — decisão formal BUILD vs INTEGRATE vs REUSE vs REJECT por componente, assente em métricas.

## Estado RIGHTWARE confirmado, 2026-11-12
- Repositório público `rightware-corporations/rightware-shared-intelligence`; `develop` para trabalho, `main` como release aprovada; seis Draft PRs históricos retidos.
- CI run https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43119637429 em develop foi SUCCESS antes deste relatório. Não é prova de benchmarks externos.
- Runtime actual: adapter + camada PostgreSQL de tarefas/handoffs, REST autenticada, MCP read-only, Mem0 OSS/Ollama/pgvector testados com dados sintéticos. Sem Jarvis/PULSE em produção.
- Não fazer merge para main, não acrescentar dados privados, não chamar doc de release.
- A investigação de SI-RD-01 **não alterou o motor Mem0 nem executou benchmarks**, não avaliou estatisticamente clientes e não aprova a H1/H2/H3.

## Próximo gate proposto
SI-RD-02 — Matriz de concorrentes por capacidade e implementação (COMMERCIAL CLAIM / SOURCE CODE / VERIFIED THIRD PARTY / RIGHTWARE TEST); registo de versões/licenças, comparação de pipelines e corpus sintético operacional; decidir primeiro o *baseline* e as 2 hipóteses que justificam provas reproduzíveis.
