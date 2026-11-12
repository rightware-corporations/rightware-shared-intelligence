# SEC-R1C — Operator Ratification of Conservative Principles (R1)

**2026-11-12 Africa/Maputo** · **OFFICIAL PRINCIPLE DECISION, NOT DEPLOYMENT APPROVAL**

The operator answered "vamos" directly after the four SEC-R1C security principles had been presented for approval and followed by a proposal to implement a SERVICE-only verifier. This checkpoint interprets that as acceptance of the **explicit high-level conservative principles**, not acceptance of unspecified roles, retention intervals, provider contracts, compliance settings, changes to production, or general user-facing verification.

| ID | Ratified security principle | Still to design/test before release |
|---|---|---|
| SEC-R1C-01 | New release tasks must use checkpoint-bound handoff; legacy exceptions only by explicit allowlist | enumerate legacy IDs, owners, deprecation date, fail-closed runtime switch and rollback |
| SEC-R1C-02 | No automatic cross-principal takeover of abandoned leases | authorized recovery authority, two-person exception protocol, revocation and emergency operations |
| SEC-R1C-03 | Never automatically repeat ambiguous external effects | durable intent/outbox, provider idempotency receipts, reconciliation and compensation |
| SEC-R1C-04 | Dedicated narrowly scoped workload recovery credentials and audited recovery | OIDC/workload identity, step-up and rate limits, tenant isolation, secret rotation/restore |

**No existing runtime behaviour changes based solely on this ratification.** Lab R1C compatibility `LEGACY_UNBOUND` remains, prior token flows remain, and no effects are executed. The intended release behavior above is a policy target, **not an implemented hardening claim**.

**R2 decision:** A minimum SERVICE-only GitHub Evidence REST adapter is approved for **disposable local laboratory execution only**, opt-in and disabled by default; it must not accept caller-generated identity/provider settings, must compare path evidence_id with policy.evidence_id before and after GitHub call, and cannot issue review/DONE. Enabling it for a real tenant/production remains unauthorized. R2-PROVIDER tenancy, R2-IDENTITY production workload assurance and R2-PRIVACY consent/retention remain UNRATIFIED, requiring explicit future approval.

**Acceptance:** verify CI and real PostgreSQL HTTP negative tests separately. CI green for the lab does not authorize production.
