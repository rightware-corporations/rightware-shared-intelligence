# Jarvis production compatibility guardrails

**Status:** interface plan only. No Jarvis code changes in this branch.

## Contract for first opt-in pilot
- Integrate via the public RIGHTWARE REST API, or a client-specific stdio MCP bridge with a read-only project token. Never import server-side database modules directly into Jarvis's process.
- Jarvis must still start and operate with no Shared Intelligence endpoint configured.
- Default configuration: \`shared_intelligence.enabled=false\`.
- Read-only methods only; no automated \`create_task\`, \`accept_handoff\`, \`approve\`, \`delete_memory\` or privileged actions.
- If the service is unreachable/slow, return an explicit "shared context unavailable" signal and continue safely using local memory. Do **not** invent remote state.
- Timeouts bounded, retries capped, no secret logging. A failure from Shared Intelligence must not cause a Qwen/Ollama or voice-service startup failure.
- Shared records are **not** personal memories; do not ingest personal conversations or identifiers without informed consent and scoped permissions.
- Verify exact Python/OpenJarvis pin and Windows environment before changing any Jarvis launcher. That verification is outside WORK-02B.
- Rollout: isolated fake → API integration → dedicated non-production Jarvis staging → opt-in read-only pilot → explicit human approval for production integration.

## Before changing Jarvis
1. Confirm the active production repo/ref/deployment and backup/rollback procedure.
2. Review WORK-02B authentication and authorization controls, close blockers.
3. Run deterministic failure modes: service down, timeout, 401, 403, stale context and network disconnection.
4. Establish security testing around memory poisoning and cross-project retrieval.
5. Do not change Jarvis production or OpenJarvis upstream pin without separate authorization.
