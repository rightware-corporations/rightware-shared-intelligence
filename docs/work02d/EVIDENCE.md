# WORK-02D Evidence Ledger

Status: awaiting actual CI execution. Never assert a PASS before observing a completed workflow.

Target: real PostgreSQL16 schema migrations 0001-0003, lease-token persistence/retry regression, full MCP stdio subprocess -> authenticated REST -> project authorization -> real Mem0 OSS -> Ollama embeddings -> PostgreSQL17 pgvector.
Test scenarios: authorized Alpha retrieval, deny Beta and intruder, revoke token, authoritative task DRAFT read, UNVERIFIED trust label.
Environment: ephemeral GitHub runner, synthetic data, local model download, no paid inference, no Jarvis modifications.

Known gaps: lost lease-token response recovery, production identity, rate limits, HTTPS deployment, memory deletion/retention, independent security review, Jarvis staging.
