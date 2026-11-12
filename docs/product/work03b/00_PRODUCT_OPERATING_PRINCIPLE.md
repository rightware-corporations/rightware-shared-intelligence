# WORK-03B R0 — Princípio de funcionamento e visão operacional do produto

> **Hierarquia:** o contrato R0 canónico e executável é `docs/work03b/UC_CORE_01_CONTRACT.json` (10 rotas existentes, 7 futuras, 14 passos, M01–M18). Este documento é arquitectura explicativa/visão mais ampla, NÃO adiciona novas rotas oficiais. Ver `05_CANONICAL_CONTRACT_ALIGNMENT.md`.


**Estado:** PROPOSTA ARQUITETURAL PARA REVISÃO — não é aprovação oficial do produto nem implementação.
**Data:** 2026-11-12, Africa/Maputo · **Base analisada:** develop@4c6f90feccccb30fa7a6aadb83512f18f50dfdac.
**Dependências:** SI-RD-01, SI-RD-02, SI-RD-02E (Perplexity triage), SI-FG-01, WORK-01, WORK-02A-D, WORK-03A.
**Restrição:** apenas develop/main; handoffs cumulativos; nenhum deploy/alteração de Jarvis nesta etapa.

## 1. Qual é o produto?

O **RIGHTWARE Shared Intelligence** é um **serviço independente de continuidade operacional e memória partilhada autorizada**, consumido por aplicações e agentes distintos. Não é um novo modelo fundacional, nem um clone de ChatGPT/Claude, nem uma versão nova de Jira, nem um simples banco de embeddings.

**Contrato central:** um agente pode parar, um segundo agente autorizado pode retomar exactamente o trabalho permitido, identificar o que foi pedido/feito/observado/aprovado, continuar a partir de um checkpoint reproduzível e deixar novas evidências — **sem presumir que um resumo produzido por LLM equivale à realidade**.

A unidade de valor NÃO é “memorizar conversas”; é o **Continuity Record** (registo autorizado, versionado e auditável de estado + referências + actor + próximo passo). Um **Continuation Package** (proposta de nome de produto, ainda não aprovado) é uma vista derivada desse registo, materializada apenas para o actor autorizado e com informações de actualidade/trust.

### Quem usa?
- **Operador humano:** define objectivo, aprova fontes/decisões, revoga permissões, vê divergências e aceita trabalho verificável.
- **Agente executor:** Jarvis, agente de programação, agente de operações ou sistema cliente; regista observações e checkpoints em seu próprio nome autorizado.
- **Agente sucessor:** recebe transferência de trabalho/lease e recupera pacote de continuação, independentemente de ter o chat original.
- **Verificador:** serviço determinístico/integração GitHub/CI que certifica somente o check realizado, não todo o resultado.
- **Sistema proprietário externo (ex.: PULSE):** pode continuar proprietário do seu task/issue; Shared Intelligence guarda referências e continuidade, não assume controlo dos dados da outra plataforma.

## 2. Princípios técnicos inegociáveis (propostas para ratificação)

