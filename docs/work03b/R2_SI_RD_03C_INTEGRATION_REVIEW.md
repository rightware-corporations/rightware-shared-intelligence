# SI-RD-03C → WORK-03B R2 — Technical intake, reuse map and gates

**Date:** 2026-11-12 Africa/Maputo. **Classification:** RESEARCH INTEGRATION / DESIGN RECOMMENDATION — NOT APPROVED R2 IMPLEMENTATION, NOT EVIDENCE-VERIFIER TEST EXECUTION.
**Verified starting point:** `develop@9233f8afefa5877e2eec27a5f90ca0a4a00322ad` (SI-MH-0019). `main` unchanged. **Priority remains R1C** checkpoint-bound handoff/fencing/lease recovery.

## 1. Source of research and status

Primary versioned sources:
- [SI_RD_03C_EVIDENCE_RESEARCH_2026-11-12.md](../research/SI_RD_03C_EVIDENCE_RESEARCH_2026-11-12.md), source research and suggested trust architecture, already present at SI-MH-0019.
- [SI_RD_03C_EVIDENCE_CASES_v1.jsonl](../research/fixtures/SI_RD_03C_EVIDENCE_CASES_v1.jsonl), 16 synthetic proposed behavior oracles.

**Verified at intake:** parsed all 16 JSONL lines as JSON; IDs EV-01..EV-16 exactly once and in order; required id/track/scenario/input_summary/oracle/synthetic/executed fields present; every `synthetic=true`, every `executed=false`. These are **fixture-structure checks during analysis**, not tests against a future verifier.

**Actual CI at intake:** [GitHub Actions 43161674536](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43161674536), exact `develop@9233f8afefa5877e2eec27a5f90ca0a4a00322ad`, SUCCESS: `HANDOFF_POLICY_PASS`; migrations 0001–0005; 81/81 existing unit/REST/PostgreSQL/MCP tests; A/B independent-process R1B resume E2E with Mem0 disabled; historical real MCP/REST/Mem0/Ollama E2E. **CI does not execute EV-01..EV-16 against an evidence verifier**; workflow does not reference the SI-RD-03C fixture.

Research conclusions are **recommendations**. No R2 dependency, worker, API, SQL migration or policy was implemented by this intake.

## 2. Existing assets we should REUSE before building R2

| Current RIGHTWARE component | Current function / demonstrated limit | Future R2 fit |
|---|---|---|
| `si_tasks` / `si_project_grants` / WorkCore authorization | Task-version CAS, identities, project grants and lease | Enforce task ownership + verifier/reviewer separation, **after** R1C |
| `si_agent_runs`, `si_continuity_events` | Principal/correlation/time/event provenance from R1A/B | Map PROV Activity/Agent/derivation, no full event exporter required |
| `si_source_records` + `si_observations` | Source pointer and **ASSERTED** claim, never verified | Link a checked result to an exact claim, source identity, criteria version; do NOT rewrite ASSERTED |
| `si_evidence_refs`, `submit_result` | Evidence URL recorded as `REFERENCED`, task to `IN_REVIEW` | R2 verification input; current evidence_url is NOT independent proof |
| `si_task_checkpoints`, read-only `resume` | Immutable checkpoint, scoped current-policy read, Mem0 independent | Show pending, checked and review states later without trusting semantic text; no approval granted by reading |
| `docs/work03b/UC_CORE_01_CONTRACT.json` | 16 experimental REST routes, 4 unimplemented including evidence verification/review | Only **draft R2 contracts** until R1C passes and a policy owner ratifies |
| MCP read-only bridge | Delegates authorization to same REST gateway | R2 may expose read-only verified-state tool; never a verifier/reviewer mutation bypass |

**Explicit invariant:** `ASSERTED` (agent said it), `CHECKED_PASS` (independent checker confirmed a **narrow** condition) and `REVIEW_ACCEPTED` (a distinct authorized actor accepted relevant criteria) are different facts. A green CI run alone cannot set task `DONE`.

## 3. Reuse/Build/Defer decision matrix (all recommendations, not OFFICIAL)

