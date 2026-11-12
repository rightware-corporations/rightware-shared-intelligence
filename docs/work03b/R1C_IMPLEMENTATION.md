# WORK-03B R1C — Checkpoint-bound Handoff & Lease Fencing

**Classification:** experimental R1C implementation in `develop`. At authoring time: **CI PENDING**; existing R1B baseline [43183197724](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43183197724) SUCCESS (81 tests and two real synthetic E2E paths). No real customer data, Jarvis/PULSE change, production deployment or change to `main`.

## Functional implementation (new code, no external dependencies)

1. **PostgreSQL migration 0006:** `si_handoffs` includes `checkpoint_id`, `checkpoint_seq`, `checkpoint_task_version`. Same-task FK and trigger prevent metadata substitution/updates; historical rows remain null. New `si_lease_fences` retains monotonic per-task generations, even after lease deletion on handoff. Seeds any active lease generation in an existing DB. `LEASE_REKEYED` is added to the continuity audit event vocabulary.
2. **Atomic offer:** `WorkCore.offer_handoff` reads latest `si_task_checkpoints` inside the task lock transaction, requires the explicit ID and matching sequence **when a checkpoint exists**, verifies `recorded_by=actor` and task version and target `task:read/context:read`, then inserts immutable binding and atomically releases old lease/transitions to BLOCKED. Missing/wrong/stale data returns 409; no task mutation.
3. **Atomic acceptance:** `accept_handoff` reauthorizes the recipient, checks bound checkpoint identity/seq/version and task blocked version, then issues new one-time lease with strictly greater persistent generation. Old A token and the idempotency-secret replay remain invalid. Old tasks **without any checkpoint** preserve explicit `LEGACY_UNBOUND` compatibility; do not claim those provide a verified continuity package.
4. **Loss/expiry recovery:** authorized current holder (same effective principal) obtains `GET /v1/projects/{project_id}/tasks/{task_id}/lease-status` with current generation but **never token/hash**. `POST .../lease-recovery` requires `task:recover` + `task:execute` + current ownership + expected task version and generation; rotates a fresh token and increments generation even after expiry. Old lease rejected, replay of issuance returns 409; audit event contains only generation numbers. **Not** a generic takeover of another agent; users without holder/grant remain blocked. This is privileged rekey, not MFA or production OIDC.
5. **Read-only resume:** response includes bound handoff ID/seq/version, whether it still matches the latest checkpoint, and `handoff_checkpoint` data even if later B creates a newer checkpoint. Everything is `ASSERTED`; old task.version may differ after accept. No secret or authority minted by `resume`.
6. **Tests / CI:** new `tests/test_work03b_r1c.py` real PostgreSQL/REST with 12 tests (strict missing/stale binding, DB immutability, ownership/grants, expired/lost credential rekey, replay/secret nonpersistence, monotonically increasing generation, concurrent rekey, historical checkpoint and compatibility). Updated existing R1B E2E for explicit bound ID and safe B rekey in a **separate subprocess**, Mem0 off. CI applies 0006 before 81 existing tests +12 R1C tests + 1 static contract inventory test; **94 expected tests**, not claimed PASS until GitHub Actions verifies it.
7. **Canonical UC-CORE-01:** `docs/work03b/UC_CORE_01_CONTRACT.json`: 18 implemented routes, 3 future R2 routes, 14 steps still **PENDING_FULL_E2E**. SI-RD-03C 16 EV oracles remain `executed=false`; no R2 work.

## Security boundaries and known limitations

- Lease fencing guarantees monotonic server-side generations, **not exactly-once external effects**. External integrations need their own idempotency/status receipts and generation awareness; none executed here.
- Holder-only recovery is enabled via `task:recover`, highly privileged in this lab. A stolen valid bearer with that grant could rotate the lease. Production requires workload identity, rate limiting, step-up policy, audit monitoring and reauthorization; no cross-user recovery/reassignment exists.
- Legacy unbound handoff path for tasks with **zero** checkpoints is explicitly supported for pre-R1B workflows; new checkpointed work fails closed unless correctly bound. Remove/phase out legacy only after deciding migration policy.
- Checkpoint text/observations remain unverified; no Git/CI independent verifier, no APPROVED decision, no DONE promotion, no privacy/subject-level ACL or consent/erasure policy.
- Trigger and FK guard the binding for ordinary writers but PostgreSQL superusers can circumvent controls. No production DB role separation, backup/replay, HSM or attestation system.
- `resume` is a current-policy read of canonic data; previously returned snapshots cannot be revoked from a client's local storage. No automatic client-side execution or remote agent-invocation engine.
- R2 research `docs/research/SI_RD_03C_EVIDENCE_RESEARCH_2026-11-12.md` and `docs/research/fixtures/SI_RD_03C_EVIDENCE_CASES_v1.jsonl` are preserved unmodified; their 16 cases are proposed synthetic oracles, **not executed**.

## E2E acceptance approach

R1B's real independent-process A/B E2E now additionally proves a checkpoint ID is bound atomically at offer/accept, that B can query current nonsecret lease generation and rekey after discarding the one-time secret response, and that identical-key replay is denied. The subprocess returns no secret in its stdout. R1C synthetic CI proof line: `WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS`.

**Next:** Verify CI for the exact implementation SHA, record actual failures/fixes and a new SI-MH checkpoint if necessary; then optional R1C security hardening/review. Do not begin R2 implementations before accepting this R1C gate and deciding the legacy-handoff/recovery policies.
