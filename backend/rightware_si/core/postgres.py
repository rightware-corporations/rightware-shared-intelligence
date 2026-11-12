"""RIGHTWARE Shared Intelligence WORK-02A — PostgreSQL task/handoff slice.

This is an internal transaction service, NOT an HTTP server nor an identity
provider. The calling application MUST authenticate the principal and authorize
its delegation before passing principal_id. No network access to external APIs,
Mem0, or LLMs occurs here. Results are not automatically verified.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
from typing import Any, Callable
from urllib.parse import urlsplit
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


class AccessDenied(PermissionError):
    pass


class Conflict(RuntimeError):
    pass


class InvalidTransition(RuntimeError):
    pass


class Missing(LookupError):
    pass


_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$")


def _valid_id(name: str, label: str) -> str:
    if not isinstance(name, str) or not _ID.fullmatch(name):
        raise ValueError(f"{label}: invalid identifier")
    return name


def _key(value: str) -> str:
    if not isinstance(value, str) or not _KEY.fullmatch(value):
        raise ValueError("idempotency key must have 8-128 safe characters")
    return value


def _fingerprint(obj: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


def _check_text(value: str, field: str, size: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > size:
        raise ValueError(f"{field} must have 1-{size} nonblank characters")
    return value.strip()


def _check_git_url(url: str) -> str:
    if not isinstance(url, str) or len(url) > 2048:
        raise ValueError("evidence URL invalid")
    p = urlsplit(url)
    if p.scheme != "https" or p.hostname != "github.com" or p.username or p.password or p.fragment:
        raise ValueError("WORK-02A accepts only HTTPS github.com evidence URLs")
    if not p.path.strip("/"):
        raise ValueError("evidence URL must include a path")
    return url


class WorkCore:
    """Synchronous PostgreSQL transaction boundary; one connection per operation."""

    def __init__(self, dsn: str) -> None:
        if not isinstance(dsn, str) or not dsn.strip():
            raise ValueError("PostgreSQL DSN required")
        self.dsn = dsn

    @staticmethod
    def _authorize(conn: psycopg.Connection, project: str, principal: str, perm: str) -> None:
        row = conn.execute(
            "SELECT 1 FROM si_project_grants "
            "WHERE project_id=%s AND principal_id=%s AND permission=%s",
            (project, principal, perm),
        ).fetchone()
        if row is None:
            raise AccessDenied("principal lacks project permission")

    @staticmethod
    def _task(conn: psycopg.Connection, project: str, task_id: str) -> dict[str, Any]:
        row = conn.execute(
            "SELECT * FROM si_tasks WHERE project_id=%s AND id=%s::uuid FOR UPDATE",
            (project, task_id),
        ).fetchone()
        if row is None:
            raise Missing("task not found in authorized project")
        return row

    @staticmethod
    def _version(task: dict[str, Any], expected: int) -> None:
        if task["version"] != expected:
            raise Conflict("stale task version")

    @staticmethod
    def _event(conn: psycopg.Connection, task: dict[str, Any], actor: str,
               event_type: str, payload: dict[str, Any]) -> None:
        conn.execute(
            "INSERT INTO si_events(project_id,task_id,task_version,actor_id,event_type,payload) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (task["project_id"],task["id"],task["version"],actor,event_type,Jsonb(payload)),
        )

    @staticmethod
    def _advance(conn: psycopg.Connection, task: dict[str, Any], status: str,
                 actor: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        next_version = task["version"] + 1
        conn.execute(
            "UPDATE si_tasks SET status=%s,version=%s,updated_at=now() WHERE id=%s",
            (status,next_version,task["id"]),
        )
        task = dict(task, status=status, version=next_version)
        WorkCore._event(conn,task,actor,event_type,payload)
        return {"task_id":str(task["id"]),"status":status,"version":next_version}

    @staticmethod
    def _lease(conn: psycopg.Connection, task_id: str, actor: str, token: str) -> dict[str, Any]:
        row = conn.execute(
            "SELECT holder_id,token_hash,expires_at,generation FROM si_task_leases "
            "WHERE task_id=%s::uuid FOR UPDATE",(task_id,),
        ).fetchone()
        if row is None or row["holder_id"] != actor:
            raise Conflict("no active lease for actor")
        if not hmac.compare_digest(row["token_hash"], hashlib.sha256(token.encode()).hexdigest()):
            raise Conflict("invalid task lease")
        valid=conn.execute("SELECT (%s::timestamptz > now()) AS valid",(row["expires_at"],)).fetchone()
        if not valid["valid"]:
            raise Conflict("expired task lease")
        return row

    @staticmethod
    def _write_lease(conn: psycopg.Connection, task_id: str, holder: str,
                     generation: int) -> str:
        # R1C: generation must be monotonic across recovery, handoff and
        # deletion of si_task_leases. Caller holds the task FOR UPDATE lock.
        fence=conn.execute(
            "INSERT INTO si_lease_fences(task_id,generation) VALUES(%s::uuid,%s) "
            "ON CONFLICT(task_id) DO UPDATE SET "
            "generation=GREATEST(si_lease_fences.generation+1, EXCLUDED.generation) "
            "RETURNING generation",
            (task_id,generation),
        ).fetchone()["generation"]
        token=secrets.token_urlsafe(32)
        conn.execute(
            "INSERT INTO si_task_leases(task_id,holder_id,token_hash,generation,expires_at) "
            "VALUES (%s::uuid,%s,%s,%s,now()+interval '30 minutes') "
            "ON CONFLICT(task_id) DO UPDATE SET holder_id=EXCLUDED.holder_id,"
            "token_hash=EXCLUDED.token_hash,generation=EXCLUDED.generation,"
            "expires_at=EXCLUDED.expires_at",
            (task_id,holder,hashlib.sha256(token.encode()).hexdigest(),fence),
        )
        return token

    def _execute(self, project: str, actor: str, permission: str, action: str,
                 idem: str, payload: dict[str, Any],
                 handler: Callable[[psycopg.Connection],dict[str, Any]]) -> dict[str, Any]:
        _valid_id(project,"project")
        _valid_id(actor,"actor")
        _key(idem)
        fingerprint=_fingerprint(payload)
        with psycopg.connect(self.dsn,row_factory=dict_row,connect_timeout=10) as conn:
            with conn.transaction():
                self._authorize(conn,project,actor,permission)
                # Reservation serializes concurrent requests for the same idempotency key.
                conn.execute(
                    "INSERT INTO si_idempotency(project_id,principal_id,action,idem_key,payload_hash) "
                    "VALUES(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                    (project,actor,action,idem,fingerprint),
                )
                reservation=conn.execute(
                    "SELECT payload_hash,response FROM si_idempotency "
                    "WHERE project_id=%s AND principal_id=%s AND action=%s AND idem_key=%s FOR UPDATE",
                    (project,actor,action,idem),
                ).fetchone()
                if reservation["payload_hash"] != fingerprint:
                    raise Conflict("idempotency key reused with different parameters")
                if reservation["response"] is not None:
                    # A one-time lease credential is never recoverable from
                    # stored idempotency data. Explicit 409 is safer than a
                    # silent replay without a usable lease credential.
                    if action in {"claim_task", "accept_handoff", "recover_lease"}:
                        raise Conflict("lease credential cannot be replayed")
                    return reservation["response"]
                response=handler(conn)
                # Never persist a bearer-capable lease secret in PostgreSQL.
                # Normal response is returned once to the authorized caller;
                # stored idempotency state retains public transaction fields.
                safe_response={k:v for k,v in response.items() if k!="lease_token"}
                conn.execute(
                    "UPDATE si_idempotency SET response=%s WHERE project_id=%s "
                    "AND principal_id=%s AND action=%s AND idem_key=%s",
                    (Jsonb(safe_response),project,actor,action,idem),
                )
                return response

    def create_task(self, project: str, actor: str, title: str,
                    acceptance_criteria: list[str], idem: str) -> dict[str, Any]:
        title=_check_text(title,"title",200)
        if (not isinstance(acceptance_criteria,list) or not acceptance_criteria
            or len(acceptance_criteria)>30 or
            any(not isinstance(x,str) or not x.strip() or len(x)>500 for x in acceptance_criteria)):
            raise ValueError("acceptance criteria must be a nonempty list of 1-30 strings")
        payload={"title":title,"acceptance_criteria":acceptance_criteria}

        def action(conn):
            task_id=str(uuid4())
            conn.execute(
                "INSERT INTO si_tasks(id,project_id,created_by,title,acceptance_criteria,status,version)"
                " VALUES(%s::uuid,%s,%s,%s,%s,'DRAFT',1)",
                (task_id,project,actor,title,Jsonb(acceptance_criteria)),
            )
            self._event(conn,{"id":task_id,"project_id":project,"version":1},
                        actor,"TASK_CREATED",{"title":title})
            return {"task_id":task_id,"status":"DRAFT","version":1}
        return self._execute(project,actor,"task:create","create_task",idem,payload,action)

    def publish_task(self, project: str, actor: str, task_id: str,
                     expected_version: int, idem: str) -> dict[str, Any]:
        def action(conn):
            task=self._task(conn,project,task_id)
            self._version(task,expected_version)
            if task["status"]!="DRAFT":
                raise InvalidTransition("publish requires DRAFT")
            return self._advance(conn,task,"READY",actor,"TASK_PUBLISHED",{})
        return self._execute(project,actor,"task:manage","publish_task",idem,
                             {"task":task_id,"v":expected_version},action)

    def claim_task(self, project: str, actor: str, task_id: str,
                   expected_version: int, idem: str) -> dict[str, Any]:
        def action(conn):
            task=self._task(conn,project,task_id)
            self._version(task,expected_version)
            if task["status"]!="READY":
                raise InvalidTransition("claim requires READY")
            token=self._write_lease(conn,task_id,actor,task["version"]+1)
            result=self._advance(conn,task,"IN_PROGRESS",actor,"TASK_CLAIMED",{})
            # Raw token is returned once, never stored in idempotency response.
            generation=conn.execute(
                "SELECT generation FROM si_task_leases WHERE task_id=%s::uuid",
                (task_id,),
            ).fetchone()["generation"]
            return dict(result,lease_token=token,lease_generation=generation)
        return self._execute(project,actor,"task:execute","claim_task",idem,
                             {"task":task_id,"v":expected_version},action)

    def offer_handoff(self, project: str, actor: str, task_id: str,
                      to_principal: str, summary: str, lease_token: str,
                      expected_version: int, idem: str,
                      checkpoint_id: str | None = None,
                      expected_checkpoint_seq: int | None = None) -> dict[str, Any]:
        _valid_id(to_principal,"target")
        summary=_check_text(summary,"summary",8000)
        if (checkpoint_id is None) != (expected_checkpoint_seq is None):
            raise ValueError("checkpoint id and sequence must be supplied together")
        if checkpoint_id is not None:
            try:
                from uuid import UUID
                checkpoint_id=str(UUID(checkpoint_id))
            except (ValueError,TypeError,AttributeError):
                raise ValueError("invalid checkpoint identifier") from None
            if (not isinstance(expected_checkpoint_seq,int)
                    or isinstance(expected_checkpoint_seq,bool)
                    or expected_checkpoint_seq <= 0):
                raise ValueError("invalid checkpoint sequence")

        def action(conn):
            self._authorize(conn,project,to_principal,"handoff:accept")
            task=self._task(conn,project,task_id)
            self._version(task,expected_version)
            if task["status"]!="IN_PROGRESS":
                raise InvalidTransition("handoff requires IN_PROGRESS")
            self._lease(conn,task_id,actor,lease_token)
            latest=conn.execute(
                "SELECT id,checkpoint_seq,task_version_recorded,recorded_by "
                "FROM si_task_checkpoints "
                "WHERE project_id=%s AND task_id=%s::uuid "
                "ORDER BY checkpoint_seq DESC LIMIT 1",
                (project,task_id),
            ).fetchone()
            if latest is not None:
                # Any work that has checkpoints requires an explicit *exact*
                # current checkpoint. Do not silently bind an older one.
                if (checkpoint_id is None
                    or str(latest["id"])!=checkpoint_id
                    or latest["checkpoint_seq"]!=expected_checkpoint_seq
                    or latest["task_version_recorded"]!=expected_version
                    or latest["recorded_by"]!=actor):
                    raise Conflict("latest owned checkpoint/version must be bound")
                # Don't hand a private checkpoint to a target without read scope.
                self._authorize(conn,project,to_principal,"task:read")
                self._authorize(conn,project,to_principal,"context:read")
                bound_id=checkpoint_id
                bound_seq=expected_checkpoint_seq
                bound_version=expected_version
            else:
                # Explicit legacy compatibility for WORK-02A tests without a
                # checkpoint. Never describe it as a complete continuity handoff.
                if checkpoint_id is not None:
                    raise Missing("checkpoint not found for this task")
                bound_id=bound_seq=bound_version=None
            handoff_id=str(uuid4())
            conn.execute(
                "INSERT INTO si_handoffs(id,project_id,task_id,from_principal_id,"
                "to_principal_id,summary,status,checkpoint_id,checkpoint_seq,"
                "checkpoint_task_version) "
                "VALUES(%s::uuid,%s,%s::uuid,%s,%s,%s,'OFFERED',%s::uuid,%s,%s)",
                (handoff_id,project,task_id,actor,to_principal,summary,
                 bound_id,bound_seq,bound_version),
            )
            conn.execute("DELETE FROM si_task_leases WHERE task_id=%s::uuid",(task_id,))
            result=self._advance(
                conn,task,"BLOCKED",actor,"HANDOFF_OFFERED",
                {"handoff_id":handoff_id,"to_principal":to_principal,
                 "checkpoint_id":bound_id,"checkpoint_seq":bound_seq},
            )
            return dict(
                result,handoff_id=handoff_id,handoff_status="OFFERED",
                checkpoint_binding=("BOUND_R1C" if bound_id else "LEGACY_UNBOUND"),
                checkpoint_id=bound_id,checkpoint_seq=bound_seq,
            )

        return self._execute(
            project,actor,"handoff:offer","offer_handoff",idem,
            {"task":task_id,"v":expected_version,
             "to":to_principal,"summary":summary,
             "checkpoint_id":checkpoint_id,"checkpoint_seq":expected_checkpoint_seq,
             "lease_hash":hashlib.sha256(lease_token.encode()).hexdigest()},action,
        )

    def accept_handoff(self, project: str, actor: str, handoff_id: str,
                       expected_version: int, idem: str) -> dict[str, Any]:
        def action(conn):
            # Lookup includes project scope; lock task before handoff for races.
            h=conn.execute(
                "SELECT task_id FROM si_handoffs WHERE project_id=%s AND id=%s::uuid",
                (project,handoff_id),
            ).fetchone()
            if h is None:
                raise Missing("handoff not found")
            task_id=str(h["task_id"])
            task=self._task(conn,project,task_id)
            self._version(task,expected_version)
            h=conn.execute(
                "SELECT * FROM si_handoffs WHERE project_id=%s AND id=%s::uuid FOR UPDATE",
                (project,handoff_id),
            ).fetchone()
            if h["status"]!="OFFERED" or h["to_principal_id"]!=actor:
                raise AccessDenied("handoff not offered to this principal")
            if task["status"]!="BLOCKED":
                raise InvalidTransition("handoff acceptance requires BLOCKED task")
            checkpoint_id=str(h["checkpoint_id"]) if h["checkpoint_id"] else None
            if checkpoint_id:
                self._authorize(conn,project,actor,"task:read")
                self._authorize(conn,project,actor,"context:read")
                latest=conn.execute(
                    "SELECT id,checkpoint_seq,task_version_recorded "
                    "FROM si_task_checkpoints WHERE project_id=%s AND task_id=%s::uuid "
                    "ORDER BY checkpoint_seq DESC LIMIT 1",
                    (project,task_id),
                ).fetchone()
                if (not latest or str(latest["id"])!=checkpoint_id
                    or latest["checkpoint_seq"]!=h["checkpoint_seq"]
                    or latest["task_version_recorded"]!=h["checkpoint_task_version"]
                    or latest["task_version_recorded"]+1!=task["version"]):
                    raise Conflict("bound checkpoint is stale or altered")
            token=self._write_lease(conn,task_id,actor,task["version"]+1)
            generation=conn.execute(
                "SELECT generation FROM si_task_leases WHERE task_id=%s::uuid",
                (task_id,),
            ).fetchone()["generation"]
            conn.execute(
                "UPDATE si_handoffs SET status='ACCEPTED',accepted_at=now() "
                "WHERE project_id=%s AND id=%s::uuid",
                (project,handoff_id),
            )
            result=self._advance(conn,task,"IN_PROGRESS",actor,"HANDOFF_ACCEPTED",
                                 {"handoff_id":handoff_id,
                                  "checkpoint_id":checkpoint_id,
                                  "lease_generation":generation})
            return dict(
                result,handoff_id=handoff_id,handoff_status="ACCEPTED",
                checkpoint_binding=("BOUND_R1C" if checkpoint_id else "LEGACY_UNBOUND"),
                checkpoint_id=checkpoint_id,
                checkpoint_seq=h["checkpoint_seq"],
                lease_token=token,lease_generation=generation,
            )
        return self._execute(project,actor,"handoff:accept","accept_handoff",idem,
                             {"handoff":handoff_id,"v":expected_version},action)

    def get_lease_state(self, project: str, actor: str, task_id: str) -> dict[str, Any]:
        """Authorized current holder can check generation but never recover token."""
        _valid_id(project,"project")
        _valid_id(actor,"actor")
        with psycopg.connect(self.dsn,row_factory=dict_row,connect_timeout=10) as conn:
            with conn.transaction():
                conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
                self._authorize(conn,project,actor,"task:recover")
                self._authorize(conn,project,actor,"task:execute")
                self._authorize(conn,project,actor,"task:read")
                task=conn.execute(
                    "SELECT id,status,version FROM si_tasks "
                    "WHERE project_id=%s AND id=%s::uuid",
                    (project,task_id),
                ).fetchone()
                if not task:
                    raise Missing("task not found")
                if task["status"]!="IN_PROGRESS":
                    raise Conflict("task does not hold an active writer")
                lease=conn.execute(
                    "SELECT holder_id,generation,expires_at,"
                    "(expires_at > now()) AS is_valid "
                    "FROM si_task_leases WHERE task_id=%s::uuid",
                    (task_id,),
                ).fetchone()
                if not lease or lease["holder_id"]!=actor:
                    raise AccessDenied("only current holder can inspect its lease")
                return {"task_id":str(task["id"]),"task_version":task["version"],
                        "lease_generation":lease["generation"],
                        "expires_at":lease["expires_at"].isoformat(),
                        "lease_valid":lease["is_valid"],
                        "token_recoverable":False}

    def recover_lease(self, project: str, actor: str, task_id: str,
                      expected_version: int, expected_generation: int,
                      idem: str) -> dict[str, Any]:
        """One-time rekey for the *same current holder*, including expired lease.

        Never allow a different agent to steal ownership via bearer alone.
        New token must never be stored in idempotency or event log.
        """
        if (not isinstance(expected_generation,int)
                or isinstance(expected_generation,bool)
                or expected_generation<=0):
            raise ValueError("invalid expected lease generation")

        def action(conn):
            self._authorize(conn,project,actor,"task:execute")
            task=self._task(conn,project,task_id)
            self._version(task,expected_version)
            if task["status"]!="IN_PROGRESS":
                raise InvalidTransition("rekey requires IN_PROGRESS")
            old=conn.execute(
                "SELECT holder_id,generation FROM si_task_leases "
                "WHERE task_id=%s::uuid FOR UPDATE",
                (task_id,),
            ).fetchone()
            if old is None or old["holder_id"]!=actor:
                raise AccessDenied("only current holder can recover its lease")
            if old["generation"]!=expected_generation:
                raise Conflict("stale lease generation")
            token=self._write_lease(conn,task_id,actor,old["generation"]+1)
            generation=conn.execute(
                "SELECT generation FROM si_task_leases WHERE task_id=%s::uuid",
                (task_id,),
            ).fetchone()["generation"]
            conn.execute(
                "INSERT INTO si_continuity_events "
                "(project_id,task_id,actor_id,task_version,event_type,entity_id,payload) "
                "VALUES(%s,%s::uuid,%s,%s,'LEASE_REKEYED',%s::uuid,%s)",
                (project,task_id,actor,task["version"],task_id,
                 Jsonb({"old_generation":old["generation"],
                        "new_generation":generation,"reason":"holder_rekey"})),
            )
            return {"task_id":task_id,"status":task["status"],
                    "version":task["version"],"lease_generation":generation,
                    "lease_token":token,"recovered":True}

        return self._execute(
            project,actor,"task:recover","recover_lease",idem,
            {"task":task_id,"v":expected_version,
             "expected_generation":expected_generation},action,
        )

    def submit_result(self, project: str, actor: str, task_id: str,
                      expected_version: int, lease_token: str, evidence_url: str,
                      idem: str) -> dict[str, Any]:
        evidence_url=_check_git_url(evidence_url)
        def action(conn):
            task=self._task(conn,project,task_id)
            self._version(task,expected_version)
            if task["status"]!="IN_PROGRESS":
                raise InvalidTransition("result submission requires IN_PROGRESS")
            self._lease(conn,task_id,actor,lease_token)
            evidence_id=str(uuid4())
            conn.execute(
                "INSERT INTO si_evidence_refs(id,project_id,task_id,submitted_by,uri) "
                "VALUES(%s::uuid,%s,%s::uuid,%s,%s)",
                (evidence_id,project,task_id,actor,evidence_url),
            )
            conn.execute("DELETE FROM si_task_leases WHERE task_id=%s::uuid",(task_id,))
            result=self._advance(conn,task,"IN_REVIEW",actor,"RESULT_SUBMITTED",
                                 {"evidence_id":evidence_id,"verification_state":"REFERENCED"})
            return dict(result,evidence_id=evidence_id,verification_state="REFERENCED")
        return self._execute(project,actor,"task:execute","submit_result",idem,
                             {"task":task_id,"v":expected_version,"url":evidence_url,
                              "lease_hash":hashlib.sha256(lease_token.encode()).hexdigest()},action)

    def get_task(self, project: str, actor: str, task_id: str) -> dict[str, Any]:
        _valid_id(project,"project")
        _valid_id(actor,"actor")
        with psycopg.connect(self.dsn,row_factory=dict_row,connect_timeout=10) as conn:
            self._authorize(conn,project,actor,"task:read")
            row=conn.execute(
                "SELECT id,title,status,version,acceptance_criteria "
                "FROM si_tasks WHERE project_id=%s AND id=%s::uuid",
                (project,task_id),
            ).fetchone()
            if row is None:
                raise Missing("task not found")
            return dict(row, id=str(row["id"]))

    def task_events(self, project: str, actor: str, task_id: str) -> list[dict[str, Any]]:
        _valid_id(project,"project")
        _valid_id(actor,"actor")
        with psycopg.connect(self.dsn,row_factory=dict_row,connect_timeout=10) as conn:
            self._authorize(conn,project,actor,"audit:read")
            rows=conn.execute(
                "SELECT task_version,actor_id,event_type,payload "
                "FROM si_events WHERE project_id=%s AND task_id=%s::uuid ORDER BY task_version",
                (project,task_id),
            ).fetchall()
            return [dict(x) for x in rows]
