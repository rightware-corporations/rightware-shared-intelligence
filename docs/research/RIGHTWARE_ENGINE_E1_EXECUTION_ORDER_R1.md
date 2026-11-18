# RIGHTWARE Intelligence Engine — E1 Learning & Evaluation Execution Order R1

**Data:** 2026-11-18, Africa/Maputo.  
**Classificação:** PRIORIDADE ESTRATÉGICA REAFIRMADA PELO OPERADOR; ORDEM DE EXECUÇÃO PROPOSTA PARA CONTROLO DE ENTREGAS, não afirmação de modelo treinado ou desempenho validado.  
**Baseline:** `develop@9461e8c8cc4ab506ad9441ea2910c058cd1b26b7` — [CI 44314535706](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/44314535706) **SUCCESS 259/259**, oito migrações, G01 laboratório LIVE e restauro lógico, MCP/Mem0/Ollama.  
**Alinhamento:** `RIGHTWARE_INTELLIGENCE_ENGINE_STRATEGY_R0.md`, `RIGHTWARE_INTELLIGENCE_ENGINE_RESEARCH_PROTOCOL_R0.md`, SI-MH-0063/0064 e G04-A0 R1.

## 1. Decisão de foco

A fase **E1 — Aprendizagem e Avaliação** é UMA missão completa: estabelecer dados independentes, treinar o primeiro reranker próprio, comparar rigorosamente com BM25 e fornecedores externos, e calibrar responder/abster-se. O trabalho anteriormente chamado `ENG-E1-01` é **E1.1**, uma subentrega, **não** toda a fase E1. Não transferir treino do ranker e calibração para um programa posterior como forma de declarar E1 concluído cedo.

**Frente principal:** RIGHTWARE Intelligence Engine E1.  
**Frente paralela necessária:** G04 IAM/tenancy, com orçamento e aceitação independentes; não integrar dados privados enquanto G04-A1/A2 estiverem por implementar e testar.  
**Não prioridade até bloqueio comprovado:** novos wrappers, novos conectores de agentes, novos fornecedores por curiosidade, UI, features JARVIS/PULSE e extensões de memória não ligadas às métricas de E1.

O objetivo E1 não é treinar um modelo fundacional. É construir e medir a primeira capacidade de ranking e decisão própria da RIGHTWARE, reprodutível e tecnicamente independente dos adaptadores Mem0/Hindsight/Ollama.

## 2. Sequência obrigatória E1

| Código | Objetivo fechado | Entregáveis obrigatórios | Gate de avanço |
|---|---|---|---|
| **E1.1 / ENG-E1-01** | Data foundation | dataset público/licenciado ou sintético independente, autorização de uso, provenance, rótulos verificáveis, splits train/dev/test por documento/projeto/tempo, hashes e auditoria de leakage; runner de avaliação | `E1_DATA_READY` apenas após integridade, diversidade, denominadores e leakage audit; **não há treino** neste gate |
| **E1.2** | Baselines comparáveis | mesmo corpus e query set, BM25, baselines dense e híbrido, config/seed/ambiente, interfaces de IDs/escopo, métricas por classe e idioma, logs brutos | `E1_BASELINES_REPRODUCED`: cada run reproduzível, sem score de fornecedor inventado |
| **E1.3** | Primeiro **RIGHTWARE RW-R1** treinável | features documentadas (léxico, dense, entidade, proveniência, tempo), treino supervisionado com pesos/versionamento/model card, ablação, testes de inferência | `E1_RW_R1_TRAINED`: artefacto real e logs, sem confundir BM25 manual com ML próprio |
| **E1.4** | Decisão calibrada | estimador de risco/coverage e limiares definidos apenas no dev set para EVIDENCE_CANDIDATE/ABSTAIN/CONFLICT/DENY; grounding separado de retrieval | `E1_CALIBRATION_VERIFIED`: erro vs cobertura, Brier/ECE ou medidas aplicáveis, casos negativos e conflito |
| **E1.5** | Avaliação independente | métricas held-out, análise PT/EN, autoridade, temporalidade, taxa de fontes proibidas, IC bootstrap pareado, custos, p95, comparação B0/B1/B2/RW-R1 e fornecedores realmente executados sob contrato comparável; relatório das falhas | `E1_SCIENCE_REVIEWED`: melhoria sustentada ou hipótese refutada, revisão independente. **Não confundir benchmark de retrieval R com qualidade da resposta G** |

**Nenhuma fase pode ser marcada PASS sem evidência do próprio gate.** CI 259/259 comprova testes já existentes do E0, não qualquer um destes cinco gates E1. E1 fecha somente depois de E1.1–E1.5; G04 é gate separado para uso privado/externo.

## 3. Regras de avaliação e rigor científico

