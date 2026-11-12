# WORK-03B R0 — Blueprint do produto, princípio de funcionamento e provas

Este dossier é o **complemento arquitectural** do contrato machine-readable em \`docs/work03b/\` e responde à pergunta: “Como o Shared Intelligence vai funcionar na prática e quais são as suas peças?”. O R0 não entrega novos endpoints.

**LER PRIMEIRO (contrato canónico):** [UC_CORE_01_CONTRACT.json](../../work03b/UC_CORE_01_CONTRACT.json) e [UC_CORE_01_ACCEPTANCE.md](../../work03b/UC_CORE_01_ACCEPTANCE.md). As novas rotas, permissões e casos de uso expostos nestes ficheiros são DRAFT para ratificação.

## Documentos do blueprint
1. [00 — Princípio de funcionamento](00_PRODUCT_OPERATING_PRINCIPLE.md): jornada de vida, fonte de verdade, continuidade, leitura/escrita, handoff, memória e modos de falha.
2. [01 — Componentes e ownership](01_COMPONENT_DOMAINS_BOUNDARIES.md): modular monolith, PULSE/Jarvis boundaries, entidades e proposta de ContinuationPackage.
3. [02 — Domain/protocol/security](02_DOMAIN_PROTOCOL_SECURITY_CONTRACTS.md): contratos alargados de horizonte, entidades, estados, REST/MCP e invariantes (nenhum endpoint extra aprovado).
4. [03 — UC-CORE-01 e execução](03_UC_CORE_01_ACCEPTANCE_AND_EXECUTION.md): narrativa completa e proposta de pequenos checkpoints R1A–R2B.
5. [04 — Pesquisa aplicada](04_RESEARCH_TO_ARCHITECTURE_DECISIONS.md): REUSE/EVALUATE/LEARN/BUILD, vantagens potenciais versus concorrência.
6. [05 — Contrato canónico](05_CANONICAL_CONTRACT_ALIGNMENT.md): reconciliação com a implementação R0 concorrente, prioridade normativa, resolução de diferenças.

## Estado real
- Código actual: PostgreSQL task/lease/handoff, FastAPI, MCP stdio read-only e Mem0 OSS local/Ollama lab.
- Contrato de produto R0: DRAFT; 10 operações existentes, 7 futuras e 18 critérios de MVP. Ainda não foram demonstrados como um fluxo completo de produto.
- SI-RD-02E Perplexity: fonte adicional de pesquisa, não aprovação nem benchmark.
- \`main\`, Jarvis e PULSE inalterados. Documentos sem segredos no repositório público.

**Próximo gate:** ratificar UC-CORE-01 e desenvolver R1A com dados sintéticos, guardas de autorização e testes claros, sem construir infraestrutura de produção prematuramente.
