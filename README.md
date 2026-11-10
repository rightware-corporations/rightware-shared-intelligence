# RIGHTWARE Shared Intelligence

Independent, model-agnostic memory and handoff infrastructure for authorized AI agents and applications.

> **Status:** WORK-00 experimental foundation; not production-ready. No Jarvis/PULSE integration has been deployed.

## Architecture direction

- **Upstream engine:** Mem0 (Apache-2.0), pinned as a Git submodule under `vendor/mem0`. This keeps the original code, history and license at its source.
- **RIGHTWARE-owned layer:** interfaces and validation for project-scoped memory, verified handoffs, and future REST/MCP adapters.
- **Consumers:** Jarvis, PULSE, n8n and other applications, each with explicit authorization.

Do not connect external models or personal/project data until auth, tenant isolation, retention and memory extraction configuration are validated.

Read `docs/ARCHITECTURE.md` and `docs/UPSTREAM_PROVENANCE.md` for the implementation boundaries.

Clone after the upstream link is added:

```sh
git clone --recurse-submodules https://github.com/rightware-corporations/rightware-shared-intelligence.git
```

Maintainer: RIGHTWARE. Mem0 is an independent upstream project; RIGHTWARE does not claim its original code.
