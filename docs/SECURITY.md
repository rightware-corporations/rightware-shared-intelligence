# Security gates

NOT production ready. This public repository intentionally contains no keys, personal histories, or private project memory.

- Never pass user-supplied project IDs straight to the shared Mem0 admin key. A future API MUST derive organization/project from the authenticated identity and enforce authorization.
- Memory is untrusted data. Treat model-written accomplishments as unverified claims and use independent evidence verification.
- Keep all LLM/embedding credentials out of git; opt out of telemetry where required.
- Use TLS for remote hosts, explicit allowlists for outbound HTTP, credential rotation, rate limits, audit logs, backups, and data retention.
- Never expose a local Mem0 port or database directly to the public internet.
- A future MCP server must validate tool schemas and authorizations at execution boundary.
- Do not import user personal memory into organizational memory without affirmative consent and defined access rights.
