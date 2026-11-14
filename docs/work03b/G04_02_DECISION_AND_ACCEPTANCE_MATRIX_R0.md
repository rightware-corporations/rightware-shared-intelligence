# G04-02 — Decisions, authorization matrix and acceptance contract R0

**2026-11-14 Africa/Maputo. STATUS: OPEN RECOMMENDATIONS; NOT OFFICIAL DECISIONS.** No defaults authorize storing private customer data. Approval is required before G04 code, migrations, staging, external IdP or customer access.

## A. Operator decision register (each explicit choice remains OPEN)

| ID | Required choice | Recommendation | Decision status |
|---|---|---|---|
| D01 | First tenant/workload pilot | One RIGHTWARE internal synthetic organization; two fake orgs for isolation tests; no customer data | OPEN |
| D02 | HUMAN identity provider | Standards-based OIDC code+PKCE with issuer allowlist and MFA; provider selection based on hosting/compliance/cost | OPEN |
| D03 | SERVICE / AGENT identity | Short-lived asymmetric workload credentials, narrow audience, rotation/revocation; compare OIDC federation vs mTLS on deployment platform | OPEN |
| D04 | Tenant principal/membership architecture | Opaque internal principal ID from `(issuer, sub)`; explicit tenant/project membership and context; no path-derived authority | OPEN |
| D05 | Authorization model | Project grants plus per-resource ACL/ABAC/consent; deny-by-default; commit-time recheck and DB RLS defense in depth | OPEN |
| D06 | Support/platform admin privileges | No blanket tenant read; scoped break-glass, dual approval, short duration and visible audit | OPEN |
| D07 | Private source connector scope | Start with public GitHub evidence only; private installation/scopes/consent require separately approved adapter | OPEN |
| D08 | Memory data segregation | Decide separate collections/DBs vs authenticated shared partition; server-controlled Mem0 scope; authorize before and after provider | OPEN |
| D09 | Categories, legal basis, data residency | Tenant and category-level processing register, controller/processor roles, local legal review for intended markets | OPEN |
| D10 | Retention and deletion | Approve each period, purge semantics, backup exception, minimal immutable audit; do not silently adopt arbitrary days | OPEN |
| D11 | Encryption/secret/key management | KMS/Vault, per-tenant envelope or other approved keying, rotation/residency, signed audit/export manifest | OPEN |
| D12 | Release/staging protections | Branch protection, security scanning/SAST, independent reviewers, tenant isolation tests, simulated incident/restore, G05 change approval | OPEN |

## B. Role and resource action matrix (proposed, NOT deployed)

Key: `A` may act only after membership+resource+purpose+consent validation; `D` denied; `C` conditional explicitly approved break-glass. Project permission alone never substitutes for resource authorization.

| Actor type | Task read/write | Approve G01 policy | Verify evidence | Private source ingest | Semantic memory read | Export/delete tenant data |
|---|---|---|---|---|---|---|
| Tenant HUMAN contributor | A / assigned resource | D | D | D unless explicit source-grant | A if resource-scoped | D |
| Tenant HUMAN policy proposer | A / scoped | D for own proposal | D | D | A if scoped | D |
| Independent HUMAN policy approver | A / scoped | A for another author's policy | D | D | A if scoped | D |
| Independent SERVICE verifier | A / read-only scoped | D | A for activated policy and allowed source | D except bounded provider verifier | D by default | D |
| AGENT executor | A / assigned workflow | D | D | D unless job-specific short grant | A only in authorized project | D |
| Tenant HUMAN reviewer | A / assigned review | D | D | D | A if scoped | D |
| Tenant administrator | A / tenant policy | D by default | D | C with delegated source-owner consent | A if allowed | C under privacy workflow |
| Privacy operator | D unless case-scoped | D | D | D | D by default | C with case/audit |
| RIGHTWARE platform operator | D by default | D | D | D | D | C on audited break-glass, not automatic |
| External connector SERVICE | D except receipt | D | D | C for approved source pull only | D | D |

## C. Required invariants to freeze before implementation

1. A path/header/query tenant or project identifier is a *requested* scope, never a trusted identity.
2. All authority derives from verified identity plus DB active membership, resource owner/scope, consent, purpose, action and expiry.
3. Missing/conflicting/outdated membership or consent fails closed on both reads and mutations; 404 vs 403 response policy must minimize enumeration.
4. Identity and grants are rechecked after slow external calls, on idempotent replay, after restore and on tenant switch.
5. SERVICE and AGENT cannot assert or inherit HUMAN reviewer/policy approver status; no task DONE from evidence CHECKED_PASS.
6. No private GitHub/source content or secret reaches Mem0, prompts, logs, CI or export by default.
7. Each memory result is bound to validated org/project and to source resource ACL; UNVERIFIED remains UNVERIFIED.
8. Deletion applies to payloads, embeddings, caches and exports; restore process honors tombstones/deletion ledger and approved audit retention.
9. Fail closed on IdP/JWKS/revocation/consent-store outage for privileged/secret operations. Determine safe degraded read behavior separately.
10. Data residence, retention durations, legal bases and permitted processors are explicit, versioned business/legal decisions, not guessed constants.
11. Emergency support access is temporary, justified, independently approved, notified and immutable-audited; default service operators have no tenant read.
12. Staging uses synthetic data and separate credentials, DBs, KMS and networks. No change to production/main without separate G05 signoff.

## D. Test / evidence contract

The machine-readable `fixtures/G04_ACCEPTANCE_ORACLES_R0.jsonl` contains 28 proposed tests. Each is labelled `NOT_IMPLEMENTED` and has a required execution level (`UNIT`, `DB_REAL`, `MULTIPROCESS`, `E2E_STAGING`, or `SECURITY_REVIEW`). This is a test inventory only, **not** a green test count. G01 still retains its independently verified **216/216 lab baseline**.

Core release blocking areas: exact token validation, identity-workload separation, tenant BOLA, project membership, RLS, Mem0 scope replay, source consent+SSRF, deletion/restore, rate limits, redaction, emergency access, branch protections and independent staging security review. Accept a gate only when execution logs, exact SHA, operator-reviewed evidence and recovery commands are recorded.

## E. Recommended approval order

**Decision packet A (first):** D01–D05 and D12 (pilot identity, tenant, authorization and repository security). Then **packet B:** D06–D08, D11 (support/source/memory/secrets). Then **packet C:** D09–D10 (legal/privacy classification and data lifecycle) with accountable legal/operational review. A staged prototype may begin *only* for explicitly approved synthetic internal scope. Do not interpret an informal 'vamos' as a production launch.

## F. References

- [RFC 9700 OAuth Security BCP](https://www.rfc-editor.org/rfc/rfc9700.html)
- [NIST SP 800-63-4](https://pages.nist.gov/800-63-4/)
- [OWASP API Top 10 (2023)](https://api-security.owasp.org/editions/2023/en/0x00-header/)
- [OIDC Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
