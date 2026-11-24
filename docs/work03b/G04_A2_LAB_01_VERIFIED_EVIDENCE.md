# SI-MH-0101 — G04-A2-LAB-01 verified PostgreSQL evidence

**2026-11-24 Africa/Maputo.** Evidence source: implementation commit `958c486d59a9524250eade6856a6840bcd22d840`, [CI 45377653608](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45377653608). Classification VERIFIED DB_REAL_LAB, not production or original formal G04 oracle promotion. Operator authorization SI-MH-0099 remains bounded.

## Executed evidence
- [A2 job 138388097032](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/45377653608/job/138388097032) completed/success. G04_A2_GUARD_PASS postgres_version_num=160016 (PostgreSQL 16.16). All sixteen named test families ok, 16 tests in 0.707s, OK. Start, test and teardown steps success; teardown command tolerates stop failure, independent container-removal attestation not claimed.
- A1 job 138388096723 completed/success: Ran 98 tests in 0.811s, OK.
- Browser job 138388097289 completed/success: E1_04_BROWSER_SMOKE_PASS synthetic_only=true actual_humans=0 submitted=0 adjudicated=0 operator_dispatch=false science_gate=REVIEW_REQUIRED.
- Core job 138388097049: in_progress/PENDING at evidence publication; deterministic/real PostgreSQL suite step success.

## Acceptance coverage (exact lab scope)
| ID | Actual scenario | Result |
|---|---|---|
| A2-01 | Distinct issuer/subject rows and duplicate insert rejected | PASS |
| A2-02 | Active org/project and resource/purpose grants return exact expected IDs | PASS |
| A2-03 | Foreign B/C projects, hidden same-org project and conflicting scope return zero | PASS |
| A2-04 | Missing object ACL returns zero | PASS |
| A2-05 | Broad SELECT returns authorized IDs; catalog ENABLE/FORCE flags; owner with bootstrap session_user sees zero | PASS |
| A2-06 | Read-only service update affects zero rows; allowed synthetic body update succeeds and fixture restored | PASS |
| A2-07 | Column privilege denial and separately probed WITH CHECK deny changed org/project/owner; temporary grants revoked | PASS |
| A2-08 | Composite FK denies inconsistent payload and membership | PASS |
| A2-09 | Absent, malformed and wrong-purpose context returns zero | PASS |
| A2-10 | Caller GUC cannot impersonate; SET ROLE/session authorization and disabling row_security denied | PASS |
| A2-11 | Restricted role attributes, no role membership, metadata/DDL/TRUNCATE/temp denied | PASS |
| A2-12 | Inactive/expired membership or grant prevents target task read in fresh transaction | PASS |
| A2-13 | Transaction-local context cleared after commit/rollback | PASS |
| A2-14 | Concurrent direct-login connections return exact separate fixture IDs | PASS |
| A2-15 | Approval predicate false, delete/invalid action denied | PASS |
| A2-16 | Foreign update affects zero rows; failed local mutation leaves baseline unchanged | PASS |

## Regression and boundaries
Verified commit diff: no existing migrations or backend runtime modified. Prior three CI jobs preserved verbatim (apart from final whitespace before appended job); nine implementation files only. Evidence commit documentation-only. No real account federation, consent, production gateway, pooler hygiene under arbitrary session-level changes, cluster-wide isolation, in-flight revocation linearizability, idempotent replay race or independent human review claimed. A2-01 duplicate insert demonstrates uniqueness failure, not a constraint-specific diagnostic assertion. A2-12 checks the target task, not exhaustive affected rows. Role-per-principal is a laboratory design; no production adoption. Original 28 G04 oracles remain unchanged; E1_DATA_READY REVIEW_REQUIRED. LEARN untouched. Next: verify any pending full Core workflow, then propose a separately bounded integration contract connecting real signed synthetic identity to DB-protected resource access (no direct operational migrations/remote MCP without approval). No new implementation in this evidence commit. Its own CI pending on publication; do not recursively commit documentation-only CI confirmations.
