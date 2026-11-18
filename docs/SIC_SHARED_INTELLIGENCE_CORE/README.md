# SIC — Shared Intelligence Core | RIGHTWARE

**Dossier permanente de continuidade e evidências.** Criado em 2026-11-18, checkpoint SI-MH-0072. NÃO é novo projecto, fork, decisão de produção ou substituto dos handoffs.

**Fontes de verdade (por ordem):** [HANDOFF operacional](../HANDOFF.md), [HANDOFF_MASTER imutável por adendas](../HANDOFF_MASTER.md), [HANDOFF_POLICY oficial](../HANDOFF_POLICY.md). Este dossier organiza as fontes; os factos devem ser revalidados contra o HEAD remoto.

## Navegação
- [00_RECOVERY.md](00_RECOVERY.md) — recuperação e política Git/handoff
- [01_HISTORY.md](01_HISTORY.md) — cronologia de desenvolvimento e SI-RD
- [02_FILES_AND_EVIDENCE.md](02_FILES_AND_EVIDENCE.md) — documentos no Git, ZIPs externos, hashes
- [03_STRATEGY_AND_GATES.md](03_STRATEGY_AND_GATES.md) — E1/G04/R2 e ordens de execução
- [04_METRICS_AND_LIMITS.md](04_METRICS_AND_LIMITS.md) — resultados numéricos e denominadores
- [05_PRIVATE_CUSTODY.md](05_PRIVATE_CUSTODY.md) — evidência externa, backup, chave privada
- [ARTIFACT_REGISTRY.json](ARTIFACT_REGISTRY.json) — índice machine-readable de 40 ficheiros Git e 10 referências externas

## Estado na data de criação
A RIGHTWARE definiu a direcção de **tecnologia própria de inteligência científica**, sem confundir BM25/OSS com um modelo treinado. O motor experimental E0 e os datasets E1.1/E1.1B já têm CI; o último relatório de engenharia confirmou **303/303 testes**, mas `E1_DATA_READY=REVIEW_REQUIRED` (0 revisores humanos, gold independente em falta). A única missão principal a seguir é **ENG-E1-03 / E1.1C — anotação humana independente e holdout seguro**, depois E1.2–E1.5. G04 IAM/RLS é frente paralela e bloqueia produção. Os ensaios PostgreSQL Server vs Mem0 vs Hindsight do desafio selado A0-GLOBAL-02 v0.8 permanecem **NOT_RUN**. Nenhum destes resultados aprova `DONE`, cliente ou deploy de produção.
