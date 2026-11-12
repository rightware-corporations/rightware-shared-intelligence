# RIGHTWARE Shared Intelligence — R1C Security & Compatibility Gate R0

**Reference implementation:** `develop@30986f53ab2b0459f4ea9eb8a5f7874d5dbcbfc4`, [Actions 43196692278](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43196692278) SUCCESS, 94 tests + A/B and Mem0 regressions.
**Date:** 2026-11-12 (Africa/Maputo).
**Status:** **RECOMMENDATIONS / OPERATOR RATIFICATION PENDING**. This review has NOT changed deployed behavior, authorized new privileges, or approved external effects.

## Decision register

| ID | What is implemented | Recommended RELEASE policy (NOT approved) | Alternatives / risk | Gate to authorize change |
|---|---|---|---|---|
| SEC-R1C-01 legacy unbound | A task with zero checkpoints can still offer a `LEGACY_UNBOUND` handoff. Tasks with checkpoints demand exact latest owned checkpoint. | **Fail closed for all newly created tasks when release mode is enabled; grandfather only specifically enumerated legacy task IDs until remediation.** Do not derive grandfathering merely from absence of checkpoints. | Immediate unconditional removal would break WORK-02A compatibility, old tests and existing clients. Unrestricted legacy mode permits continuity with no durable context. | Define explicit legacy allowlist, migration owners, expiry/deprecation window, test deny-by-default and rollback. |
| SEC-R1C-02 lost holder / takeover | The SAME current principal with `task:recover` may rekey a lost or expired lease using generation CAS; old token invalid. No cross-principal takeover exists. | **Do not enable cross-principal takeover by default.** Design an authorized, auditable reassignment requiring separate recovery authority, second-party approval or institution policy, revoking previous lease by generation fence, and notifying stakeholders; no raw token reuse. | Automatic reassignment after a timer can produce concurrent real-world effects, exfiltrate context, or let compromised admin take ownership. Leaving task BLOCKED is safer until policy ratified. | Specify identity/OIDC, 2-person rule/exception workflow, consent, emergency policy, race/revocation tests, threat review and operational recovery drill. |
| SEC-R1C-03 effects after lost response | PostgreSQL lease generations are monotonic; no external-effect protocol or outbox exists. | **Never auto-repeat an ambiguous external effect.** Require durable intent keyed by `task_id + effect_id + fencing_generation`, approved provider idempotency key, external receipt/status query, and `RECONCILE_REQUIRED` on unknown outcome. | Purely server-side fencing does not protect e.g. payment, email, inventory, device command or external API from duplicate execution. Exactly-once cannot be claimed without controlled provider semantics. | Map each connector's supported idempotency/status query; simulate timeout-after-commit, replay, concurrency, permission revocation; specify compensation/manual review. |
| SEC-R1C-04 privilege hardening | Bearer credentials + project grants in experimental lab; no OIDC, step-up, tenant isolation audit or rate-limits. | Restrict `task:recover` to dedicated workload principals, apply session binding and rate limiting with anomaly audit, no user-supplied actor IDs. | Compromised authorized bearer can rotate holder lease. | Security architecture review, OIDC/workload identity, scoped keys, logging safeguards, database least privilege, rotate/disable drills. |

## What remains OFFICIAL vs RECOMMENDED

**Verified implemented:** exact checkpoint binding for checkpointed work, read-only resume, monotonic DB generations, one-time same-holder rekey with strict grants and idempotency conflict, plus R1C tests.

**Not a company decision:** excluding `LEGACY_UNBOUND` in releases, a new admin recovery role, two-person admin quorum, specific timeouts, an outbox schema, a provider integration, or any protocol that claims exactly-once external effects. No production rollout has been authorized.

## R1C closure sequence, proposed

1. **SEC-G01 — Legacy compatibility:** inventory legacy tasks and client calls, define which projects can remain in grandfather mode, establish `STRICT_BOUND_ONLY` release default in a later separately authorized code change, add migration and metrics.
2. **SEC-G02 — Recovery authority:** document holder same-principal rekey vs administrative reassignment as different operations; no shared token, no implicit fallback to a different principal. Grant checks must be reevaluated after state-lock acquisition.
3. **SEC-G03 — Effect safety:** write `EffectIntent -> Dispatched -> ReceiptConfirmed | ReconcileRequired` contract and provider-support matrix; do not execute real external effects during CI. This is a prerequisite for reliable agent action, not evidence verification itself.
4. **SEC-G04 — Deployment review:** secrets/credential identity, DB tenant isolation, PII policy, append-only audit privilege, operational backup/restore and failure handling. R1C's 94 tests do not certify these.
5. **SEC-G05 — R2 dependency:** R2 specification can proceed on paper while G01–G04 remain pending; **R2 implementation of task DONE, trusted results and external effects must not bypass them**.

## Negative acceptance criteria for future gates (not executed in this checkpoint)

- New task with zero checkpoint is refused for handoff in strict release mode; specifically grandfathered tasks are visible with `LEGACY_UNBOUND` and warning. Historical API compatibility is tested explicitly, not erased.
- Actor B cannot recover A's lease even after expiry unless separate approved reassignment protocol exists. Owner revocation, approval timeout and concurrent admin attempts fail closed.
- An external effect with lost response is queried/reconciled before any retry, with provider idempotency and receipt matched to exact tenant/task/effect/generation.
- `task:recover` not possessed by ordinary agent credentials in production. Expired, revoked, stale or cross-project requests never return another user's task secrets.
- Immutable evidence and consent policies survive restore/replay and the audit logs never store raw bearer/lease, source secret or private user data.

**Current recommendation:** keep R1C lab behavior unchanged until operator ratification; advance to R2 **contract preparation only**, not a verifier, reviewer, or endpoint implementation.
