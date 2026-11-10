# Decision Register and Architecture Questions — WORK-01

## 1. Decision classification
This document does **not** convert discussion into company-wide approval.

| ID | Position | Classification | Status |
|---|---|---|---|
| SI-001 | Shared Intelligence remains independent of Jarvis/PULSE | STRATEGIC DIRECTION discussed with user | Recommended; architecture proposed |
| SI-002 | Mem0 is pinned as evaluation upstream component | IMPLEMENTED EXPERIMENT (WORK-00) | Technical baseline only |
| SI-003 | Operational PostgreSQL state is authoritative; Mem0 is contextual projection | ARCHITECTURE RECOMMENDATION | Needs formal approval |
| SI-004 | Python modular monolith initially; REST+MCP interfaces | ARCHITECTURE RECOMMENDATION | Needs technical validation |
| SI-005 | n8n remains optional orchestration / integration | ARCHITECTURE RECOMMENDATION | Needs functional validation |
| SI-006 | Handoff and task completion require independent authority/evidence | SAFETY/QUALITY REQUIREMENT PROPOSAL | To ratify in security review |
| SI-007 | No generic LLM tools may approve decisions in MVP | SECURITY RECOMMENDATION | To ratify in permissions policy |
| SI-008 | WORK-01 authoring is documentation-only, with isolated review branch | CURRENT WORK AUTHORIZATION | Proceed with docs, no runtime/deployment/merge |
| SI-009 | Jarvis/PULSE integrations are deferred until MVP gates | EXECUTION RECOMMENDATION | Not integrated |

## 2. Decisions the operator should review before WORK-02
1. **Pilot identity:** one organization/two projects, human reviewer, and two agent service identities — sufficient initial policy realism?
2. **Scope:** should task/handoff management be a first-class feature, or should Shared Intelligence initially only expose continuity records while PULSE retains all task management?
3. **Source-of-truth ownership:** can a standalone Shared Intelligence create tasks, or should external projects own them and publish only verified events?
4. **Memory provider:** Mem0 as dependency or future fork? Must be evaluated after real self-hosted tests.
5. **Storage:** single PostgreSQL instance with separate schemas vs independent Mem0/operational instances.
6. **Model costs:** approved local LLM/embedding solution, CPU/GPU budget, provider and licensing constraints.
7. **MCP:** read-only first or limited writes from day one? Which exact clients and protocol version to validate?
8. **Evidence:** minimum trustworthy verifier (GitHub read-only pinned commit/CI, then reproducible test metadata).
9. **Data privacy:** categories, retention, erasure, backups, consent and public/private repository policy.
10. **Go-to-market:** internal developer teams as pilot vs enterprise operational intelligence as first paying segment.

## 3. Trade-off assessment
- A **memory-only API** is fastest but weak at authoritative handoff, and overlaps heavily with existing products.
- A **full task platform** differentiates operationally but risks duplication with PULSE/Jira and scope explosion.
- **Recommended middle path:** minimum task/handoff/event domain sufficient for verified continuation; external systems remain authoritative for their separate domain-specific entities.

## 4. Proposed next gate
WORK-02 should not begin as a broad build-out. Start with a **thin deterministic transactional task/handoff slice**, explicit tenant policy, and replayable acceptance tests, then connect Mem0 as a derived memory provider.

User must explicitly approve architectural recommendations before labeling them OFFICIAL DECISIONS. Documentation review and targeted experiments may proceed independently without claiming business approval.
