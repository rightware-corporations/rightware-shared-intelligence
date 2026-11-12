# WORK-03B R0 — UC-CORE-01, matriz de aceitação e plano de execução

> **Hierarquia:** o contrato R0 canónico e executável é `docs/work03b/UC_CORE_01_CONTRACT.json` (10 rotas existentes, 7 futuras, 14 passos, M01–M18). Este documento é arquitectura explicativa/visão mais ampla, NÃO adiciona novas rotas oficiais. Ver `05_CANONICAL_CONTRACT_ALIGNMENT.md`.


**Estado:** TEST CONTRACT / PROPOSTA, não execução real. Primeiro caso que realmente prova a visão.
**Objetivo do MVP:** **dois agentes autorizados, duas sessões distintas e uma interrupção real**; B recupera tarefa, estado, contexto e evidências sem possuir o chat de A. Não usar dados privados nem o Jarvis de produção.

## UC-CORE-01: “Continuar o trabalho de outro agente com segurança”

### Actores e ambiente
- Organização fictícia \`rw-synthetic\`.
- Projecto \`alpha\`, outro projecto \`beta\` com dados de controlo negativos.
- \`operator\` humano/administrador de alpha.
- \`agent-a\` e \`agent-b\`, credenciais distintas, processos/hosts simulados independentes.
- \`intruder\` de beta sem grants de alpha.
- \`verifier\` serviço restrito que só pode ler Git/CI fixtures ou APIs autorizadas.
- \`reviewer\` com permissão de revisão distinta dos agentes executores.
- Backend FastAPI/WorkCore PostgreSQL + optional Mem0/Ollama; reinício de servidor e clientes no meio da sequência.

### Cenário integral, observável
| Passo | Evento esperado | Fonte canónica | Critério concreto |
|---:|---|---|---|
| 01 | Operator regista objectivo e critérios | WorkItem PostgreSQL | READY vN e criteria_version explícitos |
| 02 | Agent A autentica, assume lease | Principal/Grant/Lease | A é único writer; B/intruder negados |
| 03 | A abre AgentRun com id estável | AgentRun | actor+start+correlation |
| 04 | A lê contexto e refs de decisão vigente | Postgres + Mem0 opcional | sem item beta, distinção trust |
| 05 | A realiza trabalho determinístico | host de A (ferramenta de teste) | receipt/fixture verificável; nenhum side effect real |
| 06 | A regista Observations + SourceRefs | Postgres | ASSERTED, author/revision/visibility presentes |
| 07 | A grava Checkpoint: feito, pendente, blockers, refs | Postgres | imutável/versão/hash, critérios não promovidos a PASS |
| 08 | A oferece Handoff explícito para B | WorkCore + Handoff | task BLOCKED, A lease inválida, binding checkpoint |
| 09 | Processo A termina/é morto | harness | sem dependência do estado RAM nem chat original |
| 10 | B inicia novo processo/credencial | auth/Principal | identidade diferente; A token não reutilizado |
| 11 | B aceita Handoff e obtém lease nova | WorkCore | exact one writer/fencing; double accept falha |
| 12 | B pede \`resume\` | Continuity API | objectivo, critérios, último checkpoint, evidências/decisões, unknowns, watermark |
| 13 | B tenta acção com snapshot antigo | WorkCore | conflito explícito, refresh necessário |
| 14 | B continua acção autorizada e grava receipt | integração de teste | não duplica side effect, reconciliável |
| 15 | B submete artefacto + EvidenceRef | Trust/Evidence | task IN_REVIEW, não DONE |
| 16 | Verifier confirma teste delimitado | Verification | PASS para job/commit verificado, não conclusão global |
| 17 | Reviewer aceita/rejeita | Review/WorkCore | DONE somente após autorização + critérios |
| 18 | Simula Mem0 down, revogação, Beta e novo restart | API/Postgres/Outbox | canonical resume legível; index offline explícito; nenhum vazamento |
| 19 | A revê histórico sem violar grants | Event/WorkItem | cada transição rastreável por event_id/actor/version |
| 20 | Human/CI gera pacote de handoff sanitizado | ContinuationPackage | fonte/version/hashes e próximo passo, sem segredo em Git |

**Passo 17 não será suportado até R2; não declarar UC-CORE-01 PASS só por executar 1–12.** O produto pode ter uma milestone R1 parcial, mas MVP completo exige 1–20.

## UC-CORE-02: Recuperação semântica segura

**Input:** dois factos sintéticos contraditórios com datas e fontes; decisão vigente D-2 substitui D-1. Retrieval de Mem0 pode trazer ambos. **Esperado:** resposta evidencia D-2 como autoridade actual, D-1 como SUPERSEDED, e candidatas de memória como UNVERIFIED. Se source está indisponível, não inventar aprovação.

## UC-CORE-03: Origem revogada

Uma memória de alpha indexada inicialmente tem fonte cujo grant/consentimento foi revogado. Após invalidação, principal sem grant não pode recuperar via search, snapshot antigo ou MCP. O sistema devolve informação de redaction/unavailable, não o conteúdo. O índice pode ter consistência eventual; **exposição em caches deve ser bloqueada na policy layer imediatamente**, mesmo antes do purge físico.

## UC-CORE-04: Crash durante efeito externo

Agent A invoca operação externa idempotente, serviço responde tarde, A cai antes do receipt. Agent B retoma, vê ExternalEffect INCONCLUSIVE e consulta fornecedor externo; não reexecuta por default. \`duplicate_external_effects=0\` em fixture onde fornecedor suporta idempotência. Se fornecedor não permite consulta/idempotência, alerta e bloqueia execução automática.

## UC-CORE-05: Jarvis como consumidor opcional

Jarvis staging fica sem Shared Intelligence por default. Após opt-in, obtém apenas \`get_task/context/resume_readonly\` de projecto autorizado. Desligar a rede SI ou expirar token não impede iniciar/usar o Jarvis local. Não mover memória pessoal de Issa sem consentimento. Só declarar integração validada após teste em ambiente isolado, pin de host e rollback confirmado.

## Critérios de aceitação baseados nos M01–M18 originais

Abaixo, **gate pretendido** (não são resultados executados). Mapear evidência real por cenário.

| ID | Meta R1/R2 | Resultado obrigatório |
|---|---|---|
| M01 | R1 | create, publish, claim → single lease, versões correctas |
| M02 | R1 | observação+fonte ASSERTED, nunca DONE |
| M03 | R1 | Handoff OFFERED vinculado a checkpoint, A sem lease, BLOCKED |
| M04 | R1 | B ACCEPTED adquire nova generation, A stale token falha |
| M05 | R1 | \`resume\` num processo B diferente com refs/version/ACL correctas |
| M06 | R2 | submissão com EvidenceRef passa para IN_REVIEW |
| M07 | R2 | verificador independente + reviewer; somente autoridade aceita DONE |
| M08 | R1 | expected_version stale 409 sem alteração |
| M09 | R1 | mesmo idem key + body não duplica side-effect; lease token perdido requer protocolo seguro de recovery, não storage |
| M10 | R1/R2 | deny interproject read/write/search/snapshot/MCP, zero content leakage |
| M11 | R1 | double handoff accept ou concorrência → único lease |
| M12 | R1 | Mem0 down → canonical \`resume\` e audit disponíveis com degraded flag |
| M13 | R2 | consent/access revoked → zero disclosure por snapshot/cache/índice |
| M14 | R2 | prompt injection em observação/memória não vira ferramenta/estado |
| M15 | R2 | Evidence source/hash/criteria mismatch → FAIL/INCONCLUSIVE, nunca DONE |
| M16 | R1/R2 | kill/restart e outbox retry → pending work reconstruído, sem duplicar efeitos |
| M17 | R1 | REST e cliente MCP separado recebem mesmo actor-scoped state |
| M18 | R2 | evento e idempotency correlation para toda mutation sem segredos |

Todos M01–M18 precisam evidência de execução em CI/lab. Se apenas subconjunto passar, indicar explicitamente quais foram testados, skipped, partial ou NOT_APPLICABLE. **O CI histórico 55 PASS não avalia todos os 18.**

## Métricas verificáveis — não prometer números antes de medir

- \`handoff_correctness\`: aceitações correctas / tentativas válidas.
- \`resume_reconstruction_accuracy\`: campos e refs canónicos correctos / ground truth verificável.
- \`false_approved_completions\`: tem de ser 0 na suite de segurança.
- \`cross_project_leakage\`: tem de ser 0 para cenários de teste.
- \`duplicate_external_effects\`: tem de ser 0 em fixtures que permitem idempotência.
- \`memory_staleness\`: outbox watermark lag por origem e destino.
- \`memory_retrieval_precision@k\`, \`recall@k\`, \`abstention_accuracy\`: laboratório SI-RD-03 com corpus ampliado.
- \`resume_latency_p50/p95\` e \`indexing_latency_p50/p95\` sob perfil de hardware reproduzível.
- \`unknowns_exposed\`: percentagem de casos com fontes ausentes/contradições corretamente reportadas.

Não comparar estas métricas com marketing de fornecedores se dataset e condições diferirem.

## Plano por pequenos checkpoints que geram valor

### R0A — Map & ratify (document-only)
- Resolver decisões essenciais, classes de dados, actors/grants, ownership PULSE, critérios de DONE, consentimento default e comportamento resume offline.
- Fixar contrato API/schema mínimo, com review humano e exemplos sintéticos.
- Validar manualmente os oracles de UC-CORE-01 e definir teste red-team mínimo; publicar gap report por aceitação M01–M18.
- **Saída:** artefactos de contrato aprovados/revistos. Não confundir proposta com aprovação.

### R1A — Observations + sources + AgentRun
- Additive SQL migrations; API write com principal, grant, lease e idempotency.
- Testes de fonte sem consentimento e cross-project, versão/recuperação de observações.
- Mem0 ainda pode permanecer disabled; primeiro usar PostgreSQL exact read.

### R1B — Checkpoint + continuation package
- Checkpoint imutável de fontes/criteria, \`resume\` canónico e manifest com policy/time/watermark; dois clientes independentes.
- Teste de kill/restart A, B sem chat e Mem0 down; zero confiança automática em resumo de modelo.

### R1C — Handoff com checkpoint + token recovery
- Vincular o handoff existente ao checkpoint, fencing e stale-write; nova lease B.
- Corrigir lost-response recovery com rekey/fencing em transação auditada; testar concorrência e retries.

### R1D — Outbox + memória contextual consentida
- Publicar eventos controlados para indexação, \`memory:write\` com proveniência e consent/policy; habilitar Mem0 adaptador.
- Reprocessar por event ID; observar watermark e persistência de fontes; impedir leak antes do purge.

### R2A — Evidence & verification
- Verificador read-only de Git commit/CI de origem permitida, payload/hash/check spec; verificações PASS/FAIL/INCONCLUSIVE.
- \`IN_REVIEW\` não vira DONE sem role distinta e critérios; API de revisão; negative tests.

### R2B — Decisions + memory lifecycle
- Decisão PROPOSED/APPROVED/SUPERSEDED com autoridade; invalidation/tombstone/retention e serialização segura de provenance.
- Conflict/stale/revocation/prompt-injection tests; formal security review.

### R3 — Acceptance/operability before deployment
- Real UC-CORE-01 1–20 com duas identidades e três processos/serviços isolados, repetir falhas e CI.
- Regressão das 55 tests atuais; 18 M tests com logs por ID e SHA.
- Depois desenho de deploy, backups/OIDC/TLS, Jarvis staging read-only e observability.

**Recomendação de prioridade:** R1A → R1B → R1C antes de novos providers. Mostra que dois agentes podem continuar trabalho mesmo com o motor semântico desligado. R1D acrescenta relevância semântica quando a base canónica está segura.

## Matriz de decisões pendentes do operador

| Decisão | Proposta default | Por que precisa de ratificação |
|---|---|---|
| Primeiro utilizador | agentes de desenvolvimento da RIGHTWARE (duas sessões) | Caso de uso real e visibilidade de evidências |
| Escopo task | mínimo WorkItem/Run; PULSE dono dos seus tasks | Evitar duplicação |
| Escrita de memória | explícita e consentida; nenhum chat privado auto-synced | Privacidade e qualidade |
| Conclusão DONE | reviewer humano autorizado no primeiro MVP | Evitar auto-approval e falso sucesso |
| Fonte de verdade | PostgreSQL RIGHTWARE por tarefa SI; origem externa por alias | Evitar conflitos de ownership |
| Provider de memória | Mem0 pinned até benchmark SI-RD-03 | Já funcional e substituível |
| Segundo provider | Hindsight em laboratório, Graphiti se temporal justificar | Custo/licença/complexidade |
| Estrutura do backend | monólito modular + REST/MCP | Reusar código e CI |
| Primeiro cliente | probe independente, depois Jarvis staging read-only | Preservar produção |
| Deployment | após cenário de continuidade e segurança aceites | Evitar pôr em produção fluxo incompleto |

Sem ratificação, estas linhas ficam como RECOMMENDATION. Nenhum requisito deve ser apresentado como decisão oficial não concedida.

## Riscos de execução a vigiar
- Criar demasiado trabalho administrativo em SI sem dar valor ao agente.
- Modelos fabricarem “fait accompli” num checkpoint, sem verifier.
- Confundir Git SHA imutável com prova da aceitação dos critérios.
- Duplicação de PULSE ou ingerir dados privados de clientes.
- Ficar preso a fornecedor de memória antes de benchmark.
- Realocar novamente a árvore de pastas sem implementação útil.
- Não registar cada output no MASTER e HANDOFF, quebrando a regra de continuidade da RIGHTWARE.

**Conclusão técnica do R0:** Se UC-CORE-01 completo não funciona num laboratório com dados sintéticos sem depender do chat de A, o Shared Intelligence não cumpriu ainda a sua promessa de produto, mesmo que o Mem0 retrieval esteja a funcionar.
