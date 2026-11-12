# WORK-03B R0 — Alinhamento com contrato canónico e registo de decisões

**Status:** documento de harmonização, não novas APIs nem ratificação de produto.
**Problema resolvido:** houve dois trabalhos complementares em develop no mesmo período: (a) contrato funcional machine-readable e testes estáticos em \`docs/work03b/\`; (b) arquitectura de princípio de funcionamento e horizonte de produto em \`docs/product/work03b/\`. **Só pode haver um contrato executável principal.**

## 1. Ordem de autoridade entre artefactos

1. **Código real + PostgreSQL migrations + testes/CI**: única prova de implementação.
2. **\`docs/work03b/UC_CORE_01_CONTRACT.json\`**: **contrato R0 canónico DRAFT**, com 10 rotas existentes, 7 operações futuras, 14 passos e M01–M18. Acompanhado de \`WORK03B_R0_FUNCTIONAL_CONTRACT.md\`, \`UC_CORE_01_ACCEPTANCE.md\` e \`tests/test_work03b_contract.py\`.
3. **\`docs/product/work03b/00...04\`**: arquitectura explicativa, modelo operacional, eventual extensão de domínio e backlog. Não substituem o JSON nem aprovam novos endpoints.
4. **SI-RD-01/02/02E e SI-FG-01**: estudos, investigação externa e auditoria funcional. São fontes para decisões, não verdades ou aprovação empresarial.

**Qualquer divergência entre (2) e (3) deve ser apontada e reconciliada antes de escrever migrations, não interpretada como uma segunda interface pública.**

## 2. Diferenças detectadas e tratamento

| Tema | Documentos explicativos | Contrato canónico R0 | Tratamento |
|---|---|---|---|
| Jornada | Descrevem **20 passos de UX/observabilidade**, incluindo falhas e revisão | 14 passos S01–S14 como oracle sintético base | Os 20 são uma **ampliação conceptual**; a execução R1/R2 usa os 14 canónicos, sem declarar 20 testes PASS |
| Rotas REST | Lista expandida de possíveis módulos e operações R1+R2+deferred | 10 live e **7 future** exatamente no JSON | Apenas as 7 são candidatas de endpoint R0; restantes ficam **BACKLOG FUTURO**, sem decisão de criar |
| Identidade da tarefa | \`WorkItem\` mínimo ou alias PULSE | \`Task\` do WorkCore existente e referências externas se necessário | Manter \`Task\` hoje; não renomear migração/schema sem aprovação |
| Versão e observações | Evento é versionado; checkpoint exige CAS/lease | Observação pode ter sequência própria e não tem de incrementar task.version | **Seguir contrato canónico**: task version só para transições protegidas; observações usam event sequence e provenance |
| Objectos de continuação | \`ContinuationPackage\` e \`ContinuationManifest\` | \`ContextSnapshot\` e \`TaskCheckpoint\` | \`ContinuationPackage\` é **vista derivada de read/resume**, não necessariamente nova tabela; manifest = refs/version |
| Escrita na memória | Propõe memória canónica/outbox em R1D | R0 não expõe ainda memory-write, admite future lifecycle invalidation R2 | A escrita contextual fica **posterior** à observação/checkpoint autoritativos; não abrir endpoint de ingestão sem contrato |
| MCP de escrita | Possível adicionar tools de trabalho com ACL da API | R0 exige apenas REST/mesmas permissões; MCP read-only no código atual | Não expor write tool antes de análise de permissões; REST primeiro para R1 |
| DONE/review | Exemplo de aceitação e verificação | Reviewer + verifier distintos na R2 | R2; CI verde para contrato estático não é prova de DONE no produto |
| Lease secret replay | Recuperação por rekey/fencing futuro | Repetição de claim/accept com token secreto dá **409** (WORK-02D) | Manter 409; recovery route DEFERRED até threat model |
| Fonte externa/PULSE | Owner externo para tarefas do domínio PULSE | SI controla somente scope/continuation | Não duplicar gestor de tarefas de PULSE |

## 3. Convenção de decisão e progresso

**OFFICIAL:** \`develop\` construção, \`main\` release aprovado; handoff master cumulativo + current em cada saída; proteger Jarvis em produção; não assumir access a memórias privadas de vendor.

**IMPLEMENTED/LAB VERIFIED:** PostgreSQL WorkCore, REST autenticada, MCP read-only, Mem0 OSS/Ollama synthetic E2E. CI no commit do contrato R0: [43154026213](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43154026213), **60/60 static+existing tests PASS** e E2E sintético Mem0 PASS. Cinco testes novos são de **contrato estático**, não prova de UC-CORE-01 completo.

**DESIGN PROPOSAL:** packages de continuidade, fonte/provenance, outbox, verifier, memory lifecycle, user journey de 20 passos e expansão de endpoints. Nenhuma migration/código novos nesta entrega.

**OPEN RATIFICATION:** proprietário de task externa, quais dados podem ser ingeridos, actor/role de aprovação, políticas de segredo/leasing, granularidade de recursos, contrato exacto de \`resume\` para fontes indisponíveis, como oferecer uma experiência no Jarvis sem expor memória pessoal, critérios de saída do MVP.

## 4. Consequência prática para R1

A primeira implementação deve ler **\`docs/work03b/UC_CORE_01_CONTRACT.json\`** e entregar só o subconjunto R1, sem tentar implementar todas as entidades do horizonte conceptual.

**Ordem proposta:** SourceRecord + Observation + AgentRun mínimos → TaskCheckpoint / ContextSnapshot \`resume\` → completar HandoffBundle/CAS → teste dois processos com restart/forbidden/bad source → só então outbox para Mem0 e verificação/aprovação em R2.

Para o primeiro teste R1, o motor semântico pode ficar indisponível; a continuação canónica deve continuar correta. Isto prova o valor proprietário sem depender de memória vetorial.

Não realizar merge, deployment, Jarvis changes, mudanças de pin ou licenças por este documento.

## 5. Leituras obrigatórias para próximo agente

- \`docs/work03b/WORK03B_R0_FUNCTIONAL_CONTRACT.md\`
- \`docs/work03b/UC_CORE_01_CONTRACT.json\`
- \`docs/work03b/UC_CORE_01_ACCEPTANCE.md\`
- \`docs/product/work03b/00_PRODUCT_OPERATING_PRINCIPLE.md\`
- \`docs/product/work03b/01_COMPONENT_DOMAINS_BOUNDARIES.md\`
- \`docs/product/work03b/02_DOMAIN_PROTOCOL_SECURITY_CONTRACTS.md\`
- \`docs/product/work03b/03_UC_CORE_01_ACCEPTANCE_AND_EXECUTION.md\`
- \`docs/product/work03b/04_RESEARCH_TO_ARCHITECTURE_DECISIONS.md\`
- \`docs/research/SI_RD_02_EXTERNAL_PERPLEXITY_TRIAGE_2026-11-12.md\`
- \`docs/HANDOFF_MASTER.md\`, \`docs/HANDOFF.md\`

**Resultado esperado:** um único produto com uma única linha evolutiva, não duas especificações contraditórias.
