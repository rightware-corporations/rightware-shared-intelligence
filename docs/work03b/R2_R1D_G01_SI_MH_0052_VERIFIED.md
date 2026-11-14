# SI-MH-0052 — R2 R1D G01 internal pilot: verified evidence and remaining gates

**Date:** 2026-11-14 Africa/Maputo. **Classification:** VERIFIED LAB PILOT / NOT PRODUCTION, DOCUMENTATION ONLY.

## 1. Canonical source

- Code HEAD `develop@ff39c4f5e8b964b01bbe410b2004bd95c38027ea` SI-MH-0051.
- GitHub Actions [43603129072](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43603129072), job `real-mcp-mem0`: **SUCCESS**, `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`, `Ran 208 tests in 30.451s / OK`.
- PostgreSQL `MIGRATION_PASS` 0001..0008 (eight total, 0008 is G01 event journal).
- `WORK03B_R2_R1D_G01_LAB_POLICY_LIVE_PASS provider_live=true two_human_bearers=true validity_days=7 append_only_revoke=true old_idempotent_replay_denied=true no_review=true no_done=true`.
- `WORK03B_R2_R1D_LAB_HTTP_GITHUB_LIVE_PASS` (real GitHub HTTPS; authenticated SERVICE REST via in-process TestClient, pinned workflow run and SHA, PostgreSQL append-only CHECKED_PASS).
- Additional `WORK03B_R2_R1A_GITHUB_LIVE_PASS`, `WORK03B_R2_R1B_LEDGER_LIVE_PASS`, `WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS` and `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS`.
- Failed initial run [43602331541](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43602331541) preserved (1 static migration allowlist FAIL + 1 dict_row KeyError). Correction SI-MH-0050 run [43602557496](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43602557496) SUCCESS, 202/202, before G01 verifier integration.

## 2. Scope proven in G01 lab

Policy records and verification attempts remain immutable; a new append-only event ledger describes lifecycle states. HUMAN proposer is policy creator; a second HUMAN with scoped policy:approve approves exactly seven days from the PostgreSQL clock; independent SERVICE can verify. G01 is opt-in only with R2 R1C local rw_test and `RW_SI_ENABLE_R2_G01_LAB_POLICY=1`. The verifier checks ACTIVE before outbound GitHub GET and after returning, under the same task lock used by DISABLED/SUPERSEDED admin mutations. Idempotent replays cannot return prior CHECKED_PASS once the policy is disabled or expired. No review or DONE is produced.

The GitHub provider call was REAL `LIVE_HTTPS` in the G03 CI step. Other negative tests use `SIMULATED_TRANSPORT` and are not evidence of external authenticity. FastAPI was exercised through TestClient, not a public deployed server.

## 3. Gate matrix (no overclaim)

| G01 | Demonstrated in lab | Residual gap |
|---|---|---|
| 01 inactive policy | PASS: fail before provider | Production/default tenant migration unapproved |
| 02 independent approval | PASS: distinct HUMAN bearer credentials + 7-day DB-time | No enterprise approval quorum/OIDC |
| 03 expiry | PARTIAL: expired before provider with synthetic DB timestamp | Expiry during network, real clock passage |
| 04 disabled + idempotent replay | PASS: PostgreSQL + LIVE REST marker | Production revocation SLA |
| 05 disabled while external request | PASS: simulated midflight disable, no attempt | Independent separate-process concurrency stress |
| 06 supersession | PARTIAL: terminal successor not autoactive | LIVE REST new version / tenant cross-scope |
| 07 verifier/author cannot approve | PASS: HUMAN grant/credential checks, role separation | HR identity and workload attestation |
| 08 cross-project/organization | PARTIAL: preexisting R1B scope checks | Dedicated G01 admin cross-org matrix |
| 09 concurrency linearization | PARTIAL: transaction row lock + controlled midflight | Two-process race under load |
| 10 immutable journal | PASS: UPDATE/DELETE rejected | privileged DB and backup integrity |
| 11 stale generation/replay | PASS: expected sequence and old key replay 409 | policy-admin idem mismatched successor payload |
| 12 backup/restore | **OPEN** | PostgreSQL PITR/restore proof not run |
| 13 non-activated legacy | PASS under G01 flag; legacy only in explicit G01-OFF synthetic mode | Production historical migration not approved |
| 14 no auto review/DONE | PASS, task IN_REVIEW / evidence REFERENCED | Independent reviewer lifecycle unimplemented |

**This is a pilot, not full G01 closure**. Additional required gates: source ACL/tenant consent/retention, OIDC/keys, rate limiting, RLS/egress, branch protection (develop reported unprotected), incident review and full M01–M18 acceptance. G04/G05 remain blocked; JARVIS/PULSE not integrated.

## 4. Next priority

1. R1D-G01-HARDEN: two-process revoke vs verify concurrency; expiry during provider call; cross-tenant lifecycle operations; mismatched idempotency replay after SUPERSEDE; simulate DB outage, all without a new public admin route.
2. R1D-G01-RECOVERY: true PostgreSQL backup/restore or deterministic isolated restore verification of immutable policy events and terminal states; no speculative PASS.
3. R1D-G04 requirements: tenant consent/access/retention, verified identity and audit; separate explicit operator approval before production.
4. Keep policy lifecycle OFF by default outside isolated tests. Never conflate provider CHECKED_PASS with reviewer acceptance or DONE.

**This SI-MH-0052 changes documentation and handoffs only; its own Actions job is separate from the validated SI-MH-0051 code run above.**
