# Infrastructure — WORK-03A architecture preparation

**No service deployed and no Compose/Kubernetes production config is claimed in this phase.** This directory is reserved for tested deployment manifests once the security/hosting decisions are approved.

## Current reproducible synthetic CI topology

- Python 3.12 application / FastAPI local loopback port 8890.
- Mem0 OSS private local lab service port 8891; bearer/X-API-key stays internal.
- PostgreSQL 16 `rw_test` on CI localhost port 5432; operational state and grants.
- PostgreSQL 17/pgvector `mem0_lab` on CI localhost port 5433; semantic index.
- Ollama 0.40.15 localhost port 11434; downloaded `all-minilm:latest` local embedding model.
- `vendor/mem0` pinned as Git submodule, `MEM0_TELEMETRY=false` in lab.
- No paid external LLM inference. No customer data in test.

## Production gate before a deployment manifest
1. Decide if services run on the same host or separately, and which database topology/migration framework is supported.
2. Implement workload identity, secrets storage/rotation, TLS termination, rate limiting and access logs without confidential data.
3. Ensure Mem0/internal PostgreSQL/Ollama are never accidentally publicly exposed.
4. Define encrypted backups, recovery drills, migrations, memory deletion/retention and environment separation.
5. Benchmark local model dimension, CPU/RAM/latency requirements and pin model digest rather than mutable tag.
6. Approve Jarvis staging integration and rollback with its own service token and opt-in feature flag.

Build/deployment planning must never be conflated with a running production service. See `docs/ARCHITECTURE.md`.
