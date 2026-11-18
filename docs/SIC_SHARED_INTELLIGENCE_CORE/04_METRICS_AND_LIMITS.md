# 04 — Scorecards e limites de interpretação

| Experimento | Evidência | Proibição de inferência |
|---|---|---|
| A0 v0.5 PGlite-WASM | 11 docs/18 perguntas, 72 FTS; **0/15** hit@1 e hit@2 com query AND | Não é PostgreSQL Server nem resposta gerada |
| A0 v0.6 PGlite | 144 consultas; OR simple 7/15 Top1 13/15 Top2; OR portuguese 9/15 Top1 13/15 Top2; AND 0/15 | `case_id` derivado do oráculo; OR pós-hoc |
| A0 v0.7 PGlite | 49 docs/40 perguntas, 320 rankings + 160 counts; **portuguese+OR 14/31 Top1, 19/31 Top2**; simple+OR 11/31/14/31; portuguese+AND 4/31/5/31; simple+AND 0/31 | PT 14/18 vs EN 5/13 Top2; sample pequeno; escopo fixo; sem abstention validada |
| A0-GLOBAL-02 v0.8 | 82 docs/56 perguntas, 44 com gold e 12 negativas; 10 testes públicos e 18 privados de **contrato** PASS | **PostgreSQL Server, Mem0 e Hindsight NOT_RUN** sob este protocolo |
| E0 | BM25+regras sintéticas; CI total 259/259, 22 testes novos | Não um modelo RW-R1 treinado |
| E1.1 | 84 docs/60 perguntas; 36/36 positivas hit@1 em corpus fácil; negativas 24/24 com candidatos; CI 283/283 | Não generalização nem abstenção correcta |
| E1.1B | 56 docs/32 perguntas; 24 labels provisórias, 8 eval sem gold; train 7/8 positivas hit@1 e 8/8 negativas emitiram candidatos; dev 3/4 positivas hit@1 e 3/4 negativas candidatas; CI 303/303 | Sem human gold; `E1_DATA_READY REVIEW_REQUIRED` |

### Métricas distintas
`hit@k` = perguntas com fonte oráculo entre os primeiros k IDs, não `precision@k`, acerto de resposta, autorização nem `DONE`. O zero de fontes de fora do escopo observado no v0.7 foi **somente laboratório** e consultas desconhecidas/ACL ainda receberam candidatos internos irrelevantes.

**Trilhas da v0.8:** R = recuperação nativa `hit@1/2/5`, scope, custo; G = gateway comum exact-ID, autoridade/tempo, ANSWER/ABSTAIN/DENY; E = avaliação humana futura. Não pontuar fornecedores por funcionalidades que pertencem a G. Comparar pipelines só com igual corpus/eligibilidade e acesso aprovado.
