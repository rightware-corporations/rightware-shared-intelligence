# SI-MH-0058 — G04 design baseline and CI verification

**Date:** 2026-11-14 Africa/Maputo. **State:** VERIFIED DOCUMENTATION CHECKPOINT, G04 DECISIONS NOT RATIFIED, NO G04 CODE.

## Exact proof

- Source commit `aaee51f592d0746b5c25fde122909d1f4175f41c` (SI-MH-0057) records four G04 R0 artifacts and both handoffs.
- [GitHub Actions run 43608329040](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43608329040), job 132487669927: **completed SUCCESS**.
- `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`.
- PostgreSQL `MIGRATION_PASS` 0001 through 0008, **zero new migrations**.
- `Ran 216 tests in 29.006s`, `OK`; **zero new G04 tests executed**. The 28 G04 JSONL oracles are design-only and explicitly `NOT_IMPLEMENTED`.
- G01 actual GitHub HTTPS + SERVICE REST: `WORK03B_R2_R1D_G01_LAB_POLICY_LIVE_PASS` and `WORK03B_R2_R1D_LAB_HTTP_GITHUB_LIVE_PASS`.
- G01 native synthetic `pg_dump`/`pg_restore`: `WORK03B_R2_R1D_G01_NATIVE_RESTORE_PASS`.
- R1C two-agent recovery and WORK02D MCP/REST/PostgreSQL/Mem0/Ollama live synthetic chain PASS.

## Engineering state

1. G04 architecture: [G04_00_IDENTITY_TENANCY_PRIVACY_ARCHITECTURE_R0.md](G04_00_IDENTITY_TENANCY_PRIVACY_ARCHITECTURE_R0.md) **DRAFT**.
2. Threat model: [G04_01_THREAT_MODEL_AND_TRUST_BOUNDARIES_R0.md](G04_01_THREAT_MODEL_AND_TRUST_BOUNDARIES_R0.md) 18 preliminary design threats **NOT penetration-test findings**.
3. Decisions: [G04_02_DECISION_AND_ACCEPTANCE_MATRIX_R0.md](G04_02_DECISION_AND_ACCEPTANCE_MATRIX_R0.md) D01–D12 ALL OPEN, contains role/action and trust invariants.
4. Test inventory: [fixtures/G04_ACCEPTANCE_ORACLES_R0.jsonl](fixtures/G04_ACCEPTANCE_ORACLES_R0.jsonl) 28 machine-readable future negative oracles, all NOT_IMPLEMENTED.

No OIDC/tenant RLS/ACL/source consent/semantic provider authorization/privacy deletion or external deployment was created or exercised. G01 LAB remains the last **runtime code** baseline, G04 customer staging/production, G05, task reviewer/DONE blocked.

## Next decision packet

Seek explicit scoped approval of D01–D05 and D12 first for a synthetic internal G04 prototype. Do not choose the identity provider, tenant access rules, source-consent terms or retention periods implicitly. D09/D10 privacy/data-residency must be reviewed for each jurisdiction and data class.

This SI-MH-0058 changes only documents and CURRENT/MASTER handoffs. Its own CI is separately pending.