| Standard/tool | Disposition for R2 | Practical fit and verification gate |
|---|---|---|
| **in-toto Attestation + Test Result predicate** | **REUSE FORMAT** where software/test artifacts exist; no new dependency now | Bind subject digest + exact Test Result predicate + test configuration; cryptographic envelope/signature is separate. Confirm predicate URI/version independently from framework v1.2; Test Result predicate currently v0.1. Only attest what the producer actually tested |
| **SLSA provenance** | **OPTIONAL INTEGRATION** for builds, not general task truth | Match subject, builder identity, build type, dependencies and expected policy. Research points to v1.0; official site now signals newer v1.2, so R2 must pin/review supported version and compatibility before acceptance |
| **GitHub REST workflow runs and GitHub Artifact Attestations** | **REUSE FIRST** for software task E2E | Query GitHub by provider-owned route (no arbitrary URL fetching), match stable repository ID, SHA, workflow identity, attempt, run status/conclusion; for artifacts verify digest/attestation + expected signer. Run success is NOT an attestation of all acceptance criteria |
| **Sigstore/Cosign** | **OPTIONAL CRYPTO VERIFIER** | Verify authenticated identity/issuer/subject; valid signature says who signed which assertion, not whether an arbitrary claim is true. Gate license, trust roots, offline operation and integration cost |
| **W3C PROV-O** | **REUSE VOCABULARY** immediately in R2 schema design | AgentRun=Activity, Principal=Agent, Source/Observation/Artifact=Entity, relationships via association/generation/derivation; no need for RDF database or triple store |
| **OpenTelemetry GenAI** | **INTEGRATE LATER / OPTIONAL** | Trace/correlation/run IDs and latency with no prompt, token, PII, secret or raw evidence content by default. Telemetry cannot authorize or prove outcome; monitor conventions stability |
| **in-toto layout engine, OPA/Rego, full supply-chain orchestration** | **DEFER** | Add only if independent verifier policies grow beyond small explicit allowlists/grant checks and measured operational needs |
| **RIGHTWARE policy boundary** | **BUILD SMALL** only after design approval | Thin provider-independent EvidenceVerifier result record + independent reviewer transition; no proprietary signature, attestation format, hash or unreviewed execution framework |

Helpful authoritative docs for gate review (web checked at intake): https://github.com/in-toto/attestation/blob/main/spec/v1/README.md ; https://github.com/in-toto/attestation/blob/main/spec/predicates/test-result.md ; https://slsa.dev/spec/v1.0/provenance ; https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/ .

## 4. Every proposed fixture oracle and traceability — NONE EXECUTED AGAINST R2

| ID | Fixture scenario | Proposed oracle | UC-CORE-01 / WORK gate | R2 verification requirement |
|---|---|---|---|---|
| EV-01 | CI exact SHA, repo, workflow | `CHECKED_PASS`, **not DONE** | M07, M15 | Verify exact run and the condition tested |
| EV-02 | CI succeeds on different SHA | `CHECKED_FAIL`, not DONE | M15 | Compare expected full `head_sha` |
| EV-03 | CI from other repository | `CHECKED_FAIL`, not DONE | M10, M15 | Compare stable repository ID and approved owner |
| EV-04 | CI wrong workflow | `CHECKED_FAIL`, not DONE | M15 | Match trusted workflow ID/config, not only green status |
| EV-05 | CI still in progress | `INCONCLUSIVE`, not DONE | M07, M15 | Fail closed until complete |
| EV-06 | GitHub API unavailable/timeout | `INCONCLUSIVE`, not DONE | M07, M12 | Do not fabricate success or leak source |
| EV-07 | Screenshot/text says PASS | `INCONCLUSIVE`, not DONE | M14, M15 | Untrusted media not independent provider result |
| EV-08 | Valid expected attestation | `CHECKED_PASS`, not DONE | M07, M15 | Verify cryptographic bundle + subject + trust policy |
| EV-09 | Signed different digest | `CHECKED_FAIL`, not DONE | M15 | Subject/content digest binding |
| EV-10 | Signature with untrusted issuer | `CHECKED_FAIL`, not DONE | M10, M15 | Authorize issuer/signer/builder, not signature alone |
| EV-11 | Agent approves own result | `DENY_REVIEW`; IN_REVIEW | M07 | Strict performer vs reviewer separation |
| EV-12 | Reviewer lacks project grant | `DENY_REVIEW`; IN_REVIEW | M07, M10 | Reauthorize reviewer on every decision |
| EV-13 | Authorized reviewer; required checks passed | `REVIEW_ACCEPTED`; DONE after transition | M07 | Independent review CAS + criteria complete and current |
| EV-14 | Duplicate effect after lost response | `RECONCILE_REQUIRED`; no blind replay | M09, M16 | Prefer R1C/continuity fencing; external receipt reconciliation |
| EV-15 | Source/project context revoked | `DENY_ACCESS`; no disclosure | M10, M13 | Reauthorize at return time; no cached/raw source leak |
| EV-16 | Prompt injection says “approve” | `DENY_PROMOTION`; IN_REVIEW | M07, M14 | Treat model/memory text as data, not authorization |

