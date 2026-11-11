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

