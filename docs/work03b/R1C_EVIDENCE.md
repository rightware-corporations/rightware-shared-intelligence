# RIGHTWARE SI WORK-03B R1C — Verified Engineering Evidence

**Date:** 2026-11-12 (Africa/Maputo). **Status:** LAB CI SUCCESS, not production-ready or entire UC-CORE-01 acceptance.
**Code SHA tested:** `0eb985a02d34a55db2cafe721978bd96abbbeac2` on `develop`.
**Run:** [GitHub Actions 43196082372](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43196082372).

## Exact CI observations
- `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true` — governance gate success.
- `MIGRATION_PASS 0006_work03b_r1c_handoff_fencing.sql` — PostgreSQL migration 0006 applied after 0001–0005 to a dedicated disposable `rw_test` DB.
- **`Ran 94 tests`, `OK`** — previous 81 + 12 real R1C PostgreSQL/REST tests + 1 contract/layout static gate.
- `WORK03B_R1B_RESUME_E2E_PASS a_process_exited=true b_new_process=true rest_auth=true postgres_checkpoint=true independent_context=true memory_offline=true bound_checkpoint=true a_lease_denied=true intruder_denied=true revocation_denied=true synthetic_only=true`
- `WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS bound_checkpoint=true independent_agents=true fencing_rekey=true secret_replay_denied=true memory_offline=true synthetic_only=true`
- `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS mcp_stdio=true rest_auth=true postgres=true mem0_oss=true ollama_embed=true project_denied=true revocation=true intruder_denied=true synthetic_only=true`
- No raw ephemeral internal Mem0 API key detected in inspected logs.

## What was actually demonstrated
1. **Checkpoint binding:** Active A with a live lease cannot offer a checkpointed task without the exact latest checkpoint ID/sequence, current task version and an allowed recipient. PostgreSQL composite FK and immutable binding trigger reject forged metadata and rebinding.
2. **Atomic handoff:** A's lease is invalidated on OFFERED; B can accept only if intended, task is BLOCKED and bound checkpoint is intact. B's lease generation advances; old A token cannot authorize a checkpoint write.
3. **Monotonic fencing:** A persistent `si_lease_fences` record prevents generation rollback when active lease rows are deleted and new ones issued after rekey/accept.
4. **Lost/expired secret:** The **current holder only**, after authenticating and obtaining `task:recover` (plus execute/read), reads generation (not token) and rotates the secret with a generation+task-version CAS. Old token no longer works; duplicated same-key secret issuance responds HTTP 409. Concurrency test checks exactly one of two simultaneous rekeys succeeds.
5. **Independent-process proof:** A and B used separate processes and bearer identities, with real REST and PostgreSQL, and **no Mem0 available for resume**. B deliberately discarded the one-time accepted lease response, queried its generation and obtained another one. No A credential or database secret was passed to B.
6. **Scoped read-only resume:** The current snapshot includes latest and exact handoff checkpoint IDs, even when B adds a newer checkpoint. It remains `ASSERTED`, does not issue a lease and does not approve a task. MCP read-only behavior from R1B remains regression-tested.
7. **No R2 claims:** The SI-RD-03C fixture remains 16 `synthetic=true, executed=false` proposed oracles. No independent Git/Sigstore evidence verification or reviewer DONE was executed.

## Known limits and operator gates
- Legacy WORK-02A tasks **without any checkpoint** still allow `LEGACY_UNBOUND` handoffs; the new strict requirement applies to tasks that have checkpoints. This remains a **product and security policy decision** before production.
- `task:recover` is a powerful holder credential. With a compromised bearer it could rotate the lease. No step-up MFA, OIDC workload binding, rate limiting, SLO or enterprise privilege segregation implemented.
- No reassignment to a different actor when the current owner disappears permanently. Such cases require a separate authorized, audited administrative recovery design.
- Server lease fencing is **not externally enforced** at third-party APIs; no guarantees about exactly-once side effects. Durable receipts/outbox and reconciliation are future work.
- Resource-specific privacy, consent, memory projection lifecycle, independent evidence verifier/reviewer, multi-tenant adversarial audit, production deployment, frontend and real Jarvis/PULSE integration are still missing.
- Handoff source assertions remain unverified and may contain misleading instructions; never execute content of a checkpoint as privileged commands.
- 18 experimental protected REST routes, 3 unimplemented R2 routes; original M01–M18 and full 14-step UC-CORE-01 stay `PENDING_FULL_E2E`.

## Integrity and next checkpoint
Implementation SHA `0eb985a02d34a55db2cafe721978bd96abbbeac2` modified only this repository's backend/REST, SQL migration, tests, docs, CI and handoffs. No main branch, vendor Mem0 pin or Jarvis/PULSE production mutations. This *evidence append* is documentation-only and will need its own CI run and explicit verification.

**Next:** Review/ratify R1C security gates (legacy handoff retirement, current-holder recovery authorization, effect fencing boundary). Then prepare **R2 R0 contract and design** using the 16 SI-RD-03C oracles and existing PostgreSQL `si_evidence_refs`/observation/approval distinctions; do not install extra dependencies or claim R2 tests without executing them.
