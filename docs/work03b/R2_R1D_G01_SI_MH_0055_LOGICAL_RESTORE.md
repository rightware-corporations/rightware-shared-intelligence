# SI-MH-0055 — G01-HARDEN CI verified, native logical PostgreSQL restore gate introduced

**2026-11-14 Africa/Maputo. Source HEAD `develop@fc768ac8f99d4f4fc3a572c7eac26ae3c7e7493e`. Classification: VERIFIED LAB G01-HARDEN + NEW RECOVERY LAB CHECK PENDING CI.**

## Confirmed CI of SI-MH-0054

- [GitHub Actions 43606091450](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43606091450) **completed SUCCESS**, job 132480927279.
- `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`; migrations 0001..0008 `MIGRATION_PASS`; `Ran 216 tests in 32.455s`, `OK`.
- R1A/R1B real GitHub live, G03 real GitHub-through-REST G01 policy marker `WORK03B_R2_R1D_G01_LAB_POLICY_LIVE_PASS`; R1C bound lease recovery and real MCP/REST/PostgreSQL/Mem0/Ollama E2E PASS.
- Eight new tests confirmed: two separately spawned processes for disable-during-provider vs verification commit, PostgreSQL-clock expiry *during* simulated provider fetch, admin idempotency payload/generation checks, terminal historical key denial, cross-organization HUMAN denial and exact disable replay. These fixture provider tests are `SIMULATED_TRANSPORT`; separate G03 marker was real LIVE HTTPS. Avoid generalizing a single interleaving into a full production race proof.

## New G01-12 engineering, actual CI PENDING

Added `scripts/work03b_r2_r1d_g01_restore_lab.py` and a mandatory CI step **after G03 LIVE and before R1C destructive reset**, restricted to isolated local `rw_test` and G01 opt-in lab flags.

The script uses native PostgreSQL 16 utilities `pg_dump -Fc` and `pg_restore` through ephemeral `postgres:16` Docker containers (host network to CI Postgres only). It validates a synthetic G03 state (one policy; PROPOSED→ACTIVATED→DISABLED; one LIVE_HTTPS CHECKED_PASS attempt; task IN_REVIEW; evidence REFERENCED), creates an isolated random temporary database `rw_g01_restore_<random>`, restores a full logical archive into it and compares original/restored policy events, verification attempts and task/evidence states. Then it checks DB-clock effective policy remains revoked via `PolicyLifecycle.require_active`, and confirms the append-only SQL trigger still rejects DELETE. The script always drops **only** the restore DB it created, and TemporaryDirectory discards the backup archive. No archive, token or private content is committed or printed.

**Expected marker (NOT YET OBSERVED):** `WORK03B_R2_R1D_G01_NATIVE_RESTORE_PASS`. This will be a real custom-format **logical restore** proof for G01-12 in a synthetic CI lab if PASS; it will **not** be a physical PITR/failover, offsite encrypted retention, or customer disaster recovery certification.

No production or private customer data; no new migration, task DONE, public admin route, OIDC/tenant consent/retention/ACL, main/JARVIS/PULSE/vendor Mem0 changes. This checkpoint's CI is **PENDING**; on failure fix under next SI-MH checkpoint without erasing evidence.
