# SIC — Parallel engineering coordination
**2026-11-24 · SI-MH-0085.** Official operator decision: both agents actively develop in parallel, in distinct areas; not an exclusive strategy-versus-execution split. Operational allocation below implements that decision. Agent labels identify conversations/workstreams, not authenticated principals or proof of human independence.

| Track | Owner | Active mission | Write scope |
|---|---|---|---|
| TRUST | AGENT-01 — recovery/continuation conversation | ENG-E1-04B browser/packaging gate and human-review readiness | e1_03/e1_04 reviewer tooling, their tests/docs, isolated browser CI job |
| LEARN | AGENT-02 — original SIC vision conversation | E1-X01 Kaggle reproduction / provisional learning | isolated experimental notebooks, experimental datasets, metrics and research reports |

G04 security/identity and Core continuity are candidate next missions for TRUST after the concrete browser issue is resolved; open a scoped mission before touching them, preserve prior ratification boundaries. Formal E1.2–E1.5 depend on E1_DATA_READY and do not become approved by X01 experiments. Human review/adjudication/holdout require real independent people; neither AI agent may stand in for them. LEARN does not inspect reserved data, private review artifacts or sealed A0. TRUST does not modify X01 notebooks/models or tune learning metrics. Shared contracts, runtime integration, broad CI changes and roadmap changes require explicit coordination before writing.

## Protocol
1. Before each mission read remote develop HEAD, both handoffs, this registry, policy, relevant paths and CI; state owner/mission/base/allowed paths and exit criteria. If unclear whether a mission overlaps, stop that overlapping work and coordinate; other independent work may continue.
2. Work in parallel on disjoint scoped outputs. Existing official branches develop/main remain; no new branches or destructive Git operations. Reserve shared files (HANDOFF, MASTER, registry) for short publication operations only; they are not independent write scopes.
3. Before publication fetch latest HEAD, compare any intervening changes, re-read shared documents and allocate the next unused SI-MH identifier. If scoped paths changed, reconcile before writing. Create one atomic commit containing output and BOTH handoffs; publish with expected current parent SHA, fast-forward only. On conflict stop, re-read and rebase the proposed change logically without losing other work. Never overwrite concurrent edits or reuse an occupied checkpoint ID.
4. Verify remote commit/HEAD and CI; distinguish per-job failure from whole-workflow success. Record pending/failed/blocked outputs and findings, including the exact next step for both tracks. Each track owns its own failures; notify the other track via shared handoff when a dependency changes.
5. Operator remains the decision authority. Cross-track integration or promotion to official model/production is a separate approved gate. Git coordination is procedural and optimistic concurrency only, not a distributed lease or access-control implementation. Agents do not run continuously or communicate directly without a new turn or shared Git update.

## Current gates
- TRUST: prior browser CI failed twice at Playwright install on ubuntu26.04-x64; scoped pin to ubuntu-24.04 is a candidate repair, pending new CI. Actual browser run, operator distribution, human reviews (0), adjudication and independent holdout are not yet verified.
- LEARN: X01 local training performed, Kaggle evidence ZIP not yet supplied; 2 prototypes underperform best baseline; abstention coverage zero and risk undefined. No official scientific promotion.
- E1_DATA_READY=REVIEW_REQUIRED. Neither track changes main or customer/production data.

## SI-MH-0087 — synchronization
- TRUST: Ubuntu 24.04 installation verified; actual browser test failed on CSP-blocked string evaluation. Locator-only patch published, strict CSP retained; new CI pending. Human review gate remains open.
- LEARN: SI-MH-0086 records audited Kaggle X01 reproduction; next E1-X02 provisional experiment. No official model promotion. No change of write-scope ownership.

## SI-MH-0089 — TRUST gate closed; proposed G04 mission
- TRUST ENG-E1-04B verified in two green CI runs. Review tooling closed absent defects. Human execution awaiting independent reviewers and curator. Proposed G04-A1-LAB-01 awaits explicit scope approval; until then no G04 implementation. See [decision packet](../research/SI_MH_0089_TRUST_BROWSER_CLOSE_G04_A1_SCOPE.md).
- LEARN remains owner of E1-X02 Kaggle reproduction and experimental algorithm work (SI-MH-0088). Shared publication protocol unchanged.

