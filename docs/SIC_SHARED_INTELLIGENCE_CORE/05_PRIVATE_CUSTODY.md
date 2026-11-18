# 05 — Custódia de ficheiros e backup SIC

## Repositório público — permitido
Documentos, scripts e datasets **sintéticos** revistos, hashes e resultados sanitizados; pacote público v0.8 já no Git: `docs/research/bundles/RIGHTWARE_SI_RD03A_A0_GLOBAL02_PUBLIC_v08.zip`, SHA256 `c946ef45f97d932796e6ddc80c453da797f2523b0c06b19ae7dfecb38dcc1707`.

## Repositório público — proibido
Chave privada do avaliador v0.8, oráculo plaintext, credenciais, dumps, informações pessoais/cliente, conversas privadas e logs confidenciais. O ZIP público apenas contém o **oracle cifrado**. SHA256 da chave privada `f3903e8892e17d5a2f0d806b7e8db6a4c0e9c728d000b2c1d2241d6211f5270c` identifica o ficheiro, **não** significa armazenamento seguro validado.

## Lacuna de durabilidade
ZIPs de laboratório v0.1–v0.7, evidências originais Kaggle v0.6/v0.7 e relatório PDF estão inventariados no [catálogo](02_FILES_AND_EVIDENCE.md), mas alguns só existem como artefactos desta conversa. Não são anexados automaticamente ao Git, e links de ChatGPT não equivalem a backup durável.

**RECOMENDAÇÃO AINDA NÃO IMPLEMENTADA:** cofre corporativo privado, duas cópias cifradas e recuperação ensaiada; separar (A) fontes/ZIPs (B) evidências de execução (C) chaves e sealed gold, com acesso e retenção aprovados. O avaliador abre a chave somente offline após congelar resultados brutos dos motores; a chave não é usada no treino E1 nem partilhada com Kaggle/runners.

### Verificação Windows
```powershell
Get-FileHash -Algorithm SHA256 ".\RIGHTWARE_SI_RD03A_A0_GLOBAL02_PUBLIC_v08.zip"
# esperado: C946EF45F97D932796E6DDC80C453DA797F2523B0C06B19AE7DFECB38DCC1707
```
Se hash divergir, conservar duas versões e investigar, nunca sobrescrever sem rasto. Se não houver cópia externa, declarar `EVIDENCE_FILE_UNAVAILABLE` e não fabricar resultados.
