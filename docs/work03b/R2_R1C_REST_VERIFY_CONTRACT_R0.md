# WORK-03B R2 R1C — REST Verifier: API Contract, Authorization and Abuse Cases R0

**2026-11-12 (Africa/Maputo)** · **DESIGN & STATIC CONTRACT GATE ONLY** · NOT ratified, NOT implemented, NOT production. 
Baseline `develop@0eb4e662490ffb22a18cdb5e21ac4c85c14066d4`. Canonical candidate endpoint is defined in [UC_CORE_01_CONTRACT.json](UC_CORE_01_CONTRACT.json); earlier [R2 R0 draft](R2_TRUST_CONTRACT_R0.json) is historical design, **not** an authoritative representation of the implemented R1B internal ledger.

## Objective and reuse

R2 R1B already implemented `EvidenceLedger`, migration 0007, exact pinning of GitHub workflow run, SERVICE checks, append-only attempts and no-DONE invariants. [CI 43237504677](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43237504677) records 131 tests and live GitHub→PostgreSQL success for synthetic laboratory data. This phase drafts the smallest **authenticated** REST adapter, **without publishing it**.

Data path when authorized later:
`FastAPI HTTPBearer → resolve_principal → SERVICE + project grants → path evidence_id/policy ID binding → EvidenceLedger preflight → pinned GitHub HTTPS → reauthorize under PostgreSQL lock → attempt append-only → narrow response`.

**Security finding not yet fixed in code:** `EvidenceLedger.verify_and_record(project, actor, policy_id, expected_task_version, idem)` currently does **not** accept path `evidence_id`. An adapter that ignores `/evidence/{evidence_id}` may create confusion across evidence identities. The future implementation must bind `policy.evidence_id == path.evidence_id` in the ledger before network access **and** after network before insertion. An adapter-only preflight without transactional recheck is insufficient.

## Proposed exact HTTP contract

`POST /v1/projects/{project_id}/evidence/{evidence_id}/verify`

- Authentication: existing bearer dependency derives principal server-side. Reject missing/expired credentials as 401.
- Authorization: only `principal_kind=SERVICE` and current project-scoped `evidence:verify` **and** `task:read`. Reject task creator, evidence submitter and policy creator. No request body controls actor or privilege.
- Body `{"policy_id":"<UUID>","expected_task_version":<positive integer>}`. Header `Idempotency-Key` required (current 8..128 header and core `_key` semantics). Path `evidence_id` UUID. No caller `github_token`, `client`, `source_url`, SHA, repo/workflow, or channel.
- Lookup policy must match project, task, selected evidence, acceptance criterion and exact version. Operator-created immutable policy is already lab-seeded. **Tenant administration, policy lifecycle, disable/expiry and source privacy rules do not yet exist.** No production route may be enabled before these gates are designed and approved.
- Return limited `VerificationAttempt` fields on both first request and idempotent replay, HTTP 200 proposed for both. `CHECKED_PASS`, `CHECKED_FAIL`, `INCONCLUSIVE` are decisions about exact checks only.
- Error codes: 401 unauthenticated, 403 insufficient authority, 404 inaccessible resource, 409 stale/mismatched state or idempotency conflict, 422 invalid body, 503 internal unavailability. **External GitHub outage should normally record `INCONCLUSIVE` with 200**, not be presented as an application success in verifying a claim.
- Never change `si_observations.ASSERTED`, `si_evidence_refs.REFERENCED`, `si_tasks.IN_REVIEW` or produce `REVIEW_ACCEPTED`/`DONE`. Never call an arbitrary URL, follow redirects, trust proxy environment or log provider bearer/token/source body.

The machine-readable proposal and case IDs are in [R2_R1C_REST_VERIFY_CONTRACT_R0.json](R2_R1C_REST_VERIFY_CONTRACT_R0.json).

## Negative acceptance matrix — **not executed**

| Case | Scenario | Proposed expected observation |
|---|---|---|
| API-NEG-01 | No bearer | HTTP 401; No provider call, no verification insert |
| API-NEG-02 | AGENT or HUMAN holds evidence:verify | HTTP 403; Principal-kind SERVICE required |
| API-NEG-03 | SERVICE lacks task:read or evidence:verify | HTTP 403; Both project grants required |
| API-NEG-04 | Cross-project task, policy or evidence | HTTP 404; No resource details leaked |
| API-NEG-05 | Path evidence_id differs from policy.evidence_id | HTTP 409; Reject before GitHub request |
| API-NEG-06 | Policy not bound to current project/task/evidence | HTTP 404; Fail closed before network |
| API-NEG-07 | Expected task version is stale or task not IN_REVIEW | HTTP 409; No record committed |
| API-NEG-08 | Grant revoked while provider request is in flight | HTTP 403; Recheck under lock; no record |
| API-NEG-09 | GitHub workflow has wrong SHA/repo/workflow/attempt | HTTP 200; CHECKED_FAIL; no review or DONE |
| API-NEG-10 | GitHub unavailable/redirect/pending | HTTP 200; INCONCLUSIVE; never PASS |
| API-NEG-11 | Replay same idempotency key and same bound request | HTTP 200; Exactly one append-only attempt |
| API-NEG-12 | Replay key reused across evidence/policy/version | HTTP 409; No second insert or mismatched result |
| API-NEG-13 | Request tries to supply actor_id/token/client/source URL/channel | HTTP 422; No identity/provider override |
| API-NEG-14 | Policy expired, superseded or disabled | HTTP 409; Release blocker until policy lifecycle exists |
| API-NEG-15 | Simulated client reports success | HTTP 200; SIMULATED_TRANSPORT; cannot claim LIVE_HTTPS |
| API-NEG-16 | Service cannot reach PostgreSQL or secret leak attempt | HTTP 503; Sanitized error; no token/log disclosure |

**Test distinction:** `tests/test_r2_r1c_contract.py` checks only static contract integrity and current source-code boundaries. It does **not** test HTTP, credentials, database, concurrency, real provider, release policy or an actual R2 R1C endpoint. Prior 131/131 PASS remain evidence for R1B, not proof that any new R1C API case passed.

## Required authority gates and implementation sequence (RECOMMENDATION)

1. Operator must explicitly ratify or amend SEC-R1C-01..04 and scope of GitHub provider, workload identity and source privacy/retention; none are ratified by the phrase "continuar".
2. Define policy administration and disable/expiry guarantees, per-resource privacy boundaries and production secrets handling. Decide scope of tenant pilot vs product-ready release; **do not assume OIDC exists**.
3. Only in a separately authorized engineering checkpoint: add evidence-ID binding to the core, minimal FastAPI request model+route, safe exception mapping and tests; no new migration unless justified by policy requirements.
4. Run real PostgreSQL API integration and negative scenarios, real GitHub provider, idempotency/revocation/race, then existing R1C A/B and Mem0/Ollama regressions. Document separate LIVE vs MOCK results with run/SHA. Until CI, implementation status is PENDING.
5. Review and DONE remain separate workstreams gated by independent human authority and full M01–M18 acceptance, never green CI alone.

**Explicit non-changes here:** No backend runtime, migration, endpoint, provider transport, permissions, release, production deployment or modification to `main`, JARVIS, PULSE or vendor Mem0.
