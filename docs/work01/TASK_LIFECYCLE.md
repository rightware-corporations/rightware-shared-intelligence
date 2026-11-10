# Task, Handoff and Decision Lifecycle — v0.1

**Status: PROPOSED STATE MACHINES.** They are not yet backed by database constraints or runtime code.

## 1. Task lifecycle

```text
DRAFT --publish--> READY --claim(lease)--> IN_PROGRESS
                                  |              |
                                  |              +--block--> BLOCKED
                                  |              |             |
                                  |              |       --resume--> IN_PROGRESS
                                  |              +--submit--> IN_REVIEW
                                  |                              |
                                  |                        request_changes
                                  |                              v
                                  |                        IN_PROGRESS
                                  |                              |
                                  |                         accept_result
                                  |                              v
                                  +----------------------------> DONE
Any nonterminal state --cancel(by authorized actor)--> CANCELLED
```

Clarifications:
- The diagram's `DONE` path is **only** from `IN_REVIEW` after accepted verification/review; it must never be entered directly from READY.
- `DRAFT`: objective/criteria may still change. `READY`: sufficiently specified, not claimed.
- `IN_PROGRESS`: a currently valid worker lease is required for state-changing execution.
- `BLOCKED`: work suspended with reason; lease may be released. Resumption obtains a new valid lease.
- `IN_REVIEW`: worker submitted result; status is **not DONE**, even when its own narrative says "finished".
- `DONE`: an authorized acceptance operation records acceptance of explicit criteria. A passed verifier may be one acceptance condition, not a universal approval.
- `CANCELLED`: terminal. A new task is needed to restart in MVP.

### Transition table

| From | Command | To | Who may issue | Preconditions |
|---|---|---|---|---|
| DRAFT | publish_task | READY | project manager / authorized human | Objective, criteria, grants valid |
| READY | claim_task | IN_PROGRESS | authorized agent/human worker | Single lease acquired atomically |
| IN_PROGRESS | block_task | BLOCKED | lease holder or manager | Reason and audit event |
| BLOCKED | resume_task | IN_PROGRESS | authorized worker | New lease, version check |
| IN_PROGRESS | submit_result | IN_REVIEW | valid lease holder | Summary, result refs, expected_version; no self-verification claim |
| IN_REVIEW | request_changes | IN_PROGRESS | authorized reviewer | Verdict and new/renewed worker lease |
| IN_REVIEW | accept_result | DONE | authorized reviewer / configured independent policy | Explicit acceptance record, evaluation of criteria, valid evidence policy |
| Any except DONE/CANCELLED | cancel_task | CANCELLED | project manager | Audited reason |
| DONE | no state transition | DONE | — | Corrections via follow-up task / decision event |

Every transition is an ACID transaction: validate grants and expected version, check lease, update Task, append Event and optional OutboxEvent. Expected version mismatch → 409.

## 2. Exclusive lease and retry semantics
- Claim has `holder_principal_id`, `expires_at`, `lease_token` (opaque, never logged) and fencing generation.
- Lease ownership is checked at mutation time. Expired leases do not authorize writes.
- Renewal and timeout use database/server timestamps; avoid relying on agents' local clocks.
- Idempotent retry must not grant a second claim; compare `Idempotency-Key` and payload hash.
- Client cancellation does not imply immediate remote effect; callers should query authoritative state.

## 3. Handoff lifecycle (separate from task status)

```text
OFFERED --accept_handoff--> ACCEPTED
        --decline_handoff--> DECLINED
        --revoke_handoff--> REVOKED
        --deadline_passes--> EXPIRED
```

- OFFERED means the current worker offers contextual continuation to a named target; it is *not* proof of completion.
- ACCEPTED means the target explicitly accepted the handoff **and** acquired the required lease/fencing generation atomically, or the acceptance is refused.
- In WORK-01 MVP, a handoff is allowed only for a Task in IN_PROGRESS or BLOCKED. Offering can move a running Task to BLOCKED with reason `HANDOFF_PENDING`, releasing its lease transactionally. The pending handoff has no effect on its own.
- Accepting can resume the Task as IN_PROGRESS with the target's lease. Declined, revoked or expired handoffs leave the Task BLOCKED; an authorized manager can reassign.
- Never allow two active exclusive leases from concurrently accepted handoffs. Server enforces at most one accepted transfer per task version.
- ContextSnapshot contains references, versions and ACL decisions at creation; access is rechecked at retrieval. Revocation wins over a previously valid snapshot.
- All handoff notes are ASSERTED until an independent check says otherwise.

## 4. Evidence and result review
A task and evidence have separate state. Evidence is accepted only as proof of **the check recorded**.

```text
Evidence reference: RECEIVED -> CHECKING -> PASS | FAIL | INCONCLUSIVE
```

- Git commit exists → supports commit existence, not quality.
- CI completed successfully → supports that specified job/run succeeded, not that all requirements were met.
- Reviewer acceptance → records an authorized human/business decision separately.
- Any result verification is append-only; if later superseded, add a new assessment rather than rewriting the old one.
- A model must not be the sole verifier of a claim that it generated for MVP acceptance.

## 5. Decision lifecycle
`PROPOSED -> APPROVED | REJECTED`; `APPROVED -> SUPERSEDED` only by a new approved decision referencing the previous one.

No `save_memory`, `write_observation` or `create_handoff` can directly approve a decision. Decisions and task acceptance follow grants distinct from memory write.

## 6. Example transaction sequence (synthetic)
1. Manager creates `TASK-T01`, version 1 DRAFT; publishes → READY v2.
2. Agent A claims lease → IN_PROGRESS v3.
3. Agent A records an Assertion "feature implemented" and Evidence URL to GitHub; both unverified.
4. Agent A offers Handoff to Agent B and blocks TASK-T01 → BLOCKED v4, releasing its lease.
5. Agent B accepts with expected v4 → IN_PROGRESS v5; original Agent A lease remains invalid.
6. Agent B submits → IN_REVIEW v6.
7. Independent verifier checks cited evidence and records PASS/FAIL with scope.
8. Authorized reviewer accepts according to criteria → DONE v7 (or requests changes → IN_PROGRESS).
9. Another actor tries to write using v4 → 409 CONFLICT, with no mutation.

This sequence is a model to test, **not a historical record from Jarvis or GitHub**.