- **Benchmark selado** `SI-RD-03A A0-GLOBAL-02 v0.8`: 82 fontes e 56 perguntas PT/EN, chave do oráculo separada. **PROIBIDO** usar perguntas ou resultados ocultos para feature engineering, treino, threshold, prompt tuning ou escolha repetida de modelo. Manter E1 train/dev/test completamente independente. Só aplicar teste final em protocolo congelado e guardar outputs imutáveis.
- BEIR: generalização de recuperação em diferentes tarefas/domínios; LongMemEval: memória longa, temporalidade, atualização e abstenção; RAGAS: fidelidade/contexto/resposta. **São referências de metodologia, não modelos próprios nem métricas já medidas.**
- Exigir baseline congelado, mesma granularidade/source IDs, scope aplicado antes de ranking, 0 IDs proibidos como **hard gate**, rastreio de todos os experimentos, licença de dados, hashes, splits sem duplicados/fuga, e resultados positivos e negativos.
- Métricas primárias: nDCG@5 e MRR/Hit@k para retrieval; curva risco-cobertura para seletor de decisão; taxa de violação de escopo como guardrail. Complementares: ECE/Brier quando probabilidades existentes, PT/EN/temporal/authority por estrato, p50/p95 e custo.
- Sem metas percentuais de melhoria inventadas sem medições. Pré-registar comparação relevante e intervalo de confiança e reportar efeito, variabilidade e eventuais fracassos. Se não melhorar, não promover RW-R1.
- Retrieval = candidatos; autoridade = contrato verificado no ledger; resposta final = hipótese e grounding analisados separadamente; nenhum modelo dá permissão para reviewer/DONE.

## 4. G04 paralelo, mas não concorrente ao foco de investigação

| Via | Estado observado | Responsabilidade e dependência |
|---|---|---|
| **G04-A0** | Princípios D01–D05/D12 aprovados apenas para laboratório, 21 testes sintéticos incluídos nos 259 | Regressão sem exposição pública |
| **G04-A1** | OIDC HUMAN e credencial workload SERVICE/AGENT real **NÃO IMPLEMENTADOS** | Definir fornecedor/issuer e provar autenticação criptográfica, binding org/tenant e revogação |
| **G04-A2** | ACL por recurso, memberships reais e PostgreSQL RLS **NÃO IMPLEMENTADOS** | Testar proibição real inter-tenant e por recurso; não adaptar claims falsas do E0 |
| **G04 demais** | D06–D11, consentimento, retenção, eliminação, fonte privada e production DR **ABERTOS** | Decisões institucionais, legais, técnicas separadas |
| **D12** | Proteção de `develop` observada `protected=false` | Necessária antes de staging/release, sem alterar rulesets nesta decisão |

**Regra de paralelismo:** E1 pode usar dados sintéticos/licenciados offline enquanto G04 avança. E1 fica bloqueado na transição para fontes privadas, clientes, API pública e integração comercial enquanto gates G04 relevantes estiverem pendentes. G04 não transforma uma avaliação científica mal feita em modelo válido; E1 não substitui autorização de acesso.

## 5. Quadro semanal mínimo de controlo

1. **Entrega atual:** `E1.1 / ENG-E1-01`. Uma única tarefa E1 em execução, com artefactos e critérios de aceitação binários.
2. **Resultado verificável:** dados/splits e benchmark runner reproduzidos em CI; registar PASS/FAIL/NOT_RUN com SHA.
3. **KPI 1 — Science:** melhor nDCG@5/MRR vs B0 (só após dataset independente); qualquer diferença exige análise de incerteza.
4. **KPI 2 — Safety:** número de IDs fora do escopo = 0, obrigatório em todos os testes.
5. **KPI 3 — Reproducibility:** percentagem de runs que podem ser reproduzidos a partir de manifest/seed/hashes; para gate, exigir **todos os runs aceites reproduzíveis**, sem alegar que já foram.
6. **Distrações e bloqueios:** máximo uma exceção de segurança urgente, com registo de motivo; nenhuma ramificação de produto fora do plano E1 principal.
7. **Comissão de avanço:** declarar E1.1 PASS antes de iniciar treino E1.3; não saltar baselines E1.2. Não fechar E1 com resultados E0.

## 6. Estado e próxima execução

| Trabalho | Estado |
|---|---|
| E0 referência lexical/temporal/autoridade + 22 testes | **VERIFIED LAB**, baseline CI 259 |
| E1.1 dataset, splits, labels e runner | **NEXT — NOT_IMPLEMENTED** |
| E1.2 BM25/dense/híbrido reproduzíveis no mesmo dataset | **NOT_IMPLEMENTED** |
| E1.3 RW-R1 com pesos treinados | **NOT_IMPLEMENTED** |
| E1.4 calibração decisão | **NOT_IMPLEMENTED** |
| E1.5 avaliação blindada e revisão | **NOT_IMPLEMENTED** |
| OIDC/RLS real e aprovação acesso privado | **G04 OPEN** |

**Ação técnica seguinte:** implementar `ENG-E1-01` sob uma missão fechada, sem alterar a arquitetura Core, sem usar oráculo selado, sem instalar componentes de produção. Passar logs e hash por checkpoint. O plano de E1 não autoriza novas mudanças em `main`, JARVIS, PULSE ou vendor Mem0.
