# Upstream provenance — Mem0

- Canonical source: https://github.com/mem0ai/mem0
- Git submodule path: vendor/mem0
- Pinned upstream commit: f1791daa86d469249c9b002f62644d58a1eb96a0
- Source license: Apache License 2.0; retained inside vendor/mem0/LICENSE.
- Captured baseline: 2026-11-10.
- Local vendor modifications: NONE. Do not patch vendor/mem0 silently.
- Official self-hosted server: vendor/mem0/server/ (FastAPI, API-key auth, PostgreSQL/pgvector, local dashboard).
- Default provider profile inspected in upstream server/main.py: OpenAI LLM and embedding. No default claim of offline/no paid API.
- Older mem0ai/mem0-mcp repository is archived and cloud-oriented. Do not add it as the compulsory MCP connector.

The gitlink preserves the exact upstream commit without copying or misrepresenting authorship. Retrieve code/history with:

    git clone --recurse-submodules https://github.com/rightware-corporations/rightware-shared-intelligence.git

Or, inside an existing checkout:

    git submodule update --init --recursive

Updates require an explicit new upstream SHA, license/security review, change log, and tests. No automatic pin drift.

RIGHTWARE-authored integration files remain separate from the upstream repository. Review dependency licenses and trademark rules before distributing a commercial package.
