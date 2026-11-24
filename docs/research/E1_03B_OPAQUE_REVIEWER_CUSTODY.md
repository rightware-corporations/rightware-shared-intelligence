# ENG-E1-03B — Guard de IDs opacos para revisão sintética

**Data:** 24/11/2026 (Africa/Maputo). **Estado:** IMPLEMENTADO, CI DO NOVO SHA PENDENTE, GOLD HUMANO AUSENTE.

## Motivo
[SI-MH-0076](SI_MH_0076_E1_03_BLIND_ID_AUDIT.md) confirmou fuga metodológica: o pacote E1.1C antigo expunha `q1/d1`, `q2/d2`, `q3/q4` que permitem deduzir 24/24 labels provisórios. Os 328 testes anteriores permanecem PASS, mas **o pacote antigo NÃO PODE ser entregue aos revisores**.

## Entrega ENG-E1-03B

- Novo `e1_03_blind_alias.py` cria aliases `DOC-...`/`QUE-...` criptograficamente aleatórios e diferentes por revisor A/B, embaralha ordem, preserva texto e metadados de escopo.
- `scripts/e1_03_review.py --mode export` cria **separadamente** `.runtime/e1_03/reviewer_A`, `reviewer_B` e `CUSTODY_ONLY`. Apenas `reviewer_A/` vai para A e apenas `reviewer_B/` para B. **NUNCA partilhar CUSTODY_ONLY/PRIVATE_ALIAS_MAP.json**.
- `--mode compare --a .runtime/e1_03/reviewer_A/SUBMITTED.json --b .runtime/e1_03/reviewer_B/SUBMITTED.json` valida as submissões específicas e reconcilia os aliases somente dentro da custódia local. Estatísticas kappa/discordância permanecem locais e não expõem IDs originais.
- 13 novos testes de anti-leakage, mapa privado, hash, swapping, tentativa de submissão com ID original, reconciliação mock e isolamento da API. **341 testes esperados**, NÃO PASS antes do CI deste SHA.
- Código e dados E1.1B originais intocados; 56 fontes/32 perguntas, 24 labels provisórios e 8 eval unlabeled permanecem iguais.

## Limites
Um ID opaco **não transforma dados públicos com labels publicados em avaliação verdadeiramente cega**. Revisores ainda poderiam localizar texto e regras no GitHub, e os 8 itens eval públicos não são um holdout secreto. **Dois humanos independentes, adjudicação e novo corpus reservado com gold são obrigatórios para E1_DATA_READY**. Os testes mock não equivalem a pessoas.

P1 `AUTHORITY_CONFLICT` continua ABERTO: relevância textual e elegibilidade de autoridade precisam de campos distintos antes de avaliar contradições entre fonte oficial e afirmação não verificada. Não alterar sem protocolo. G04 identidade/RLS real, dados privados, produção, E1.2–E1.5 e modelo treinado seguem bloqueados.

**Comandos:** `python scripts/e1_03_review.py --mode self-check`, depois `--mode export` local. Não partilhar o diretório inteiro; proteger os ficheiros privados e verificar autorização dos revisores fora deste código.
