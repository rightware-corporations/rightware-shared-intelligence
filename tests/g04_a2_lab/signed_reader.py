"""G04-A2-LAB-02: read-only synthetic identity -> real PostgreSQL proof.

This module lives only in the test laboratory. It accepts no DSN, role or
password from requests, exposes no network service and is not a runtime gateway.
Trusted bootstrap provisions the directory and per-principal connection factory.
"""
from dataclasses import dataclass, field
import os
from threading import Lock

from rightware_si.g04_a1_lab import SyntheticPrincipalResolver, ident, number

DENIED = "DENY_SYNTHETIC"
PURPOSES = ("syn-work","syn-audit")


@dataclass(frozen=True)
class ReadResult:
    status: str
    resource_id: str | None = field(default=None,repr=False)
    body: str | None = field(default=None,repr=False)


def enabled():
    return (os.getenv("GITHUB_ACTIONS")=="true"
            and os.getenv("RUNNER_ENVIRONMENT")=="github-hosted"
            and os.getenv("RW_SI_ENABLE_G04_A2_LAB")=="1"
            and os.getenv("RW_SI_ENABLE_G04_A1_LAB")=="1"
            and os.getenv("RW_SI_ENVIRONMENT")=="lab")


class SignedResourceReader:
    def __init__(self,key_snapshot,directory_snapshot,clock,login_by_principal,connect):
        if not enabled():
            raise RuntimeError("synthetic reader disabled")
        self._resolver=SyntheticPrincipalResolver(key_snapshot,directory_snapshot,clock)
        self._clock=clock
        self._roles=dict(login_by_principal)
        if (not self._roles or not all(ident(k) for k in self._roles)
                or not all(v in ("g04_alpha","g04_beta","g04_service") for v in self._roles.values())
                or len(set(self._roles.values()))!=len(self._roles)):
            raise RuntimeError("invalid synthetic provisioning")
        self._connect=connect
        self._lock=Lock()

    def read(self,token,kind,org,project,resource,purpose):
        try:
            with self._lock:
                if (not enabled() or kind not in ("AGENT","SERVICE")
                        or not all(ident(v) for v in (org,project,resource))
                        or purpose not in PURPOSES):
                    return ReadResult(DENIED)
                principal=self._resolver.resolve(token,kind)
                role=self._roles.get(principal.principal_id)
                if role is None:
                    return ReadResult(DENIED)
                # Fresh connection, no pooling or session reuse. Connector is
                # trusted fixture only, and the actual login is checked.
                with self._connect(role) as conn,conn.transaction():
                    conn.execute("SET TRANSACTION READ ONLY")
                    conn.execute("SET LOCAL statement_timeout='3000ms'")
                    conn.execute("SET LOCAL lock_timeout='1000ms'")
                    if conn.execute("SELECT session_user,current_user,current_database()").fetchone()!=(
                            role,role,"rw_g04_a2_lab"):
                        return ReadResult(DENIED)
                    for key,value in (("rw_g04.org",org),("rw_g04.project",project),
                                      ("rw_g04.purpose",purpose)):
                        conn.execute("SELECT set_config(%s,%s,true)",(key,value))
                    query=("SELECT resource_id,body FROM g04_lab.payload "
                           "WHERE resource_id=%s AND org_id=%s AND project_id=%s "
                           "AND g04_lab.bound_identity(%s,%s,%s,%s)")
                    args=(resource,org,project,principal.issuer,principal.subject,
                          principal.principal_id,principal.kind)
                    first=conn.execute(query,args).fetchall()
                    if len(first)!=1:
                        return ReadResult(DENIED)
                    fresh=self._resolver.resolve(token,kind)
                    if (fresh.principal_id,fresh.issuer,fresh.subject,fresh.kind)!=(
                            principal.principal_id,principal.issuer,principal.subject,principal.kind):
                        return ReadResult(DENIED)
                    # READ COMMITTED: second statement rechecks persisted
                    # identity/membership/grants and payload after verification.
                    second=conn.execute(query,args).fetchall()
                    end=self._clock()
                    if (second!=first or not number(end)
                            or end>=min(principal.expires_at,fresh.expires_at)
                            or not enabled()):
                        return ReadResult(DENIED)
                    result=ReadResult("ALLOW_SYNTHETIC_READ",second[0][0],second[0][1])
                return result
        except Exception:
            # No returned exception details, tokens, credentials or partial rows.
            return ReadResult(DENIED)