1. **Estado antes de memória:** PostgreSQL RIGHTWARE guarda objectivo, tarefas, versões, grants, execução, decisões, eventos, evidências e handoffs autoritativos. Mem0 é índice derivado e substituível; não valida nem decide.
2. **Toda afirmação tem proveniência:** quem disse, quando, em qual execução, sobre que projecto, a partir de que artefacto/fonte, e o que foi realmente verificado. Não há “conclusão” inferida de texto persuasivo do modelo.
3. **Autoridade não é semelhança semântica:** project ID ou Mem0 user_id nunca concedem acesso. A API autentica, aplica grants e ACL por recurso, e volta a verificar antes de servir um snapshot.
4. **Uma operação, um estado transaccional:** command + version precondition + transition + evento + outbox numa transacção DB; a pesquisa semântica pode estar atrasada/indisponível sem corromper o núcleo.
5. **Continuidade não exige chat completo:** guardar checkpoints, decisões e refs/version hashes, não reproduzir automaticamente conversas privadas de fornecedores; a app cliente só fornece o que está autorizada a compartilhar.
6. **Verificar ≠ aprovar:** o agente declara; o verificador observa prova delimitada; a autoridade humana/configurada aprova. Modelos não se auto-aprovam como DONE.
7. **Falha previsível:** queda de Mem0 => modo contexto canónico reduzido; queda DB/autorização => rejeitar alterações/reads protegidos; operações externas usam idempotência e reconciliação, não promessa de exactly-once.
8. **Escolher peças existentes:** Mem0 inicialmente; testar Hindsight/Graphiti se os benchmarks justificarem; aproveitar padrões LangGraph/Temporal/DBOS se a recuperação/retry exceder o WorkCore; REST/MCP já implementados; A2A opcional para interoperabilidade futura.
9. **Privacidade por desenho:** consentimento/classificação, retenção, apagamento/revogação e redacção são responsabilidades do serviço; memória recuperada é dado não confiável e não pode injectar instruções.
10. **Modular monolith primeiro:** preservar Python/FastAPI + Postgres, adicionar módulos e contratos somente quando um caso de uso os exigir; evitar microserviços e frontend decorativo.
11. **Handoffs de engenharia e runtime são relacionados, não idênticos:** docs/HANDOFF_MASTER.md e docs/HANDOFF.md são a evidência de desenvolvimento do repositório; o produto deve emitir um pacote estruturado de continuação e poder exportar um handoff sanitizado, sem gravar memória pessoal num repo público.

## 3. Diagrama do fluxo do produto proposto

