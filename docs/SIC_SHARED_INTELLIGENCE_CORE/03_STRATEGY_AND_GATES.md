# 03 — Prioridades e gates de execução SIC

**DIRECÇÃO OFICIAL:** RIGHTWARE construir tecnologia própria comprovável de ranking, conhecimento temporal e decisão evidencial — não apenas montar APIs de terceiros. **Não** afirmar que BM25 é IP própria, que RW-R1 já foi treinado, ou que existe produto público.

## Sequência principal E1 (obrigatória)
1. **E1.1C / ENG-E1-03 — AGORA:** obter **dois revisores humanos independentes**; relevância/answerability/trechos, adjudicação, acordo, custódia do gold verdadeiro em holdout separado. Hoje há **0 revisores**, dados E1.1B provisórios e 8 eval queries sem gold; `E1_DATA_READY=REVIEW_REQUIRED`.
2. **E1.2:** BM25, dense, híbrido no mesmo corpus autorizado, configs/hashes, qualidade PT/EN.
3. **E1.3:** treinar RW-R1 com pesos/features, model card e ablação real, não mera regra lexical.
4. **E1.4:** calibrar `EVIDENCE_CANDIDATE/ABSTAIN/CONFLICT/DENY` em dev, medir risco vs cobertura.
5. **E1.5:** comparar no teste independente held-out (fonte, tempo, autoridade, língua, custos, segurança), avaliação científica honesta.

## Frentes paralelas (sem roubar foco)
- **G04:** apenas D01–D05/D12 do piloto sintético ratificados; OIDC real, identidade SERVICE, memberships, resource ACL/RLS, consentimento/privacy e G05 não implementados. Bloqueia dados privados/clientes e produção.
- **Core R1/R2/G01:** PostgreSQL e verificação GitHub/REST em laboratório, memória Mem0/Ollama sem autoridade; `CHECKED_PASS` nunca é `DONE`.
- **SI-RD-03A A0 v0.8:** 82 docs/56 perguntas com oracle cifrado e separado; benchmark PostgreSQL Server/Mem0/Hindsight igualitário ainda NOT_RUN. Preparar adaptadores só em infraestrutura isolada e não misturar com dataset de treino E1.

**Não prioridade:** UI, novos conectores por curiosidade, releases de JARVIS/PULSE, production deploy, alterações `main`, novos ramos. Próximo trabalho: E1.1C com custódia e revisão humana reais, sem fabricar scores nem assinaturas.

## SI-MH-0076 — Reviewer ID blinding gap (auditoria, não implementação)
- [Relatório completo](../research/SI_MH_0076_E1_03_BLIND_ID_AUDIT.md): apesar do CI E1.1C **328/328 PASS**, o pacote revela IDs que permitem reconstruir **24/24** labels provisórios, embora os valores gold não sejam exportados. Não distribuir como blind review sem aliases e custódia. Próximo patch **ENG-E1-03B**; E1_DATA_READY segue REVIEW_REQUIRED e reviewers reais=0.

## Adenda SI-MH-0078 — E1.1C
O pacote v2 distingue suporte autoritativo de evidência contraditória não verificada. [Contrato](../research/SI_MH_0078_E1_03C_CONFLICT_CONTRACT.md). CI pendente; não distribuir v1. E1_DATA_READY REVIEW_REQUIRED, 0 revisores humanos documentados. Depois de CI aprovado, executar revisão humana e curadoria reservada, não saltar para treino.

## SI-MH-0080 — Human execution gate
[ENG-E1-04 runbook](../research/e1_04/OPERATOR_RUNBOOK.md) and [report](../research/SI_MH_0080_E1_04_REVIEW_OPERATIONS.md). v2 356/356 CI verified; actual distribution and browser smoke pending; no human results. E1.1C is waiting for real reviewers and reserved curator, not more model code.

## SI-MH-0082 — Human execution helper
[Local packaging](../research/SI_MH_0082_E1_04_PACKAGING_GATE.md); five mock checks passed; actual human reviews absent, browser smoke not run. No scientific pass.
