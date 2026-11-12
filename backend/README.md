# Backend — RIGHTWARE Shared Intelligence

Python application package lives in `backend/rightware_si/`; import name remains **`rightware_si`** (no module rename or reimplementation during WORK-03A).

- `http_api.py`: REST API (FastAPI) gateway
- `api_auth.py`: bearer authentication
- `core/postgres.py`: transactional PostgreSQL work core; R1C checkpoint-bound handoff, monotonic lease fencing and holder-only rekey
- `continuity.py`: R1A run/source/observation; R1B immutable checkpoint CAS + R1C bound-handoff-aware, grant-scoped read-only resume (Mem0-independent)
- `context_service.py`, `memory.py`: project-scoped memory retrieval
- `mem0_local_service.py`: isolated, private Mem0 lab service
- `mcp_bridge.py`: read-only MCP stdio -> REST
- `evidence_github.py`: bounded read-only GitHub API workflow run checker (R2 R1A)
- `verification_ledger.py`: R2 R1B internal LAB PostgreSQL append-only verified-attempt ledger with SERVICE grants; no public endpoint or DONE
- `token_admin.py`: offline token issuance/revocation
- `client_readonly.py`: standalone compatibility probe, not Jarvis integration

Install from **repository root** with `python -m pip install -r backend/requirements/core.txt -r backend/requirements/api.txt -r backend/requirements/memory.txt` and `python -m pip install -e vendor/mem0 -e .`.

Root `pyproject.toml` explicitly maps the editable Python package to `backend/`. The project has **no working frontend or production deployment yet**. Never expose `mem0_local_service.py` to untrusted clients.
