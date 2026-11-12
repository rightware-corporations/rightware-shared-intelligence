# RIGHTWARE Shared Intelligence — WORK-03B R2 R0: Evidence Verification & Trust Contract

**Date:** 2026-11-12 (Africa/Maputo). **Status:** **DRAFT FOR OPERATOR RATIFICATION / DESIGN ONLY — NO R2 IMPLEMENTATION.**
**Reference:** `develop@30986f53ab2b0459f4ea9eb8a5f7874d5dbcbfc4`, [R1C final CI 43196692278](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43196692278) SUCCESS, 94/94 tests, real A/B and Mem0/Ollama paths. **R2 verifier runs: 0; EV-01..EV-16 executed: 0.**
**Companion:** [machine-readable R0 draft](R2_TRUST_CONTRACT_R0.json).
**Critical dependency:** [R1C security decision register](R1C_SECURITY_POLICY_GATE_R0.md), not yet ratified. This does not silently approve the four recommendations.

## 1. What problem this contract actually solves

R1A/B/C have durable tasks, source-linked ASSERTED observations, immutable checkpoint transfer and rekey/lease fencing. This is **continuity**, not **truth**. A signed blob, a screenshot, a green workflow run, a model summary or a Mem0 hit must never directly set a task to DONE.

The R2 contract proposes **three separate authority boundaries**:

1. **Assertion (agent-authored):** `si_observations.trust_state=ASSERTED`, references to exact source and task/checkpoint. Agent-authored text stays untrusted indefinitely; it is not overwritten with VERIFIED.
2. **Verification (independent service):** a new append-only record (design only) of the exact observed provider result, for a specific evidence ID, criteria/policy version, repo/subject digest, SHA, run/attempt, trusted identity, timestamp and reason. Result limited to `CHECKED_PASS`, `CHECKED_FAIL`, `INCONCLUSIVE`; PASS means *this specific condition* checked under a pinned policy.
3. **Review (independent authorized decision):** a separate actor with `task:review` rechecks grants, task version, policy and **all required criterion results**. Only a valid `REVIEW_ACCEPTED` and transactional CAS may change `si_tasks.status` from IN_REVIEW to DONE. Agent, tool, verifier and memory cannot self-approve.

**Never conflate:** `ASSERTED != CHECKED_PASS != REVIEW_ACCEPTED != DONE`. No primitive introduced by R1C grants verifier/reviewer authority.

## 2. Existing infrastructure REUSE vs proposed new boundaries

| Current concrete asset | Reuse, without replacement | New R2 concern, design only |
|---|---|---|
| `si_tasks` + `si_project_grants` | Project authorization, task CAS, status `IN_REVIEW` | Add `task:review` grant policy, independent reviewer identity and all-required criteria policy |
| `si_evidence_refs` | Source pointer after `submit_result`, currently `REFERENCED` | Do NOT set PASS merely for a URL; bind immutable attempt and exact provider observation |
| `si_source_records`, `si_observations` | Exact source references + `ASSERTED` claim | Link verification to original claim/evidence without mutating its trust_state |
| `si_agent_runs`, `si_continuity_events` | Correlation/provenance and append-only sequence | Add canonical provider check/decision audit; W3C PROV-compatible vocabulary, no RDF database |
| `si_task_checkpoints`, R1C handoffs | Durable scoped context, bound snapshots, generation fence | Use exact checkpoint/criteria version to refuse stale verification/review |
| REST bearer + `mcp_bridge` | Server-derived identity/authorization; MCP read-only | Future tools must never become a direct DONE or verification bypass |
| Mem0 OSS / Ollama embeddings | Recall only, UNVERIFIED data | Never use model/embedding answer as provider API evidence |

**Do not build:** new crypto, custom hash format, a full supply-chain attestation engine, general browsing to arbitrary evidence URLs or a new orchestrator to do verification. Prefer verifiable provider APIs and established formats.

## 3. Future R2 data contract — not migrations

### 3.1 VerificationPolicy (versioned)
- Project and policy ID/version; accepted source type, expected stable repository ID, allowlisted workflow ID/builder identity; criteria-to-test mapping and required check configurations.
- Signature/attestation trust roots if applicable; allowed verifier service principal; retry/backoff/timeout, privacy class/retention.
- Changes to policy versions must not silently retroactively approve old claims.

