# SI-RD-02 — Experimental Benchmark Contract (proposto; NÃO EXECUTADO)

**Objectivo:** comparar com justiça memória, continuidade e segurança sem confundir pipelines ou vantagens de modelos.
**Fixture sintética:** `docs/research/fixtures/SI_RD_02_cases_v1.jsonl` — 18 casos, 6 MEMORY, 6 CONTINUITY, 6 SECURITY; nenhum dado real de utilizador.

## Tracks independentes
1. **Memory retrieval (A):** PostgreSQL exact/FTS vs Mem0 pinned vs Hindsight. Mesmos factos, mesmo filtro de autorização externo, mesmo `top_k`, timestamps e consultas. 2 variantes: **A0** indexação determinística/infer=false para separar retrieval; **A1** extracção automática com mesmo modelo/prompt/budget, medindo também erro de ingestão. Graphiti entra como candidato temporal B quando preparado, sem obrigar grafos aos outros participantes. Leitura manual de resultados e URLs/shas das fontes.
2. **Durable task continuity (C):** WorkCore RIGHTWARE vs protótipos LangGraph e Temporal apenas se o custo de integração justificar. Medir recuperação após crash, conflito, lease expirado, handoff e replay de efeitos simulados; não atribuir 0 a motores de memória que não prometem tais funções.
3. **Security and evidence (S):** avaliar gateway RIGHTWARE e limites de cada integração. As soluções externas podem não implementar auth completa; então medir arquitectura de sistema ao redor da memória, não atribuir falsamente uma funcionalidade nativa ao motor.
4. **Interoperability (I):** A2A/MCP contract tests separados; perda de mensagens transitórias e continuidade através de artefactos persistidos.

## Métricas e denominadores
- `precision@k = relevant_retrieved / retrieved` no conjunto de consultas com ground truth; `recall@k = relevant_retrieved / relevant_total`; `answer_grounded = correct_answers_supported / answered_cases`; `abstention_accuracy = correct_abstentions / cases_with_unanswerable_ground_truth`.
- `state_recovery_success = successfully_reconstructed_pending_task / resumable_cases`; `unauthorized_disclosures = count`; `false_completions = count`; `duplicate_external_effects = count`.
- p50/p95 por **operação observada**, tokens por extracção/resposta, memória residente, custo de inferência e armazenamento; reportar também custo de observabilidade/administração quando aferível.
- Não converter um caso de 18 itens em claims de `market-leading`; este dataset é **smoke de contrato**, não amostra estatística representativa.
- Segurança/autoridade: critérios hard-gate = **0** divulgações inter-tenant, **0** mudanças de estado por memória não verificada, **0** efeitos duplicados; falha implica NO-GO no cenário, não se esconde em score médio.

## Reprodutibilidade
- Pin por SHA exacto de cada fornecedor, versão PostgreSQL/pgvector/Ollama, hash de modelo local, sistema operativo, RAM/CPU/GPU, configurações, temperatura e `top_k`; uso de política idêntica para os consumidores autorizados.
- Ingestão cria instâncias/bancos separados por participante/caso, com `seed` e tempos fixos; sem tráfego externo ou uploads de dados privados.
- Ground truth retirado de eventos/proveniência sintéticos, **não gerado pelo mesmo modelo que está a ser testado**.
- Caminho de memória, estado autoritativo e execução de ferramentas têm logs separados. Qualquer etapa FAKE sinalizada; ferramenta real só com `tool_result` verificado.
- Cada execução guarda `run_id`, pin SHA, dataset hash, config sanitizada, prompt id, input id, resultado bruto sanitizado, classificação, métricas recalculáveis, incidentes e limites.
- Não introduzir no runtime da RIGHTWARE qualquer dependência para benchmark sem aprovação; construir primeiro em laboratório isolado.

## Formato do JSONL
Cada linha tem `id`, `track`, `scenario`, `inputs[]`, `query`, `oracle{decision,...}`, `critical`, `synthetic=true`.
Decisões `ANSWER`, `ABSTAIN`, `DENY`, `DENY_ACTION`, `DENY_PROMOTION`, `CONFLICT`, `RESUME_PENDING`, `DENY_OR_RECONCILE`, `NO`. Estas são **expectativas de teste** propostas, não resultado de execuções.

## Critério para executar SI-RD-03
Revisar primeiro a taxonomia e o oracle humano. Adapters que não suportam um track são `NOT_APPLICABLE`, nunca FAIL. Fixar termos/licenças/versões; preparar instalação isolada com rollback; ensaio inicial dos 18 casos; depois ampliar corpus e decidir necessidade de comparação estatística.
