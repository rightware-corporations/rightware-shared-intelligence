# RIGHTWARE Shared Intelligence — CURRENT HANDOFF

**Refreshed:** 2026-11-12 (Africa/Maputo) · **Source of historical truth:** [HANDOFF_MASTER.md](HANDOFF_MASTER.md) · **Policy:** [HANDOFF_POLICY.md](HANDOFF_POLICY.md)

## Immediate recovery
- Repository: https://github.com/rightware-corporations/rightware-shared-intelligence
- Active development branch: **develop**. Created from verified WORK-02D code+docs commit **6345fb4f6238ecea2d376e82b659238d4684f30f**; current branch head must always be fetched at the start of a new task.
- Stable release branch: **main**, SHA **87c3351055aaf58d37f233dbc96eaa8f0b749c5c** (only initial README). main is NOT a tested deployment/release of the shared intelligence service.
- All new work directly in develop; main only receives an explicitly approved release. Historical feat/docs branches and six Draft PRs are retained as forensic anchors until safely reconciled. **Do not delete them or merge automatically.**
- MASTER entry SI-MH-0001 reconstructs WORK-00 -> WORK-02D. SI-MH-0002 records the operator's two-branch + per-output handoff decisions.

## Current implemented scope
- Python package rightware_si: PostgreSQL task/handoff lifecycle, scoped project grants, append-only task events, bearer auth FastAPI, read-only MCP stdio bridge, contextual memory retrieval and isolated Mem0 local laboratory service.
- DB: core migrations 0001 (tasks/leases/grants), 0002 (API token registry), 0003 (remove sensitive lease credentials from idempotency responses).
- Memory engine: Mem0 OSS pinned submodule vendor/mem0 SHA f1791daa86d469249c9b002f62644d58a1eb96a0, Ollama local all-minilm embeddings + pgvector in test.
- NO frontend application or deployment infrastructure ready yet. NO Jarvis/PULSE production integration. NO model training, no global approved-decision engine.

## Last verified tests and status
- WORK-02D code base SHA 6345fb4f6238ecea2d376e82b659238d4684f30f: Actions https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43109095085 **SUCCESS**.
- 48/48 unit+PostgreSQL/REST/MCP tests PASS; separate real MCP subprocess -> REST auth -> PostgreSQL task/grants -> real Mem0 OSS -> Ollama local embeddings -> pgvector E2E PASS. Synthetic data only.
- Corrected fail runs: 43107788463 and 43108113909. Preserve these failures and fixes in evidence, not delete history.
- DEVELOP CI after governance commit: PENDING until verified. Do NOT claim new commit PASS just because its base was verified.

## Official operator decisions (2026-11-12)
1. Only develop (building/testing) and main (approved stable release) as ongoing working branches.
2. Every technical output/checkpoint must be durable: append MASTER, refresh CURRENT HANDOFF and commit alongside output. Research conclusions, blocked work and test failures count as outputs.
3. Preserving future work in docs is mandatory to survive loss of the chat. Use history and SHA, not chat session as the source of truth.

## Unresolved risks
- Repository is public; no private memories, keys, tokens, personal data or CI secrets may be committed.
- Lease-token idempotency secrecy improved in WORK-02D, but a lost response still requires recovery/reassignment policy.
- Workload identity/OIDC, TLS for remote clients, rate limits, resource-level grants, memory retention/deletion, event outbox and independent security review remain unimplemented.
- Embedding model tag not immutable; vendor MCP hosts and actual Jarvis staging require separate test; no production readiness claim.
- Existing six Draft PRs + historical branches need careful inventory/archival before deletion. GitHub branch protections and separate backup/restore remain unconfigured.

## Next exact work
**WORK-03A — Repository architecture consolidation:** adopt backend/, database/, infrastructure/, tests/, docs/ and vendor/ layout without rewriting tested functions; adapt packaging/CI; run full 48 tests + real E2E; append MASTER and refresh this HANDOFF in the same commit. Only then stage optional read-only Jarvis compatibility.

## Recovery protocol
1. Read develop HEAD and docs/HANDOFF_MASTER.md last entry.
2. Read docs/HANDOFF_POLICY.md and matching checkpoint.
3. Review last GitHub Actions result + diff and any open blockers.
4. Execute limited work; commit output and both handoffs atomically; review actual CI and append follow-up if outcome arrives later.

