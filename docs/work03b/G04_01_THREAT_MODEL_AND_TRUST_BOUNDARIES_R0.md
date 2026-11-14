# G04-01 — Tenant isolation & privacy threat model R0

**2026-11-14 Africa/Maputo. STATE: DRAFT threat model, not a penetration test.** Scope: future G04, not proof of production vulnerability or exploitable public endpoint. Baseline code in commit 072f7f4a5922eab105dc2d063a376c9a8a7c974c.

## Trust boundaries

TB-01 Browser → gateway: spoofed bearer, forged tenant selection, CSRF/session theft.
TB-02 Service/agent → gateway: workload impersonation, credentials forwarded from tools/prompts.
TB-03 Gateway → PostgreSQL: overprivileged runtime DB role, broken resource-level authorization and unscoped joins.
TB-04 Gateway → Mem0: shared service key, caller-provided `user_id`, vector-store cross-scope leakage.
TB-05 Gateway → external source: arbitrary URL/SSRF, redirect/token exfiltration, stale consent and overbroad provider scope.
TB-06 Application → logs/backup/cache: personal-data duplication, key leakage and deletion resurrection.
TB-07 Tenant admin → support/platform ops: confused deputy, cross-tenant break-glass and unreviewed export.

## Threat register (LIKELIHOOD/IMPACT are preliminary judgment, NOT measured incidents)

| ID / priority | Attack path and precondition | Existing control verified | Required G04 mitigation | Test oracle |
|---|---|---|---|---|
| T01 P0 | Alter project ID to read another tenant's task | Current `_authorize` project grant | Validate org membership, resource ACL and RLS; no information leaks | G04-02,03 |
| T02 P0 | Reuse one global principal across organizations to elevate | Global principals and project grants | `(issuer,sub)` principal mapping; tenant-bound membership; negative cross-tenant combinations | G04-01,04 |
| T03 P0 | Forged/expired OIDC token, wrong issuer/audience, algorithm confusion | Local opaque bearer checks | Issuer/aud/JWKS/nonce/jti, PKCE + session replay controls | G04-05,06,07 |
| T04 P0 | SERVICE impersonates HUMAN policy approver or reviewer | G01 checks `principal_kind=HUMAN` on local bearer | Federated human identity, MFA/step-up and workload claims separation | G04-08,09 |
| T05 P0 | Shared Mem0 backend key used with another `user_id` to read unrelated tenant | Namespace and gateway result-check, but shared key in Mem0 shim | Credential scoped to tenant/context or trusted per-tenant proxy; server-enforced authorization + isolated collections | G04-10,11 |
| T06 P0 | Private repo URL with overbroad secret or stale source consent | R2 public pinned source only | Provider installation allowlist, org source grant and purpose/expiry/revocation transaction gates | G04-12,13 |
| T07 P0 | Hostname/redirect tricks/metadata IP SSRF via provider integration | Bounded G03 GitHub verification | Locked source adapters, DNS+IP at connect, redirect blocking and egress policy | G04-14,15 |
| T08 P0 | Deleted memory survives in embedding index, cache or restored backups | No production deletion contract | End-to-end deletion graph and restore-then-redelete process; auditable completion | G04-16,17 |
| T09 P0 | Runtime DB user bypasses logical tenant check via SQL or insecure join | Project predicates but no RLS | Composite tenant FK, forced RLS under least-privileged DB roles | G04-18,19 |
| T10 P1 | Approval/revocation races with slow provider or policy cache | G01 task-row lock under synthetic lab | Tenant-scoped generations, cache invalidation and revocation SLA | G04-20 |
| T11 P1 | Rate-limit bypass exhausting embedding provider, tokens or database | Request bounds exist, no systemic limits | per-tenant/actor/source budgets and retry policies, overload fail closed | G04-21 |
| T12 P1 | Log, crash dump, traceback leaks API bearer or source token | Some redaction implemented in R2 | structured sensitive-field filtering, no raw body, DLP and retention audit | G04-22 |
| T13 P1 | Uncontrolled operator break-glass bypasses tenant ACL | Offline token admin, no prod break-glass model | dual approval, short-lived emergency scope, immutable justified audit | G04-23 |
| T14 P1 | Unknown backup residency/retention, no tested production RPO/RTO | G01 synthetic logical restore | per-client data location/retention decisions and encrypted PITR restore drills | G04-24 |
| T15 P1 | GitHub `develop` modified without required review | `develop` branch currently `protected=false` | protected develop/main, CODEOWNERS, required CI, no force push, separated publish duty | G04-25 |
| T16 P1 | Agent/tool reply promotes unverified claim to approval/DONE | R2 state separation and UNVERIFIED Mem0 | preserve two-person review and server-driven state machine across tenant ops | G04-26 |
| T17 P1 | Tenant export includes another org or unauthorized field | Project grants only, no field-level export model | projection authorization, redaction and signed export manifest | G04-27 |
| T18 P1 | Credential revoked but app session/cache remains authorized | DB checks current local opaque token | session/workload generations, revocation propagation and max stale time | G04-28 |

## STRIDE and abuse-case interpretations

- **Spoofing:** forged tenant identity, stolen bearer, fake workload credentials (T02–T05, T18).
- **Tampering:** changed project/resource pointer, replayed policy or source grant; protected by DB-generated authorization context and journal fencing (T01, T06, T10).
- **Repudiation:** operator override or stale service issuance without auditable issuer, jti and actor claim (T13).
- **Information disclosure:** cross-tenant context, Mem0 search, export, logs and backup resurrection (T01, T05, T08, T12, T14, T17).
- **Denial of service:** unbounded embedding requests/provider abuse (T11).
- **Elevation of privilege:** service-to-HUMAN approver, project-only vs resource authority, DB bypass (T04, T09).

## Negative-first assumptions

Do not conclude the listed threats are public exploits: the relevant current G01 routes and Mem0 shim are lab-only or internal, and the source code was reviewed without external authenticated vulnerability scanning. Mark each P0 as an **unmitigated design gate**, not a demonstrated breach.

## Measurable exit requirements for design

Every P0 threat must have an accountable owner, a server-side enforcement boundary, a negative acceptance test, and telemetry plus failure-mode semantics. A passing test on a mocked provider never proves private-source permission. Threat decisions must be re-evaluated if deployment, IDP, tenant model or data processor changes.

**No release, migrations, API exposure, customer data, review/DONE, or assumed legal compliance is authorized here.**
