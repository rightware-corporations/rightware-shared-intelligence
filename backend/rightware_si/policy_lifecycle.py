"""Internal G01 lab policy lifecycle. No public API, no production authority.

Admin uses real bearer credentials resolved again within each transaction.
All writes lock the same task row used by the verification ledger.
"""
from __future__ import annotations
import hashlib
import os
from uuid import UUID, uuid4
import psycopg
from psycopg.rows import dict_row
from rightware_si.core.postgres import WorkCore, AccessDenied, Conflict, Missing, _key, _valid_id
from rightware_si.lab_boundary import require_disposable_postgres

FLAG = "RW_SI_ENABLE_R2_G01_LAB_POLICY"

def pilot_enabled(dsn: str) -> bool:
    if os.environ.get(FLAG) != "1":
        return False
    if os.environ.get("RW_SI_ENVIRONMENT") != "lab" or os.environ.get("RW_SI_ENABLE_R2_R1C_LAB_API") != "1":
        raise RuntimeError("G01 requires both explicit LAB and R1C flags")
    require_disposable_postgres(dsn, expected_user="rw")
    return True

def _uuid(x: str) -> str:
    try:
        return str(UUID(str(x)))
    except (ValueError, TypeError, AttributeError):
        raise ValueError("invalid policy identifier") from None