### 3.2 VerificationAttempt (append-only)
- Exact `project_id,task_id,evidence_id,criteria_id,policy_id,policy_version`; expected subject identity (digest/SHA), observed provider owner/repo ID/workflow/run/attempt, `verified_by` independent service, timestamps, result/reason and bounded provider receipt metadata.
- Reject a wrong repository, workflow, SHA, artifact digest, principal, source scope, or revocation. Pending/network timeout -> INCONCLUSIVE, never PASS.
- Never persist provider bearer credential, full private prompt, raw secrets or arbitrary fetched HTML in verification result.

### 3.3 ReviewDecision (append-only)
- Exact project/task and optimistic task version, independent reviewer principal, selected policy/criteria/verification attempt IDs and source provenance; `REVIEW_ACCEPTED` or `REVIEW_REJECTED`; actor/time/reason.
- Distinct principal and permission required for reviews by default; compare task performer and reviewer. Self-review always denied.
- Any missing/expired/INCONCLUSIVE/FAIL mandatory check forbids DONE. Task transitions after all checks only, in one auditable transaction. Re-evaluate grant and policy under transactional lock to mitigate TOCTOU.

### 3.4 State machine (proposed, not actual code)

```text
submit_result -> si_evidence_refs:REFERENCED, task:IN_REVIEW
                     |
                     +-- independently CHECKED_PASS ---+
                     +-- independently CHECKED_FAIL --+--> independent authorized REVIEW
                     +-- INCONCLUSIVE / timeout ------+          |
                           no approval                |         +-- REVIEW_ACCEPTED + all required PASS
                           no automatic retry         |             + task.version CAS -> DONE
                                                     +---------+-- else remain IN_REVIEW
```

Verification never automatically authorizes execution. The R1C external-effect recovery policy must be ratified before any worker resubmits effects.

## 4. REST and persistence boundaries (proposed only)

The canonical `UC_CORE_01_CONTRACT.json` already lists these two R2 routes **as future**, not implemented:

- `POST /v1/projects/{project_id}/evidence/{evidence_id}/verify`: requires `evidence:verify` from authenticated trusted verifier; binds the evidence/criteria/policy version and writes immutable attempt in an authorized project transaction. Cannot emit DONE.
- `POST /v1/projects/{project_id}/tasks/{task_id}/review`: requires `task:review`, independent reviewer identity and all mandatory verified conditions. Valid decision stores an audit record; only authorized acceptance changes IN_REVIEW to DONE after CAS.
- Memory invalidation route remains a separate future lifecycle concern, **not** implied by R2 verification.

Recommended first supported evidence type: **GitHub workflow run** with stable repository ID, full expected commit SHA, workflow ID, attempt, completed/conclusion, and approved organization/builder. Server uses a constrained GitHub API client, **never HTTP-fetches caller-supplied arbitrary URLs** (SSRF risk). No source-level ACL/consent deployment before its own gate.

## 5. External standards / buy-vs-build

- **GitHub Actions API / Artifact Attestations:** REUSE to verify provider-owned run/subject/identity. Green run can support only configured test criteria, not truth of unrelated tasks.
- **in-toto attestations + Test Result predicate:** optional STANDARD format for signed test-result artifacts. Need verify subject digest, predicate type/version and policy; signed statement can still contain a false claim.
- **SLSA provenance:** optional for build provenance; version pin and trusted builder must be reviewed. It does not verify agent behavior outside a documented build.
- **Sigstore/Cosign:** future crypto verifier for actual signed synthetic fixtures; NEVER pretend unverified JSON is signed.
- **W3C PROV:** minimal schema vocabulary `Entity/Activity/Agent` mapping to existing PostgreSQL relations, not a new triple store.
- **OpenTelemetry:** later traces/latency/correlation, with prompts and private content disabled by default; not authority.
- **OPA/Rego, full in-toto engine:** defer until policy complexity is measured, not assumed.

## 6. Traceability of all 16 synthetic EV oracles — NOT run

