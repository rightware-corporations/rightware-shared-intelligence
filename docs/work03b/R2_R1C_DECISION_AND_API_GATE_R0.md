# WORK-03B R2 R1C — Session Recovery, Policy Ratification & Operational API Gate R0

**Data:** 2026-11-12, Africa/Maputo.
**Classificação:** INVESTIGAÇÃO / DECISION PACKET / PROPOSTA, NÃO APROVADO, SEM IMPLEMENTAÇÃO R2 R1C.
**Branch/HEAD pré-checkpoint:** `develop@e43a653b3c5999028abe4571fb9730b7f9b25dea`.
**Fonte canónica:** [HANDOFF_MASTER](../HANDOFF_MASTER.md), [HANDOFF corrente](../HANDOFF.md), [R1C security gate](R1C_SECURITY_POLICY_GATE_R0.md), [R2 trust contract](R2_TRUST_CONTRACT_R0.md) e [UC-CORE-01](UC_CORE_01_CONTRACT.json).

## 1. Recuperação do contexto do chat anterior

O operador atingiu o limite do chat e pediu que o trabalho fosse preservado e continuado através dos handoffs oficiais. O chat foi fornecido como contexto, **não** é a fonte canónica do estado de código. Este documento resume apenas os factos técnicos verificáveis e próximos gates; não copia conversas privadas completas nem dados pessoais.

- R1C: checkpoint-bound handoff, monotonic lease fencing e same-holder lease recovery verificados em laboratório, 94/94 testes no [CI 43196082372](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43196082372).
- R2 R0: contrato técnico DRAFT com testes estáticos; CI de contrato [43201981635](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43201981635), 100/100 PASS.
- R2 R1A: GitHub provider verifier com EV-01..04 LIVE API e resultados esperados (PASS exacto; FAIL SHA/repo/workflow errados), EV-05..07 só adaptador simulado; [CI 43214573166](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43214573166), 115/115 PASS.
- R2 R1B: migration 0007, si_evidence_verification_policies e si_verification_attempts append-only, principal SERVICE autorizado, GitHub LIVE API → bearer SERVICE → PostgreSQL, idempotência e revogação, [CI 43237504677](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43237504677), 131/131 PASS em laboratório. [Relatório de evidências](R2_R1B_EVIDENCE.md). O [CI da adenda SI-MH-0029](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43238519552) tem job success no estado consultado.
- Os 16 casos originais SI-RD-03C são fixtures `synthetic=true, executed=false`; as provas LIVE/MOCK dos subconjuntos estão nos relatórios de execução, **não** na fixture de investigação.
- `ASSERTED != CHECKED_PASS != REVIEW_ACCEPTED != DONE`. A verificação R1B não altera `IN_REVIEW` nem `REFERENCED`.
- R2 R1C não está implementado. Sem REST de verificação pública, sem reviewer independente, sem decisão DONE; M01–M18 ainda `PENDING_FULL_E2E`. `main`, JARVIS, PULSE e vendor Mem0 não foram alterados por este checkpoint.

## 2. Políticas SEC-R1C — opções para decisão formal do operador

| Gate | Recomendação sujeita a ratificação | Estado antes desta entrega | Condição mínima de aceitação |
|---|---|---|---|
| SEC-R1C-01 | Novas tarefas em release exigem checkpoint-bound handoff; `LEGACY_UNBOUND` apenas por allowlist nominativa, prazo e migração explícita | NÃO RATIFICADA | inventário legacy; migração; teste fail-closed; rollback |
| SEC-R1C-02 | Sem takeover automático do titular ausente; eventual reassignment via fluxo administrativo auditável, identidade separada, revisão a dois atores | NÃO RATIFICADA | threat model, revogação, race tests, consent/authority |
| SEC-R1C-03 | Nunca repetir efeitos externos de resultado ambíguo sem reconciliação, recibo do provider e idempotency key do efeito | NÃO RATIFICADA | effect intent/outbox, resultado UNKNOWN, replay e timeout-after-commit |
| SEC-R1C-04 | `task:recover` com credenciais de workload dedicadas, rate limit, step-up/políticas e auditoria sem segredos | NÃO RATIFICADA | OIDC/workload identity, least privilege, tenant+key revoke drills |