class PolicyLifecycle:
    def __init__(self, dsn: str):
        if not pilot_enabled(dsn):
            raise RuntimeError("G01 internal pilot disabled")
        self.dsn=dsn

    @staticmethod
    def _bearer_human(conn, project, token, permission):
        if not isinstance(token,str) or not token.startswith("rwsi_"):
            raise AccessDenied("invalid bearer")
        digest=hashlib.sha256(token.encode("utf-8")).hexdigest()
        actor=conn.execute(
            "SELECT p.id,p.principal_kind FROM si_api_tokens t "
            "JOIN si_principals p ON p.id=t.principal_id "
            "WHERE t.secret_sha256=%s AND t.revoked_at IS NULL "
            "AND t.expires_at>clock_timestamp()", (digest,)).fetchone()
        if not actor or actor["principal_kind"]!="HUMAN":
            raise AccessDenied("authenticated HUMAN required")
        WorkCore._authorize(conn,project,actor["id"],permission)
        return actor["id"]

    @staticmethod
    def _locked_policy(conn, project, policy_id):
        task=conn.execute(
            "SELECT id FROM si_tasks WHERE project_id=%s AND id=("
            "SELECT task_id FROM si_evidence_verification_policies "
            "WHERE project_id=%s AND id=%s::uuid) FOR UPDATE",
            (project,project,policy_id)).fetchone()
        if not task:
            raise Missing("policy task not found in project")
        policy=conn.execute(
            "SELECT * FROM si_evidence_verification_policies "
            "WHERE project_id=%s AND id=%s::uuid AND task_id=%s::uuid",
            (project,policy_id,task["id"])).fetchone()
        if not policy:
            raise Missing("policy not found")
        return policy

    @staticmethod
    def _events(conn, project, policy_id):
        return conn.execute(
            "SELECT * FROM si_policy_lifecycle_events "
            "WHERE project_id=%s AND policy_id=%s::uuid ORDER BY sequence",
            (project,policy_id)).fetchall()

    @staticmethod
    def require_active(conn, project, policy_id):
        ev=PolicyLifecycle._events(conn,project,policy_id)
        approved=next((x for x in ev if x["event_type"]=="ACTIVATED"),None)
        if approved is None or any(x["event_type"] in ("DISABLED","SUPERSEDED") for x in ev):
            raise Conflict("policy inactive or revoked")
        current=conn.execute("SELECT clock_timestamp() AS now").fetchone()["now"]
        if approved["valid_until"]<=current:
            raise Conflict("policy expired")

    def _write(self,project,token,policy_id,idem,event,expected_sequence,
               *,reason=None,successor=None):
        if not pilot_enabled(self.dsn):
            raise RuntimeError("G01 internal pilot disabled")
        project=_valid_id(project,"project")
        policy_id=_uuid(policy_id)
        _key(idem)
        if not isinstance(expected_sequence,int) or isinstance(expected_sequence,bool) or expected_sequence<0:
            raise ValueError("invalid expected sequence")
        grant={"PROPOSED":"policy:propose","ACTIVATED":"policy:approve",
               "DISABLED":"policy:disable","SUPERSEDED":"policy:approve"}[event]
        if event=="DISABLED" and (not isinstance(reason,str) or
          len(reason)>64 or len(reason)<3 or
          any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_" for c in reason)):
            raise ValueError("invalid disable reason")
        if successor is not None:
            successor=_uuid(successor)
        with psycopg.connect(self.dsn,row_factory=dict_row,connect_timeout=10) as conn:
            with conn.transaction():
                policy=self._locked_policy(conn,project,policy_id)
                actor=self._bearer_human(conn,project,token,grant)
                ev=self._events(conn,project,policy_id)
                previous=conn.execute(
                    "SELECT * FROM si_policy_lifecycle_events "
                    "WHERE project_id=%s AND actor_id=%s AND idempotency_key=%s",
                    (project,actor,idem)).fetchone()
                if previous:
                    if str(previous["policy_id"])!=policy_id or previous["event_type"]!=event:
                        raise Conflict("policy idempotency key conflict")
                    if event=="ACTIVATED":
                        self.require_active(conn,project,policy_id)
                    return {"event_id":str(previous["id"]),"sequence":previous["sequence"],
                            "event_type":event,"replayed":True}
                latest=ev[-1]["sequence"] if ev else 0
                if expected_sequence!=latest:
                    raise Conflict("stale policy generation")
                if any(x["event_type"] in ("DISABLED","SUPERSEDED") for x in ev):
                    raise Conflict("terminal policy")
                proposed=next((x for x in ev if x["event_type"]=="PROPOSED"),None)
                if event=="PROPOSED":
                    if ev or actor!=policy["created_by"]:
                        raise AccessDenied("only original HUMAN author proposes")
                else:
                    if proposed is None:
                        raise Conflict("policy has not been proposed")
                    if event in ("ACTIVATED","SUPERSEDED") and actor==proposed["actor_id"]:
                        raise AccessDenied("independent HUMAN approver required")
                    if event=="ACTIVATED":
                        if any(x["event_type"]=="ACTIVATED" for x in ev):
                            raise Conflict("policy already active")
                    else:
                        self.require_active(conn,project,policy_id)
                if event=="SUPERSEDED":
                    if successor is None or successor==policy_id:
                        raise ValueError("valid successor required")
                    candidate=conn.execute(
                        "SELECT policy_version FROM si_evidence_verification_policies "
                        "WHERE project_id=%s AND task_id=%s::uuid AND evidence_id=%s::uuid "
                        "AND id=%s::uuid",
                        (project,policy["task_id"],policy["evidence_id"],successor)).fetchone()
                    if not candidate or candidate["policy_version"]<=policy["policy_version"]:
                        raise Conflict("successor must be a higher version in same scope")
                expires=None
                if event=="ACTIVATED":
                    expires=conn.execute(
                        "SELECT clock_timestamp()+interval '7 days' AS expiry"
                    ).fetchone()["expiry"]
                saved=conn.execute(
                    "INSERT INTO si_policy_lifecycle_events "
                    "(id,project_id,task_id,evidence_id,policy_id,event_type,"
                    "actor_id,idempotency_key,valid_until,successor_policy_id,reason_code) "
                    "VALUES(%s::uuid,%s,%s::uuid,%s::uuid,%s::uuid,%s,%s,%s,%s,%s::uuid,%s) "
                    "RETURNING id,sequence,event_type",
                    (str(uuid4()),project,policy["task_id"],policy["evidence_id"],
                     policy_id,event,actor,idem,expires,successor,reason)).fetchone()
                return {"event_id":str(saved["id"]),"sequence":saved["sequence"],
                        "event_type":event,"replayed":False}

    def propose(self,project,bearer,policy_id,idem,expected_sequence=0):
        return self._write(project,bearer,policy_id,idem,"PROPOSED",expected_sequence)

    def approve(self,project,bearer,policy_id,idem,expected_sequence):
        return self._write(project,bearer,policy_id,idem,"ACTIVATED",expected_sequence)

    def disable(self,project,bearer,policy_id,idem,expected_sequence,reason="PILOT_REVOKE"):
        return self._write(project,bearer,policy_id,idem,"DISABLED",expected_sequence,reason=reason)

    def supersede(self,project,bearer,policy_id,successor,idem,expected_sequence):
        return self._write(project,bearer,policy_id,idem,"SUPERSEDED",expected_sequence,successor=successor)
