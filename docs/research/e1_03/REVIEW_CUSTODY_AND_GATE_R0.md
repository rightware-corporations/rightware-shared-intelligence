# ENG-E1-03 — Custódia e revisão independente de rótulos (E1.1C)

**24/11/2026 | ESTADO: FERRAMENTAS PREPARADAS; NENHUMA REVISÃO HUMANA RECOLHIDA.**

Este procedimento complementa [o rubric E1.1B](../e1_02/ANNOTATION_RUBRIC_R0.md) e a prioridade [E1 R1](../RIGHTWARE_ENGINE_E1_EXECUTION_ORDER_R1.md). Não substitui o avaliador científico, uma decisão de governança de dados ou a segurança G04.

## O que existe tecnicamente

- `e1_03_review_protocol.py` cria um pacote **apenas train/dev** do E1.1B: 42 fontes e 24 perguntas, com metadados de âmbito, autoridade e tempo. Não inclui `role`, `group_id`, rótulos provisórios, classes gold ou quaisquer documentos e perguntas `eval`.
- Cria dois formulários **vazios e idênticos**, um por slot de avaliação. Nenhum ID humano nem assinatura é colocado automaticamente. Os formulários, respostas e relatórios ficam exclusivamente em `.runtime/`, já ignorada por Git.
- Verifica que cada avaliação abrange as 24 perguntas e todas as 560 relações pergunta/documento por avaliador; exige justificação, classificação, citações literais de fonte para grades positivas, respeito por organização/projeto/autoridade/validade temporal.
- Compara dois registos submetidos, identifica divergências, calcula concordância exata, Cohen kappa para classes e kappa quadrático ponderado para grades. **Kappa indefinido com distribuição degenerada é `null`, nunca 1.**
- Uma submissão com `independence_attested=true` é **auto declaração**, não prova criptográfica de que são pessoas diferentes. Duas assinaturas fictícias ou dois pseudónimos distintos não contam como dois humanos. Não é gerado gold de avaliação.

## Procedimento do operador

1. Preparar um ambiente com ACLs, disco encriptado e cópia de segurança fora do Git público. Não partilhar ficheiros da pasta `.runtime/` em PR, issues, anexos públicos, screenshots ou CI.
2. No repositório local, executar `python scripts/e1_03_review.py --mode export --output-dir .runtime/e1_03`. O comando cria `review_packet.json`, `review_A_BLANK.json`, `review_B_BLANK.json`. Rejeita um diretório fora de `.runtime/` e não sobrescreve ficheiros existentes.
3. Nomear dois revisores reais **independentes**, de preferência um técnico de domínio e um segundo com competência relevante em relevância/avaliação ML, e registrar a sua autorização num sistema privado. Verificar pessoalmente que não participaram na autoria das regras ou exemplos e não consultaram `labels_provisional.jsonl`.
4. Entregar cópias separadas do pacote (sem acesso à resposta do outro revisor). Cada revisor atribui classe e grades 0–3 a cada fonte do split, justifica e inclui excerto literal quando o grade é positivo. O ID público é um pseudónimo `RV-...`; os nomes verdadeiros ficam num registo privado de custódia e não no Git.
5. Verificar submissões **apenas localmente**: `python scripts/e1_03_review.py --mode compare --a .runtime/e1_03/review_A_SUBMITTED.json --b .runtime/e1_03/review_B_SUBMITTED.json --output-dir .runtime/e1_03`. Isto cria `agreement_PRIVATE.json`; o programa não verifica identidade física e não afirma consenso.
6. Um **terceiro adjudicador independente** deve rever as divergências sem aceder a hipóteses do modelo. A equipa responsável regista origem da decisão, razão, exceções e concordância, sob custódia privada e auditável. O código deste checkpoint **não gera gold adjudicado**.
7. Para um verdadeiro teste blindado, um curador externo ao desenvolvimento deve produzir/controlar um conjunto adicional não publicado de perguntas/fontes/rótulos, com hashes e licença, e executar a avaliação sem devolver as respostas ao treino. Os oito `eval` públicos E1.1B continuam sem gold; *não são blindados*.
8. Antes de `E1_DATA_READY`, exigir relatório humano de qualidade de anotação por classe e idioma, auditoria semântica manual de near-duplicates, revisão dos negativos, validade/consentimento, receção dos dois revisores, adjudicação, isolamento do evaluator e aprovação institucional documentada.

## Controlo de segurança e ciência

- O repositorio é público. Os formulários preenchidos podem conter nomes ou opiniões de pessoas; nunca submetê-los ao Git público. `.runtime/` é uma proteção contra `git add` normal, **não** encriptação nem custódia legal de dados.
- Pacotes são apenas de fontes sintéticas, mas mesmo assim as decisões dos revisores devem ficar privadas para evitar contaminação. A ferramenta não consulta `labels_provisional.jsonl` para produzir qualquer resposta do pacote.
- Dois revisores não devem ser simulados com LLMs ou pela mesma pessoa. Os testes unitários usam `RV-MOCK-...` como dados falsos de teste de schema, **zero** respostas humanas.
- Conservação, identidade, autorização de acesso, assinaturas digitais e política de retenção estão ainda por aprovar via G04/D09–D11.
- Não usar o desafio selado SI-RD-03A A0-GLOBAL-02 para treino, heurísticas, limiares ou calibração.

**Gate:** `E1_REVIEW_INFRA_READY` pode ser atribuído depois do CI verde deste mecanismo. `E1_DATA_READY` **continua REVIEW_REQUIRED** até revisões humanas e avaliação verdadeiramente independente. E1.2 baselines, E1.3 RW-R1, E1.4 calibração e E1.5 revisão científica permanecem pendentes.
