# SI-RD-03A A0 v0.7 — Protocolo de recuperação GLOBAL sem oracle leakage

**Data:** 2026-11-13 Africa/Maputo. **Classificação:** INVESTIGAÇÃO / PROTOCOLO CONGELADO ANTES DE EXECUÇÃO PGlite; **não é aprovação de arquitectura, benchmark de fornecedores ou release.**
**Início verificado:** `develop@3906bf49f1d67acdacaf55d14af28b660f614ba1`. CI anterior [43482600418](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43482600418) `completed/success`.

## Problema técnico
No ensaio v0.6, a pesquisa OR pós-hoc obteve 13/15 no Top 2, mas usava `WHERE case_id = q.base_case_id` — identidade proveniente do oráculo, que restringia cada consulta a 1–3 fontes. A0 v0.7 remove esse filtro. Nenhum número v0.6 deve ser tratado como performance num corpus global.

## Artefacto técnico permanente
- [Notebook Kaggle SELF-CONTAINED v0.7](RIGHTWARE_A0_GLOBAL_KAGGLE_V07.ipynb) — localizado neste directório, inclui pacote ZIP incorporado com ficheiros Python/JS, fixtures, testes, hash e protocolo. **NÃO necessita outro dataset Kaggle**.
- SHA-256 do notebook: `034a13379a6153284d33fd9c3f8cab50846e3bb46708630b11cb50fd992af6ca`; SHA-256 do ZIP de fontes standalone entregue ao operador: `dbabdecc94ae6f25c2af3d5d110be7d63de6f3b56058c9327b914baa4cafbb1b`; SHA-256 do ZIP incorporado no notebook: `170d44e36e513239d68e6fc8e2959b9eeddd18d61bd21fa685775f0117599dab`.
- Fontes do ensaio: 11 registos originais intactos, com hash de v0.5 `c5d3c01e3b3d6dd422a6dc7a09eed84dcf09cfeed7fd5893d2c59e292a202ac4`, + fontes sintéticas novas.
- Public fixture SHA-256 `a72420867367a25e36c26c7fca29abdbfb4fe80008877f61c4e85444d53c68d8`; scoring oracle separado SHA-256 `2c03b8500beef185f6780a98eb7c7356b816e72ff0613c89467c7994688d024e`.

## Desenho congelado — A0 v0.7
- **49 fontes sintéticas**: 29 no âmbito autorizado fixo `rw:lab:shared` e 20 em dois âmbitos alheios. O SQL consulta todos os 29 do âmbito; não recebe `case_id`, rótulo do cenário, ground truth, gold source ID, role ou scope da pergunta.
- **40 perguntas**: 18 históricas, 16 novos desafios identificados PT/EN, 4 sondagens ACL e 2 desconhecidas. De 40, 31 têm oráculo de fonte; 9 não têm. Seis perguntas MEM-02/MEM-03 históricas são ambíguas com corpus global.
- **8 configurações:** `simple` vs `portuguese`; `strict_websearch_AND` vs `relaxed_websearch_OR_V06_CONTINUATION`; Top 1 vs Top 2. A variante OR é continuidade **pós-hoc da v0.6**, não hipótese cega.
- **320 consultas de ranking**, 160 consultas de contagem de candidatos, 2 sentinelas de FTS com PGlite pin `@electric-sql/pglite@0.5.8` e PostgreSQL-WASM. Em Kaggle verificar ainda versão de PostgreSQL via `SELECT version()` e integridade sha512 lockfile.
- Runner lê exclusivamente `A0_V07_PUBLIC_CORPUS.json`; a avaliação posterior carrega `A0_V07_SEALED_ORACLES.json` apenas depois de gravar raw; nenhum LLM/extração de respostas e nenhuma DB remota.
- Métricas pré-fixadas: hit@1, hit@2 e candidatos por coorte; `scope_violations=0` como hard-gate; tempos WASM apenas descritivos. `abstention_accuracy`, `authority_correctness` e `temporal_correctness` são `NOT_EVALUATED`.

## Provas e limites
- Verificado localmente nesta preparação: **15/15 testes de contrato PASS**, JS `node --check` PASS, schema/digests/reprodução determinística PASS, bloco inicial do notebook executado com 15 testes PASS. Os testes de scoring com resultados artificialmente perfeitos são **FAKE DE TESTE**, não resultados de fornecedor.
- **Não executado nesta etapa:** 320 consultas reais PGlite v0.7; PostgreSQL Server, Mem0, Hindsight, teste de resposta/abstenção, validação de controlo multi-tenant real e decisões de reviewer/DONE. Até receber ZIP de evidências Kaggle: `NO_PROVIDER_DECISION`.
- **Limites:** corpus pequeno e dependente; desafios novos desenhados pelos investigadores (não holdout cego); perguntas inglesas contra fontes portuguesas; atribuição de âmbito fixa em laboratório, não sistema de autorização de produção.

## Sequência de execução
1. Importar notebook completo em Kaggle, CPU/Internet On; o notebook inclui os dados, portanto nenhum ZIP ou Dataset externo é necessário.
2. Run All; verificar PGlite 0.5.8 instalado, 15 testes de contrato, 320 queries e scorecard com ACL hard-gate.
3. Descarregar `RIGHTWARE_SI_RD_03A_A0_V07_EVIDENCE.zip`; analisar independentemente os 8 grupos de resultados, misses, ambiguidades e scope.
4. Só depois estudar corpus cego e PostgreSQL Server / Mem0 `infer=false` / Hindsight `chunks` comparáveis.

**Não alterado:** codebase WorkCore R1/R2, migrations, APIs, workflows, dependências do produto, produção, `main`, Jarvis/PULSE. Este checkpoint adiciona apenas notebook de investigação, manifesto, protocolo e handoffs. O CI do novo commit deve ser verificado separadamente; CI verde anterior NÃO demonstra PGlite v0.7.
