# WORK-03B R2 R1D-R0 — Security Completion and Tenant Policy Design Gate

**Date:** 2026-11-12 (Africa/Maputo). **Status: RECOMMENDED PLAN, NOT RATIFIED, NO R1D CODE, NO PRODUCTION.**
**Baseline:** `develop@5adb8165eddf54c5145c5aba983882a72dca4b43`, [SI-MH-0035 verified laboratory evidence](R2_R1C_SI_MH_0035_VERIFIED_EVIDENCE.md).

## Objective

Close the limitations left by the R2 R1C experimental SERVICE-only endpoint **without** prematurely introducing production identity, privileged review/DONE or arbitrary execution. Existing release-safe rule: all verification results are separate from agent ASSERTED claims and any human REVIEW decision.

## Priorities in required order

| Gate | Required closure | Required proof | Classification now |
|---|---|---|---|
| R1D-G01 | Contract and tenant ownership of VerificationPolicy: repo/workflow/run/criteria/version, policy expiry/disable/supersede, operator approval/rollback and revoked-source response | Negative tests for expired/disabled/replaced policy and atomic revocation | DESIGN/APPROVAL PENDING |
| R1D-G02 | Complete API-NEG-02/03/06/07/09/10/12/13/16, including HUMAN spoof, missing each grant, wrong task bind, non-IN_REVIEW, wrong repo/workflow/attempt, timeouts/redirects, replay key across version/evidence, forbidden inputs, DB outage/secret-safe 503 | Individually named and executed PostgreSQL/HTTP tests under disposable `/rw_test`; record cases LIVE vs MOCK | TEST EXPANSION PROPOSED |
| R1D-G03 | Real GitHub API via R2 R1C **HTTP endpoint** in isolated CI, pinned historical run, SERVICE bearer, postfetch lock/recheck; no secret/response body logging | New distinct `LAB_HTTP_GITHUB_LIVE_PASS` and run+SHA, independent of existing internal R1B live smoke | E2E PROPOSED |
| R1D-G04 | Authenticated tenant policy/identity/consent: workload OIDC/key lifecycle, least privilege, secret storage, rate limits, source ACL/retention/erasure and audit | Negative security matrix, multi-project security tests, role/revocation drills, policy approval | PRODUCTION DESIGN AND RATIFICATION PENDING |
| R1D-G05 | Release controls: branch protection, backup/restore, scoped DB roles/RLS review, deployment boundary, load/fault injection, acceptance M01–M18 | Release decision based on separate CI, security review and operator sign-off | RELEASE BLOCKED |

## Open choices requiring operator ratification (not defaults)

- Authoritative people/roles allowed to create or revoke policy per tenant, exceptions, approval quorum and precise lifecycle/retention durations.
- Accepted provider categories beyond the pinned GitHub Action run; whether first pilot is internal RIGHTWARE only, not arbitrary client repos.
- Privacy class and source access rights: evidence may be a link to a private repository; **a valid CI result is not permission to reveal source data**.
- Workload/service identity deployment model, key rotation, tenant segmentation, rate limits, audit/incident procedures.
- Any integration with JARVIS/PULSE or user-visible task DONE requires **independent** future approval and full acceptance.

## No bypass

R1D shall not enable production based solely on 158/158 lab tests. It shall not remove the laboratory guard `RW_SI_ENABLE_R2_R1C_LAB_API=1`, `RW_SI_ENVIRONMENT=lab`, loopback `rw_test` nor implement automatic `REVIEW_ACCEPTED`/DONE. Consent, expiry and trust policies must fail closed before exposing new external clients.

## CI context

- [R2 R1C code verification 43251091244](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43251091244): 158/158, SUCCESS.
- [SI-MH-0035 documentation CI 43252042999](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43252042999): 158/158, SUCCESS; seven migrations, real GitHub R1A/R1B and MCP/REST/PostgreSQL/Mem0/Ollama regressions PASS.
- A new CI for this R1D **documentation proposal** must be observed separately after commit. No R1D API-NEG fixes or LIVE-through-REST trial were executed by writing this document.
