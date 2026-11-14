# SI-RD-03A — Auditoria independente dos resultados Kaggle A0 v0.7 (14/11/2026)

**Classificação:** EXPERIMENTO MEDIDO / AUDITORIA DE RESULTADOS, **NÃO decisão de fornecedor**, **NÃO autorização de produção**, **NÃO evidencia segurança operacional de multi-tenancy ou conclusão de tarefa**.  
**Baseline do relatório:** `develop@9ce3286a121ff6b0c9287dd39d314570278d064c`, CI anterior [43603562803](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43603562803) `success`. O resultado foi produzido numa sessão Kaggle do operador; a análise deste documento recalculou os resultados do ZIP original, **sem reexecutar o motor PGlite**.

## Evidência primária e integridade

- ZIP fornecido pelo operador: `RIGHTWARE_SI_RD_03A_A0_V07_EVIDENCE.zip` (não publicado integralmente no repositório público), SHA-256 `064c4ce8ec24c257ee9b34adb973fa832df725fcaffd5a8bb095b870c0eab4f9`, teste CRC ZIP sem entradas inválidas.
- Manifesto incluído: 14 ficheiros com tamanho e SHA-256 **todos conferidos byte a byte**, incluindo as fixtures, runner JavaScript, scorer Python, resultados brutos e scorecard.
- `results/A0_V07_RAW_RETRIEVAL.json` SHA-256 `0ad278bbf50fbc928114d3ec020cb50bc2929d3e9f4094d4e73ee92b8537c98a`; `results/A0_V07_SCORECARD.json` SHA-256 `dc82b7154301e179005d03bd42d7cb03ecffe9148547411891d39995b83aba71`.
- Corpus SHA-256 `a72420867367a25e36c26c7fca29abdbfb4fe80008877f61c4e85444d53c68d8`; oráculos separados SHA-256 `2c03b8500beef185f6780a98eb7c7356b816e72ff0613c89467c7994688d024e`. O scorer foi refeito de modo independente dos outputs brutos (não se limitou a copiar o scorecard Kaggle).
- Ambiente reportado pelo ficheiro de execução: **PGlite 0.5.8 / PostgreSQL 18.3 WebAssembly**, Node.js v22.23.4, npm integrity SHA-512 presente; **binário/ambiente Kaggle não atestado externamente nesta análise**.
- 49 fontes sintéticas (29 autorizadas `rw:lab:shared`, 10 outro projecto, 10 outra organização), 40 queries, 31 queries com gold source, 9 sem gold (5 perguntas desconhecidas e 4 sondagens ACL). 4 `dictionary × method` runs com 80 rows cada (Top 1 e Top 2), total **320 rankings** e **160 contagens de candidatos** reportadas.
- As fontes devolvidas foram comparadas aos 49 IDs e ao `scope_id` local; não foi observada nenhuma devolução de fonte de outro scope (**0 violações nos outputs**). O runner usou apenas a fixture pública, um scope constante e SQL parametrizado; **não usou `case_id` ou oráculos** no WHERE. Verificação de código estática, não audit completo de uma identidade empresarial.

## Recontagem independentemente calculada — hit@k de fonte gold, n=31

| Dicionário | Formulação | Top 1 | Top 2 |
|---|---|---:|---:|
| `simple` | strict AND | 0/31 (0,00%) | 0/31 (0,00%) |
| `portuguese` | strict AND | 4/31 (12,90%) | 5/31 (16,13%) |
| `simple` | relaxed OR (pós-hoc v0.6) | 11/31 (35,48%) | 14/31 (45,16%) |
| `portuguese` | relaxed OR (pós-hoc v0.6) | **14/31 (45,16%)** | **19/31 (61,29%)** |

Todos os 8 valores reconciliarem com os runs brutos e scorecard original. Top 1 é prefixo do Top 2 em cada par de queries; os counts entre k=1 e k=2 são iguais; sem sources repetidas nos outputs. A métrica **não é accuracy de resposta**, `precision@k`, recall de todos os factos nem prova de autorização.

### Diferenças por coorte, melhor configuração `portuguese + OR`

- Histórico v0.5 com gold source: Top 1 **4/15**, Top 2 **9/15**. Desses 15, **6 são intencionalmente ambíguos** no corpus global; não contam como prova de raciocínio temporal.
- Novos desafios v0.7: Top 1 **10/16**, Top 2 **10/16** (8 questões PT e 8 EN, relacionadas entre si; não são blind holdout).
- Por idioma no conjunto scored: **PT 14/18** e **EN 5/13** em Top 2. Evidência de degradação lexical entre idiomas, não prova da qualidade comparativa de modelos multilingues.
- Consultas scored com pelo menos 1 candidato sob `portuguese + OR`: **29/31**; cobertura de candidatos não equivale a fontes correctas.
- O valor 13/15 (86,7%) em Top 2 da v0.6 era pós-hoc e **case-scoped pelo próprio oráculo**. O valor 19/31 deste corpus é metodologicamente diferente; a queda não pode ser atribuída apenas à remoção do case filter.

