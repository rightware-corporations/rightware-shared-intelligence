# SI-MH-0062 — G04-A0 synthetic design & security contract validated

**2026-11-17 Africa/Maputo. Classification:** VERIFIED SYNTHETIC LAB CODE/TESTS; G04 REAL-TENANT SECURITY NOT IMPLEMENTED. Code source: develop@c387217e75bb6fab836e62a4306f648debd9e213.

## Exact verified CI

- [GitHub Actions 44113475872](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/44113475872), job 134145055234: completed **SUCCESS**.
- HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true.
- MIGRATION_PASS 0001 through 0008, unchanged schema.
- Ran **237 tests in 35.672s**, **OK** (previous 216 + 21 standalone G04-A0 synthetic-only tests).
- WORK03B_R2_R1A_GITHUB_LIVE_PASS, WORK03B_R2_R1D_G01_LAB_POLICY_LIVE_PASS, WORK03B_R2_R1D_G01_NATIVE_RESTORE_PASS, WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS and WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS confirmed in actual logs.

## Exactly what passed

The 21 G04-A0 pure unit tests exercise in-memory fake issuer/subject matching, synthetic RIGHTWARE project access with two fake adversary organizations, deny-by-default resource grants, expired or revoked membership/grant/claim, audience/role spoof, unsupported privileged actions and PRIVATE class, feature flag/local test DB guard, duplicate ambiguous data, and static nonwiring in the HTTP gateway.

**This is not an identity-provider test.** Fake Claim objects have no signature and are freely constructible. The G04-A0 module is not imported by runtime HTTP, MCP or Mem0 and is unsuitable for any real client/production authorization.

D01,D02,D03,D04,D05,D12 principles and synthetic scope recorded in [operator decision R1](G04_A0_OPERATOR_DECISION_R1.md). D02 actual IdP selection, D03 concrete workload federation/mTLS technology, D12 technical branch protection remain unresolved. D06–D11 entirely OPEN including client/legal consent/retention. GitHub develop branch was previously observed unprotected; this checkpoint does not alter its settings.

The 28 G04-R0 machine-readable acceptance oracles remain NOT_IMPLEMENTED and **none were marked PASS**. No new migrations, RLS, OIDC, source connector, private data, production/staging, customer onboarding, task reviewer/DONE, main/JARVIS/PULSE/vendor Mem0 modifications.

## Next gated work

1. G04-A1: provider/issuer decision and separate isolated OIDC/workload authentication implementation, with cryptographic negative tests, *not* reusing fake claims.
2. G04-A2: separate schema/resource ACL/RLS approval and real PostgreSQL cross-tenant tests.
3. D12 actual protected-branch configuration coordinated with parallel research work, avoiding disruptions.
4. D09/D10 privacy/retention and legal jurisdiction decisions before private sources or customer data.

This SI-MH-0062 changes only evidence report and current/master handoffs. Its own docs-only CI run is separately pending.
