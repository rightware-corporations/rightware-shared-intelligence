# WORK-03B R0 — UC-CORE-01 Acceptance Matrix

**Status:** DRAFT / future acceptance tests, not proof of implementation.  
**Evidence hierarchy:** actual CI and test logs > code + isolated tests > docs/contract > vendor claims.  
**Source:** WORK-01 `docs/work01/MVP_ACCEPTANCE.md` (M01–M18), SI-FG-01 audit and current `backend/rightware_si/`.

## 1. Crosswalk to original WORK-01 MVP acceptance
`LAB_PARTIAL` means a narrow test path already exists but does not establish the complete original M contract; `SPEC_CONFLICT` means the original generic idempotency wording changed intentionally for secret issuance; `MISSING` means proposed product capability not present; `UNPROVEN` means currently not demonstrated. `PENDING_FULL_E2E` on every row prevents false claims.

| ID | Required result | Existing coverage | Target | Full result |
|---|---|---|---|---|
| M01 | Task created/published/claimed | LAB_PARTIAL | R1 | PENDING_FULL_E2E |
| M02 | Observation appended as ASSERTED, with source | R1A_LAB_PARTIAL | R1 | PENDING_FULL_E2E |
| M03 | Handoff offer blocks and releases old lease | R1C_BOUND_HANDOFF_LAB_PARTIAL | R1 | PENDING_FULL_E2E |
| M04 | Atomic acceptance to B / old lease invalid | R1C_BOUND_ACCEPT_FENCED_LAB_PARTIAL | R1 | PENDING_FULL_E2E |
| M05 | Scoped context includes versioned and authorized refs | R1B_LAB_PARTIAL | R1 | PENDING_FULL_E2E |
| M06 | Submission enters IN_REVIEW, never DONE | LAB_PARTIAL | R1 | PENDING_FULL_E2E |
| M07 | Independent verification and authorized DONE acceptance | MISSING | R2 | PENDING_FULL_E2E |
| M08 | Optimistic task version conflict | LAB_PARTIAL | R1 | PENDING_FULL_E2E |
| M09 | Idempotency under lost secret response | SPEC_CONFLICT | R1 | PENDING_FULL_E2E |
| M10 | Cross-project denial for all reads/mutations/MCP | LAB_PARTIAL | R1_R2 | PENDING_FULL_E2E |
| M11 | Concurrent accepted handoff / one lease | R1C_MONOTONIC_LEASE_LAB_PARTIAL | R1 | PENDING_FULL_E2E |
| M12 | Memory offline degrades without losing task state | R1B_CANONICAL_FALLBACK_PARTIAL | R1 | PENDING_FULL_E2E |
| M13 | Revoked source or grant blocks snapshot replay | MISSING | R2 | PENDING_FULL_E2E |
| M14 | Prompt injection in memory cannot authorize action | UNPROVEN | R2 | PENDING_FULL_E2E |
| M15 | Misleading evidence fails specific verification | MISSING | R2 | PENDING_FULL_E2E |
| M16 | New process restart reconstructs progress and outbox | R1B_RESTART_PARTIAL_NO_OUTBOX | R1_R2 | PENDING_FULL_E2E |
| M17 | REST/MCP parity without policy bypass | R1B_MCP_READ_PARITY_PARTIAL | R1_R2 | PENDING_FULL_E2E |
| M18 | All mutations have actor/version/correlation/audit | LAB_PARTIAL | R1_R2 | PENDING_FULL_E2E |

## 2. Executable R1 target / deterministic tests
- Task/version: create v1, publish v2, claim v3, observe/checkpoint without fabricated APPROVED, offer v4, accept v5, submit v6. Assert no multiple leases, old lease invalid and event journal monotonic.
- Process boundary: start A and B as **separate process principals**; kill A; B recovers via fresh authenticated `GET resume`, no access to A's chat transcript; compare expected snapshot references + state version.
- Scope: Alpha/Beta organizations/projects; revoked grants and memory-scoped metadatas cannot grant access to unrelated task, snapshot, source or semantic record.
- Failure: Mem0 down = task/events remain readable with explicit degraded memory_status; lost response to claim/accept = 409 on secret replay and recovery BLOCKED until approved alternate procedure.
- R1 evidence: submit only `REFERENCED` and `IN_REVIEW`; reviewer and verifier endpoints remain NOT IMPLEMENTED.

