# 00 — Recuperação independente do chat

**A fonte normativa é [HANDOFF_POLICY.md](../HANDOFF_POLICY.md)**, e nunca este resumo. Recuperar sempre código e CI no SHA actual:

```powershell
# Primeira utilização
git clone https://github.com/rightware-corporations/rightware-shared-intelligence.git
cd rightware-shared-intelligence
git fetch origin
git switch develop
git pull --ff-only origin develop
git rev-parse HEAD
git status --short
Get-Content docs/HANDOFF.md -TotalCount 100
Get-Content docs/HANDOFF_MASTER.md -Tail 150
```

Se já existe clone, omitir `clone`. Não usar reset ou force-push; um `git pull --ff-only` falhado exige reconciliação de alterações. Validar GitHub Actions do SHA real, não assumir que CI do commit anterior valida novos ficheiros.

## Gates para registar trabalho
1. Consultar HEAD, CI, CURRENT/MASTER e decisões mais recentes; distinguir DECISÃO OFICIAL, IMPLEMENTAÇÃO, PROPOSTA, EXPERIMENTO e HIPÓTESE.
2. Executar no escopo autorizado; separar testes locais, CI, PGlite WASM, PostgreSQL Server, Mem0/Ollama E2E e benchmark de fornecedores.
3. No **mesmo commit em develop**, actualizar `docs/HANDOFF.md` e acrescentar SI-MH-XXXX a `docs/HANDOFF_MASTER.md`. MASTER só recebe adendas, nunca apagar/reinterpretar histórico.
4. Confirmar branch SHA, ficheiros e CI após commit. Se CI não terminou, marcar PENDING e registar verificação noutro checkpoint.
5. `main` só com autorização expressa; não integrar JARVIS/PULSE, dados privados ou novos sistemas sem gate próprio.
6. Chaves de avaliação, plaintext de oráculos, tokens, dados de utilizadores/clientes e raw dumps **fora do Git público, Kaggle e runners**. Versão selada A0-GLOBAL-02 não entra em treino nem tuning E1.

**Correcção de erro:** usar adenda posterior SI-MH, e nunca apagar erro histórico. Se ZIP externo não está acessível, declarar `EVIDENCE_FILE_UNAVAILABLE`, não simular medição.
