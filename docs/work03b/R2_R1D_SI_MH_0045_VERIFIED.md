# WORK-03B — SI-MH-0045 Verified test-fixture security checkpoint

**2026-11-13 Africa/Maputo · VERIFIED LAB CODE CI, DOCUMENTATION ONLY.** G01 still NOT RATIFIED.

## Exact proof

- **Code commit** `bc50bf4652301ad0770c5463c3efcdc629cae433` (SI-MH-0044).
- GitHub Actions [43478925313](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43478925313), job `real-mcp-mem0` 132070019680: completed **SUCCESS**.
- Handoff gate: `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`.
- PostgreSQL isolated migrations 0001–0007: all PASS (no schema added).
- `Ran 194 tests in 28.840s`, `OK` (190 baseline +4 new tests).
- `WORK03B_R2_R1A_GITHUB_LIVE_PASS`, `WORK03B_R2_R1B_LEDGER_LIVE_PASS`, `WORK03B_R2_R1D_LAB_HTTP_GITHUB_LIVE_PASS`: live real GitHub provider, only the bounded synthetic REST/TestClient chain and append-only ledger; no DONE.
- `WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS`: independent agents and fencing; `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS`: actual MCP stdio/REST/PostgreSQL/Mem0 OSS/Ollama in local CI.

## What was fixed

Seven test files that execute `TRUNCATE si_organizations,si_principals RESTART IDENTITY CASCADE` used weak `urlsplit` checks and did not revalidate at `setUp`. They now use the shared fail-closed `is_disposable_postgres` collection helper and `require_disposable_postgres` at the start of each `setUp`, before any SQL connection. The four new pure tests cover valid/invalid URI, libpq environment override, changing env after discovery, and seven fixture source checks. The previous R1C REST lab inherits the fixed R1B fixture.

**Limitations:** This does not establish a production network sandbox or resistance to malicious local host administrators. No G01 lifecycle activation/expiry/disable/supersession, tenant consent/retention/approver authority, OIDC, source ACL, rate limits, production rollout, review or DONE is implemented/ratified. Keep R2 API disabled by default and isolated in `/rw_test`.

This SI-MH-0045 adds an evidence report and updates current/append-only master handoffs only. Its **own CI is not yet observed**; the SUCCESS belongs to the code commit above. `main`, JARVIS, PULSE, vendor Mem0 untouched.

**Next:** operator approval or revision of [G01 lifecycle decision packet](R2_R1D_G01_POLICY_LIFECYCLE_DECISION_R0.md) before any policy schema/API implementation. All 14 G01 lifecycle oracles remain NOT_EXECUTED.
