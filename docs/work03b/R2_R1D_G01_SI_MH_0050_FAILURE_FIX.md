# SI-MH-0050 — R2 R1D G01 CI failure investigation and targeted repair

**2026-11-14 Africa/Maputo. Base `develop@4b1d9eff569b0d108dd8e1c6fd3a7589619f1b20`. State: CORRECTION COMMITTED / NEW CI PENDING.**

## Prior failure verified

[Actions 43602331541](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43602331541), SI-MH-0049, **FAILED**. Eight PostgreSQL migrations 0001..0008 PASS. `Ran 202 tests in 23.121s`, **FAILED (failures=1, errors=1)**. All other G01 integration tests (7/8) passed; baseline suite tests outside these failures passed.

1. `test_05_disable_is_terminal_and_preserves_history`: the connection uses `psycopg.rows.dict_row`; a `count(*)` result is a dict, so positional `fetchone()[0]` raised `KeyError: 0`. Fixed by `AS n` and `fetchone()["n"]`. This was a **test-code issue**, not PostgreSQL inability to disable a policy.
2. `test_repository_layout.test_authoritative_sql_migrations_are_under_database`: static migration allowlist omitted the new actual 0008 migration. Included 0008, preserving the check for unauthorized schema files.

**No changes** to schema, runtime policy semantics, CI workflow, permissions, production, main, JARVIS/PULSE, or pinned Mem0. Existing G01 lab policy remains OFF by default; provider ledger enforcement and LIVE through policy are still separate next steps, not yet done. This checkpoint only repairs the two demonstrated failures; await its own CI before any PASS claim. Both HANDOFF docs updated in the same commit.
