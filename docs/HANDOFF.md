# RIGHTWARE Shared Intelligence — Engineering Handoff

Updated 2026-11-11. Durable state for continuation after a token limit or chat change.

## WORK-02D VERIFIED CHECKPOINT — 2026-11-11
- Draft PR #6: https://github.com/rightware-corporations/rightware-shared-intelligence/pull/6, stacked on WORK-02C, unmerged.
- Tested code HEAD: 8d7f5234d375d29df774388529094708a4e0cb3c.
- WORK-02D GitHub Actions run 43108517846: **SUCCESS**. 48/48 Python tests PASS on REAL PostgreSQL16 (including lease-secret and migration regression). Migrations 0001/0002/0003 PASS.
- Same run: `WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS` with **external MCP v2 stdio subprocess -> REST bearer gateway -> PostgreSQL project grants/task -> real Mem0 OSS -> Ollama local embeddings -> PostgreSQL17/pgvector**.
- E2E verified authorized Alpha, canonical task state, UNVERIFIED context, denial of Beta/unprivileged principal, and rejection after bearer revocation. All content synthetic.
- Initial run 43107788463 FAILED in older disabled-Mem0 test due to CI environment leakage; fixture made hermetic. Retest 43108113909: 48/48 PASS, but E2E FAILED on duplicate synthetic project fixture after unit tests. Reset restricted to local rw_test fixed this; 43108517846 SUCCESS.
- Client-side read-only Jarvis integration is NOT deployed; no Jarvis source or runtime modified. No merge to main.
- Follow-up: independently review lease retry/recovery design; workload identity, rate limits, retention/erasure, outbox; staging Jarvis opt-in under explicit approval. See docs/work02d/EVIDENCE.md.

## Project
Independent RIGHTWARE-owned memory and operational-continuity infrastructure; public repo https://github.com/rightware-corporations/rightware-shared-intelligence.
Mem0 submodule vendor/mem0 pinned to f1791daa86d469249c9b002f62644d58a1eb96a0, Apache-2.0. Do not modify this pin without review.
No Shared Intelligence or Jarvis/PULSE production deployment was performed.

## Open stacked Draft PRs (all unmerged)
#1 WORK-00 -> #2 WORK-01 -> #3 WORK-02A -> #4 WORK-02B -> #5 WORK-02C. Proposed WORK-02D branch: feat/work02d-e2e-security-hardening, based on WORK-02C f82147d49cfe65560462acff420974f56684e09a.

## Verified prior evidence
WORK-02B: 29/29 tests PASS, Actions run 43067218210.
WORK-02C: 45/45 tests PASS, Actions run 43070689611.
WORK-02C actual Mem0 OSS + Ollama embeddings + PostgreSQL/pgvector: REAL_MEM0_SMOKE_PASS, Actions run 43071532909; final WORK-02C SHA f82147d49c CI real run 43072249164 SUCCESS.
Qwen text generation NOT tested; infer=false. Prior synthetic scope test is not security certification.

## WORK-02D plan (not yet accepted)
1. Ensure lease secrets are NEVER stored in si_idempotency.response; migration 0003 scrubs legacy values; claim/accept retry returns explicit 409 because the one-time lease secret cannot be safely replayed.
2. Real independent MCP stdio subprocess client -> REST FastAPI auth -> PostgreSQL permissions/tasks -> Mem0 OSS -> Ollama embeddings -> PG17/pgvector.
3. Negative cases: Beta project denial, unprivileged principal denial, token revocation, no unverified promotion.
4. Record actual CI results, commit SHA, fixes, PR URL and remaining gaps in docs/work02d/EVIDENCE.md; update this HANDOFF after verified checkpoint.

## Safety boundaries
PostgreSQL tasks/events are authoritative; Mem0 produces UNVERIFIED context. Authenticated project grants are applied server-side; client-supplied Mem0 user_id is never permission.
Public repo: no real tokens, private chats, or production business data. CI keys must be ephemeral and masked.
Remaining production gates: workload identity, rate limiting/TLS, lease recovery after lost response, outbox, retention/erasure, red-team isolation, real Jarvis staging and opt-in rollback.
Jarvis is production-sensitive: no changes to Jarvis repository, runtime or deployment here. No merge to main.

## Next action
Run WORK-02D CI, inspect logs, fix failures, update evidence and HANDOFF before ending the work.
