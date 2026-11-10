# Product Vision — RIGHTWARE Shared Intelligence (WORK-01)

**Status: STRATEGIC PROPOSAL, not an official product approval.**

## 1. Problem
Information and state are fragmented across AI clients, local agents, project-management systems, repositories and automation tools. Human operators repeatedly copy handoff documents, reconstruct previous decisions, and reconcile inconsistent status claims. Generic conversational memory alone does not provide reliable multi-agent task continuation.

## 2. Proposed solution
A model-agnostic, independently deployable **shared intelligence service** that exposes:
1. **Context** — query and persist scoped, provenance-aware contextual knowledge.
2. **Continuity** — structured tasks, leases, handoffs and resume snapshots.
3. **Trust** — separate assertions, verified evidence and authorized decisions.
4. **Interoperability** — REST plus MCP interfaces; future SDKs/webhooks.

The product does **not** require a unified chat frontend, a paid external LLM, or n8n for its core functionality.

## 3. Initial user/job
Primary first-user hypothesis: an operator coordinating different coding agents on one software project who needs to resume safely from an earlier implementation. Secondary hypotheses: internal AI-enhanced work platforms (PULSE), personal assistants (Jarvis), workflow automation (n8n), external B2B applications.

These are customer hypotheses, not validated demand or approved commercial segmentation.

## 4. Example, explicitly synthetic
- Agent A receives a task to implement an isolated feature, reads authorized context, starts with a leased task claim.
- Agent A submits a result referencing an immutable Git commit and CI run.
- A trusted verifier examines the evidence; task remains IN_REVIEW until acceptance.
- Agent A offers a handoff; Agent B accepts it and obtains a scoped context snapshot plus outstanding requirements.
- No agent can update tasks in another project or approve its own results unless an explicit authorization policy grants that capability.

## 5. What makes the product distinct (hypothesis to test)
- Deterministic, auditable operational state alongside probabilistic semantic retrieval.
- Source-linked evidence and a distinction between agent assertions and verified outcomes.
- Handoff lifecycle, version-controlled ownership and recoverable context across client types.
- Multi-tenant policy enforced on the server, never delegated to LLM prompts.

Mem0, Letta, LangGraph, Graphiti and other tools already solve overlapping problems. The presence of a sustainable market gap remains **unvalidated**.

## 6. Out of scope for MVP
- Training foundation models; a five-model chat interface; autonomous unrestricted execution.
- Full Jira/Notion replacement; browser/Windows control; always-on monitoring.
- Automatic synchronization of private memories from vendor-controlled ChatGPT/Claude apps.
- Real customer data, private business documents, or ingestion without consent.
- Agent-written "approved" decisions, unaudited external writes, or unrestricted tools.
- Kubernetes, distributed microservices, complex graph-RAG and embedding benchmarks before a deterministic baseline.

## 7. Strategic guardrails
- Python-first integration, but no Python-only client lock-in.
- Keep the Mem0 memory provider replaceable behind an adapter.
- PostgreSQL is the operational source of truth; memory index is derived.
- Dependence on the Mem0 cloud service or external paid model APIs is not mandatory by design; zero-cost local execution remains to be proven.
- Pilot internally with synthetic records before any Jarvis/PULSE integration or B2B release.

## 8. Success hypothesis
Two independently running authorized clients on the same project can create a task, exchange an evidence-backed handoff, read the correct continuation context, detect conflicting updates, and remain isolated from a second project. Human review should be able to reconstruct who asserted, verified and accepted each change.
