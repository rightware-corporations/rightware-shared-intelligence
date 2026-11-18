# RIGHTWARE Intelligence Engine — Protocolo de investigação científica R0

**2026-11-18 Africa/Maputo. Protocolo PROPOSTO; nenhum resultado de modelo treinado ou ganho declarado.**

## A. Perguntas e hipóteses falsificáveis

- **H1**: recuperação lexical+semântica+features de proveniência/autoridade melhora ranking de fontes válidas face a BM25, mesmo corpus e escopo. Rejeitar se não houver diferença em split independente.
- **H2**: modelação explícita de validade temporal reduz seleção de fonte obsoleta face a recuperação apenas por relevância.
- **H3**: decisão calibrada ANSWER/ABSTAIN reduz taxa de erro nas respostas emitidas a uma mesma cobertura, com custo de abstenção explicitamente definido.
- **H4**: o núcleo próprio mantém isolamento lógico de escopo e proveniência, mesmo com fornecedor de memória substituído.
- **H5**: ganho de qualidade/custo/latência sobre concorrentes é sustentado em PT/EN e em dados não vistos.

## B. Datasets e política de separação

- **E0 dev suite**: corpus original pequeno `syn-*`, testes construídos independentemente do desafio selado, para correção do código.
- **E1 dev/train separado**: dados públicos/licenciados ou sintéticos com rótulos de relevância e autoridade revistos por humanos; split por **fonte, projeto, tempo e pergunta**, prevenindo memorizar duplicatas. Definir distribuição, número de rótulos e acordo entre anotadores antes de treino.
- **E2 avaliação interna**: conjunto novo, não utilizado para ajuste; documento de datas, hashes, versões dos dados/modelo e regras de exclusão.
- **SI-RD-03A A0-GLOBAL-02 v0.8**: 82 fontes (70 alpha e 12 beta), 56 queries PT/EN, 44 com fonte e 12 negativas; benchmark selado e pré-registado **não usar o oráculo nem métricas ocultas para treinar, escolher thresholds, ajustar prompts, selecionar features ou repetir experiências**. Chave privada mantida pelo operador, proibida no Git/runner. R-tier retrieval não pode ser misturado com G-tier gateway.
- **Avaliação externa**: só depois de pré-registo, data leakage audit e licença correta. Revisão humana cega dos casos autoridade, temporalidade e negação.

## C. Pipeline de modelos e ablações

| Perfil | Camada | Natureza | Ponto de comparação |
|---|---|---|---|
| B0 | BM25 lexical | baseline aberto | E0 lexical |
| B1 | Vetorial isolado (pinned embedding) | baseline | mesmo corpus/split |
| B2 | Híbrido léxico+dense | baseline | sem provenance |
| RW-R1 | reranker treinável com features lexical/dense, entidade, autoridade, validade, origem | modelo próprio HIPOTÉTICO | provar ganho além B2 |
| RW-K1 | estado factual temporal + deduplicação + resolução de conflitos | algoritmo próprio HIPOTÉTICO | redução erro/stale |
| RW-C1 | seletor calibrado responder/abster/negar | modelo próprio HIPOTÉTICO | risk–coverage |

**Não atribuir propriedade exclusiva ao BM25 nem a modelos open source.** Métodos treináveis requerem pesos, seed, hyperparameters, feature provenance, inferência reprodutível e licença dos dados. Desvios do protocolo exigem nova versão explícita.

## D. Métricas pré-registadas

- **Recuperação**: hit@1/@2/@5, Recall@5, MRR@k, nDCG@5. Denominadores por idioma, fonte e tipo de pergunta. Exigir 0 source IDs proibidos como gate duro, não média.
- **Autoridade/temporalidade**: taxa de autoridade válida, decisões temporalmente corretas, conflito detectado e stale-source rate; intervalos de confiança com bootstrap pareado 95% em conjunto fixo.
- **Incerteza**: coverage, risk-at-coverage, AURC (área risco-cobertura), Brier score e ECE para probabilidades calibradas; custos e limiares escolhidos só no dev set.
- **Resposta/grounding**: grounded claim precision, hallucination/unsupported-claim rate e qualidade humana adjudicada; não confundir seleção de documento com resposta correta.
- **Operacional**: latência p50/p95, CPU/RAM/GPU pico, ingestão, custo por 1k queries, tamanho do índice, energia quando mensurável, métricas de falhas e reprodutibilidade.
- **Segurança**: 0 consultas inter-tenant, 0 propagação de dados não autorizados, 0 promoção de afirmação não verificada para decisão oficial.
- **Estatística**: reportar número de exemplos por estrato, repetições, IC, ablações e todos os runs (incluindo falhas) sem escolher apenas o melhor. Mudanças pós-hoc em um desafio selado exigem novo benchmark.

## E. Contratos técnicos de dados

`Query` = (org, project, texto, as_of, top_k, auth context verificado por G04). `Source` = (source_id, tenant, projeto, proveniência assinada/validada, valid_from/until, texto/rótulos permitidos, class/consent). `ModelVersion` = (git SHA, data SHA, feature schema, pesos/embeddings hashes, hyperparams, seeds, licença). `EvidenceDecision` = (candidatos, rankings, fontes, autoridade/temporalidade, estado EVIDENCE_CANDIDATE/ABSTAIN/CONFLICT/DENY, razão sem dados privados). O resultado **nunca** é autorização de tarefa nem DONE.

E0 usa campos de corpus sintético já validados pelo fixture, sem proveniência assinada; não é API de produção.

## F. Gating e responsável pela prova

- **GATE-E0:** CI do algoritmo e testes sem rede, com falsos dados, e audit de não importação no HTTP/MCP.
- **GATE-E1:** corpus desenvolvimento versionado, qualidade dos rótulos, reprodução de BM25 e análise por estrato.
- **GATE-E2:** modelo treinado, held-out evaluation, ablations, robustez PT/EN e incerteza calibrada.
- **GATE-E3:** comparação blindada A0-GLOBAL-02 com vendor runs imutáveis; sem abrir oracle para runner.
- **GATE-E4:** security acceptance G04 de identidade, consentimento, RLS e recursos; evidência real.
- **GATE-E5:** integração produto separada, performance, rollback e revisão independente; não há autorização de produção.

## G. Base científica

- BEIR (NeurIPS 2021): diversidade de tarefas de recuperação e generalização fora do treino.
- LongMemEval (ICLR 2025): extração, raciocínio entre sessões, temporalidade, atualização de conhecimento e abstenção.
- RAGAS (EACL 2024): separar relevância do contexto, fidelidade e qualidade da resposta.
- Calibração/Selective Prediction: risco-cobertura para fundamentar quando abster.

Referências:
- https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/hash/65b9eea6e1cc6bb9f0cd2a47751a186f-Abstract-round2.html
- https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html
- https://aclanthology.org/2024.eacl-demo.16/
- https://nlp.stanford.edu/pubs/kamath2020selective.pdf

**Estado:** PLANO + código E0 de referência; nenhuma medição comparativa real ou treino de pesos foi realizado neste checkpoint.
