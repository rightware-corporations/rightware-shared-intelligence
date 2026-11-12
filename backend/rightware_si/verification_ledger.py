"""WORK-03B R2 R1B — PostgreSQL-only evidence verification ledger (LAB).

No public API, MCP mutation, task approval, new dependencies or production use.
Policies are operator-seeded and immutable. The provider request happens outside
the database transaction, with authorization and task/version rechecked on commit.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any
from urllib.parse import urlsplit
from uuid import UUID, uuid4

import httpx
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from rightware_si.core.postgres import (
    WorkCore, AccessDenied, Conflict, InvalidTransition, Missing, _key, _valid_id,
)
from rightware_si.evidence_github import GithubRunPolicy, verify_github_run


def _uuid(value: str) -> str:
    try:
        return str(UUID(str(value)))
    except (TypeError, ValueError, AttributeError):
        raise ValueError("invalid UUID") from None


def _positive_version(value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError("positive task version required")
    return value


class EvidenceLedger:
    """Trusted application boundary. Caller principal MUST be authenticated.

    The R1B lab CLI uses resolve_principal(bearer), but this module does not
    accept a caller-controlled 'actor_id' from a public HTTP request.
    """

    def __init__(self, dsn: str) -> None:
        if not isinstance(dsn, str) or not dsn:
            raise ValueError("PostgreSQL DSN required")
        self.dsn = dsn

    @staticmethod
    def _authorize_service(conn: psycopg.Connection, project: str, actor: str):
        row = conn.execute(
            "SELECT principal_kind FROM si_principals WHERE id=%s",
            (actor,),
        ).fetchone()
        if not row or row["principal_kind"] != "SERVICE":
            raise AccessDenied("an independent SERVICE principal is required")
        WorkCore._authorize(conn, project, actor, "evidence:verify")
        WorkCore._authorize(conn, project, actor, "task:read")

    @classmethod
    def _load(cls, conn: psycopg.Connection, project: str, actor: str,
              policy_id: str, expected_version: int, lock: bool) -> tuple[dict, dict, dict]:
        cls._authorize_service(conn, project, actor)
        task_query = (
            "SELECT id,project_id,status,version,acceptance_criteria,created_by "
            "FROM si_tasks WHERE project_id=%s AND id=("
            "SELECT task_id FROM si_evidence_verification_policies "
            "WHERE project_id=%s AND id=%s::uuid)"
        )
        if lock:
            task_query += " FOR UPDATE"
        task = conn.execute(task_query, (project, project, policy_id)).fetchone()
        if not task:
            raise Missing("policy task not found in this project")
        if task["version"] != expected_version:
            raise Conflict("task version changed during verification")
        if task["status"] != "IN_REVIEW":
            raise InvalidTransition("only submitted tasks can be checked")
        policy = conn.execute(
            "SELECT * FROM si_evidence_verification_policies "
            "WHERE project_id=%s AND task_id=%s::uuid AND id=%s::uuid",
            (project, task["id"], policy_id),
        ).fetchone()
        if not policy:
            raise Missing("verification policy not found in this project")
        evidence = conn.execute(
            "SELECT id,uri,submitted_by,verification_state "
            "FROM si_evidence_refs WHERE project_id=%s AND task_id=%s::uuid "
            "AND id=%s::uuid",
            (project, task["id"], policy["evidence_id"]),
        ).fetchone()
        if not evidence:
            raise Missing("evidence not found in this project")
        if evidence["verification_state"] != "REFERENCED":
            raise Conflict("evidence has an unexpected existing verification state")
        # Separate agent, service and author. Being a SERVICE with a grant is
        # necessary, but not enough if it authored or submitted this evidence.
        if actor in {task["created_by"], evidence["submitted_by"], policy["created_by"]}:
            raise AccessDenied("verifier cannot check own task, evidence or policy")
        criteria = task["acceptance_criteria"]
        if not isinstance(criteria, list) or policy["criteria_index"] >= len(criteria):
            raise Conflict("policy criterion not bound to task acceptance criteria")
        cls._policy_from_row(policy)
        # The submitted URI is a pointer, NEVER an HTTP request target. It
        # must match operator-pinned policy exactly; no redirects/query/fragment.
        u = urlsplit(evidence["uri"])
        path = (
            f"/{policy['repository_owner']}/{policy['repository_name']}"
            f"/actions/runs/{policy['run_id']}"
        )
        if (u.scheme != "https" or u.hostname != "github.com" or
                u.username or u.password or u.query or u.fragment or
                u.path != path or u.netloc.lower() != "github.com"):
            raise Conflict("submitted evidence URL does not match pinned policy")
        return task, policy, evidence

    @staticmethod
    def _policy_from_row(policy: dict) -> GithubRunPolicy:
        return GithubRunPolicy(
            owner=policy["repository_owner"],
            repository=policy["repository_name"],
            repository_id=policy["repository_id"],
            workflow_id=policy["workflow_id"],
            head_sha=policy["expected_sha"].strip(),
            run_id=policy["run_id"],
            run_attempt=policy["run_attempt"],
            event=policy["expected_event"],
        )

    @staticmethod
    def _attempt_dict(row: dict) -> dict[str, Any]:
        return {
            "attempt_id": str(row["id"]),
            "project_id": row["project_id"],
            "task_id": str(row["task_id"]),
            "evidence_id": str(row["evidence_id"]),
            "policy_id": str(row["policy_id"]),
            "policy_version": row["policy_version"],
            "criteria_index": row["criteria_index"],
            "task_version_checked": row["task_version_checked"],
            "verified_by": row["verified_by"],
            "result": row["result"],
            "reason_code": row["reason_code"],
            "observation_channel": row["observation_channel"],
            "observed_at": row["observed_at"].isoformat(),
            "task_approved": False,
            "review_decision": "NOT_IMPLEMENTED_R2_R1B",
        }

    def verify_and_record(
        self, project: str, actor: str, policy_id: str,
        expected_task_version: int, idem: str, *,
        client: httpx.Client | None = None, github_token: str | None = None,
    ) -> dict[str, Any]:
        """Provider fetch is bounded and outside DB lock; commit rechecks grants.

        Providing a client is deliberately marked SIMULATED_TRANSPORT and must
        never be used as real signed evidence. No task state transition occurs.
        """
        project = _valid_id(project, "project")
        actor = _valid_id(actor, "actor")
        policy_id = _uuid(policy_id)
        _key(idem)
        _positive_version(expected_task_version)

        with psycopg.connect(self.dsn, row_factory=dict_row, connect_timeout=10) as conn:
            with conn.transaction():
                conn.execute("SET TRANSACTION READ ONLY")
                _, policy, _ = self._load(
                    conn, project, actor, policy_id, expected_task_version, False,
                )
                # Safe repeat is allowed, but the exact policy and version
                # must match. Permission is checked even on this fast path.
                prior = conn.execute(
                    "SELECT * FROM si_verification_attempts "
                    "WHERE project_id=%s AND verified_by=%s AND idempotency_key=%s",
                    (project, actor, idem),
                ).fetchone()
                if prior:
                    if (str(prior["policy_id"]) != policy_id or
                            prior["task_version_checked"] != expected_task_version):
                        raise Conflict("idempotency key reused for another verification")
                    return self._attempt_dict(prior)
                pinned = self._policy_from_row(policy)

        channel = "SIMULATED_TRANSPORT" if client is not None else "LIVE_HTTPS"
        check = verify_github_run(pinned, client=client, token=github_token)
        # Provider result can never cause an automatic DONE transition.
        if check.task_approved or check.state_authoritative:
            raise Conflict("untrusted verifier attempted approval")

        with psycopg.connect(self.dsn, row_factory=dict_row, connect_timeout=10) as conn:
            with conn.transaction():
                task, policy, _ = self._load(
                    conn, project, actor, policy_id, expected_task_version, True,
                )
                # Pinned policy fields are append-only and checked again.
                if self._policy_from_row(policy) != pinned:
                    raise Conflict("verification policy changed during provider request")
                row = conn.execute(
                    "INSERT INTO si_verification_attempts("
                    "id,project_id,task_id,evidence_id,policy_id,policy_version,"
                    "criteria_index,task_version_checked,verified_by,idempotency_key,"
                    "result,reason_code,observation_channel,provider_run_id,"
                    "provider_repository_id,provider_workflow_id,provider_attempt,"
                    "provider_head_sha)"
                    " VALUES(%s::uuid,%s,%s::uuid,%s::uuid,%s::uuid,%s,%s,%s,%s,%s,"
                    "%s,%s,%s,%s,%s,%s,%s,%s)"
                    " ON CONFLICT(project_id,verified_by,idempotency_key) DO NOTHING "
                    "RETURNING *",
                    (str(uuid4()),project,task["id"],policy["evidence_id"],
                     policy_id,policy["policy_version"],policy["criteria_index"],
                     task["version"],actor,idem,check.decision,check.reason,channel,
                     check.run_id,check.repository_id,check.workflow_id,
                     check.run_attempt,check.head_sha),
                ).fetchone()
                if row is None:
                    prior = conn.execute(
                        "SELECT * FROM si_verification_attempts "
                        "WHERE project_id=%s AND verified_by=%s AND idempotency_key=%s",
                        (project,actor,idem),
                    ).fetchone()
                    if (prior is None or str(prior["policy_id"]) != policy_id or
                            prior["task_version_checked"] != expected_task_version):
                        raise Conflict("idempotency conflict")
                    return self._attempt_dict(prior)
                conn.execute(
                    "INSERT INTO si_continuity_events "
                    "(project_id,task_id,actor_id,task_version,event_type,entity_id,payload) "
                    "VALUES(%s,%s::uuid,%s,%s,'EVIDENCE_CHECKED',%s::uuid,%s)",
                    (project,task["id"],actor,task["version"],row["id"],
                     Jsonb({"evidence_id":str(policy["evidence_id"]),
                            "policy_id":policy_id,"policy_version":policy["policy_version"],
                            "result":check.decision,"reason":check.reason,
                            "observation_channel":channel})),
                )
                return self._attempt_dict(row)

    def list_attempts(self, project: str, actor: str, task_id: str) -> list[dict[str, Any]]:
        """Current project read grants checked again, with no provider body."""
        project = _valid_id(project, "project")
        actor = _valid_id(actor, "actor")
        task_id = _uuid(task_id)
        with psycopg.connect(self.dsn,row_factory=dict_row,connect_timeout=10) as conn:
            with conn.transaction():
                conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
                WorkCore._authorize(conn,project,actor,"task:read")
                WorkCore._authorize(conn,project,actor,"evidence:read")
                task = conn.execute(
                    "SELECT id FROM si_tasks WHERE project_id=%s AND id=%s::uuid",
                    (project,task_id),
                ).fetchone()
                if not task:
                    raise Missing("task not found in authorized project")
                rows = conn.execute(
                    "SELECT * FROM si_verification_attempts "
                    "WHERE project_id=%s AND task_id=%s::uuid "
                    "ORDER BY observed_at,id LIMIT 100",
                    (project,task_id),
                ).fetchall()
                return [self._attempt_dict(r) for r in rows]
