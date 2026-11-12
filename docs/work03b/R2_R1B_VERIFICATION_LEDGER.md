# RIGHTWARE Shared Intelligence — WORK-03B R2 R1B Evidence Ledger

**Date:** 2026-11-12 Africa/Maputo. **Status at code commit:** IMPLEMENTED IN SYNTHETIC LAB; CI PENDING. This is not a production verifier, ratified security policy, reviewer or DONE implementation.

**Baseline:** develop at 7e38f617c851d8c70911e15001aec945eac5ebda; [CI 43215546691](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43215546691) SUCCESS (115 tests, R2-R1A GitHub API EV-01..04 live, R1C and Mem0/Ollama regressions).

## Implemented technical scope

1. **PostgreSQL migration 0007:** a pinned versioned policy table si_evidence_verification_policies and append-only si_verification_attempts. Same-project/task/evidence composite FKs, UNIQUE idempotency, PostgreSQL triggers preventing UPDATE/DELETE, and new EVIDENCE_CHECKED continuity event. The original si_evidence_refs.verification_state stays REFERENCED; agent observations stay ASSERTED.
2. **Independent SERVICE identity:** internal EvidenceLedger accepts a trusted application-authenticated actor, requires principal_kind SERVICE with current evidence:verify and task:read grants. An AGENT cannot verify even with a grant string. Actor may not be the task creator, evidence submitter or policy author. Policies are seeded only by the lab's trusted operator, not from a public request.
3. **Exact policy binding:** task must be IN_REVIEW and match expected task version; criterion index must exist; evidence URL must exactly match pinned repository owner/name and GitHub Actions run ID. Submitted evidence URI is NEVER used as an HTTP fetch target. Stable repository ID, workflow ID, SHA, run attempt and event are pinned by immutable policy.
4. **Safe network and transaction:** preflight scope/identity/grant check; bounded real GitHub API call outside a database lock; repeat task/version/grant/policy/source checks under a task row lock before inserting any result. A grant revoked during the provider call blocks persistence. A provider outage returns INCONCLUSIVE, not PASS.
5. **Provenance:** observation_channel LIVE_HTTPS for real fixed GitHub API, SIMULATED_TRANSPORT for injected fake/mock transports. The result is CHECKED_PASS / CHECKED_FAIL / INCONCLUSIVE with reason code, not a signature and not a statement of product correctness.
6. **Replay and privacy:** unique project/verifier/idempotency key; repeat same key/scope returns the same append-only record, cross-policy key reuse is a conflict. Reading requires both evidence:read and task:read with current project grants. Persisted attempts contain only bounded result/provider identifiers and no raw URL, token, JSON body or private model prompt.
7. **No DONE:** no task status/version transition, no approved review, no modifying the historical submitted evidence or observations. Every result carries task_approved=false and review_decision NOT_IMPLEMENTED_R2_R1B.

## Files and tests

- database/migrations/0007_work03b_r2_r1b_verification_ledger.sql — two scoped tables, immutability, continuity event.
- backend/rightware_si/verification_ledger.py — internal authorized two-phase verification/persistence and scoped evidence read.
- tests/test_r2_r1b_ledger.py — **16 real PostgreSQL/application tests** covering mock PASS/FAIL/INCONCLUSIVE, SERVICE and grants, self-check prohibition, URL binding, stale version, revocation mid-flight, idempotency, immutability, criteria index, scoped reads and parallel attempt creation.
- scripts/work03b_r2_r1b_live_ledger.py — isolated **real GitHub API → service-authenticated PostgreSQL ledger** smoke. Refuses any database except disposable localhost:5432/rw_test and uses only synthetic tasks. Calls WorkCore create/publish/claim/submit_result, seeded policy, bearer-resolved SERVICE identity, actual GitHub run lookup, append-only record, replay and read revocation. Verifies task remains IN_REVIEW and evidence state REFERENCED.
- .github/workflows/ci.yml — apply migration 0007 and run new live ledger smoke before R1C/real Mem0 E2E.

**Expected count:** previous 115 + 16 new = 131 tests, plus separate GitHub live and Mem0 integration smokes. THIS IS EXPECTATION, NOT VERIFIED RESULT until CI runs on the implementation SHA.

## Boundaries and open decisions

- No public REST/MCP verifier endpoint. Original R2_TRUST_CONTRACT_R0.json remains an unratified draft with **zero operational R2 routes**. Existing canonical UC-CORE-01 route inventory remains 18 lab + 3 future. New internal ledger is a lab technical experiment, not an approved API product.
- SEC-R1C-01..04 (legacy unbound handoffs, absent owner, external effect safety, recovery privilege hardening) remain **recommendations awaiting operator ratification**. This implementation changes none of them.
- No enterprise workload OIDC, multi-tenant RLS security audit, policy approval workflow, source consent/erasure/retention, rate limiting, production secrets vault, human reviewer, task DONE, immutable offsite audit or deployment.
- A LIVE_HTTPS result records what GitHub provider said about exact workflow fields; it is not in-toto/Sigstore signature verification or proof of every task criterion. Mocked results are tagged SIMULATED_TRANSPORT and must not be treated as authentic provider evidence.
- Original SI-RD-03C 16 oracle research fixture remains unchanged: EV-01..04 were previously run live against a historical run; EV-05..07 simulated in earlier R1A tests; EV-08..16 remain unexecuted. R1B's new PostgreSQL tests are a **separate implementation slice**, not full acceptance of all oracles.
- No main, Jarvis, PULSE, Mem0 pin, new dependency or production deployment changes.

## Next engineering gate

Verify CI results, record actual observations in a new MASTER/CURRENT handoff addendum. Then obtain explicit operator ratification of production security/defaults and provider+criteria policy before enabling authorized public verification API or a separate review decision workflow. Never use this lab PASS to auto-DONE.
