# WORK-01 — Domain, Lifecycle & Architecture

**Project:** RIGHTWARE Shared Intelligence  
**Date:** 2026-11-10  
**Status:** PROPOSAL FOR REVIEW — specification only. **Not an approved architecture, production implementation, or deployed service.**

## Objective
Define a model-independent, integrable system for **shared contextual memory**, **operational continuity**, and **verified cooperation** between separately authorized agents and applications.

The project must remain independent of Jarvis, PULSE, Claude, ChatGPT, n8n, and the Mem0 implementation.

## Canonical reading order
1. [PRODUCT_VISION.md](PRODUCT_VISION.md) — problem, customer, product boundaries.
2. [DOMAIN_MODEL.md](DOMAIN_MODEL.md) — entities, invariants, ownership.
3. [TASK_LIFECYCLE.md](TASK_LIFECYCLE.md) — state machine, authority, handoffs.
4. [ARCHITECTURE_V1.md](ARCHITECTURE_V1.md) — architecture and failure semantics.
5. [API_MCP_CONTRACT.md](API_MCP_CONTRACT.md) — proposed REST/MCP contract.
6. [SECURITY_MODEL.md](SECURITY_MODEL.md) — tenancy, model trust and data controls.
7. [MVP_ACCEPTANCE.md](MVP_ACCEPTANCE.md) — falsifiable acceptance matrix.
8. [DECISIONS_AND_OPEN_QUESTIONS.md](DECISIONS_AND_OPEN_QUESTIONS.md) — undecided items and review gates.

## Context from WORK-00
- `vendor/mem0`: unmodified submodule pinned to `f1791daa86d469249c9b002f62644d58a1eb96a0`, Apache-2.0.
- `rightware_si/memory.py`: experimental Python REST adapter for **trusted callers only**; `rw:org:project` is a *namespace convention, not an authorization control*.
- Upstream Mem0 / PostgreSQL / MCP / Ollama / Jarvis integration **has not been verified** end to end.
- Deterministic tests use a FAKE transport. See `docs/WORK00_AUDIT.md`.
- Existing WORK-00 Draft PR remains separate and must not be merged automatically.

## Change policy
This work contains only written specifications. It must not modify Jarvis/PULSE, change the Mem0 pin, publish private memories, deploy services, invoke paid LLM APIs, merge any branch, or claim acceptance. Domain choices in these files are recommendations until explicitly reviewed and approved.

## Design thesis
**Mem0 indexes and retrieves contextual memory; RIGHTWARE owns authoritative operational state, access policy, source-linked evidence, and cross-agent handoff semantics.** A model claim never becomes an approved decision or verified task merely because it was stored as memory.
