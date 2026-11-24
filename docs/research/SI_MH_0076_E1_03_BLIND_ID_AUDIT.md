# SI-MH-0076 — E1.1C Identificador preditivo e risco de revisão parcialmente cega

**Data:** 2026-11-24 Africa/Maputo. **Classificação:** AUDITORIA METODOLÓGICA INDEPENDENTE / BUG DE DESENHO DE AVALIAÇÃO (P0 para alegações de blind review, não falha da suite de software). **Não** altera resultados de CI, corpus ou implementação; é adenda ao SI-MH-0075, nunca reescrita retrospectiva.

## Contexto e prova
- Baseline de leitura: `develop@ae7d2f58b062c1814b7b78e024dc08d1ea8b1b61`, [CI anterior](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45344939725) SUCCESS com 328/328 testes. E1_REVIEW_INFRA_READY significa schema/contrato de software operacional, não verdadeiro blind review.
- Em `backend/rightware_si/e1_03_review_protocol.py`, `DOC_FIELDS` contém `source_id` original e `QUERY_FIELDS` contém `query_id` original. `make_packet()` exporta estes valores de `docs/research/e1_02`. Eliminar `role`, `group_id` e o ficheiro `labels_provisional` é necessário mas **não suficiente**.
- Conferência independente contra os 24 labels provisórios: **12/12 perguntas positivas** são inferíveis pelo padrão `...-q1→...-d1` e `...-q2→...-d2`; **12/12 perguntas negativas** são `...-q3` ou `...-q4` com relevância vazia. Portanto **24/24** labels provisórios são reconstruíveis a partir dos IDs que constam do pacote sem abrir o ficheiro de labels.
- Os dois formulários A/B são estruturalmente idênticos, com os IDs originais. Existem 0 revisores humanos registados, 0 decisões adjudicadas e 0 gold externo. Oito perguntas eval são públicas e não foram exportadas (correcto), mas também não constituem holdout cego.

**Conclusão:** o sistema passou a auditoria de *não exportar os valores dos labels*, mas falha a protecção contra **informação da resposta codificada nos IDs**. Um revisor pode ser influenciado por q1/d1 mesmo sem ter lido o gold. Não usar as anotações deste pacote para reivindicar avaliação independente sem eliminar o canal. Este achado NÃO implica fuga de tenant ou dados privados, nem invalida que 328 testes foram executados com PASS.

## Risco adicional (P1): classe AUTHORITY_CONFLICT
O validador exige pelo menos dois `grade>=2` elegíveis para `AUTHORITY_CONFLICT`, mas `_eligible()` recusa grades positivos em fontes `UNVERIFIED_CLAIM`. Isso impede codificar directamente o cenário típico 'fonte oficial contradiz alegação não verificada' como duas evidências em conflito. Diferenciar *relevância textual da alegação* de *elegibilidade para resposta autoritativa*, ou definir uma lista tipada de claims contraditórias. Necessita teste de caso, não afirmar regressão em produção.

## Recomendação técnica ENG-E1-03B (a implementar, não executada aqui)
1. Criar IDs opacos aleatórios, independentes para revisor A e B, para perguntas e fontes; não preservar ordinal `q1/d1` no output; embaralhar a ordem. Mapa de reconciliação **só no cofre privado**, com hash e permissão restrita, fora do Git/CI e de cada revisor.
2. Alterar o validador para aceitar aliases emitidos no pacote e resolver IDs originais **somente após** recepção; nunca exigir acesso do revisor a `labels_provisional.jsonl` ou ao repositório público. Versão nova de schema/manifesto, não substituição silenciosa.
3. Tests negative-first: nenhum ID original, `group_id`, `role`, `labels_provisional`, `source_relevance`, `q1/d1` implícitos nos pacotes; aliases não colidem, não são previsíveis, cobrem todas as fontes do split, chaves de mapping não aparecem nos forms; A/B não são idênticos. Simular submissões e verificação sem dar pontuações científicas.
4. Deixar intactos os 56 documentos e 32 perguntas E1.1B, 24 rótulos provisórios e 8 eval publicamente sem gold. **Mesmo após aliases**, o E1.1B publicamente rotulado NÃO se transforma num verdadeiro holdout independente; o curador de avaliação deverá criar/guardar novo conjunto oculto.
5. Rever `AUTHORITY_CONFLICT` com testes que separem fonte citada e fonte válida para resposta. Antes de distribuir A/B, executar CI, verificar os outputs redigidos e confirmar custódia externa. Só depois organizar dois humanos realmente independentes e adjudicador.

## Estado e limites
- `E1_REVIEW_INFRA_READY` tecnicamente após CI SI-MH-0075, **com bloqueio de distribuição** por leakage.
- `E1_DATA_READY=REVIEW_REQUIRED`; E1.2–E1.5 e RW-R1 treinado ainda não realizados.
- **Não alterado:** código, testes, CI, dados, segredos, runtime, main, JARVIS/PULSE, R2/G04, PostgreSQL Server/Mem0/Hindsight A0-GLOBAL-02. Esta entrega só produz documentação de investigação + ambos handoffs.
- Próximo passo especificado: ENG-E1-03B alias/blinding guard e CI; depois anotação humana real. O CI do checkpoint documental deve ser verificado separadamente.
