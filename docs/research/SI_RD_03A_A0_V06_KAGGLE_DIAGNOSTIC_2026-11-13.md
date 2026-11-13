# SI-RD-03A A0 v0.6 — Auditoria das evidências Kaggle PostgreSQL-WASM (13/11/2026)

**Classificação:** EXPERIMENTO/VALIDAÇÃO ESTÁTICA DE EVIDÊNCIA (não decisão, não benchmark comparativo aprovado, não produção).  
**Repo:** `rightware-corporations/rightware-shared-intelligence` (relatório importado sobre `develop@4e6715be0ff811fe6daae6024855a4826d0b36b1`).  
**Origem da evidência:** ficheiro ZIP sintético entregue pelo operador a partir do Kaggle; não armazenado integralmente no repositório público.  
**ZIP SHA-256:** `ac24694e9a0baa36d88646c741f203e1d890e7ed321c6105bc9bebef2566e1b9` (6 entradas, CRC/ZIP íntegros).  
**JSON resultados SHA-256:** `d974631c755d54b31c3ef7e8dedb3f90abbca5a55965d7ae9f91b330389e0ea6`.  
**Fixture SHA-256:** `c5d3c01e3b3d6dd422a6dc7a09eed84dcf09cfeed7fd5893d2c59e292a202ac4` (conferido com `A0_PGLITE_DATASET_V05.sha256`).

## 1. O que foi realmente executado

O artefacto entregue reporta **PostgreSQL 18.3 via PGlite 0.5.8, WebAssembly**, Node e ambiente Kaggle, com 11 documentos sintéticos, 18 perguntas e **144 consultas** (2 dicionários × 2 formulações × 2 top-k × 18). Controlo positivo de `identificador` em ambos os dicionários consta do código e foi condição para prosseguir. A auditoria independente desta importação confirmou estrutura JSON, contagens, hashes e recalculou os 8 numeradores/denominadores a partir dos 18 registos de cada configuração. **Não foi reexecutado o PostgreSQL no ambiente de auditoria** nem verificado externamente o binário/processo Kaggle; a identidade da versão é reportada pelo resultado.

| Dicionário | Formulação | Top 1 | Top 2 | Documentos encontrados (das 18 consultas) |
|---|---|---:|---:|---:|
| simple | strict AND (`websearch_to_tsquery` da pergunta inteira) | 0/15 | 0/15 | 0/18 |
| portuguese | strict AND | 0/15 | 0/15 | 1/18 |
| simple | relaxed OR **POST-HOC** | 7/15 (46,7%) | 13/15 (86,7%) | 16/18 |
| portuguese | relaxed OR **POST-HOC** | 9/15 (60,0%) | 13/15 (86,7%) | 16/18 |

A métrica é **hit@k da fonte esperada**, não precisão@k, exactidão de resposta, recall de toda a informação, qualidade de memória ou segurança. Apenas 15 das 18 consultas têm fonte-oráculo; três casos de resposta desconhecida (`MEM-05`) **não entram no denominador**. Cinco perguntas são originais e dez são reformulações PT/EN; não são 15 observações estatisticamente independentes. O caso MEM-06 usa oráculo derivado dos duplicados.

## 2. Diagnóstico causal e erros encontrados