| Case | Scenario | Expected verifier/policy result | Expected task outcome | Future gate | Actual |
|---|---|---|---|---|---|
| EV-01 | `ci_exact_sha` | `CHECKED_PASS` | `not_DONE` | R2-02 | NOT EXECUTED |
| EV-02 | `ci_wrong_sha` | `CHECKED_FAIL` | `not_DONE` | R2-02 | NOT EXECUTED |
| EV-03 | `ci_wrong_repository` | `CHECKED_FAIL` | `not_DONE` | R2-02 | NOT EXECUTED |
| EV-04 | `ci_wrong_workflow` | `CHECKED_FAIL` | `not_DONE` | R2-02 | NOT EXECUTED |
| EV-05 | `ci_pending` | `INCONCLUSIVE` | `not_DONE` | R2-02 | NOT EXECUTED |
| EV-06 | `ci_external_api_down` | `INCONCLUSIVE` | `not_DONE` | R2-02 | NOT EXECUTED |
| EV-07 | `fake_screenshot` | `INCONCLUSIVE` | `not_DONE` | R2-02 | NOT EXECUTED |
| EV-08 | `attestation_valid` | `CHECKED_PASS` | `not_DONE` | R2-04 | NOT EXECUTED |
| EV-09 | `attestation_wrong_digest` | `CHECKED_FAIL` | `not_DONE` | R2-04 | NOT EXECUTED |
| EV-10 | `attestation_untrusted_issuer` | `CHECKED_FAIL` | `not_DONE` | R2-04 | NOT EXECUTED |
| EV-11 | `agent_self_review` | `DENY_REVIEW` | `stay_IN_REVIEW` | R2-03 | NOT EXECUTED |
| EV-12 | `reviewer_without_scope` | `DENY_REVIEW` | `stay_IN_REVIEW` | R2-03 | NOT EXECUTED |
| EV-13 | `reviewer_with_checks` | `REVIEW_ACCEPTED` | `DONE_after_authorized_transition` | R2-03 | NOT EXECUTED |
| EV-14 | `duplicate_external_effect` | `RECONCILE_REQUIRED` | `no_reexecution_without_check` | R2-03 | NOT EXECUTED |
| EV-15 | `revoked_context` | `DENY_ACCESS` | `no_data_disclosure` | R2-03 | NOT EXECUTED |
| EV-16 | `llm_prompt_injection` | `DENY_PROMOTION` | `stay_IN_REVIEW` | R2-03 | NOT EXECUTED |

The JSONL fixture remains unchanged, with `synthetic=true` and `executed=false` for all 16. A *static contract consistency test* may assert IDs/expected outcomes, but that is **not** a test of the future verifier or a claim that the oracles passed.

## 7. Development gates and release blockers

- **R2-00 (decision):** Ratify R1C SEC-R1C-01..04, scope and ownership/criteria policy from UC-CORE-01; record approval explicitly in both handoffs. No implicit approval via this document.
- **R2-01 (contract):** Review immutable VerificationPolicy/Attempt/ReviewDecision schemas, status mappings, privacy/retention, one-way transition and actor independence. No database migration until acceptance.
- **R2-02 (first executable slice):** Local independent GitHub run verifier; ground EV-01..EV-07 in fixture-controlled real provider/adapter observations, test wrong repo/SHA/workflow, pending/timeout and fake screenshots. State **actual** PASS/FAIL/SKIP per case in CI.
- **R2-03 (permissions and safety):** Implement independent review and no-self-approval, source revocation, prompt injection and ambiguous-effect reconciliation; run EV-11..EV-16 with actual PostgreSQL and negative tests.
- **R2-04 (crypto optional):** Only if needed, verify **real signed synthetic bundles** for EV-08..EV-10 and pin trust roots/identity. Otherwise keep gate NOT_STARTED, do not mark PASS.
- **R2-05 (acceptance):** Run entire UC-CORE-01 across agents, evidence verifier and reviewer; M01–M18 still PENDING_FULL_E2E until observed, not just contract lint. Production requires separate security/deployment review.

## 8. Decisions needed from RIGHTWARE

The operator must ratify (or revise) SEC-R1C-01..04 and select which evidence providers/criteria justify the MVP verifier. Until then, **R1C implementation stays as tested** and R2 stays an unimplemented, inspectable contract.

**Checkpoint hygiene:** On every Git commit, append to `docs/HANDOFF_MASTER.md` and refresh `docs/HANDOFF.md`; separate plan, code, CI-observed fact and approved policy. Do not modify `main`, Jarvis/PULSE, vendor Mem0 or research fixture during this contract checkpoint.
