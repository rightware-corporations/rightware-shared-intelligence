# G04-A0 — Ato de decisão do piloto sintético R1

**2026-11-17 Africa/Maputo. Estado: DECISÃO OFICIAL LIMITADA A LABORATÓRIO.**

O operador confirmou avançar com o pacote G04-A0 apresentado imediatamente antes: exclusivamente RIGHTWARE e organizações fictícias, sem produção, privados ou clientes. A ratificação restringe-se aos princípios seguintes, não à contratação/configuração de fornecedores ou implantação.

| ID | Ratificado estritamente para desenho/piloto interno | Pendente |
|---|---|---|
| D01 | Um contexto RIGHTWARE interno e pelo menos duas organizações adversárias 100% fictícias | Clientes, dados reais e staging |
| D02 | HUMAN OIDC Authorization Code+PKCE; emissor/audiência verificados e MFA para atos privilegiados | Escolha de IdP, credenciais, domínio |
| D03 | SERVICE/AGENT credenciais assimétricas curtas e separadas de HUMAN, audiência e revogação | OIDC workload vs mTLS, fornecedor |
| D04 | Vinculação validada (issuer, subject)→principal interno→pertença institucional/projeto explícita | Migrações, IDP real, sessões |
| D05 | Deny-by-default, grants por recurso/finalidade, revalidação, RLS como requisito de defesa adicional | ACL real, DB RLS e migração |
| D12 | CI obrigatório, revisão independente, branch protection e gate G05 antes de staging/produção | Configurar efetivamente GitHub e processos |
| D06–D08,D11 | NÃO RATIFICADOS | Apoio, memória privada, integração, chaves |
| D09–D10 | NÃO RATIFICADOS | Base jurídica, jurisdição, consentimento, retenção/apagamento |

**Cuidado:** approval D12 como requisito não significa que a branch develop passou a estar protegida. O GitHub reportou protected=false. Não foi alterado qualquer ruleset nem feito merge para main.

**Execução autorizada agora:** criar somente evaluator in-memory com dados e identificadores syn-*, guardado pelo modo LAB, testes negativos e documentação de prova. As claims sintéticas NÃO são tokens assinados, NÃO autenticam utilizadores e não podem ser ligadas a HTTP, MCP, Mem0 ou tarefas reais. Sem endpoints, novas tabelas, migrações, dados de clientes ou fontes privadas.

O R0 de decisões mantém-se como registo de proposta histórica. Este R1 aprova somente D01–D05/D12 nestas fronteiras. A implantação real G04-A1/A2, vendor e política de dados exigem nova decisão explícita.