**Nenhuma recomendação acima é uma decisão oficial.** O comportamento do R1C em laboratório não foi modificado aqui.

## 3. Proposta do primeiro provider R2 operacional — contratos que faltam aprovar

1. **Scope do tenant:** cada projecto autoriza explicitamente repository ID e workflow ID; registrar quem aprova a versão da `VerificationPolicy`, por quanto tempo vale e como revogar.
2. **Identidade:** apenas `SERVICE` com `evidence:verify` e `task:read`, credenciais vinculadas ao workload/project. Separação obrigatória de autor da evidência, dono de policy, serviço verificador e reviewer.
3. **Critério:** `CHECKED_PASS` significa correspondência exacta dos campos fixados do GitHub run, **não** qualidade do artefacto, aceitação empresarial, assinatura ou task DONE. Determinar requisitos de run/conclusion/status/event/run_attempt/SHA e validade temporal antes de expor API.
4. **Proveniência:** registrar `LIVE_HTTPS` vs `SIMULATED_TRANSPORT`, run/attempt e policy version; provider outage/pending/incomplete → `INCONCLUSIVE`; redirect/host arbitrário → rejeição.
5. **Dados e privacidade:** consent e access control por fonte, minimização de metadados, prazo de retenção, revogação e erasure; evitar secrets e conteúdo privado em repos públicos e logs.
6. **Review/DONE:** futuro `task:review` requer ator independente, quorum/authority definidos, CAS e todos os critérios mandatórios PASS; **fora do escopo R1C**.

### Opções de alcance do R2 R1C

- **Opção A (recomendada para primeira implementação, dependente de autorização):** endpoint privado e allowlisted para `POST /v1/projects/{project_id}/evidence/{evidence_id}/verify`; SERVICE-only, sem capacidade de review, project-bound, limites de chamada, feedback de CHECKED_*, sem DONE. Reusar `EvidenceLedger` e schema 0007; introduzir o mínimo de novos componentes.
- **Opção B (posterior):** integração service-to-service com OIDC/attestation e gestão de policy por tenant; adicionar apenas depois de testes de isolamento e rotação.
- **Fora deste gate:** `POST .../tasks/{task_id}/review`, `DONE`, execução de ferramentas externas, external-effect outbox em produção e public LLM judgement.

## 4. Testes exigidos antes de declarar R2 R1C pronto

- API authenticated SERVICE/AGENT/HUMAN: allow/deny, spoofed principal, cross-project/source, scope revoked before/after provider call.
- Criterion/policy: wrong SHA/repo/workflow/run/attempt/event, expired/superseded policy, stale task version, duplicate idempotency key e concurrent call.
- Network: timeout, GitHub HTTP errors, pending, redirect, untrusted URL e invalid response → nunca CHECKED_PASS sem fonte verificada.
- Persistência: attempt append-only, `LIVE_HTTPS` não falsificável por caller, sem mutation de `IN_REVIEW`/trust_state; read revocation; sem tokens no log.
- Recuperação: API offline/falha da resposta de gravação, idempotência e ausência de duas verificações inconsistentes.
- CI deve preservar regressão R1C A/B e MCP/REST/PostgreSQL/Mem0/Ollama; testes reais LIVE distintos de MOCK, com run+SHA. M01–M18 só passam a `PASS` após E2E específico.

## 5. Estado e próximos passos

**Neste checkpoint:** só documentação de continuidade e gate; nenhum código, migration, dependência, endpoint, grant ou política de runtime alterados. Nenhuma decisão pendente foi aprovada e nenhum EV-08..16 foi executado.

**Próximo passo exacto:** obter ratificação (ou emendas) da matriz SEC-R1C-01..04 e do escopo minimo para GitHub Provider/API R2 R1C. Depois, criar implementação em `develop`, preservar ambos handoffs no mesmo commit, executar suites reais e registar CI em novo SI-MH; preparar reviewer/DONE em fase separada.
