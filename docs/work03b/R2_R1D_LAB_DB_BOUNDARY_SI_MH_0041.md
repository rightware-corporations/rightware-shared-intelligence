# SI-MH-0041 — Hardened disposable PostgreSQL LAB guard

**2026-11-13 Africa/Maputo. STATE: LAB CODE IMPLEMENTED, CI PENDING; G01 STILL NOT RATIFIED.**

## Source-backed starting point

Verified `develop@099b5e9d405bb16660a2b565bf221db33e689638`; [Actions 43259970366](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43259970366) SUCCESS, `Ran 174 tests in 24.945s / OK`; PostgreSQL migrations 0001..0007, GitHub HTTPS LIVE via R1D REST TestClient and all R1A/R1B/R1C/Mem0/Ollama regressions passed.

## Security issue and scope

Existing R2 R1C experimental FastAPI and four CI scripts check parsed URI host=localhost, port=5432, database=/rw_test. PostgreSQL libpq can override network destination via query `hostaddr` or `PGHOSTADDR` environment. These scripts execute `TRUNCATE` of synthetic tables, so a misleading URI is unsafe.

New `backend/rightware_si/lab_boundary.py` implements a shared fail-closed preflight. It rejects URL query/fragment, remote host/port/database, absent or wrong requested username, nonloopback resolution for `localhost`, and `PGHOSTADDR`/`PGSERVICE`/`PGSERVICEFILE` environment indirection. Applied to R2 R1C opt-in API and four synthetic destructive scripts: R2 R1B LIVE, R2 R1D G03 LIVE, R1C agents A/B, WORK02D Mem0/MCP. Does not change production endpoints or main.

New `tests/test_lab_db_boundary.py` contains 16 pure positive/negative tests including URI query/env hostaddr bypass and FastAPI fail-closed. **190 tests expected (174+16), not validated until new Actions run.** No new migrations/dependencies, no private data or secrets; the R2 endpoint remains disabled by default.

**Limit:** this is a configuration safety check, not a sandbox against compromised host/container or administrators. CI still must be isolated from production networks. G01 activation/expiry/disable, G04 identity/privacy, G05 release and reviewer/DONE remain NOT IMPLEMENTED/NOT RATIFIED. Do not claim these from this patch.

NEXT: verify 190/190 and all GitHub LIVE, R1C and Mem0/Ollama steps; if failure append correction SI-MH-0042 with actual logs.
