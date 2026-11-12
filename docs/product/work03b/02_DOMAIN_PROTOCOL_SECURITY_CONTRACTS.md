# WORK-03B R0 — Contratos de dados, estados, APIs e segurança (proposta v0.1)

> **Hierarquia:** o contrato R0 canónico e executável é `docs/work03b/UC_CORE_01_CONTRACT.json` (10 rotas existentes, 7 futuras, 14 passos, M01–M18). Este documento é arquitectura explicativa/visão mais ampla, NÃO adiciona novas rotas oficiais. Ver `05_CANONICAL_CONTRACT_ALIGNMENT.md`.


**Estado:** SPEC / PROPOSTA, não código nem migração. Fonte do princípio de funcionamento: \`00_PRODUCT_OPERATING_PRINCIPLE.md\`.
**Regra:** conservar REST+MCP e WorkCore existentes; qualquer extensão é aditiva e requer testes de regressão.
**Versão de esquema proposta:** Continuity Contract v0.1, ainda não ratificado.

## 1. Identidade do trabalho — nunca confundir

- \`organization_id\`: tenant, autoridade de isolamento.
- \`project_id\`: scope de trabalho e autorização.
- \`principal_id\`: identidade autenticada de humano/serviço; \`agent_id\` é identificador lógico, não credencial.
- \`work_item_id\`: objectivo persistente mesmo que vários agentes e sessões trabalhem nele; pode apontar a origem externa.
- \`agent_run_id\`: execução concreta, instância de agente/cliente, com início, fim e correlação.
- \`checkpoint_id\`: declaração versionada do ponto de retoma criado por um run.
- \`handoff_id\`: oferta/aceitação de transferência de responsabilidade; diferente de um Markdown handoff.
- \`continuation_manifest_id\`: referências atuais/versões fornecidas num momento, com ACL revalidada ao entregar.
- \`source_record_id\`: fonte tipada com revision/digest e owner.
- \`observation_id\`: alegação ou resultado observado; não aprovado por default.
- \`evidence_id\` / \`verification_id\` / \`review_id\`: referência → verificação delimitada → aceite autorizado.
- \`event_id\` / \`outbox_id\`: commit canónico e intenção de projectar/notificar.
- \`memory_projection_id\`: item indexado com ligação de volta a fonte canónica e estado de invalidação.

## 2. Estados propostos (deverão coexistir com WORK-02A)

### WorkItem (task)
\`DRAFT -> READY -> IN_PROGRESS -> IN_REVIEW -> DONE\`, com \`BLOCKED\`, \`CANCELLED\` e retorno \`IN_REVIEW -> IN_PROGRESS\` apenas por revisão. DONE apenas após critérios e revisão; cancelamentos auditados.

### AgentRun
\`CREATED -> ACTIVE -> CHECKPOINTED -> SUSPENDED | COMPLETED | ABORTED\`. Um processo/crash sem mensagem explícita pode deixar \`ACTIVE\` vencido; detector de lease marca \`LOST_HEARTBEAT\` como sinal operacional e inicia reconciliação, **não** reexecuta ferramentas autonomamente.

### Handoff
\`OFFERED -> ACCEPTED | DECLINED | REVOKED | EXPIRED\`. Aceitar obtém lease com fencing em transação. Não existe estado \`APPROVED\` para handoff.

### Observation
\`ASSERTED -> SOURCE_LINKED -> REVIEWED\` é possibilidade de enriquecimento, mas **nunca** herda autoridade de decisão; informação pode ser \`SUPERSEDED\`/\`RETRACTED\`. Um novo Event aponta para observação anterior sem destruir proveniência.

### Evidence/Verification
\`REFERENCED -> QUEUED -> CHECKING -> PASS | FAIL | INCONCLUSIVE\`. PASS descreve o check específico, não significa que o work item está DONE.

### Decision
\`PROPOSED -> APPROVED | REJECTED\`; uma decisão aprovada pode ser \`SUPERSEDED\` apenas por outra decisão autorizada. Conteúdo de memória semanticamente semelhante não substitui decisão.

### Projection
\`PENDING -> INDEXED | RETRYING | FAILED | INVALIDATED\`; reader expõe watermark/lag, não usa PENDING como se já fosse memória disponível.

## 3. Contratos REST propostos (NÃO endpoints existentes)

**Padrão:** \`Authorization\` + \`Idempotency-Key\` em writes + \`expected_version\` se agregado; \`trace_id/correlation_id\` de servidor; \`403\` forbidden, \`404\` unknown, \`409\` state version, \`422\` schema, \`503\` dependent optional unavailable. Um cliente não pode passar \`principal_id\` como autoridade.

| Endpoint conceitual | Permissão proposta | Saída/verificações |
|---|---|---|
| \`POST /v1/projects/{p}/work-items/{id}/runs\` | \`run:start\` | AgentRun + versão; actor é o token |
| \`POST /v1/projects/{p}/work-items/{id}/observations\` | \`observation:write\` + active lease | Assertion/SourceRef/Event, sempre não aprovado |
| \`POST /v1/projects/{p}/work-items/{id}/checkpoints\` | \`checkpoint:write\` + active lease | checkpoint imutável com referências e criteria, checkpoint_version |
| \`POST /v1/projects/{p}/work-items/{id}/handoffs\` | \`handoff:offer\` + active lease | Handoff vinculado ao checkpoint versionado, transação já existente estendida |
| \`POST /v1/projects/{p}/handoffs/{id}/accept\` | \`handoff:accept\` + target binding | nova lease, generation; não devolver raw secret reusável em idempotency store |
| \`GET /v1/projects/{p}/work-items/{id}/resume\` | \`context:read\` + \`task:read\` + source ACL | pacote com state/checkpoint/decisions/unknowns/semantic + freshness |
| \`POST /v1/projects/{p}/work-items/{id}/evidence\` | \`evidence:submit\` + active lease | referência e claims a verificar; sem PASS automático |
| \`POST /v1/projects/{p}/evidence/{id}/verify\` | \`evidence:verify\` (service verifier) | verificação apenas do check declarado |
| \`POST /v1/projects/{p}/work-items/{id}/reviews\` | \`review:accept\` (separado do actor) | revisão e transição DONE condicionada |
| \`POST /v1/projects/{p}/memory/records\` | \`memory:write\` + consent | fonte autoritativa + outbox; NÃO gravação Mem0 directa |
| \`POST /v1/projects/{p}/memory/{id}/invalidate\` | \`memory:correct\` / \`memory:delete\` | tombstone e purge de projecções, auditado |
| \`GET /v1/projects/{p}/memory/retrieval\` | \`memory:read\` + resource ACL | candidatos semânticos com provenance/trust |
| \`POST /v1/projects/{p}/tasks/{id}/lease/recover\` | \`lease:recover\` controlado | invalidar lease antiga; criar nova generation; recuperação auditada |
| \`GET /v1/projects/{p}/events?cursor=...\` | \`audit:read\` | eventos canónicos paginados, classificação e ACL |

**Compatibilidade:** as operações WORK-02A existentes continuam estáveis; novos endpoints podem reutilizar \`tasks/{id}\` em vez de criar \`work-items\` no MVP. A tabela acima não constitui decisão de renomear API.

## 4. Contratos MCP propostos (mesmas operações, mesma política)

MCP stdio actualmente expõe apenas \`get_task\`, \`get_task_events\`, \`get_project_context\`. 
- Fase R1: \`record_observation\`, \`checkpoint_work\`, \`offer_handoff\`, \`accept_handoff\`, \`resume_work\`, \`get_continuation_package\`; todas passam pela API REST e actor token, sem superpoderes.
- Fase R2: \`submit_evidence\` possível; \`verify_evidence\` apenas credencial verificador; **não expor** \`approve_decision\` ou \`complete_task\` genericamente a qualquer cliente modelo.
- O servidor valida origem, request scope e project grants para cada tool. A2A opcional poderá adoptar \`taskId/contextId/artifact\`, sem trocar a persistência de eventos.

## 5. Exemplo: input de checkpoint (todos os valores sintéticos)

\`\`\`json
{
  "work_item_id": "T-001",
  "run_id": "RUN-A-4",
  "expected_task_version": 8,
  "criteria_version": 2,
  "progress": [
    {"criterion_id": "C1", "reported": "completed", "source_ref": "SRC-1"},
    {"criterion_id": "C2", "reported": "pending", "reason": "integration tests missing"}
  ],
  "observations": ["OBS-7"],
  "evidence_refs": ["EV-5"],
  "blockers": ["Review CI configuration for Windows compatibility"],
  "next_actions": [{"action": "run_tests", "side_effect_class": "read_only", "preconditions": ["source_rev=abc"]}],
  "source_refs": [{"id": "SRC-1", "revision": "sha256:abc", "classification": "internal"}],
  "resume_policy": {"target_principal": "agent-b", "expires_at": "2026-11-13T12:00:00Z"}
}
\`\`\`

A API valida que o actor possui lease ativa, que os source_refs pertencem ao projecto autorizado, que a versão é actual e que critérios \`reported=completed\` não viram automaticamente \`verified\`. Em caso de alteração de versão, falhar sem modificar estado.

## 6. Erros e concorrência — matriz de invariantes

| Invariante | Aplicação | Comportamento esperado |
|---|---|---|
| actor autenticado | Todas as APIs/MCP | 401/403; ignorar identity no body como autoridade |
| tenant/project/resource grant | Todo recurso, incluindo source refs | Deny; nenhum conteúdo de outro projecto no erro |
| expected_version | Transições e checkpoints com lease | 409 sem lost-update |
| single active writer | Claim/handoff/renew/recover | fencing generation e no stale-write |
| owner recheck at resume | Snapshot/render | filtrar/remover refs revogados, informar redaction |
| provenance | Observation e Evidence | armazenar source id+revision/hash, claimed vs observed |
| evidence separation | Reviewer/Verifier | agente executor não se autoprova; no DONE by memory |
| no replayable token-at-rest | Idempotency/lease recovery | segredo de lease nunca é retornado numa reexecução genérica |
| outbox reliability | Projector | DB commit não depende de Mem0; retry idempotente |
| deletion | Memory index + caches | invalidar/limpar, com política documentada de audit minimal |
| hostile source | Memory retrieval | conteúdo não pode virar system prompt/tool call |
| external side effects | Tool/operation receipt | at-least-once + idempotency/reconcile, jamais garantia universal de exactly-once |
| unavailable memory | Context response | canonical task/checkpoint semântica degraded explicitamente |
| audit integrity | Event transitions | histórico com actor/time/correlation e redacção de segredos |

## 7. Continuidade após crash — sem duplicar efeito externo

Sequência:
1. Agent A envia comando externo com idempotency_key \`K\` e grava \`ExternalEffect PENDING\`.
2. O sistema externo pode executar antes do ACK. Se A morrer, o novo B não sabe de imediato se a operação sucedeu.
3. B reconsulta receipt/status no sistema externo sob identidade própria. Se confirmado, regista \`CONFIRMED\`; se impossível, \`INCONCLUSIVE\` e solicita intervenção humana.
4. Só repetir comando se idempotência/estado externo permitirem; nunca duplicar pagamento/edição só porque o LLM “não viu resposta”.
5. Snapshot e Mem0 não são provas de que um efeito ocorreu.

Este procedimento aplica os riscos de retry descritos na investigação Temporal/DBOS, sem instalar motores de workflow antes de justificar necessidade.

## 8. Segurança/privacidade: gates anteriores a produção

- Definir fonte de identidades e serviços (OIDC workload), scopes de Project/Resource e auditoria de acesso.
- Garantir consentimento da origem, taxonomia de classificação, retenção, export/apagamento, redacções e limitação de dataset.
- Chaves em secrets manager, nunca gravação no repositório público nem exposição no MCP prompt.
- Rate limiting/quotas, revogação, resource policy, encrypted backup, TLS/network segmentation e limites de tamanho de payload.
- Dados pessoalmente identificáveis não são ingestados por default; o teste R1 usa apenas casos sintéticos.
- Verificador de artefactos deve tratar URLs SSRF, redirect, downloads e autenticação; só conectores allowlisted, ref imutável e timeout.
- Verificar que Mem0 e fornecedor substituto não são fonte de authority de tenant.
- Fallback para memória indisponível mantém estado canónico e não retorna memórias de cache obsoleto por acidente.

## 9. Decisões ainda abertas (não fixar por implementação tácita)

- \`work_item\` como entidade mínima SI ou \`task\` de PULSE como autoridade externa?
- Quem pode aprovar \`DONE\` (humano exclusivamente no MVP ou verificador/role explícito em tarefas de baixo risco)?
- Quais categorias de conhecimento entram na memória derivada, e qual a política de consentimento default?
- Tokens e grant model para clientes diferentes; quais hosts MCP são suportados?
- Qual é a retenção/destruição de eventos vs dados privados; política de backup?
- Como tratar mudança de owner PULSE e conflito entre duas fontes “oficiais”?
- Qual é o critério aceitável de falha de Mem0, snapshot stale e recall para o piloto?

Antes de migrar SQL, registar estas respostas em DECISIONS.md com classificação APPROVED / PROPOSED / EXPERIMENT.
