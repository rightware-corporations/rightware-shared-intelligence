# SI-MH-0089 — TRUST: ENG-E1-04B closed, G04-A1 scope and decision packet

**2026-11-24 Africa/Maputo. Base:** develop@c4e46021afef8c55b7deda2e60e4af2c3f205470. **Classification:** VERIFIED LAB ENGINEERING / PROPOSED NEXT MISSION. Owner TRUST; LEARN keeps E1-X02. No new operator authorization inferred beyond existing G04-A0 decision.

## 1. Exact browser and core evidence
- SI-MH-0087 [CI 45364884789](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45364884789), completed/success; core job 138343926801: 356 tests in 21.782s, HANDOFF_POLICY_PASS, real MCP/Mem0/Ollama E2E PASS. Browser job 138343927067: Chromium 143.0.7499.4, SLOT_A_PASS and SLOT_B_PASS: ZIP allowlist, 24 questions and 560 rating fields each, wrong pair rejected, blank and partial rejected, draft roundtrip, zero external page requests. E1_04_BROWSER_SMOKE_PASS synthetic_only=true actual_humans=0 submitted=0 adjudicated=0 operator_dispatch=false science_gate=REVIEW_REQUIRED.
- SI-MH-0088 [CI 45365605458](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45365605458), completed/success; browser job 138346403820 repeats both slot and final PASS; core job 138346404245: 356 tests in 43.951s, handoff and real MCP/Mem0/Ollama PASS. The Ubuntu 26.04 and CSP failures remain preserved in history.
- ENG-E1-04B engineering gate CLOSED. No more review tooling development absent a concrete defect. Actual local operator export and dispatch, real human identity/independence, 2 submitted reviews, adjudication and independent reserved holdout are NOT VERIFIED/NOT RUN. No humans documented; status AWAITING_HUMAN_INPUT / BLOCKED_HUMAN_REVIEW for scientific progression, E1_DATA_READY=REVIEW_REQUIRED. This is not a claim that no qualified humans exist.
- Operator action on controlled, access-restricted encrypted local checkout: follow [runbook](e1_04/OPERATOR_RUNBOOK.md), use scripts/e1_04_prepare_review.py on clean develop, check final packages locally, share separately with verified human reviewers. Never publish custody mapping, submissions, raw holdout or private identities.

## 2. Next independent engineering area: G04 identity
Sources re-read: [A0 ratification](../work03b/G04_A0_OPERATOR_DECISION_R1.md), [A0 verified](../work03b/G04_A0_SI_MH_0062_VERIFIED.md), [architecture](../work03b/G04_00_IDENTITY_TENANCY_PRIVACY_ARCHITECTURE_R0.md), [threat model](../work03b/G04_01_THREAT_MODEL_AND_TRUST_BOUNDARIES_R0.md), [decision matrix](../work03b/G04_02_DECISION_AND_ACCEPTANCE_MATRIX_R0.md), [28 oracles](../work03b/fixtures/G04_ACCEPTANCE_ORACLES_R0.jsonl), actual backend/rightware_si/g04_a0_synthetic_policy.py. A0 authorizes only in-memory synthetic evaluator, never real authentication. Its 21 tests previously passed, no real IdP, signatures, runtime wiring, memberships/RLS or provider selection. The 28 original acceptance oracles remain NOT_IMPLEMENTED. D01–D05/D12 principles ratified with A0 boundaries; D06–D11 open. A1/A2 require new explicit decision. No provider or release choice made.

### Recommended new scope for operator approval: G04-A1-LAB-01
Goal: isolated offline signed credential verification experiment, distinct from full OIDC implementation and A0 fake Claim. No external IdP, real accounts, network listeners, persistent credentials, secrets in repo, database migrations, HTTP/MCP/Mem0 wiring, production or staging. Use ephemeral generated asymmetric keypairs, synthetic issuer profiles, separate HUMAN/SERVICE/AGENT credential validation profiles, synthetic clock and revocation store. Compare maintained JOSE library support and license/dependencies before pinning one; no custom cryptographic primitives or remote key fetch. Candidate algorithm RS256, explicit issuer-specific keys and fixed audiences; final choices to be captured in experiment manifest. HUMAN ID token and workload access token are separate token profiles; token verification does not authenticate an interactive human or complete PKCE/MFA. Privileged actions, policy approval, reviewer/DONE all denied in this lab. A valid signature never directly authorizes access to a tenant, project or resource.

Proposed allowed files after approval: new isolated lab module under backend/rightware_si/ (not imported by runtime), dedicated G04-A1 tests, lab-only dependency manifest if necessary, docs/work03b/G04_A1* and handoffs. No changes to production dependencies, existing G04-A0, LEARN artifacts, formal evaluation corpus or sealed A0. Coordinate any shared CI changes.

Proposed exit criteria (not executed, no PASS):
| Lab test family | Expected |
|---|---|
| Valid ephemeral signed synthetic credential with exact issuer/audience/profile | Verified identity candidate only |
| Tampered payload/signature, wrong key, alg none, HS/RS confusion | Reject |
| Unknown issuer/key, unexpected token type, cross-issuer kid collision | Reject without fetching token-supplied URL |
| Wrong/missing audience, expiry, nbf, iat, missing/invalid subject or credential identifier as required by frozen profile | Reject |
| Same subject across issuers, workload token presented as HUMAN, caller-provided tenant/role | No impersonation or elevation |
| Revoked credential or generation, stale key/revocation snapshot, unavailable verifier | Fail closed |
| Replay test for explicitly one-time synthetic exchange receipt | Reject second use; do not conflate reusable bearer access tokens with one-time exchanges |
| Raw token/key material in errors/logs; runtime import or unexpected egress | No disclosure, no wiring/egress |

G04-05/06 UNIT are partially targeted; original G04-06 includes replay and requires exact frozen semantics. G04-01/08/09 DB_REAL, G04-07 full OIDC session E2E, G04-28 multiprocess remain NOT_IMPLEMENTED. No oracle promotion until its required execution level and all conditions are satisfied. A1-LAB-01 cannot satisfy provider-backed login or real tenancy authorization. Later A1 provider selection and A2 DB ACL/RLS need separate approved scopes.

### Decision requested
Approve or decline G04-A1-LAB-01 only. No paid services or deployment needed. If declined, retain A0 and work on other explicitly approved scope. Human review gate remains independent of this experiment.

## 3. LEARN synchronization
SI-MH-0088 records local X02 experiment: 4320 rankings, 90 recalculated metrics, full pairwise nDCG@5 .9052 vs explicit hybrid .9341 and pointwise .9385; dev abstention zero coverage. Different X01/X02 corpora, no superiority or formal gate claim. Kaggle reproduction pending as reported in latest LEARN handoff; TRUST has not executed or audited its ZIP. Next LEARN owns X02 Kaggle/audit.

**Changes here:** documentation only, no code, new tests, dependencies, schema, CI workflow, G04 implementation, notebook, model, main, JARVIS/PULSE, vendor or deployment change. Current commit CI pending. Next TRUST: operator human review in parallel with approved G04-A1-LAB-01, if authorized. No new browser infrastructure by default.
