# WORK-03B R2 R1B — Verified Evidence Ledger Results

**Date:** 2026-11-12 Africa/Maputo. **Classification:** VERIFIED IN SYNTHETIC LAB, NOT PRODUCTION/REVIEW/DONE.
**Tested implementation:** develop@cfa6153c4e8bbebd27d30f629e1681966312663f.
**CI:** [GitHub Actions run 43237504677](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43237504677) **SUCCESS**.

## Actual CI observations

- HANDOFF_POLICY_PASS audited_commits=1 both_files_updated=true.
- PostgreSQL 16 disposable rw_test migrations 0001–0007 SUCCESS, including MIGRATION_PASS 0007_work03b_r2_r1b_verification_ledger.sql.
- Ran **131 tests in 17.123s**, OK: 115 previous tests + 16 actual PostgreSQL/application ledger tests (synthetic provider responses).
- R2 R1A existing live GitHub provider checks: EV-01 CHECKED_PASS and EV-02/03/04 CHECKED_FAIL (expected wrong SHA/repository/workflow); no task approved.
- WORK03B_R2_R1B_LEDGER_LIVE_PASS provider=github_api result=CHECKED_PASS postgres_append_only=true independent_service=true scope_checked=true revoked_read_denied=true idempotent=true task_status=IN_REVIEW evidence_state=REFERENCED no_review=true no_done=true synthetic_lab=true.
- WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS for independent agent processes/lease rekey, Mem0 off, secret replay denied.
- WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS for actual MCP stdio → REST → PostgreSQL → pinned Mem0 OSS → local Ollama embedding (scope/denials/revocation, synthetic only).
- No unmasked ephemeral internal Mem0 API key was observed in the inspected logs.

## Which evidence was LIVE, MOCKED, or not executed?

| Component | Actual execution | Status / limit |
|---|---|---|
| R2 R1A EV-01–EV-04 | LIVE GitHub REST API, historical completed workflow | Correct provider run passes exact identity; wrong SHA/repo/workflow fails. No DONE. |
| R2 R1A EV-05–EV-07 | MOCKED/controlled adapter tests | Code handles pending/outage/screenshot as inconclusive; no real outage tested. |
| R2 R1B Postgres ledger | **LIVE GitHub API + real PostgreSQL + SERVICE bearer** | Verified stored append-only CHECKED_PASS with LIVE_HTTPS channel and revocation/idempotency; synthetic task only. |
| R2 R1B unit/DB suite | 16 REAL PostgreSQL transactions, MOCKED provider transport | Grants, policy, immutable records, no DONE, mid-flight revocation, concurrency and simulated provenance. |
| SI-RD-03C EV-08–EV-16 | NOT EXECUTED | No real signed in-toto/Sigstore bundle, independent reviewer, DONE, ambiguous external effect, source-level consent or injection acceptance. |

The original SI-RD-03C fixture intentionally remains unchanged with synthetic=true and executed=false for all 16: it is a proposed oracle specification, **not** the execution journal. R1A's actual EV-01..04 live and EV-05..07 mock outcomes and R1B's new live PostgreSQL evidence are documented separately here.

## Verified guarantees within this lab

1. A trusted SERVICE principal authorized with current project evidence:verify and task:read grants, separate from agent author/evidence submitter/operator policy author, can check an exact pinned GitHub workflow run.
2. Evidence URL is matched to the pinned operator policy before network access; the supplied evidence URI is not fetched as an arbitrary URL. A bounded TLS GitHub API read occurs outside any PostgreSQL write lock. Grants/task version/policy/source are checked again under lock before append-only storage; mid-flight grant revocation is denied.
3. Result has source provenance LIVE_HTTPS or SIMULATED_TRANSPORT and CHECKED_PASS/FAIL/INCONCLUSIVE, with reason, criteria reference, task version, verifier identity and narrow provider identifiers.
4. PostgreSQL scoped foreign keys and triggers prevent cross-project reference and ordinary UPDATE/DELETE of policy/verification rows. Correct same-key retry returns one attempt; different request keys remain separate append-only attempts. Evidence read requires current task:read and evidence:read grants.
5. Task remains IN_REVIEW and original evidence remains REFERENCED. No model assertion is overwritten. No event or service returns REVIEW_ACCEPTED or DONE.

## Limits and security policy remaining

- No public evidence verification REST/MCP endpoint; two R2 R0 proposed routes remain unimplemented. No operator-approved provider policy UI or production workload identity, OIDC, source-level privacy/consent/retention, database role least privilege/RLS hardening, reviewer, DONE or deployment. The internal ledger is not yet a product-ready multi-tenant trust service.
- SEC-R1C-01 through SEC-R1C-04 remain **RECOMMENDATIONS NOT RATIFIED**. R2 R0 contract remains DRAFT. Green CI and exact GitHub run fields do not certify software acceptance or business correctness.
- The immutable policy currently must be seeded by an operator through the trusted disposable lab. PostgreSQL superusers bypass ordinary immutability triggers. No external tool-effect reconciliation or guaranteed exactly-once semantics.
- No new paid API, cryptographic attestation checker, new dependency, main/Jarvis/PULSE change or Mem0 upstream pin alteration.

## Handoff continuity / next

This evidence report is added in a documentation-only commit together with append-only MASTER entry SI-MH-0029 and refreshed CURRENT handoff. The evidence-documentation commit must be independently CI-verified (do not assign PASS before its run completes).

**Next recommended gate:** ratify/revise source/provider acceptance policy, SEC-R1C-01..04, minimum service privilege and privacy requirements. Only then decide whether to enable a tenant-authorized evidence:verify REST endpoint and a separate independent reviewer workflow; neither may infer DONE from a verified workflow run alone.
