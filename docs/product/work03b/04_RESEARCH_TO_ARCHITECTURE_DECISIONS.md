# WORK-03B R0 — Aplicação da investigação: reutilizar, integrar, construir ou adiar

**Status:** síntese de design proposta, não decisão empresarial de compra/licença/migração.
**Fontes internas:** SI-RD-01 landscape; SI-RD-02 source-code matrix; SI-RD-02E Perplexity triage; SI-FG-01 funcional; WORK-01 e código actual. Actualizar esta matriz se benchmark SI-RD-03 contradisser premissas.

## 1. Porque não começar por tecnologia?

A pergunta técnica principal não é “qual é a melhor framework de memória?”. É:

**“Consigo entregar a um agente B, depois do desaparecimento de A, uma continuação segura, explicável e verificável — com o estado persistente, com a memória correcta, sem duplicar efeitos e sem permissão indevida?”**

Memória sem continuidade fica incompleta; continuidade sem factos e evidência gera falsa certeza; demasiadas frameworks produzem custo e pouca melhoria. Por isso a arquitectura separa **source-of-truth**, **memory provider**, **runtime de agentes**, **integrações** e **verificação**.

## 2. Adopção faseada

| Tecnologia/ideia | Investigação confirma | Decisão recomendada | Quando testar/reutilizar |
|---|---|---|---|
| PostgreSQL transactions + optimistic versions | WorkCore em produção de laboratório, E2E real sintético | **KEEP** núcleo autoritativo; estender additively | WORK-03B R1A–R2 |
| Mem0 OSS pinned | add/search e embeddings Ollama reais já passaram no laboratório | **KEEP** adapter; não substituir ainda | R1D e SI-RD-03A |
| Hindsight (MIT, confirmação transitiva pendente) | Retain/Recall/Reflect, memory defense, BM25/temporal/semantic no código auditado | **EVALUATE** provider isolado, não instalar no runtime já | SI-RD-03A retrieval controlado |
| Graphiti | temporal edges + episódios, provenance e retrieval combinado | **EVALUATE** se temporal contradictions falharem baseline mais simples | R2 benchmark opcional |
| Letta Code | Git-backed memory, resumption/context patterns | **LEARN** mecanismos/versioning, não importar harness inteiro | desenho de ContinuationManifest |
| LangGraph | runtime checkpointing, durable execution por modo | **LEARN/COMPARE** se WORK-03B R1B/R1C não resolver restart/replay | durabilidade track isolado |
| Temporal | retry, activity receipt, workflow durability | **EVALUATE** apenas se orchestration complexa o exigir | R3, nunca exigência MVP |
| DBOS Python | workflows duráveis usando PostgreSQL | **EVALUATE** alternativa ao Temporal depois de benchmark | SI-RD-03 continuity track |
| A2A | Task/contextId/artifact/streaming; mensagens podem ser transitórias | **ALIGN PROTOCOL LATER** sem usar mensagem como audit | integração terceiros depois de MVP |
| MCP v2 stdio | ferramentas REST-backed read-only testadas | **EXTEND CAREFULLY** às mutations com mesmo ACL | WORK-03B R1, depois vendor client |
| SoMem | paper+code promissores para memória documental linkada | **RESEARCH** pipeline sem importar código por promessa | SI-RD-03B documental |
| XTDB, LadybugDB, sqlite-vec, LanceDB, etc. | candidatos e licenças preliminarmente triados | **DEFER** sem problema claro a resolver | depois de benchmark baseline |
| OTel conventions / W3C PROV-O | campos rastreáveis e provenance | **LEARN/APPLY MINIMAL FIELDS** | R1A e R2A |
| React/Vite frontend | possibilidade de gestão humana | **DEFER** até ter review/grants visíveis | pós R2 (admin piloto) |
| n8n | gatilhos/orquestração por API | **OPTIONAL** integração, não base de dados | pós R1, se tiver cenário |
| Jarvis production | consumidor alvo já em operação, sem integração | **PROTECT**; staging opt-in read-only primeiro | após R2/R3 gates |

## 3. O que é propriedade intelectual legítima da RIGHTWARE?

**Candidato a diferenciação e produto próprio:** modelo canónico de work continuity, política/autoridade por projecto, packaging de estado/evidências com proveniência, handoff versionado e restituição determinística, fluxos de revisão com recibos externos, compatibilidade entre clientes. O código Python/SQL original correspondente, regras e schemas são geridos pela RIGHTWARE.

