# Database — authoritative operational state

All RIGHTWARE-owned migrations live in `database/migrations/`, in numeric order:

1. `0001_work02_core.sql` — identity/grants, task state/leases/handoffs/events/idempotency.
2. `0002_work02b_api_credentials.sql` — experimental API token hash, expiry and revocation.
3. `0003_work02d_scrub_lease_replays.sql` — scrub legacy replayable lease secret fields.
4. `0004_work03b_r1a_continuity.sql` — task-bound AgentRun, SourceRecord, Observation, associations, continuation event stream.
5. `0005_work03b_r1b_checkpoints.sql` — immutable task checkpoints and same-task Observation bindings; database triggers, independent checkpoint sequence and checkpoint event.
6. `0006_work03b_r1c_handoff_fencing.sql` — exact checkpoint ID/seq/task version binding for new checkpointed task handoffs, FK/immutability guard and persistent per-task lease generation fence; holder-rekey audit event.

7. `0007_work03b_r2_r1b_verification_ledger.sql` — immutable evidence policies, append-only verification attempts, project/task/evidence FKs, simulated vs real observation provenance and EVIDENCE_CHECKED continuity events. Internal laboratory only; no review/DONE or public verifier API.

`database/` owns RIGHTWARE operational schema; the vendored Mem0 library controls its own memory index/schema and is **not** allowed to rewrite RIGHTWARE task state.

**Lab setup:** PostgreSQL 16 `rw_test` (disposable operational DB) and a separate PostgreSQL 17/pgvector Mem0 DB. Production schema ownership and deployment migration tooling remain undecided. Never run tests/migrations against Jarvis, PULSE, customer or production databases.

Real tested invocation is in `.github/workflows/ci.yml`. Historical migration paths in WORK-02A/B/C/D documents describe the tree at those historical commits.