## 3. Executable R2 target / trust and lifecycle
- Git/CI verifier must fetch external state independently, bind it to evidence URI and criterion; verifier reports PASS only for exact check. Fake success and wrong SHA remain FAIL/INCONCLUSIVE; no model self-verification.
- Distinct REVIEWER with `task:review` can accept only after declared criterion policy met; executor and reviewer effective identity cannot coincide by default.
- Deletion/revocation is observable after projection reconciliation; old snapshots cannot leak revoked refs, including on MCP.
- Memory injection cannot issue commands; authoritative Postgres tasks cannot change due to untrusted memory text.
- Crash after initiating a side-effect requires durable intent/receipt & reconciliation; prove zero duplicate effects with controlled synthetic external service; do not generalize to arbitrary providers.

## 4. Three class labels for results
- `CONTRACT_PASS`: static schema/doc tests (NOT runtime).
- `INTEGRATION_PASS`: real PostgreSQL/REST/MCP and independent synthetic processes.
- `PRODUCT_ACCEPTANCE_PASS`: M01–M18 full tested plus independent evidence and reviewer decision after an operator accepts policy. Absent until R1/R2 complete.

## 5. Explicit change from WORK-01
For M09, **secret issuance claim/accept replay** cannot return the same lease token from idempotency storage. The current security design returns 409 rather than reproducing credentials. Other safe writes may replay according to their defined contract. This security exception must be reflected in revised M09 tests and approved policy, never bypassed for a green test.

## 6. Required evidence artifacts for the future E2E
Git SHA; database migration version; test command/environment; independent client process logs sanitized; scoped tokens NEVER logged; current and previous task states; event versions; handoff status, lease generation but no token; source IDs; verifier details; reviewer verdict; negative-case counts and projection watermark. Handoffs and evidence status committed in the same engineering checkpoint with exact run links. This document alone has no actual run results.

## WORK-03B R1A laboratory progress (not full acceptance)
- Implemented four experimental authenticated REST operations for AgentRun start, SourceRecord registration, source-linked Observation write and authorized task Observation reads. They do not expose generic memory writing or verification.
- PostgreSQL 0004 keeps observations in an independent append-only continuity event stream and keeps task.version unchanged. Mutations require task lease, effective principal and project grants. Source URI is a pointer and is never fetched by this service.
- Original M02 is **R1A_LAB_PARTIAL**; M01–M18 remain **PENDING_FULL_E2E**. Nothing yet proves ContextSnapshot, checkpoint, resume, outbox, verifier, review, Jarvis staging or production.
- SourceRecord GIT_REF currently accepts HTTPS github.com URL; TOOL_RECEIPT accepts a safe local urn:rw: reference only. Privacy/retention, real source verification and resource-level ACL still require design.

## WORK-03B R1B laboratory progress (NOT full UC-CORE-01)
- Implemented lease-bound immutable TaskCheckpoint with `expected_checkpoint_seq` CAS and source-linked Observation refs, plus current-grant and project-scoped read-only Resume. Checkpoint seq is separate from task.version.
- MCP read-only `resume_task` delegates to the same authenticated REST route, no write tools. A new independent process B accepts the handoff and reconstructs A's checkpoint without A's chat or credentials; Mem0 service is deliberately unavailable in this test.
- **Limit:** existing handoff does NOT bind a specific checkpoint (R1C), not all source-level revocations/consent/outbox or verification/review implemented. The entire M01-M18 remains PENDING_FULL_E2E.

## WORK-03B R1C — Bounded laboratory progress, not complete acceptance
- Handoff of a task **with an existing checkpoint** requires exact immutable latest checkpoint ID/sequence, same current writer and task version, checked before deleting A's lease. B is reauthorized for task:read/context:read on offer and accept. New bounded handoffs carry a DB-enforced checkpoint foreign key with frozen checkpoint seq/version.
- No-checkpoint historical flows remain `LEGACY_UNBOUND` for backward compatibility; never claim them as a complete continuity transfer. Any later product release should deliberately phase out this legacy mode.
- Task leases now have persistent per-task monotonic `si_lease_fences` generations across handoffs and rekeys. Holder-only `GET lease-status` and `POST lease-recovery` require explicit `task:recover` plus execution/ownership and expected generation; one-time secrets cannot be replayed. No automatic takeover by another agent/administrator is implemented.
- Test real PostgreSQL/REST interleaving and independent subprocess A→B: exact binding, stale rejection, CAS, lost-reply rekey, monotonic fencing, revocation and Mem0-offline read-only resume. Full M01–M18 acceptance remains `PENDING_FULL_E2E`; no source-level consent, R2 independent verification or DONE.


## R2 R0 preparation checkpoint — DOCUMENT/CONTRACT GATE ONLY

