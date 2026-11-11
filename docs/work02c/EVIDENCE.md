# WORK-02C — Evidence Register

**Status:** Experimental, separately verifiable. Not merged or deployed to Jarvis.

## Contract tests: PostgreSQL/REST/MCP
- Workflow: `.github/workflows/work02c-context-mem0.yml`.
- Source run: `43070689611`, SHA `b390733c855ed860178a13e1a0129039dc20f3d1`.
- **45/45 PASS**: synthetic Mem0 backend; REAL PostgreSQL 16, authenticated FastAPI, and MCP SDK in-memory; untrusted/cross-project memory negative cases.
- These contract tests are not real embedding/inference tests.

## Actual Mem0 + Ollama + pgvector
- Workflow: `.github/workflows/work02c-real-mem0-local.yml`.
- Library: original `vendor/mem0`, commit `f1791daa86d469249c9b002f62644d58a1eb96a0`, Python 3.12.
- Backend: PostgreSQL 17 with pgvector, local `ollama/ollama:0.40.15`, embedding `all-minilm:latest`.
- Initial workflow run `43071128516`: FAILED due to script packaging (`ModuleNotFoundError: rightware_si`). This failure was not a Mem0 behavior failure. Fixed by installing RIGHTWARE package in the runner.
- Corrected run `43071532909`: **SUCCESS**; logs include `ACTUAL_MEM0_LIBRARY_IMPORT_PASS`, `OLLAMA_READY`, `MEM0_SHIM_AUTH_READY`, `REAL_MEM0_SMOKE_PASS`.
- Scenario: synthetic two-project namespaces, add one memory for each via actual OSS Mem0, search Alpha using locally computed embeddings, confirm retrieved Alpha (1 result) and no Beta leakage.
- `infer=false`: Qwen text generation was NOT executed. Ollama was used for embeddings locally. Model download came from a public model registry and did not require a paid inference API.
- Ephemeral CI key, no production credentials or private memories. A later follow-up masks this generated key in Actions logs.

## Limitations
- This is a small happy-path synthetic integration smoke, not comprehensive security, retrieval precision, or load certification.
- The model tag `all-minilm:latest` is mutable; record a digest before reproducing regulated or commercial deployments.
- The smoke accesses the internal Mem0 adapter directly. Full external agent → MCP host → RIGHTWARE FastAPI → Mem0 integration is NOT YET independently tested with a vendor host.
- No Jarvis code, runtime, or environment has been modified in WORK-02C. No production rollout or merge authorized.
- Critical hardening remains: lease-token storage in idempotency responses, workload identity, rate limits, tenant isolation audit, memory retention/deletion and secure ingestion/outbox.
