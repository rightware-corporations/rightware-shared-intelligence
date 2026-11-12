# WORK-03B R2 R1D-G03 — Real GitHub API through SERVICE-only REST (LAB)

**Date:** 2026-11-12 Africa/Maputo. **Status:** CODE CHECKPOINT CI PENDING; NOT PRODUCED, NOT RATIFIED FOR TENANTS.
**Baseline:** `develop@a3a29dfba16b2bcfca1c523ac7c1229b46c10735`.

## Starting evidence

- [SI-MH-0037 Actions 43256900860](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43256900860): **SUCCESS**, log `Ran 174 tests in 20.220s` / `OK`; seven PostgreSQL migrations, GitHub R1A/R1B LIVE, R1C A/B and Mem0/Ollama E2Es PASS. R1D-G02 negative tests verified in synthetic HTTP+PostgreSQL.
- Endpoint `POST /v1/projects/{project_id}/evidence/{evidence_id}/verify` remains registered **only** when `RW_SI_ENVIRONMENT=lab` and `RW_SI_ENABLE_R2_R1C_LAB_API=1` with disposable localhost:5432/rw_test.
- No production identity or policy revocation lifecycle exists.

## Implementation

- `backend/rightware_si/http_api.py` passes optional GitHub provider credential from **server-only** `RW_SI_GITHUB_PROVIDER_TOKEN` to `EvidenceLedger.verify_and_record`. Clients cannot submit `github_token`, `actor_id`, `client`, provider URL or observation channel; Pydantic rejects unexpected body fields. The token is never emitted in response, DB attempt or test marker.
- New `scripts/work03b_r2_r1d_live_http.py` refuses any database except the disposable local `/rw_test` and explicit lab flags *before* destructive synthetic seeding. Creates SERVICE + AGENT principals, project grants, synthetic IN_REVIEW task and immutable pinned policy for GitHub public workflow run `43202560651` at expected SHA `0c63b2f2d3d4cf00926752ab2c58d42ccbd64901`.
- Uses real FastAPI `TestClient`, authenticated SERVICE bearer and server-side provider token to reach real GitHub API over HTTPS, record `CHECKED_PASS` `LIVE_HTTPS` into PostgreSQL, ensure idempotent replay, revoke permission and assert 403, preserve task IN_REVIEW/evidence REFERENCED, no review/DONE. Prints **one** sanitized marker on fully passing chain.
- `.github/workflows/ci.yml` adds a separate explicit step **after** R2 R1B internal GitHub LIVE smoke and **before** R1C/Mem0 regressions, using ephemeral GitHub Actions `github.token` passed only to the G03 server process as `RW_SI_GITHUB_PROVIDER_TOKEN`.

## Evidence hierarchy and limitations

- G02 174/174 **verified on baseline**, G03 live-through-REST is **not declared PASS until its own workflow job logs show marker and SUCCESS at G03 SHA**.
- A GitHub workflow green proves only the **pinned provider fields**; does not prove task acceptance/claims, user permissions outside the lab or production data privacy.
- G01 policy lifecycle expiry/disable/supersede, G04 workload identity/OIDC/consent/retention/rate limits, G05 production release and M01–M18 full E2E remain UNIMPLEMENTED/UNRATIFIED.
- ZERO migrations/dependencies/JARVIS/PULSE/main/vendor Mem0 changes; no LLM or arbitrary effect calls.

## Acceptance and rollback

- Observe `WORK03B_R2_R1D_LAB_HTTP_GITHUB_LIVE_PASS`, `Ran 174 tests / OK`, all existing live and Mem0/Ollama regression markers, seven migrations, new SHA and run ID.
- If unavailable/rate-limited provider, mark FAIL/INCONCLUSIVE; do **not** fabricate a PASS or remove the step. Repair only with a new checkpoint.
- Feature flag remains OFF by default and script is an isolated ephemeral CI lab; no production rollout.
