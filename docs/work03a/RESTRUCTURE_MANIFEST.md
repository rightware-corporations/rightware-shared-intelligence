# WORK-03A — Manifesto de Reorganização

**Data:** 2026-11-12 · **Branch:** `develop` · **Base:** `6c257ff70b5ac961b455cc23fb96a6676e575939` · **Estado no commit:** implementação, CI pendente.

## Regra de integridade
Verificação das árvores do GitHub: **17/17 blobs originais conservam exatamente o mesmo SHA** depois de mover de diretório. Não houve reescrita dos 11 ficheiros Python do pacote, 3 migrações SQL ou 3 ficheiros de requisitos.

## Mapeamento exacto
```text
rightware_si/**                     -> backend/rightware_si/**     [11 blobs]
requirements-work02.txt             -> backend/requirements/core.txt
requirements-work02b.txt            -> backend/requirements/api.txt
requirements-work02c.txt            -> backend/requirements/memory.txt
db/migrations/0001_work02_core.sql  -> database/migrations/0001_work02_core.sql
db/migrations/0002_work02b_api_credentials.sql
                                    -> database/migrations/0002_work02b_api_credentials.sql
db/migrations/0003_work02d_scrub_lease_replays.sql
                                    -> database/migrations/0003_work02d_scrub_lease_replays.sql
.github/workflows/work02d-real-e2e.yml
                                    -> .github/workflows/ci.yml [actualizado]
outros cinco .github/workflows/*.yml antigos
                                    -> disponíveis no histórico Git (não duplicados no CI actual)
```

## Nova árvore de topo
```text
backend/
    rightware_si/             # aplicação Python, FastAPI, auth, MCP, Mem0
    requirements/             # core.txt, api.txt, memory.txt
database/
    migrations/               # 0001-0003 (SQL original)
frontend/
    README.md                 # futuro; frontend NÃO implementada
infrastructure/
    README.md                 # critérios de deployment; nenhum Compose implementado
tests/                        # testes existentes e novos testes de layout
scripts/                      # checker de handoffs e laboratório E2E
docs/
    ARCHITECTURE.md           # fonte de verdade actual
    HANDOFF.md
    HANDOFF_MASTER.md
    HANDOFF_POLICY.md
    research/                 # SI-RD-01 preservado
    work03a/                  # este manifesto
vendor/mem0                   # mesmo submódulo fixado
.github/workflows/ci.yml      # único workflow em develop
pyproject.toml                 # setuptools package-dir=backend
README.md
```

## Gates que têm de ser PASS após o commit
- Instalar `backend/requirements/{core,api,memory}.txt`, `vendor/mem0` e `pip install -e .`.
- Provar que `rightware_si.__file__` está fisicamente em `backend/rightware_si/`.
- Migrações SQL 0001/0002/0003 na base PostgreSQL descartável `rw_test`.
- Testar auth REST, transações, grants, contexto, MCP e quatro testes novos do layout. Contagem esperada = baseline 51 + 4 = **55 testes**, condicionada ao real CI.
- E2E real externo MCP subprocess → REST → PostgreSQL16 → Mem0 OSS + PostgreSQL17/pgvector → Ollama embeddings; dados sintéticos.
- CI rejeitar commits que não actualizem os dois handoffs. Não fazer merge para main.
- Confirmar preservação da pesquisa SI-RD-01 e seis PRs históricos. Tratar SI-RD-02 como investigação não executada.

## Ainda NÃO implementado
Frontend React, Docker Compose de produção, gestão de segredos e OAuth/OIDC, limites de API, recovery de lease, backups, memory retention/deletion, outbox, staging Jarvis e benchmark comparativo de memória. Não confundir estrutura de pastas com funcionalidades entregues.

## Reversão e evidência
Caso CI falhe, aplicar correcções em `develop` com novo checkpoint no MASTER e HANDOFF; nunca falsear o resultado pendente. `main` e Jarvis são intocáveis neste trabalho. 