- A formulação AND de `websearch_to_tsquery` exige a intersecção de quase todos os tokens da pergunta; termos como `qual`, `identificador`, `exacto` não constam todos na fonte MEM-01. Assim, o documento é descartado **antes** de ser ordenado. Em `simple` nenhuma das 18 perguntas obteve sequer candidato; em `portuguese`, apenas MEM-04 obteve candidato, mas este era a **afirmação não verificada** do agente.
- A variante OR foi proposta **depois de observar o 0/15**, logo é diagnóstico pós-hoc. Recupera fontes antes excluídas, mas não é um vencedor de benchmark pré-registado.
- No **Top 1** do MEM-04, a variante OR frequentemente prioriza `LAB:MEM-04:agent:claim/7` («terminei e aprovei») acima de `LAB:MEM-04:postgres:task/7` («IN_REVIEW»). Encontrar ambas em Top 2 não resolve a confiança; o servidor autoritativo e o estado de aprovação continuam separados do ranking textual.
- As duas consultas sem candidato no OR são `MEM-01:stress:2` (“Which reference number identifies this synthetic case?”) e `MEM-06:stress:2` (“Which database does the team use?”). O corpus está em português: o método lexical não traduz nem infere equivalência semântica.
- Em MEM-02/MEM-03, os resultados Top 2 podem trazer simultaneamente estados anteriores e posteriores. Não existe aí uma regra autónoma de resolução temporal; ranking textual NÃO equivale a `as-of` fiável.
- Em MEM-05 o motor encontra o documento «não tem orçamento registado» sob OR, mas não executa geração nem decisão **ABSTAIN**. Não declarar abstention accuracy.
- **Limitação grave da elegibilidade:** o SQL usa `WHERE case_id = $1` com `q.base_case_id` retirado do próprio dataset/oráculo. O motor recebe antecipadamente qual dos seis casos contém a resposta; cada busca passa a competir com apenas 1–3 documentos. Portanto **13/15 Top 2 não estima recuperação em corpus global nem um contexto empresarial real**. Este filtro é uma *oracle leak* metodológica; deve ser removido em teste futuro, excepto quando o contexto autorizado fornecer legitimamente esse caso antes da consulta.
- As diferenças dos métodos v0.2/v0.5 e as latências single-run WASM não suportam ranking de fornecedores ou estimativa de throughput de servidor. Não se deve reutilizar o score OR como aprovação de PostgreSQL FTS ou rejeição de Mem0/Hindsight.

## 3. Recontagem independente (grupos)

| Método / k | Canonical PT (5) | Stress PT (5) | Stress EN (5) | Total |
|---|---:|---:|---:|---:|
| simple OR Top 1 | 4/5 | 2/5 | 1/5 | 7/15 |
| portuguese OR Top 1 | 4/5 | 3/5 | 2/5 | 9/15 |
| simple OR Top 2 | 5/5 | 5/5 | 3/5 | 13/15 |
| portuguese OR Top 2 | 5/5 | 5/5 | 3/5 | 13/15 |

## 4. Gates para o próximo ensaio (RECOMENDAÇÃO; NÃO IMPLEMENTADO)

1. **A0-G01 — Correcção de elegibilidade:** remover `q.base_case_id` de qualquer filtro que dependa do ground truth; preservar filtros derivados de identidade/organização/projecto autenticados. Reportar em paralelo a versão `case_scoped_diagnostic` para continuidade histórica.
2. **A0-G02 — Pré-registo:** fechar taxonomia/tokenização/ranking, `top_k`, stemmer, language handling e tratamento de queries sem resposta **antes de executar** a nova fixture. FTS `simple`/`portuguese`, AND/OR e eventualmente TSQuery com intenção/normalização devem ser versões nomeadas.
3. **A0-G03 — Oráculos separados:** métricas de `hit@1`, `hit@2`, `candidate_coverage`, `authority_correct`, `temporal_correct`, `abstention_correct`; não derivar decisões de aprovação do score lexical. Testar MEM-04 e as-of em camada de confiança separada.
4. **A0-G04 — Corpus maior e cego:** criar distractores cross-case, reformulações novas PT/EN, ambiguidade de IDs, estados contraditórios, múltiplos projectos autorizados. Avaliar separadamente 6 casos canónicos, derivados e holdout independente; relatar amostra/dados por coorte.
5. **A0-G05 — Execução de fornecedores reais:** só após gates de fairness executar PostgreSQL Server FTS, Mem0 pin `infer=false`, Hindsight pin `chunks`, com corpus, granularidade e permissões comparáveis; atestar versões e logs. Nunca promover memória recuperada a revisão ou DONE.

## 5. Limites e não alterado

Nenhuma nova API, migration, runtime, modelo, dependência, branch, PR, acção externa ou teste de fornecedor foi criado por esta importação. **Mem0, Hindsight e PostgreSQL Server = NOT_RUN neste experimento**. Não alterar `main`, JARVIS ou PULSE. A engenharia R2 e os seus gates de segurança no outro chat preservam prioridade; a presente pesquisa não ratifica G01 ou outras políticas.

**Resultado: MÉTODO CORRIGÍVEL / DECISÃO DE FORNECEDOR NÃO PRONTA.**