## Defeitos e limites identificados

1. **Ranking lexical vulnerável a distratores genéricos.** Em várias perguntas Top 2, surgem `V07:DISTRACTOR:CH01` e `V07:DISTRACTOR:CH02` antes da fonte gold, sobretudo questões EN e referências cruzadas. A normalização OR transforma termos genéricos em candidatos de alta frequência. Não adoptar `OR` puro como política de produção.
2. **Autoridade não é a ordem de ranking.** Na pergunta `MEM-04:canonical`, `portuguese + OR` Top 1 devolveu `LAB:MEM-04:agent:claim/7` (agente `UNVERIFIED_AGENT`), e só no Top 2 apareceu `LAB:MEM-04:postgres:task/7` (`AUTHORITATIVE`). A tarefa permanece `IN_REVIEW`; nenhuma decisão de aprovação é inferida da recuperação.
3. **ACL não é abstention.** Todas as 4 sondagens cujo dado pertence exclusivamente a um âmbito alheio tiveram candidatos **internos irrelevantes** sob OR; **0 fonte proibida foi devolvida** graças ao filtro fixo, mas um gerador poderia responder falsamente a partir das fontes erradas. `abstention_accuracy` ficou `NOT_EVALUATED`.
4. **Perguntas desconhecidas também retornam candidatos.** As 5 questões sem gold tiveram ao menos uma fonte autorizada sob OR. Não há mecanismo que decida `ABSTAIN` ou recuse informação insuficiente.
5. **Temporalidade/estado não avaliada.** MEM-02/MEM-03 partilham “pedido X” e estados DRAFT/IN_REVIEW; 6 perguntas são ambíguas quando colocadas em corpus global. A configuração de ranking não resolve `as-of` nem elimina sobreposições. `temporal_correctness=NOT_EVALUATED`.
6. **Isolamento simplificado.** `scope_id` é uma constante de laboratório, não derivada de autenticação/grants reais. O hard gate sem violações protege este ensaio mas não valida segurança de produção.
7. **Pequena amostra e leakage na investigação.** 49 documentos/31 consultas pontuadas com questões correlacionadas e casos desenhados pelos investigadores; OR nasceu pós-hoc no v0.6. O ensaio é um smoke experimental, não uma prova estatística robusta ou comparação de fornecedores.
8. **Latência não transferível.** Métricas do PostgreSQL-WASM single-process/Node não são latência de PostgreSQL Server e não devem orientar cálculos de performance/infra de produção.

## Gates propostos depois desta execução (RECOMENDAÇÃO, NÃO IMPLEMENTAÇÃO)

**A0-GLOBAL-02:** congelar v0.7 como controlo medido. Antes de qualquer nova contagem comparativa, definir nova coorte cega com IDs exactos, distractores altamente semelhantes e perguntas PT/EN naturais sem pistas do oráculo. **Não apagar os casos falhados.**

**A0-GLOBAL-03:** construir matrizes *candidate generation vs ranking vs authority*: `exact_identifier_lookup` para IDs, FTS com tratamento PT/EN, sem obrigar qualquer fornecedor a implementar “aprovação” como memória. Relatar `hit@1`, `hit@2`, cobertura semântica, autorização/scope e erros de abstention separadamente.

**A0-GLOBAL-04:** só após fixar avaliação, executar PostgreSQL Server, Mem0 OSS `infer=false` (SHA pin actual) e Hindsight `chunks` (SHA pin e configuração actual verificada) em bancos isolados, usando o mesmo corpus elegível, tamanho/top-k e ID das fontes. Não comparar custos de forma conclusiva sem registar embeddings/modelos/CPU/RAM.

**A0-GLOBAL-05:** separar em produto `RETRIEVED`, `AUTHORITATIVE`, `CHECKED_PASS` e `REVIEW_ACCEPTED`; não tratar matching vector/FTS ou LLM como evidência para `DONE`. O Core R2 deve continuar com as suas ratificações de segurança no outro chat.

**Decisão técnica:** `READY_WITH_CAVEATS` como baseline de pesquisa. **NO_PROVIDER_SELECTION / NO_PRODUCTION_AUTHORIZATION**. O ZIP original Kaggle deve permanecer guardado como evidência, fora do repositório público até existir política de armazenamento e retenção aprovada.
