# SI-MH-0049 — G01 Internal Policy Lifecycle LAB Foundation

**Date:** 2026-11-14 Africa/Maputo. **State:** LAB SCHEMA + INTERNAL POLICY SERVICE, CI PENDING, NOT PRODUCTION. Baseline `develop@dc2daaff69df6357454473d2e7fc7ecdce9903e7` [Actions 43601430844](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43601430844) SUCCESS. SI-MH-0046/47/48 independent research retained.

The user's go-ahead follows the proposal for an internal RIGHTWARE pilot; this authorizes only a reversible opt-in laboratory proof, NOT customer onboarding, general production consent/privacy settings, or unreviewed policy governance.

### Implemented

- Migration `0008_work03b_r2_r1d_g01_policy_lifecycle_lab.sql`: append-only policy PROPOSED/ACTIVATED/DISABLED/SUPERSEDED, composite project/task/evidence/policy FK, immutable trigger, sequence fence, idempotency uniqueness, distinct terminal events. Pinned GitHub policy and earlier verification ledger remain immutable.
- `backend/rightware_si/policy_lifecycle.py`: requires `RW_SI_ENABLE_R2_G01_LAB_POLICY=1` plus `RW_SI_ENVIRONMENT=lab`, existing R1C LAB flag and local rw_test. Internal only: caller presents high-entropy API bearer, principal resolution against database in transaction, HUMAN grant checks. Policy author proposes; independent HUMAN with policy:approve activates for 7 DB-clock days. Revocation is terminal, same task FOR UPDATE lock. New policy must be separately approved on supersession. No REST admin route.
- `tests/test_r2_r1d_g01_policy_lab.py`: eight PostgreSQL integration tests for inactive, two-human approval + 7-day window, nonhuman denied, self-approval denied, disabled terminal, supersede, stale sequence and immutable rows. **194+8=202 expected, NOT VALIDATED until new CI.**
- CI migration registration 0008; **G01 enforcement in EvidenceLedger NOT YET CONNECTED**. G03 LIVE through REST still baseline mode, no policy activation in that step; do not claim G01-04 idempotency replay/midflight protection proven by this commit.

### Pending next engineering

Implement G01 opt-in check in EvidenceLedger at preflight and after provider with same task lock (including idempotent replay), CI G03 LIVE with two HUMAN bearer tokens and post-verify revocation, plus DB-clock expiry/midflight tests. Test actual CI and repair. G01 backup/restore, tenant source ACL/consent/retention, G04/G05 release and reviewer/DONE remain open.

No production deployment, main/JARVIS/PULSE/vendor Mem0 modifications.
