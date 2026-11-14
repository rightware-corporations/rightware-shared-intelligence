# SI-MH-0056 — G01 lab recovery and hardening: verified CI evidence

**2026-11-14 Africa/Maputo. Classification:** VERIFIED INTERNAL LAB / DOCUMENTATION ONLY. **Baseline code:** `develop@ecb3a45e4a0be6b55eba561a3519c19fd76ebfa2` (SI-MH-0055).

## CI evidence — actually observed

[GitHub Actions run 43606718445](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43606718445), job 132482831414, **completed / SUCCESS**.

- `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`.
- PostgreSQL migrations `0001`–`0008`: all `MIGRATION_PASS` (no new schema from G01-HARDEN/restore).
- `Ran 216 tests in 36.279s`; `OK`.
- `WORK03B_R2_R1D_G01_LAB_POLICY_LIVE_PASS`: real GitHub provider through SERVICE-only REST/TestClient, independent HUMAN proposer and approver, seven-day DB validity, append-only DISABLED, replay after revoke rejected.
- `WORK03B_R2_R1D_G01_NATIVE_RESTORE_PASS native_pg_dump=true native_pg_restore=true separate_ephemeral_database=true full_archive=true events_immutable=true revocation_survives_restore=true live_provider_attempt_preserved=true task_in_review=true target_cleaned=true synthetic_only=true no_done=true`.
- `WORK03B_R2_R1D_LAB_HTTP_GITHUB_LIVE_PASS`, `WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS`, and `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS` all in successful job logs.
- G01-HARDEN source code itself was verified separately on [run 43606091450](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43606091450), 216/216 PASS. These are **two different code commits**, both tested.

## What the restore gate actually proves

In CI, `scripts/work03b_r2_r1d_g01_restore_lab.py` checked the synthetic prior GitHub LIVE verification state, invoked **real PostgreSQL 16 pg_dump custom-format and pg_restore**, created a fresh random database `rw_g01_restore_<suffix>`, compared source/restored immutable policies, lifecycle events, attempts and task/evidence snapshots, re-evaluated revoked policy as inactive using the PostgreSQL clock, and confirmed the immutability DELETE trigger still rejects modification. It deleted the temporary backup and dropped only the database created by that run.

**G01-12 status: LAB LOGICAL RESTORE VERIFIED / PRODUCTION DR OPEN.** This is not a PostgreSQL physical WAL/PITR restore, automatic failover, offsite encrypted backup, RPO/RTO validation or multi-region restore. A synthetic ephemeral service provides no enterprise recovery SLA.

## Updated G01 security matrix

| Gate | Evidence state | Remaining requirement |
|---|---|---|
| G01-01 inactive | LAB PASS | Production activation governance |
| G01-02 independent HUMAN | LAB PASS | Enterprise approval/OIDC |
| G01-03 expiry before and during provider GET | LAB PASS with mock-time DB seed and controlled delay | Natural 7-day passage and long-running live provider |
| G01-04 disabled + old key replay | LAB + GitHub REAL REST PASS | Tenant deployment revocation SLA |
| G01-05 midflight disable | LAB PASS with two genuinely spawned Python processes | Wider load/chaos race interleavings |
| G01-06 supersession | LAB PARTIAL | Successor live REST and cross-version source scope |
| G01-07 independent roles | LAB PASS | Workload attestations, key lifecycle |
| G01-08 cross-project/organization | LAB PASS for project-bound HUMAN | Resource-source ACL/consent |
| G01-09 concurrent revoke vs verify | LAB PASS for deterministic two-process interleaving | Repeated multi-worker stress and crash recovery |
| G01-10 immutable events | LAB PASS, including after native restore | Database privileged operator/WAL audit |
| G01-11 idempotency / stale generation | LAB PASS incl. reason/successor mismatch | Distributed retries under deployment |
| G01-12 backup/restore | **LAB LOGICAL RESTORE PASS** | Physical PITR, offsite encryption, RPO/RTO |
| G01-13 legacy not activated | LAB PASS with G01 opt-in | Explicit production migration strategy |
| G01-14 no reviewer or DONE | LAB PASS | Independent review business workflow |

No claim of full G01 production certification. Production G04/G05, tenant consent/retention, private-source ACL, workload OIDC, mTLS, rate limits, RLS, app-level operational security and branch protection remain unimplemented. GitHub `develop` was reported `protected=false` in branch metadata; harden before release, but branch settings were NOT changed.

## Recommended next work

Move to an explicitly scoped G04 identity/privacy **design and threat model**, followed by an internal staging gate; do not onboard customers or deploy production without authorized tenant identity, source consent, retention/deletion decisions, RBAC/resource ACL, workload identity and independent security sign-off.

**Changes in SI-MH-0056:** this report plus refreshed `docs/HANDOFF.md` and append-only `docs/HANDOFF_MASTER.md` only. Its OWN docs-only Actions run is separate and should be checked after publication. main/JARVIS/PULSE/vendor Mem0 unchanged.
