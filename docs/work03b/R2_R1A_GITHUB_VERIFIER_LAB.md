# WORK-03B R2 R1A — GitHub Workflow Run Verifier (bounded experimental adapter)

**Date:** 2026-11-12 Africa/Maputo · **Status at code commit:** IMPLEMENTED IN LAB, CI PENDING · **Authority:** EXPERIMENT, **NOT** operator ratification of R1C security policies or full R2 trust contract. **Repo:** develop only. No main/Jarvis/PULSE or Mem0 changes.

## Objective and threat boundary

Build a small **read-only** adapter that checks a precise GitHub Actions workflow run against a pre-specified trust policy without granting task approval. This is an experiment justified by the user's direction to continue with Evidence Verification and Trust; it does **not** accept or silently enact the four SEC-R1C-01..04 security policy recommendations. No R2 database migration or REST/MCP endpoint has been added; review/DONE is still absent.

**Expected exact identity** of a proposed run:
- stable GitHub repository ID **1452533938** and full owner/repository `rightware-corporations/rightware-shared-intelligence`
- workflow ID **415280241**, head commit **0c63b2f2d3d4cf00926752ab2c58d42ccbd64901**
- workflow run ID **43202560651**, attempt **1**, event **push**
- API must report `status=completed, conclusion=success`; head repository must not contradict trusted repository

This policy deliberately uses a previously completed, **real historical synthetic CI run** (GitHub Actions run 43202560651); do not confuse a CI green run with approval of all acceptance criteria, or commit/repository identity with a cryptographic artifact signature. A real GitHub API check can prove only that the provider returned those specific fields.

## Code

- `backend/rightware_si/evidence_github.py`: `GithubRunPolicy` (strict owner/repository slug, positive IDs, 40-char SHA, approved event), `GithubCheck` (CHECKED_PASS, CHECKED_FAIL, INCONCLUSIVE, reason code; task_approved and state_authoritative always false), `verify_github_run` with fixed `https://api.github.com/repos/{owner}/{repo}/actions/runs/{id}` target, strict timeout, TLS validation, redirects/proxy env disabled, bounded JSON response and no arbitrary URL fetching.
- `check_github_record`: validates run/repository/workflow/attempt/SHA/event/head repository; a wrong identity returns CHECKED_FAIL, an unavailable/pending/untrusted provider returns INCONCLUSIVE, a matching completed successful run returns CHECKED_PASS; external results do not authorize task transitions.
- `tests/test_r2_r1a_github_lab.py`: 15 deterministic *actual adapter code* tests, including EV-01..EV-07 mapped to the unchanged SI-RD-03C JSONL oracle; note EV-01..04 in this unit suite use an **httpx mocked provider record** and cannot prove provider authenticity. Additional tests enforce no redirect/SSRF, malformed/forked/wrong attempt data, safe failure and no task approval.
- `scripts/work03b_r2_r1a_github_live.py`: **live** fixed GitHub API smoke with Actions read-only token from CI (GITHUB_TOKEN). Checks EV-01 expected completed success, EV-02 wrong commit, EV-03 wrong stable repository ID, EV-04 wrong workflow ID, with **four actual provider requests**. Prints only reason/status/IDs, never credentials or provider JSON body.
- `.github/workflows/ci.yml`: add `actions:read` to job token (no writes) and live smoke after deterministic tests. Existing core/PostgreSQL, independent-process R1C and Mem0/Ollama E2E remain unchanged.

## Strict separation and limits

| Result class | What may be concluded | What must NOT be concluded |
|---|---|---|
| `CHECKED_PASS` | GitHub API reported the exact expected finished successful run | Software is secure; source matches business acceptance; task approved; signature valid; DONE |
| `CHECKED_FAIL` | A concrete stable field of that provider record contradicted pre-pinned policy, or run had non-success conclusion | That any other untested proposition is false |
| `INCONCLUSIVE` | The expected condition could not be trusted/established; pending, API down, rate limit, redirect, screenshot, incomplete JSON | Approval, or authoritative FAIL without observed contradiction |

Source research fixtures `docs/research/fixtures/SI_RD_03C_EVIDENCE_CASES_v1.jsonl` remain **unchanged**, with `executed=false` as original proposal metadata. This implementation adds a **separate execution log in CI** for a limited subset, which must be described precisely by test type: EV-01..04 live provider if CI passes; EV-05..07 synthetic mocked provider. EV-08..16 **NOT EXECUTED**. It is deliberately not the operator-approved official complete R2 verifier.

This prototype does not persist results into `si_evidence_refs` or a new VerificationAttempt table, does not authenticate a dedicated verifier principal, does not apply the source-level consent/retention policies, and does not reauthorize PostgreSQL project grants. Therefore do NOT expose this as a multi-tenant public verification API or a review decision.

## Source and version reference

Provider: [GitHub REST API — Workflow Runs](https://docs.github.com/en/rest/actions/workflow-runs). Fine-grained token for private repos requires Actions read; CI token is read-only. GitHub primary/secondary rate limits and temporary 403/429 must be handled as **INCONCLUSIVE**, no retry storm. See [GitHub API rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api). The live smoke depends on network/Actions availability and can fail independently of the deterministic adapter; failed live evidence must be recorded honestly.

## Validation and handoff

At commit time: **CI PENDING**, 115 tests **expected** (100 existing + 15 new); live EV-01..04 checks expected, not claimed PASS before GitHub Actions output. Record actual CI SHA, run ID, count and proof lines in a later SI-MH checkpoint. Do not update the R2-R0 JSON `implemented_r2_routes=0` or the original canonical 18/3 route inventory until real APIs are introduced.

**Next decision (R2 R1B):** operator must ratify/revise SEC-R1C-01..04, choose which policy owner/repository/workflow/criteria apply to clients, approve the independent verifier identity/privacy rules, then authorize a PostgreSQL `VerificationAttempt` append-only table and authenticated verification endpoint. In-toto/SLSA/Sigstore and human review/DONE remain future gates.

## Post-implementation CI result — VERIFIED (SI-MH-0027)

[Actions 43214573166](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43214573166) SUCCESS on `develop@1aa40c0d54c96d7c59bb7118326700a974cbb46e`: **115/115 tests PASS** (100 baseline + 15 synthetic adapter tests), 6 PostgreSQL migrations, real GitHub API EV-01 CHECKED_PASS and EV-02/03/04 CHECKED_FAIL (expected, no DONE), independent R1C E2E and real Mem0/Ollama/MCP regression PASS. Detailed evidence and LIVE/MOCK separation are in [R2_R1A_EVIDENCE.md](R2_R1A_EVIDENCE.md). EV-05..07 are controlled/mock; EV-08..16 not executed.

No R2 verification API, persisted VerificationAttempt, reviewer or approval is implemented by this PASS. Original research fixture remains unchanged.
