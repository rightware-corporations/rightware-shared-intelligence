# 01 — Cronologia SIC e relação com os handoffs

| Referência | Evidência e escopo | Limite |
|---|---|---|
| WORK-00 → WORK-02D | Core PostgreSQL tarefas/handoffs/leases, REST/MCP, Mem0/Ollama em laboratório | Não serviço produtivo |
| WORK-03B R1A/R1B/R1C | fontes/observações, checkpoints, resume, lease fences | Não reviewer nem auto-DONE |
| R2 R1D/G01 · SI-MH-0040..0056 | GitHub evidence lab, política de ciclo de vida sintética, PostgreSQL restore/guards | G04/G05 produção bloqueada |
| SI-RD-01/02/03C | estudo de código OSS, contrato comparativo, evidência/autoridade | Pesquisa, não fornecedor seleccionado |
| A0 v0.1–v0.5 | testes lexicais e PostgreSQL-WASM inicial | Motor PGlite, não PostgreSQL Server |
| A0 v0.6 · SI-MH-0046 | 144 buscas; AND 0/15; OR pós-hoc 13/15 Top2 | `case_id` do oráculo contaminava avaliação |
| A0 v0.7 · SI-MH-0047/48/53 | 49 docs, 40 perguntas, 320 rankings; PT+OR 19/31 Top2 | Escopo sintético fixo, sample pequeno |
| A0-GLOBAL-02 v0.8 · SI-MH-0060 | 82 docs, 56 perguntas, 44 com fonte/12 negativas; pacote público e gold cifrado | 10+18 testes de contrato, 0 ensaios reais comparáveis dos três fornecedores |
| G04-A0 · SI-MH-0061/62 | D01–D05/D12 aprovados **só para laboratório sintético**, 21 testes, CI 237/237 | OIDC/ACL/RLS reais ausentes |
| Engine E0 · SI-MH-0063/64 | BM25 e regras sintéticas próprias, 22 testes, CI 259/259 | RW-R1 ML treinado NÃO existe |
| E1 ordem · SI-MH-0065/66 | E1.1 dados → E1.2 baselines → E1.3 RW-R1 → E1.4 calibração → E1.5 blind review | Ciência completa pendente |
| E1.1 · SI-MH-0067..69 | 84 docs/60 perguntas, CI inicial FAILED e reparado, depois 283/283 | 24/24 negativas emitiram candidatos; gold de regras |
| E1.1B · SI-MH-0070/71 | 56 docs/32 perguntas, 24 labels provisórias, 8 eval sem gold, CI 303/303 | 0 reviewers, `E1_DATA_READY=REVIEW_REQUIRED` |

**Não confundir:** CI Mem0/Ollama do Core com benchmark Mem0 da v0.8; E1.1 303 testes com modelo treinado; PGlite/WASM com PostgreSQL Server; resultado `EVIDENCE_CANDIDATE` com aprovação/revisão/DONE. O histórico completo é o [MASTER](../HANDOFF_MASTER.md), não esta tabela.