\`\`\`text
   OPERADOR                          CLIENTES INDEPENDENTES
  define objectivo        Jarvis / Claude* / ChatGPT* / coding agent / PULSE / n8n
          |                           |              |
          +---------------------------+--------------+
                                      |
                         CONTINUITY API — REST/MCP
                            auth + scoped policy
                                      |
                 +--------------------+-------------------+
                 |                     |                   |
          COMMAND/STATE           CONTINUITY           READ MODEL
          task/lease/run          checkpoint +         snapshot/context
          review/decision         handoff + source       packet + freshness
                 |                     |                   |
                 +---------------------+-------------------+
                                      |
                      POSTGRESQL AUTHORITY + EVENTS
                   authoritative state / history / outbox
                                      |
                          OUTBOX PROJECTION WORKER
                                      |
                    MEM0 adapter -> Mem0 / pgvector / Ollama
                    (unverified contextual retrieval only)
                                      |
                               source-linked candidates
                                      |
                policy re-check + conflict/supersession filter
                                      |
                     CONTINUATION PACKAGE FOR AGENT B
\`\`\`

*Claude/ChatGPT não fornecem automaticamente o seu histórico ou memória privada à RIGHTWARE. Integração depende das interfaces autorizadas disponíveis no respectivo cliente; sem conector permitido, apenas handoff explícito/manual/ficheiro/MCP sob controlo do utilizador.*

## 4. O que acontece quando um agente trabalha? (write path)

**E1 — Autenticar:** o cliente apresenta credencial; a API resolve Principal + Organização/Projecto + Scope de operação. Negação auditável. Nunca confiar em actor ID fornecido no corpo como origem de autoridade.

**E2 — Abrir execução:** criar/retomar WorkItem e AgentRun com version, expected_version, correlation ID, actor, capacidade e tempo. O WorkItem pode ser tarefa nativa mínima ou referência a tarefa externa de PULSE.

**E3 — Trabalhar:** o agente executa tarefas através das ferramentas do seu próprio runtime; Shared Intelligence não executa shell, browsing ou alterações no SO por si. Os efeitos externos são responsabilidade do sistema executante.

**E4 — Registar observação/checkpoint:** payload tipado \`Observation\` e \`Checkpoint\`: observado/feito, resultado e estado reportado, passos seguintes, bloqueios, referências e hashes, proveniência e classificação; nunca acceptar \`trust=APPROVED\` da origem.

**E5 — Commit canónico:** transacção PostgreSQL valida ACL, idempotência/version/lease, grava event e referência do checkpoint/artefacto; adiciona OutboxEvent para projecção semântica. Commit DB é a condição de sucesso da operação, não indexação Mem0.

**E6 — Projecção:** worker consome outbox com at-least-once + idempotência, filtra dados autorizados e aprovados para indexação, actualiza metadata source_ref/version/hash/scope/validity. Regista watermark/lag e retries. Se falhar, projectar depois; NÃO perder o estado canónico.

**E7 — Corrigir/superar:** uma informação antiga não desaparece silenciosamente. Revision/supersession/correction e eventual tombstone removem o dado inadequado dos índices pesquisáveis e invalidam snapshots antigos, obedecendo a políticas de retenção/eliminação.

## 5. Como acontece o handoff e o resume? (control path)

**H1 — Checkpoint seguro:** antes de sair, Agent A grava: objectivo/critério, tarefas realizadas, o que ainda falta, obstáculos, comando/artefacto seguro para retomar, source refs, evidence refs, decisões aprovadas e riscos. Um resumo de LLM sem referências permanece ASSERTED.

**H2 — Offer:** com lease válido e versão esperada, A oferece transferência para B e vincula \`CheckpointVersion\` + refs. A transacção faz BLOCKED/OFFERED e revoga a autoridade de escrita de A nesse trabalho.

**H3 — Accept:** B autentica-se como principal diferente com grant correcto; verifica preconditions/versões e aceita. O servidor atribui nova lease com fencing generation. Nunca existirão duas leases de escrita válidas simultaneamente.

**H4 — Resume em novo processo:** B pede \`resume(work_item_id)\`. A API relê estado actual, recalcula ACL, reúne último checkpoint válido, decisões aprovadas, evidências com verificação delimitada, pendências, claims não verificados, e candidatos Mem0 filtrados; devolve \`ContinuationPackage\` com \`snapshot_version\`, \`watermark\`, \`stale\`, \`missing_sources\`, \`lease\` e \`next_actions\`.

**H5 — Reconciliar antes de agir:** B não usa snapshot como nova autoridade; compara versões e estado de origem, pede refresh se necessário e só executa efeitos com autorização e chave de idempotência. Se token de lease perder-se, **não** regressar ao velho truque de expor secret da tabela; implementar reassign/recover com audit e novo fencing sob política.

**H6 — Submeter e rever:** B regista artefacto e evidência. Verificador independente confere factos específicos (ex.: commit presente, CI job passou naquela SHA); revisor autorizado decide aceitar ou pedir correcção. Só depois WorkItem chega a DONE se os critérios forem satisfeitos.

## 6. Como funciona a leitura? (read path)

**R1** Autenticar e autorizar cada consulta. **R2** Ler dados tipados do Postgres + ACL e versões atuais. **R3** Consultar Mem0 somente se o recurso/projecto permitir e o motor estiver disponível; limitar top_k, volume, classificação e fontes. **R4** Reunir candidatos em camadas de confiança: APPROVED DECISION, OBSERVED VERIFICATION, SOURCE_LINKED CLAIM, UNVERIFIED MEMORY. Não somar todos num número mágico de “verdade”. **R5** Aplicar supersession temporal, tombstones, revogação, conflitos e stale flags. **R6** Devolver pacote explícito; consumidor deve distinguir \`canonical\`, \`verified_claims\`, \`assertions\`, \`semantic_candidates\`, \`unknowns\`.

A recuperação semântica sozinha jamais controla versão ou propriedade da tarefa.

## 7. Modos de falha esperados

| Falha | Comportamento correcto (a implementar/testar) |
|---|---|
| Mem0/Ollama indisponível | Ler task, checkpoint e evidência canónicos; \`memory_status=unavailable\`, sem falsos resultados |
| PostgreSQL indisponível | Não autorizar novos writes/resumes; erro explícito, nunca “estado lembrado” como verdade |
| Lease expirada | Bloquear write, renovar/reassign com policy; nunca reutilizar token antigo |
| A morre após side effect externo mas antes de receipt | Marcar INCONCLUSIVE; consultar sistema externo por idempotency/reference antes de retry |
| Versão task divergiu entre checkpoint e resume | 409/rebuild; snapshot antigo é referência histórica, não permissões |
| Permissão revogada | Revalidar cada lookup/snapshot; não devolver recurso devido ao cache vectorial |
| Memória contraditória/obsoleta | Preferir decisão vigente e fonte canónica; exibir conflito e exigir verificação |
| Texto com “ignore as instruções...” no índice | Texto continua dado não executável; proibir promoção a ferramentas/roles |
| Pedido de apagar uma memória | Criar tombstone/mandato de remoção, limpar índices e caches; garantir política legal de event/audit minimization |
| Chat/agent host desaparece | Checkpoint persiste; novo cliente reconstitui estado canónico sem histórico privado original |

## 8. Experiência do produto — sem frontend obrigatório

**Comandos da experiência, não UI implementada:** \`start_work\` → \`checkpoint\` → \`offer_handoff\` → \`accept_handoff\` → \`resume\` → \`submit_evidence\` → \`review\`. Através de REST/MCP e de um cliente compatível, isto forma o MVP funcional. Uma webapp administrativa só se justifica para revisão/grants/auditoria após o fluxo técnico ser comprovado.

**Resultado visível ao agente B:** “Tarefa T-001, versão 9; 3/5 critérios concluídos (2 verificados), decisão D-04 vigente, handoff H-02 aceite, 2 riscos abertos, 1 fonte indisponível, próxima acção X. Estado de memória semântica = available/stale/disabled; nada foi aprovado automaticamente”.

## 9. Fronteiras e não-objectivos

- PULSE continua autoridade sobre entidades de negócio que nele nascerem; SI guarda aliases e continuidade de agentes, não sincroniza ou altera silenciosamente issue/task externo.
- Jarvis é consumidor, não dependência; mantém memória/voz/inferência locais se SI estiver fora do ar. Não recolher automaticamente memória privada de Issa nem forçar cloud/custos pagos.
- ChatGPT/Claude só partilham dados pelos meios autorizados/conectados; uma ferramenta MCP não garante acesso às suas memórias nativas.
- n8n opcional para triggers/notificações, não gestor de estado canónico; A2A pode transportar artefactos, mas mensagens transitórias não são audit log.
- Sem inventar “verdade garantida”, “exactly once externo”, “memória perfeita”, ou “integração com qualquer IA” sem testes por cliente.

## 10. Fontes técnicas e origem de princípios

- SI-RD-01/02/02E e SI-FG-01: \`docs/research/\` e \`docs/product/\`.
- Mem0 OSS em gitlink \`vendor/mem0\`, SHA f1791daa86d469249c9b002f62644d58a1eb96a0; https://github.com/mem0ai/mem0/tree/f1791daa86d469249c9b002f62644d58a1eb96a0
- Hindsight: https://github.com/vectorize-io/hindsight — candidato de memory provider, não instalado.
- Graphiti: https://github.com/getzep/graphiti — temporal retrieval a testar, não instalado.
- Letta Code: https://github.com/letta-ai/letta-code — padrões de memória Git, não dependência.
- A2A: https://a2a-protocol.org/v1.0.0/specification/ — mensagens/artifacts/task/context, não persistência garantida para todas as mensagens.
- Temporal: https://github.com/temporalio/documentation/blob/main/docs/best-practices/error-handling.mdx — idempotência necessária em actividades retry.
- W3C PROV-O: https://www.w3.org/TR/prov-o/ — Agent/Activity/Entity para campos de proveniência, não verificação de factos.
- MCP Authorization: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/basic/authorization.mdx — padrões OAuth a avaliar para clientes remotos.

**Tudo nesta proposta necessita de contratos implementados e critérios aceites antes de ser chamado de funcionalidade real.**
