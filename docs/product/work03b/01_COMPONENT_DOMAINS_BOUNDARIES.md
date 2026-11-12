# WORK-03B R0 — Componentes, domínios e fronteiras de responsabilidade

**Estado:** arquitectura recomendada para revisão, não implementação. Sem microserviços adicionais nem integrações produtivas.

## 1. Arquitectura lógica: cinco componentes internos, um backend

\`\`\`text
Client adapters (REST / MCP / futuras interfaces A2A)
             |
 API + Principal/AuthZ + RateLimit/Gates
             |
             v
   +---------+------------+---------------+
   |                      |               |
 Work/Lease         Continuity       Trust/Review
 Tasks/Handoffs     Runs/Checkpoints  Evidence/Decisions
   |                      |               |
   +----------------------+---------------+
                          |
                    PostgreSQL core
             events + outbox + versioned refs
                          |
        +-----------------+--------------------+
        |                                      |
  Index projection worker               Optional notifications
        |                                      |
 MemoryProvider interface               n8n / webhook (future)
        |
 Mem0 pinned OR replacement provider (future)
        |
 Ollama embeddings + pgvector (lab)
\`\`\`

Isto é um **monólito modular** com responsabilidades e contratos claros, não três servidores REST nem uma fusão de PULSE com Jarvis. Cada módulo pode ter subpacote Python e testes isolados, sem exigir deployment distribuído.

## 2. Domínios e ownership

| Bounded context | Responsabilidade | Guarda estado autoritativo? | Hoje | Decisão/implementação necessária |
|---|---|---|---|---|
| Identity & Policy | Principal, ServiceClient, ProjectGrant, ResourceGrant, consent scopes, issuer | Sim | Bearer/project grants básico | workload/OIDC, recursos/atributos, grants delegados, revogação de memória |
| Work & Lease | WorkItem/Task, ownership, status, optimistic version, fencing lease | Sim | Parcialmente implementado | expiry/recovery, bloqueios, reassign, aliased external tasks |
| Continuity | AgentRun, Observation, Checkpoint, ContinuationManifest, Handoff bundle | Sim | Handoff simples; sem snapshot/restart | nova implementação R1 |
| Trust & Evidence | SourceRecord, ArtifactRef, Evidence, Verification, Approval/Decision | Sim | Evidence URL não verificado | verificador Git/CI, aprovação separada R2 |
| Memory & Projection | MemoryRecord indexável, tombstone, validity, Outbox, retrieval adapters | Fonte indexável é derivada | Mem0 read demo | ingest consentido, lifecycle, outbox, provider contract |
| Integration | HTTP REST, MCP, futura A2A/SDK, eventos | Não cria autoridade extra | REST + MCP read-only | comandos write delegados com mesmos grants |
| Operations | Admin policy, maintenance, backup/restore, monitoring, metrics | Estado operacional/control plane | CI lab apenas | staging, separação ambientes, deploy, auditoria |

## 3. Autoridade e sobreposição de responsabilidades

**PULSE versus Shared Intelligence**:
- Se PULSE criou a actividade comercial/operacional, PULSE é dono do registo da tarefa e de regras de negócio; SI guarda \`external_work_ref\`, checkpoint do agente, artefactos e eventos de continuidade.
- Se o trabalho nasceu fora do PULSE, Shared Intelligence pode criar um \`WorkItem\` mínimo exclusivamente para continuidade; não acrescentar calendários, boards, sprints, SLAs, CRM ou módulo financeiro só para imitar Jira.
- Mutação de tarefa PULSE deve ser realizada por API PULSE com credenciais/autorização próprias; SI documenta a tentativa e a confirmação, sem assumir sucesso por texto de agente.
- Se um alias externo muda ou é removido, o snapshot apresenta \`external_source_unavailable\` e não inventa o status.

**Jarvis versus Shared Intelligence**:
- Jarvis executa voz/LLM/tools e mantém dados pessoais localmente ou em armazenamento próprio.
- SI expõe comandos de continuação autorizados; não executa ações do SO nem assume o motor do Jarvis.
- Se SI indisponível, Jarvis continua funções locais e apresenta “contexto partilhado indisponível”; não tenta escrever em projetos sem autorização.
- O primeiro pilot pode consultar somente dados sintéticos sem alterar Jarvis production.

## 4. Unidade mínima de informação e armazenamento recomendado

**Apenas para proposta; nenhuma migration aprovada.**

### Grupo A — identidade e limites (existente + extensão)
- \`organization(id, policy_version)\` e \`project(id, organization_id, scope)\`.
- \`principal(id, type, issuer, disabled_at)\`, \`service_client(id, principal_id, secret_ref)\`.
- \`grant(principal_id, resource_scope, action, expires_at, conditions)\`. Grants de project baseline existem, resource-level ainda não.
- \`consent_record(subject_ref, source_scope, purpose, allowed_ops, revoked_at, policy_version)\`.

### Grupo B — trabalho e execução (estado)
- \`work_item(id, project_id, origin, external_work_ref?, goal, criteria_version, status, version, owner)\`. Hoje \`si_tasks\` é o WorkItem inicial.
- \`agent_run(id, work_item_id, actor_principal_id, host_kind, tool_capabilities_digest, started, ended, last_checkpoint_id, correlation_id)\`.
- \`task_lease(work_item_id, holder, fencing_generation, expires_at, state)\`. Já existe lease parcial; recovery e fencing precisam auditoria.
- \`handoff(id, work_item_id, from_run, to_principal, checkpoint_id, task_version, status, expires_at, accepted_at)\`. Já existe transferência, sem checkpoint versionado.

### Grupo C — fonte, continuidade e conhecimento
- \`source_record(id, project_id, owner, kind, canonical_uri, immutable_rev, digest, observed_at, visibility, validity, consent_ref)\`. Fonte é referência, não material pessoal por padrão.
- \`observation(id, run_id, source_record_ids, text_or_structured_payload, assertion_kind, recorded_by, asserted_at, trust=ASSERTED)\`. Um resultado de tool pode ser observational but not automatic acceptance.
- \`checkpoint(id, work_item_id, run_id, version, completed_criteria[], pending_criteria[], blockers[], next_safe_actions[], artifact_refs[], observation_refs[], signed_by_actor, created_at)\`. **A lista deve ser derivada/verificável quando possível, não substitui estados oficiais.**
- \`continuation_manifest(id, project_id, work_item_id, task_version, checkpoint_id, ref_versions/hashes[], policy_version, projection_watermark, created_at, created_for_principal, expires_at)\`. Guardar **manifesto de refs** e não um prompt gigante como fonte de verdade.
- \`memory_projection(id, source_record_id, provider, provider_id, index_version, last_event_id, indexed_at, invalidated_at)\`. É ponte reversível entre fonte e Mem0.

### Grupo D — prova e decisões (separados)
- \`artifact_ref(id, source_uri, immutable_sha/digest, media_type, owner, sensitivity)\`.
- \`evidence_record(id, work_item_id, artifact_ref, claim, criteria_id, submitted_by, submitted_at, status=REFERENCED)\`.
- \`verification(id, evidence_id, verifier_principal, verifier_kind, check_spec_version, observed_input_sha, result=PASS|FAIL|INCONCLUSIVE, checked_at, raw_ref)\`.
- \`review(id, work_item_id, reviewer_principal, criteria_version, decision=ACCEPT|REJECT|REQUEST_CHANGES, verification_ids[], signed_at)\`.
- \`decision(id, scope, statement, status=PROPOSED|APPROVED|REJECTED|SUPERSEDED, proposer, approver, supersedes_id, policy_version)\`. Nunca derivar APPROVED de memória textual.

### Grupo E — auditabilidade
- \`event(id, aggregate_id, expected_aggregate_version, new_version, actor, action, payload_redacted, correlation_id, occurred_at)\`.
- \`outbox(id, event_id, destination, operation, payload_ref/digest, status, attempts, retry_after)\`.
- \`external_effect(id, run_id, tool_ref, idempotency_key, requested_action_digest, receipt_uri, state=PENDING|CONFIRMED|INCONCLUSIVE|FAILED)\`.
- Histórico lógico imutável não exclui política de redacção/apagamento de dados pessoais. Privacidade, audit trail e legal hold requerem desenho separado, sem logging de segredos.

## 5. Qual é a unidade de partilha entre agentes?

**ContinuationPackage v0.1**, uma resposta dinâmica (não uma entidade que pode conceder novos direitos):

\`\`\`json
{
  "work_item_id": "T-001",
  "work_version": 9,
  "project_id": "alpha",
  "run_id": "run-b-01",
  "last_checkpoint_id": "cp-004",
  "handoff": {"id": "h-005", "state": "ACCEPTED"},
  "canonical_status": "IN_PROGRESS",
  "verified": [
    {"criterion": "test-suite", "check": "CI job passed", "evidence_id": "ev-008"}
  ],
  "decisions": [{"id": "D-04", "status": "APPROVED", "current": true}],
  "observations": [{"id": "O-27", "trust": "ASSERTED", "source_ref": "source-2"}],
  "next_actions": ["Revalidar configuração e executar teste de integração"],
  "unresolved": ["Revisão de segurança pendente"],
  "semantic_memory": {
    "status": "available",
    "items": [{"id": "mem-09", "trust": "UNVERIFIED", "source_ref": "source-2"}]
  },
  "freshness": {"task_version": 9, "memory_watermark": 81, "stale": false},
  "policy": {"access_checked_at": "2026-11-12T12:00:00Z"}
}
\`\`\`

Campos de exemplo **100% sintéticos**; não é resposta do backend existente. Cada campo de decisão/evidência deve vir de store autorizado e verificador/role específico. O pacote pode omitir campos confidenciais por ACL, mas deve indicar quando há redacções relevantes ao resultado.

**Não guardar segredos de lease no pacote exportável ou handoff Git público.** Se um executor precisa de lease, recebe handle/token dedicado num canal autenticado e com expiração, sujeito a fencing.

## 6. Interface interna mínima entre componentes

\`\`\`text
IdentityPolicy.authorize(actor, action, resource, purpose) -> Decision(allow, policy_version)
WorkCore.transition(cmd, expected_version, idempotency_key, lease) -> TaskState+Event
Continuity.record_observation(actor, work_ref, claim, source_refs) -> ObservationID
Continuity.create_checkpoint(run_id, expected_version, manifest) -> CheckpointID
Continuity.offer_handoff(work_ref, target, checkpoint_id, expected_version) -> HandoffID
Continuity.accept_handoff(target, handoff_id, expected_version) -> LeaseHandle
Continuity.resume(actor, work_ref, criteria) -> ContinuationPackage
Trust.submit_evidence(run, artifact_ref, criterion) -> EvidenceID
Trust.verify(evidence, verifier, check_spec) -> VerificationID
Trust.review(work, reviewer, decision, checks) -> updated_state
MemoryProvider.index(source_ref, policy, idempotency_key) -> ProjectionResult
MemoryProvider.search(query, scoped_filters, watermark) -> Candidate[]
Outbox.dispatch(event) -> Attempt+Receipt
\`\`\`

Isso é uma **contrato lógico de implementação futura**, não funções já existentes no código. Podemos mapear os métodos existentes sem reescrevê-los.

## 7. Decisões de modelação que impedem erros futuros

- **Task vs Run:** uma tarefa pode atravessar várias execuções e vários agentes; não fundir identidade do trabalho com processo/chat.
- **Checkpoint vs Memory:** checkpoint é o ponto canónico de retoma; memória é um índice auxiliar de contexto possivelmente incompleto.
- **Evidence vs Approval:** CI PASS significa uma observação de CI, não aceitação do produto. Reviewer aprovou = decisão de autoridade, não “verdade universal”.
- **Decision vs Observation:** memória “o utilizador escolheu X” é observação até existir decisão autenticada.
- **SourceRef vs full file:** de preferência armazenar URL/rev/digest sob acesso; ficheiros privados ficam num vault/object store privado aprovado, nunca no repo público.
- **Handoff vs Export:** exportar Markdown pode apoiar humanos, mas um ficheiro não faz lease transfer ou granting.
- **Outbox vs synchronous LLM:** indexação executa depois do commit principal; não bloquear conclusão de writes por latência do Ollama.
- **Resource revocation:** token ou ACL revogado deve impedir novos reads e invalidar snapshots; dados já obtidos não podem ser magicamente apagados do host cliente, limitação a declarar.
- **Approval roles:** em MVP, evitar que o próprio executor seja o único revisor de resultado da sua tarefa.
- **Lease lost response:** implementar fluxo explícito de recuperação que invalida credencial anterior, em vez de regravar token na idempotency store.

## 8. Proposta de árvore backend sem mover já os ficheiros existentes

\`\`\`text
backend/rightware_si/
  api/                     # versioned routes, auth dependencies
  core/                    # current postgres WorkCore -> WorkItem/Lease domain
  continuity/              # AgentRun, Observation, Checkpoint, Handoff, Resume
  trust/                   # Evidence, Verification, Review, Decision
  memory/                  # MemoryProvider ABC, Mem0, projection, revocation
  integrations/            # MCP / REST adapters; A2A future, PULSE/Jarvis later
  operations/              # outbox worker, audit and health
\`\`\`

Isto é mapa de responsabilidades, não ordem imediata de criar dezenas de packages. **Não mover novamente a árvore sem gate funcional**. Estrutura actual já é suficiente para primeiro R1; split por módulo quando o código crescer.

## 9. Lições de investigação aplicadas

- Mem0: \`add/search\` cobre descoberta de lembranças, não tarefa/approval/ACL. **REUSE**, mantendo pin e testes.
- Hindsight: memória com defesa e retrieval híbrido já disponível. **EVALUATE** adaptador; não reivindicar capacidades como inovação exclusiva.
- Graphiti: temporalidade útil para decisões superseded; **EVALUATE** apenas se o baseline SQL+versão falhar cenário real.
- Letta Code: Git-backed memory mostra valor de artefacto persistido; **LEARN**, sem carregar agente inteiro.
- LangGraph: checkpointing de runtime; **COMPARE** se a retomada determinística não for suficiente.
- Temporal/DBOS: retries/durabilidade; **COMPARE** após demonstrar necessidade. Activity externo pode repetir e exige idempotência/receipts.
- A2A: Task/Message/Artifact/Context ajudam protocolos de agentes; **ALIGN**, sem usar mensagens efémeras como audit log.
- SoMem/XTDB e restantes propostas Perplexity: **RESEARCH**, sem importar código até evidência/métrica/licença.
- PostgreSQL exact/FTS: baseline obrigatório para IDs/decisões/refs e comparação com Mem0; nunca resolver decisão oficial só por nearest vector.

## 10. Gates de revisão

Antes de escrever migrations: confirmar limites de autoridade PULSE vs SI, quais fontes e PII permitidas, política mínima de grants e da revisão humana, significado de DONE e checkpoint, retorno de resume com Mem0 desligado, e política de lease recovery. Se houver desacordo, anotar no registo de decisões, não implementar “default” silencioso.

**Documento associado:** \`03_UC_CORE_01_ACCEPTANCE_AND_EXECUTION.md\`.