## SI-MH-0091 — TRUST mission active
- Operator approved G04-A1-LAB-01 exactly as SI-MH-0089. TRUST owns new g04_a1_lab module, dedicated tests, lab requirements, standalone path-scoped CI and G04_A1 documentation; no shared runtime or broad CI edits. Implementation published, execution pending. LEARN owns X03; no overlap. ENG-E1-04B remains verified; human review awaiting real input.

## SI-MH-0092 — TRUST lab CI repair
- Initial lab 25/26 passed, one fixture construction error; fixed and hardened retired key continuity, 29 expected, CI pending. LEARN remains separate; human and formal G04 gates unchanged.

## SI-MH-0093 — TRUST CI layout reconciliation
- G04-A1 lab remains isolated by job and dependency installation, now in the single existing ci.yml to satisfy the established repository layout. Previous core failure preserved; no test weakening or changes to LEARN or other jobs. New combined CI pending.

## SI-MH-0096 — TRUST LAB-02
- G04-A1-LAB-01 verified (29 tests); G04-A1-LAB-02 active: synthetic principal binding in existing lab module and dedicated tests only. No real identity, runtime or DB scope. CI pending, LEARN X03 unchanged. SIC-PILOT-01 remains proposed; human review awaiting actual input.

## SI-MH-0097 — TRUST LAB-03
- LAB-02 dedicated 50 tests PASS; LAB-03 active, existing isolated module + tests and docs only, explicit synthetic memberships, no resource grant or real tenant. CI pending. LEARN independent. No cross-track integration or deployment.

## SI-MH-0098 — TRUST LAB-04
- LAB-03 verified all jobs (73 lab,356 core,browser). LAB-04 active, synthetic resource policy only in existing lab, dedicated tests and docs; CI pending. No real client integration/production. LEARN remains independent; next bounded integration proposal after CI.

## SI-MH-0099 — TRUST A1 closed; A2 proposal
- LAB-04 and full baseline verified; 98 isolated A1 + 356 core tests, browser PASS. G04-A2-LAB-01 awaits explicit bounded approval for new disposable DB tables/roles/job only. No operational migrations, real identity, deployment or LEARN edits. [Decision packet](../work03b/G04_A2_LAB_01_DECISION_PACKET.md).

## SI-MH-0100 — TRUST A2 lab active
- Explicit operator approval for disposable DB lab. TRUST owns database/labs/g04_a2/, tests/g04_a2_lab/, G04_A2 lab documentation, isolated appended CI job and shared publication files only. 16 DB_REAL_LAB test families implemented, CI pending. No existing migrations or runtime/LEARN changes.

## SI-MH-0101 — TRUST A2 DB proof verified
- G04-A2-LAB-01 16/16 DB_REAL_LAB PASS on PostgreSQL 16.16, A1 98/98 and browser PASS. Core job 138388097049: in_progress/PENDING at evidence publication; deterministic/real PostgreSQL suite step success. No runtime integration, original oracle promotion or LEARN edits. [Evidence](../work03b/G04_A2_LAB_01_VERIFIED_EVIDENCE.md).

## SI-MH-0102 — TRUST A2 LAB-02 active
- Prior full CI green. Signed synthetic identity to real RLS-protected payload read, existing A2 test directory/schema and isolated job only; 29 expected A2 tests. No runtime or LEARN changes; CI pending. No external MCP or production scope.

## SI-MH-0103 — TRUST research checkpoint
- LAB-02 verified all four jobs. Operator requested adversarial research; proposed SEC-R gate before further MCP implementation. Research/static hypotheses only; no runtime, CI, operational DB or LEARN edits. [Research register](../research/SI_MH_0103_TRUST_SECURITY_RESEARCH_ADVERSARIAL_PROGRAM.md). Await scope decision before expansion.

## SI-MH-0104 — TRUST independent research A reviewed
- Source audit and experiment contract proposed; SEC-R0/R1 partial, SR-F01/F02 NOT_RUN. No MCP expansion or runtime/LEARN changes. [Research audit](../research/SI_MH_0104_SEC_R_INDEPENDENT_RESEARCH_A_AUDIT.md). Await bounded synthetic test authorization.

## SI-MH-0105 — TRUST SEC-R2-X01 active
- Explicit operator approval for SR-F01/F02 only; test-only diagnostics on existing guarded disposable DB. Baseline unchanged, no fixes/MCP/LEARN. CI pending. [Protocol](../research/SI_MH_0105_SEC_R2_X01_EXPERIMENT_PROTOCOL.md).
