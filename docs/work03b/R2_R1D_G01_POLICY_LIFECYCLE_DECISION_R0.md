# WORK-03B R2 R1D-G01 — VerificationPolicy Lifecycle Decision Packet R0

**2026-11-12 Africa/Maputo · DRAFT RECOMMENDATION / RATIFICATION REQUIRED · NO CODE, MIGRATION OR PROD.**
Baseline `develop@b101aa8f64970524aab496e62e3032862fcf4b6c`. The 0007 PostgreSQL migration makes `si_evidence_verification_policies` and `si_verification_attempts` immutable. Existing R1B/R1C/R1D verification requires SERVICE + project grants, exact GitHub run binding, task IN_REVIEW, and an independent check; **it has no policy expiry/disable/supersession lifecycle yet.**

## 1. Evidence of the previous checkpoint

- [SI-MH-0038 Actions 43257931058](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43257931058): **SUCCESS, 174/174 tests**, LIVE GitHub via the new REST TestClient to PostgreSQL append-only.
- [SI-MH-0039 documentation CI 43258863694](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43258863694): **SUCCESS** at `b101aa8f64970524aab496e62e3032862fcf4b6c`, `Ran 174 tests in 26.358s / OK`, seven migrations, `HANDOFF_POLICY_PASS`, `WORK03B_R2_R1D_LAB_HTTP_GITHUB_LIVE_PASS` and all R1A/R1B/R1C/Mem0/Ollama regressions PASS.
- LIVE proves pinned GitHub run fields and scoped lab record only; not source privacy, business truth or task DONE.

## 2. Model proposed — preserve immutable policy rows

| Record | Fields / role | Rule |
|---|---|---|
| Existing `si_evidence_verification_policies` | project/task/evidence/policy/version/criterion and GitHub repo/workflow/run/SHA/attempt/event | Immutable forever; never UPDATE/DELETE to disable |
| `PolicyActivation` (future) | policy scope, approval reference, proposer, independent approver, `valid_from`, `valid_until`, generation, idempotency | Policy defaults INACTIVE; only explicit authorized activation |
| `PolicyLifecycleEvent` (future) | policy scope, DISABLED or SUPERSEDED, reason, actor, event time, successor ID, generation, idempotency | Append-only; terminal for old policy ID |
| `EffectivePolicyView` | derived ACTIVE/EXPIRED/DISABLED/SUPERSEDED from DB clock and events | Never trust client timestamps, Mem0 or LLM claims |

Suggested states: `CREATED → ACTIVE → {DISABLED | SUPERSEDED | EXPIRED}`. EXPIRED should derive from PostgreSQL time when `valid_until` is reached, not rely on a cleanup job. Re-enabling the same terminal policy ID is disallowed; a replacement has new ID and version with new approval.

## 3. Concurrency and authority contract

1. The verifier must check ACTIVE policy and source ACL/grants **before** contacting GitHub. Do not contact arbitrary user URLs.
2. On return, lock the **same task row** used by lifecycle mutations, and recheck project grants, task version/status, evidence binding, active generation, expiry and disable/supersede status before append-only attempt insertion.
3. A DISABLED/SUPERSEDED/EXPIRED policy discovered after the external call aborts the insert: **409 with no CHECKED_PASS record**.
4. Even replay of an old successful idempotency key must fail closed if policy was disabled in the meantime. The historical attempt remains intact and audit-visible subject to current read permission.
5. Lifecycle administration must acquire the same transactional task lock before inserting events; never rely on a cached projection. Test concurrent DISABLE-vs-VERIFY in separate processes.
6. Production with no activation event must fail closed. Existing synthetic R1B/G03 fixtures need an **explicit lab-only compatibility migration**, not automatic production grandfathering.
7. SERVICE verifiers may not approve/revoke their own policy; reviewer/DONE remains a separate future workflow.

## 4. Options requiring operator ratification

| Question | Option A | Option B | Recommendation |
|---|---|---|---|
| Activation | One trusted operator for isolated CI | Independent HUMAN policy creator + approver for real clients | A only in disposable lab; B for tenants |
| Revocation | Mutate policy boolean | Append-only event + expected generation | **B** |
| Missing activation | Accept historical policy implicitly | Deny, except named lab-only test records | **B** |
| Version replacement | Overwrite GitHub pin | New immutable version and supersede old | **B** |
| First provider | Client-supplied repositories | Operator allowlist of RIGHTWARE GitHub repo/workflow | **B** initially |
| Retention/consent | Invent default periods | Decide per source class and tenant before client data | **B** |

No named human authority, expiry interval, retention number, quorum size, tenant IDs, private repo scope, or exception was approved by this document.

## 5. Future G01 acceptance matrix — all NOT EXECUTED

| IDs | Required cases |
|---|---|
| G01-01..03 | Unapproved denied; independently approved in window; expired denied before/after GitHub |
| G01-04..06 | Disabled denies including idempotent replay; disable midflight blocks insert; successor needs new approval |
| G01-07..08 | Verifier cannot self-approve/revoke; cross-project/organization control denied |
| G01-09..10 | Concurrent disable vs verification serializes on same row; lifecycle records immutable |
| G01-11..12 | Stale generation and action replay fail closed; restore preserves revocation |
| G01-13..14 | No implicit active legacy in release; zero REVIEW_ACCEPTED/DONE from policy events |

## 6. Decision gate

**RATIFICATION STILL REQUIRED**: approval authority/quorum; first internal RIGHTWARE-only scope; expiry/renewal; lifecycle event ownership; exact legacy exceptions; source consent/access/retention; emergency disable authority. Only after approval may new migration, ledger checks, bounded policy lifecycle service and PostgreSQL tests be implemented.

**No current production/OIDC or G04/G05 release, no main/JARVIS/PULSE/vendor Mem0 change.** The default R2 R1C lab route remains disabled.
