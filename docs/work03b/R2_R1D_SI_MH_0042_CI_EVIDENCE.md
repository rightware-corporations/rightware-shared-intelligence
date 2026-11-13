# WORK-03B — SI-MH-0042: Verified synthetic database boundary CI

**Date:** 2026-11-13, Africa/Maputo. **Status:** LAB SECURITY FIX VERIFIED, NOT PRODUCTION RELEASE OR G01 RATIFICATION.

## Evidence from actual GitHub Actions

- Code SHA `develop@d2c06290ec5593324b8c1b84ad96ef3bd335a05e`.
- [GitHub Actions 43401900930](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43401900930), job `real-mcp-mem0` (ID 131806539362): **completed / SUCCESS**.
- `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`.
- Seven `MIGRATION_PASS` entries for `0001` through `0007` (no new migration).
- **`Ran 190 tests in 24.218s` / `OK`**, 16 additional laboratory connection safety tests plus previous 174.
- `WORK03B_R2_R1A_GITHUB_LIVE_PASS`; `WORK03B_R2_R1B_LEDGER_LIVE_PASS`; `WORK03B_R2_R1D_LAB_HTTP_GITHUB_LIVE_PASS`: actual provider GitHub via in-process REST TestClient with SERVICE identity to PostgreSQL append-only, no DONE.
- `WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS`; `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS`: bound agent lease recovery and actual MCP stdio/REST/PostgreSQL/Mem0/Ollama embedding chain passed in synthetic lab.

## Precisely validated / not validated

**Verified:** `require_disposable_postgres` rejects URI query/fragment, PGHOSTADDR/PGSERVICE/PGSERVICEFILE environment connection overrides, external/wrong database/port/username, and nonloopback localhost resolutions; FastAPI experimental lab mode and four destructive synthetic CI scripts call the guard before opening DB connections.

**Not guaranteed:** compromised OS/hosts networking or malicious operator with network capability, remote production egress firewall, private source ACL/consent, workload OIDC, policy expiry/disable/supersession, approved tenant lifecycle authority, browser-external HTTP deployment, reviewer/DONE, complete M01–M18. None of these is covered by 190/190.

**R2 R1D G01 decision gate remains unratified.** See [G01 lifecycle decision packet](R2_R1D_G01_POLICY_LIFECYCLE_DECISION_R0.md). No runtime G01 schema or grants were modified here.

This document is a documentation-only checkpoint SI-MH-0042. Its **own** CI should be observed after commit; SUCCESS above belongs to SHA `d2c06290ec5593324b8c1b84ad96ef3bd335a05e`. No main/JARVIS/PULSE/vendor Mem0 changes.