**Não reivindicar como exclusivo:** extracção semântica, embeddings, retrieval híbrido, grafos temporais, checkpointing, OAuth, A2A/MCP, audit logs ou “memory defense” em abstracto. Outras soluções já têm estas capacidades. A vantagem é **a implementação verificável e o produto integrado**, se provarmos utilidade/custo/segurança.

**Licenças:** não copiar código upstream para ficheiros próprios sem revisão de licença, avisos e derivados. Manter \`vendor/mem0\` no pin actual e preservar atribuição. Licença da repo principal não equivale à licença de todas as dependências ou modelos.

## 4. Evidência e desconfiança disciplinada

A investigação Perplexity de 11 páginas foi classificada como \`SI_RD_02_PARTIAL\`; nomes, rankings e scores corrigidos não são critério formal de adopção. Os principais sistemas foram lidos em código pela SI-RD-02 com SHAs, mas desempenho e bugs de versões não foram replicados. A taxonomia e links externos são pistas de pesquisa.

Critérios para promover EVALUATE a ADOPT:
1. Código fixado e auditoria de licença/transitive deps.
2. Mesma fixture e top_k com ground truth independente; resultado reproduzível.
3. Nenhuma divulgação cross-project ou promoção de memória a autoridade.
4. Custos operacionais e latência medidos; RAM/GPU e modelo fixados.
5. Integração por interface pequena, com rollback e sem bloquear backend canónico.
6. Melhoria prática num caso de uso importante comparada com PostgreSQL+Mem0.

Scores dos vendors, likes e opiniões não substituem estes gates.

## 5. Posicionamento do MVP

**Segmento inicial proposto:** equipas de desenvolvimento da RIGHTWARE que alternam agentes/sessões, sofrem perda de contexto e exigem evidência de execução. Isto é hipótese de primeiro utilizador, não validação comercial.

**Proposta de valor para o primeiro piloto:** menos reconstrução manual; handoff mais fiel; registos claros de que tarefa/versão/artefacto foi aceite; menos falsas afirmações de “tudo concluído”; auditabilidade e privacidade entre projectos.

**O que não vender/afirmar ainda:** plataforma pronta para todas as IAs, agentes com execução autónoma geral, memória perfeita, zero erros em produção, exactly-once de APIs externas ou vantagem comercial comprovada.

**Seguinte decisão de produto:** rever a jornada UC-CORE-01 e 18 critérios de aceitação; depois construir apenas o vertical R1A–R1C. Investigar alternativas em laboratório separado, para não congelar a execução enquanto surgem novos papers.

## 6. Backlog imediato proposto (se aprovado)

- CONTRACT-01: actor/tenant/resource permission + explicit data/consent classes.
- CONTRACT-02: AgentRun/Observation/SourceRef canonical field/validity schemas.
- CONTRACT-03: checkpoint versioned + ContinuationManifest freshness policy.
- CONTRACT-04: handoff bind-to-checkpoint and new-run resume guarantees.
- CONTRACT-05: lease recovery/reassignment after missing secret response.
- CONTRACT-06: evidence verifier/reviewer separation and decision supersession.
- CONTRACT-07: memory projection outbox + update/delete/revoke semantics.
- CONTRACT-08: synthetic two-agent E2E acceptance + negative trust/security tests.
- EVAL-01: SI-RD-03A baseline retrieval PostgreSQL vs pinned Mem0 vs Hindsight.
- EVAL-02: SI-RD-03B SoMem temporal/source-linked evidence study.

Cada contrato deve ter definição de pronto (schema/API/migration/negative tests) e cada output deve actualizar ambos os handoffs. Nenhum é implementado por este documento.

## 7. Estado e próximos passos

**Recomendação:** submeter ao operador R0A como baseline funcional de MVP; manter as políticas oficiais de branches, handoffs, protecção do Jarvis e prioridade a segurança. Nenhum deployment antes de UC-CORE-01 ter prova completa.

**Artefactos deste pacote:** \`00_PRODUCT_OPERATING_PRINCIPLE.md\`, \`01_COMPONENT_DOMAINS_BOUNDARIES.md\`, \`02_DOMAIN_PROTOCOL_SECURITY_CONTRACTS.md\`, \`03_UC_CORE_01_ACCEPTANCE_AND_EXECUTION.md\`, esta matriz e registo no MASTER/CURRENT.
