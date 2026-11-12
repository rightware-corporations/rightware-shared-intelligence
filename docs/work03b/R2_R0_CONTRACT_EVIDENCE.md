# WORK-03B R2 R0 — Verified contract-only CI evidence

**Date:** 2026-11-12 Africa/Maputo · **Tested SHA:** `22d71632caa6f7e442af5964561b42b1b4ea8693` · **Branch:** `develop` · **CI:** [GitHub Actions run 43201981635](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43201981635) **SUCCESS**.

## Exactly what CI established

- `HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true`: both MASTER and CURRENT handoffs updated in the contract commit.
- PostgreSQL lab migrations 0001–0006; `MIGRATION_PASS 0006_work03b_r1c_handoff_fencing.sql`.
- `Ran 100 tests`, `OK`: 94 previously validated R1C tests + six new **static/document-contract tests** in `tests/test_r2_r0_contract.py`.
- `WORK03B_R1B_RESUME_E2E_PASS`: two independent agents, PostgreSQL checkpoint and Mem0-offline resume; denied invalid stale lease, intruder and revoked grant.
- `WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS`: exact bound checkpoint, lease-generation fencing, one-time rekey and idempotency secret replay denial, synthetic only.
- `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS`: real MCP stdio, REST, PostgreSQL, Mem0 OSS, Ollama embedding; cross-project denial and revocation.
- Observed logs show no unmasked ephemeral internal API key.

## Six new static checks; what they do NOT prove

The new suite parses a machine-readable contract and the original 16-case JSONL, ensures all IDs and expected oracles match, confirms every `executed=false` and `observed_decision=null`, checks proposed R2 routes do not appear as live FastAPI decorators, enforces the no-auto-DONE trust split, and checks R1C operator gate labels/UC-CORE-01 pending acceptance.

**This is a CONTRACT CONSISTENCY PASS, NOT an EVIDENCE VERIFICATION PASS.** No independent GitHub verification call, real signed in-toto/Sigstore artifact, GitHub attestation signature check, review decision, automated task DONE, external effect reconciliation or EV-01..EV-16 execution happened.

## New documents and checkpoint governance

- `docs/work03b/R1C_SECURITY_POLICY_GATE_R0.md`: SEC-R1C-01..04 are **RECOMMENDATIONS AWAITING OPERATOR RATIFICATION**, no runtime policy change.
- `docs/work03b/R2_TRUST_CONTRACT_R0.md`, `R2_TRUST_CONTRACT_R0.json`: 0 R2 implemented routes, two R2 proposed routes, three-layer authority model (ASSERTED / CHECKED_* / REVIEW_*) and gates R2-00..05.
- `docs/ARCHITECTURE.md`, `docs/work03b/UC_CORE_01_ACCEPTANCE.md`, root `README.md` linked to these drafts.
- Original canonical UC_CORE_01_CONTRACT.json unchanged: 18 experimental routes, three future, M01–M18 still PENDING_FULL_E2E. SI-RD-03C source research/fixtures unchanged.
- No changes to backend runtime, SQL, packages, CI workflow, external services, Mem0 gitlink, `main`, JARVIS or PULSE. This evidence addendum is documentation-only and requires its own CI result.

## Next action

Present SEC-R1C-01..04 for explicit operator ratification/adjustment: legacy no-checkpoint handoff migration, privileged same-holder rekey vs absent-holder reassignment, effect intent/receipt reconciliation, and production workload auth/rate limits.

Then select a narrowly scoped R2 R1 GitHub Workflow Run verifier policy (exact repository ID, workflow ID, commit SHA and criteria), and **only after authorization** implement a real independent provider adapter with EV-01..07 tests. No assertion from a model or green CI alone may promote DONE.