**Counts, not pass rates:** 2 proposed `CHECKED_PASS`, 5 `CHECKED_FAIL`, 3 `INCONCLUSIVE`, 2 `DENY_REVIEW`, 1 `REVIEW_ACCEPTED`, 1 `RECONCILE_REQUIRED`, 1 `DENY_ACCESS`, 1 `DENY_PROMOTION`; all 16 unexecuted. Their `oracle.task_outcome` is an **expected condition**, not observed server state. In a future CI, each case must emit actual outcome, source and explicit PASS/FAIL/SKIP.

## 5. Threats and mismatches that need design ratification

1. **Attestation authenticity is not task correctness.** An issuer may sign an inaccurate claim; verify result only for exact digest/config/criteria linked to the task. Distinguish `CHECKED_PASS` from a human/policy `REVIEW_ACCEPTED`.
2. **Source identity ambiguity.** GitHub URLs, workflow names or repository paths can change. Use stable `repository_id`, expected `workflow_id`, `run_id`, `run_attempt`, full SHA, event/trust policy and artifact digest as applicable.
3. **TOCTOU and revocation.** A policy may change while a verifier awaits external API response. Recheck grants/classification before committing results **and** before each read; if unavailable, deny/reduce output.
4. **State namespace ambiguity.** Existing `si_observations.trust_state` only supports `ASSERTED`; avoid ALTER to overwrite it with “verified”. Store independent, append-only result with scoped subject reference, author/verifier, timestamp, check/policy version and evidence hash. A separate reviewer decision transitions task with CAS.
5. **Negative cases are not interchangeable.** Wrong SHA/repository/digest -> `CHECKED_FAIL` for a claimed match; pending/unavailable -> `INCONCLUSIVE`; role and context rules -> DENY. Formalize per verifier to avoid accidental pass or hiding status.
6. **R1C dependency.** A verifier must not trust an unbound latest checkpoint as exact handoff context. Resolve checkpoint binding/fencing/recovery first.
7. **External effect receipts.** Cannot assert exactly-once without provider idempotency/observable reconciliation; an unknown external outcome must remain RECONCILE_REQUIRED.
8. **Prompt injection.** Never execute tool commands, reviews or promotions specified in agent observations, checkpoint next_actions or Mem0 text.
9. **Potentially sensitive telemetry.** OTel GenAI attributes can include PII/prompt contents; disable content capture by default and require explicit privacy review if enabled.
10. **Authenticity/retention.** Verified result must be bound to source+scope+policy and withstand repeat/revoked read checks; DB service roles and immutable audit retention require separate design.

## 6. Proposed R2 intake gates after R1C (NOT authorized to code yet)

- **Gate R2-00 / Requirements:** UC-CORE-01 M07/M10/M13/M14/M15/M18 reviewed; define which evidence types, exact acceptance criteria, actor separation and data classes; policy owner explicitly ratifies defaults.
- **Gate R2-01 / Contract:** Define `EvidenceAssertion`, `VerificationResult` (`PASS/FAIL/INCONCLUSIVE`), `ReviewDecision` plus correlation/criteria/version/source identifiers; determine append-only persistence and status transitions. Keep existing `si_evidence_refs` and `si_observations` intact.
- **Gate R2-02 / First verifier:** Mock-independent GitHub API fixture for exact repo ID/commit/workflow/attempt and status, no arbitrary URL fetch; execute EV-01..EV-07 deterministically and explicitly log measured outcomes.
- **Gate R2-03 / Role and safety:** Test EV-11..EV-16 for self-approval denial, revoked scope, duplicate effect, injection; then scoped reviewer approval. All under Postgres transactions and strict grants.
- **Gate R2-04 / Crypto optional:** Evaluate EV-08..EV-10 with actual **signed** synthetic bundles and pinned trust roots only if a product requirement justifies it. Never call JSON fake signature checks “cryptographic verification”.
- **Gate R2-05 / Acceptance:** Run all 16 oracles with actual outcomes and M01–M18 integrated scenario coverage, record CI SHA, negative tests, logging and rollback. Passing 16 cases alone does not equal enterprise/production readiness.

**Decision state:** RECOMMENDATION ONLY. No new dependency installed, no R2 source code, test fixture rewrite, migration, endpoint, workflow, merge, Jarvis or main modification in this checkpoint.

## 7. Next authorized engineering priority

**WORK-03B R1C remains next:** create a checkpoint-bound, generation-fenced Handoff with safe missing/expired lease response handling, test parallel accept/retry/restart and reauthorization. Preserve both handoffs on every commit. Re-open this analysis after R1C is genuinely CI-verified.