- [R1C security decisions](R1C_SECURITY_POLICY_GATE_R0.md): four explicit recommendations and their outstanding operator ratification gates. Current `LEGACY_UNBOUND`, holder-only rekey and absence of external-effect protection remain **as implemented** in the lab.
- [R2 written trust contract](R2_TRUST_CONTRACT_R0.md) and [machine-readable oracles](R2_TRUST_CONTRACT_R0.json): three separate states ASSERTED, CHECKED_*, REVIEW_*; exact future GitHub evidence provider binding and scoped reviewer; no automatic DONE. The original `UC_CORE_01_CONTRACT.json` is unchanged and still has 18 experimental REST routes, three future R2 routes and M01–M18 `PENDING_FULL_E2E`.
- `tests/test_r2_r0_contract.py` checks only that 16 SI-RD-03C fixture oracles remain `executed=false` and match the R2 draft and that its routes aren't live. **A static lint PASS must not be reported as EV-01..EV-16 execution.** 
- Do not initiate evidence verifier, crypto installation, review endpoint or policy-based deployment before operator ratification.


## WORK-03B R2 R1A — Limited experimental code (CI pending until observed)
- Implemented a **standalone** GitHub Workflow Run checker; there is no public verification REST/MCP operation, no SQL verification-attempt record, no registered independent principal, no reviewer or DONE transition.
- Fifteen new synthetic adapter tests execute the actual decision logic and include the proposed EV-01..EV-07 outcomes using mocked provider responses; the original SI-RD-03C JSONL keeps `executed=false` as historical/specification metadata. The separate live fixed-GitHub-run script is an independent actual-provider check for EV-01..EV-04 when successful, not evidence that all original oracles or customer acceptance criteria passed.
- `M07`, `M13`, `M14`, `M15` and every M01–M18 final acceptance remain **PENDING_FULL_E2E**. SEC-R1C-01..04 still require explicit operator ratification before operationalizing policy, persistence and reviewer.

## R2 R1A CI verified (narrow evidence, not UC-CORE-01 completion)

[Actions 43214573166](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43214573166) SUCCESS: 115/115 unit/real PG tests, **LIVE GitHub provider** EV-01..EV-04 (exact matching run and deliberate policy mismatch cases), MOCK/controlled EV-05..EV-07 unit cases. The source research fixture EV-01..EV-16 still has `executed=false` because it documents proposed oracles; new execution results are separately recorded in [R2_R1A_EVIDENCE.md](R2_R1A_EVIDENCE.md). EV-08..EV-16 unexecuted. No new R2 REST route or real reviewer and all M01–M18 remain `PENDING_FULL_E2E`.


## WORK-03B R2 R1B — Isolated ledger implementation, NOT M01–M18 approval

- PostgreSQL migration 0007 adds immutable operator-seeded policies, append-only VerificationAttempt and EVIDENCE_CHECKED continuity event. Scope and future criteria attached to the same project/task/evidence; results are independent of existing si_evidence_refs and ASSERTED observations.
- Internal SERVICE verifier with evidence:verify + task:read, distinct from creator/submitter/policy author; external GitHub run fetched outside DB, authorization rechecked transactionally before insert. Read access requires evidence:read + task:read, both current grants.
- 16 real PostgreSQL unit/integration tests were added to verify mock PASS/FAIL/INCONCLUSIVE, authorization, revocation during slow check, no DONE, immutability, idempotent replay, cross-project isolation, criteria binding, source URI policy, and concurrent new attempts. Separate live lab script verifies actual GitHub provider run and stores a scoped result in disposable PostgreSQL.
- **Expected count: 131 tests (115 prior + 16 new)** at time of implementation; do NOT mark PASS until actual CI. The original EV-01..EV-16 research fixture remains unchanged (proposal oracles, not execution journal); R2 R1B tests do not execute all EV scenarios. No public REST verify route or review/DONE exists.
- SEC-R1C-01..04 and official R2 provider/criteria/consent policies remain pending. M01–M18 FINAL status PENDING_FULL_E2E remains unchanged. See [R2_R1B_VERIFICATION_LEDGER.md](R2_R1B_VERIFICATION_LEDGER.md).


## WORK-03B R2 R1B CI verified — scoped ledger only

[GitHub Actions 43237504677](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43237504677) SUCCESS with 131/131 tests, real GitHub API → SERVICE authorized → PostgreSQL immutable attempt, source read revocation, idempotency, and regression R1C/Mem0. **No reviewer or DONE**. Original si_evidence_refs stays REFERENCED and si_observations ASSERTED; new checks do not alter task IN_REVIEW. Only the narrow ledger capability was proven; M01–M18 final acceptance remain PENDING_FULL_E2E and SEC-R1C-01..04 are not ratified. [Evidence detail](R2_R1B_EVIDENCE.md).
