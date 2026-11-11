# Database — authoritative operational state

All RIGHTWARE-owned migrations live in `database/migrations/`, in numeric order:

1. `0001_work02_core.sql` — identity/grants, task state/leases/handoffs/events/idempotency.
2. `0002_work02b_api_credentials.sql` — experimental API token hash, expiry and revocation.
3. `0003_work02d_scrub_lease_replays.sql` — scrub legacy replayable lease secret fields.

`database/` owns RIGHTWARE operational schema; the vendored Mem0 library controls its own memory index/schema and is **not** allowed to rewrite RIGHTWARE task state.

**Lab setup:** PostgreSQL 16 `rw_test` (disposable operational DB) and a separate PostgreSQL 17/pgvector Mem0 DB. Production schema ownership and deployment migration tooling remain undecided. Never run tests/migrations against Jarvis, PULSE, customer or production databases.

Real tested invocation is in `.github/workflows/ci.yml`. Historical migration paths in WORK-02A/B/C/D documents describe the tree at those historical commits.
