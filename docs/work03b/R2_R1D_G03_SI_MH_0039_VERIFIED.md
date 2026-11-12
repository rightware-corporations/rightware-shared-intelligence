# WORK-03B R2 R1D-G03 — SI-MH-0039 verified HTTP→LIVE GitHub→PostgreSQL

**Date:** 2026-11-12 (Africa/Maputo). **Status:** VERIFIED LAB EXPERIMENTAL ONLY; NO RELEASE, NO REVIEW, NO DONE.

## Canonical evidence

| Item | Exact result |
|---|---|
| Tested SHA | `develop@4086e9b62fa06c8c28b9af48c47fe56354e73b2d` |
| GitHub Actions run | [43257931058](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43257931058) |
| Workflow job | `real-mcp-mem0`, completed / **SUCCESS** |
| Handoff gate | `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true` |
| PostgreSQL migrations | `MIGRATION_PASS 0001..0007` (all seven) |
| Unit + integration suite | **`Ran 174 tests in 23.223s` / `OK`** |
| Existing R1A and R1B live | `WORK03B_R2_R1A_GITHUB_LIVE_PASS`, `WORK03B_R2_R1B_LEDGER_LIVE_PASS` |
| **New G03 through HTTP** | **`WORK03B_R2_R1D_LAB_HTTP_GITHUB_LIVE_PASS`** |
| Continuity | `WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS` |
| Real memory chain | `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS` |

The G03 marker in the job logs is:

```text
WORK03B_R2_R1D_LAB_HTTP_GITHUB_LIVE_PASS transport=GitHub_API_HTTPS provider_live=true bearer_service=true pinned_policy=true postgres_append_only=true same_key_replay=true permission_revocation_denied=true evidence_state=REFERENCED task_state=IN_REVIEW no_review=true no_done=true synthetic_lab=true
```

No tokens, raw bearer credentials, DB passwords or provider bodies were included in this report or the marker.

## What G03 actually demonstrates

An in-process FastAPI `TestClient` submitted an authenticated REST POST with SERVICE bearer, `policy_id`, `expected_task_version`, and `Idempotency-Key` through the guarded R2 R1C lab route. Server-only `RW_SI_GITHUB_PROVIDER_TOKEN` authenticated a real HTTPS GET against the **pinned public GitHub Actions workflow run**. The R2 verifier checked the exact workflow/repo/SHA/run/attempt/event/status, inserted a single `CHECKED_PASS` attempt with `LIVE_HTTPS` in the PostgreSQL ledger, returned the same immutable attempt for idempotent replay, and rejected a replay after `evidence:verify` was revoked. Task remained `IN_REVIEW`; evidence remained `REFERENCED`; no reviewer or DONE state was created.

**This is not a deployed HTTP server or production tenant**, nor an external request from a separate browser/network. The FastAPI adapter ran through TestClient in the GitHub runner, while the GitHub provider call and PostgreSQL transaction were real within the isolated CI laboratory. Earlier 16 plus 16 R1C/R1D HTTP tests with `MockTransport` remain simulated for their provider inputs. Their results are not replaced with a LIVE label.

## Remaining restrictions and decisions

- **G01 BLOCKED FOR APPROVAL:** VerificationPolicy expiry, disable, supersede and tenant-specific authority not implemented. Current `si_evidence_verification_policies` is immutable; changes require a separate control/event model that cannot silently mutate historical policy rows.
- **G02:** 16 additional negative tests are validated, but the complete production abuse/tenant matrix remains open, including rate limiting and malicious client/resource behavior outside this synthetic lab.
- **G04 BLOCKED FOR APPROVAL:** enterprise workload identity/OIDC and key rotation; source ACL, consent, retention and erasure; service audit, rate limits, DB RLS and least privilege.
- **G05 BLOCKED:** branch `develop` had no branch protection when inspected, no production release, no complete M01–M18 E2E acceptance, and no independent task reviewer/DONE.
- G03 does not support checking arbitrary private repositories/custom providers, provider attestation signatures or business criteria truth. It validates only the pinned GitHub run fields. No JARVIS/PULSE/vendor Mem0/main changes.

## Next work recommendation

Design a **fail-closed, append-only policy lifecycle** for a first internal RIGHTWARE tenant only. Define who can create/disable/supersede a policy, when it expires, and how revocation is enforced before/after the GitHub request with transaction-time lock. Obtain operator approval of the precise controls before schema/API changes. Then write policy lifecycle tests and migrations, preserving G03 as a regression gate. Production rollout/reviewer/DONE remain out of scope.

**This SI-MH-0039 is a documentation-only checkpoint; its own GitHub Actions job will have a different SHA/run and must be observed separately.**
