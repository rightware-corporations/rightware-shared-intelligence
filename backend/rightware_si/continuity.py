"""WORK-03B R1A: source-linked, unverified observations on a valid task lease.

This is a transactional *internal* service. Only the HTTP gateway can supply
authenticated principals. Source URIs are pointers, never fetched or trusted.
Task version remains unchanged: si_continuity_events is a separate audit stream.
"""
from __future__ import annotations

import hashlib
import re
from urllib.parse import urlsplit
from uuid import UUID, uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from rightware_si.core.postgres import (
    WorkCore, AccessDenied, Conflict, InvalidTransition, Missing,
    _check_text, _valid_id,
)

_REV = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_DIGEST = re.compile(r"^[a-f0-9]{64}$")
_URN = re.compile(r"^urn:rw:[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")


def _uuid(value: str, label: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError):
        raise ValueError(f"invalid {label}") from None


def _source_pointer(kind: str, uri: str, revision: str, digest: str | None):
    if kind not in ("GIT_REF", "TOOL_RECEIPT"):
        raise ValueError("unsupported source kind")
    if not isinstance(uri, str) or not (1 <= len(uri) <= 2048):
        raise ValueError("source URI length invalid")
    if kind == "GIT_REF":
        url = urlsplit(uri)
        if (url.scheme != "https" or url.hostname != "github.com"
                or url.username or url.password or url.fragment
                or not url.path.strip("/")):
            raise ValueError("only HTTPS github.com source references are allowed")
    elif not _URN.fullmatch(uri):
        raise ValueError("tool receipt must use a safe urn:rw: reference")
    if not isinstance(revision, str) or not _REV.fullmatch(revision):
        raise ValueError("invalid source revision")
    if digest is not None and (not isinstance(digest, str) or not _DIGEST.fullmatch(digest)):
        raise ValueError("invalid sha256 digest")
    return uri, revision, digest


def _lease_fingerprint(token: str) -> str:
    if not isinstance(token, str) or not (20 <= len(token) <= 256):
        raise ValueError("invalid lease token")
    return hashlib.sha256(token.encode()).hexdigest()


class ContinuityCore(WorkCore):
    """R1A service; PostgreSQL is authoritative, Mem0 is not involved."""

    @staticmethod
    def _working(conn, project: str, actor: str, task_id: str,
                 expected_version: int, lease_token: str):
        task = WorkCore._task(conn, project, task_id)
        WorkCore._version(task, expected_version)
        if task["status"] != "IN_PROGRESS":
            raise InvalidTransition("continuity write requires IN_PROGRESS task")
        WorkCore._lease(conn, task_id, actor, lease_token)
        return task

    @staticmethod
    def _owned_run(conn, project: str, actor: str, task_id: str, run_id: str):
        row = conn.execute(
            "SELECT actor_id FROM si_agent_runs "
            "WHERE project_id=%s AND task_id=%s::uuid AND id=%s::uuid",
            (project, task_id, run_id),
        ).fetchone()
        if row is None:
            raise Missing("agent run does not belong to this task/project")
        if row["actor_id"] != actor:
            raise AccessDenied("agent run is owned by a different principal")

    @staticmethod
    def _continuity_event(conn, task, actor: str, event_type: str,
                          entity_id: str, payload: dict):
        conn.execute(
            "INSERT INTO si_continuity_events "
            "(project_id,task_id,actor_id,task_version,event_type,entity_id,payload) "
            "VALUES(%s,%s,%s,%s,%s,%s::uuid,%s)",
            (task["project_id"], task["id"], actor, task["version"],
             event_type, entity_id, Jsonb(payload)),
        )

    def start_run(self, project: str, actor: str, task_id: str,
                  expected_version: int, lease_token: str, runtime_label: str,
                  idem: str) -> dict:
        task_id = _uuid(task_id, "task id")
        label = _check_text(runtime_label, "runtime_label", 120)
        lease_hash = _lease_fingerprint(lease_token)

        def action(conn):
            task = self._working(conn, project, actor, task_id,
                                 expected_version, lease_token)
            previous = conn.execute(
                "SELECT 1 FROM si_agent_runs "
                "WHERE project_id=%s AND task_id=%s::uuid AND actor_id=%s "
                "AND task_version_started=%s",
                (project, task_id, actor, expected_version),
            ).fetchone()
            if previous:
                raise Conflict("run already exists for this task lease generation")
            run_id = str(uuid4())
            correlation_id = str(uuid4())
            conn.execute(
                "INSERT INTO si_agent_runs "
                "(id,project_id,task_id,actor_id,correlation_id,"
                "runtime_label,task_version_started) "
                "VALUES(%s::uuid,%s,%s::uuid,%s,%s::uuid,%s,%s)",
                (run_id, project, task_id, actor, correlation_id,
                 label, expected_version),
            )
            self._continuity_event(conn, task, actor, "AGENT_RUN_STARTED",
                                   run_id, {"run_id": run_id, "correlation_id": correlation_id})
            return {"run_id": run_id, "task_id": task_id, "project_id": project,
                    "actor_id": actor, "correlation_id": correlation_id,
                    "task_version": expected_version}

        return self._execute(
            project, actor, "task:execute", "start_run", idem,
            {"task": task_id, "v": expected_version,
             "label": label, "lease_hash": lease_hash}, action,
        )

    def register_source(self, project: str, actor: str, task_id: str,
                        run_id: str, expected_version: int, lease_token: str,
                        source_kind: str, source_uri: str, source_revision: str,
                        digest_sha256: str | None, idem: str) -> dict:
        task_id = _uuid(task_id, "task id")
        run_id = _uuid(run_id, "run id")
        uri, revision, digest = _source_pointer(
            source_kind, source_uri, source_revision, digest_sha256
        )
        lease_hash = _lease_fingerprint(lease_token)

        def action(conn):
            task = self._working(conn, project, actor, task_id,
                                 expected_version, lease_token)
            self._owned_run(conn, project, actor, task_id, run_id)
            existing = conn.execute(
                "SELECT 1 FROM si_source_records "
                "WHERE project_id=%s AND task_id=%s::uuid "
                "AND source_kind=%s AND source_uri=%s AND source_revision=%s",
                (project, task_id, source_kind, uri, revision),
            ).fetchone()
            if existing:
                raise Conflict("source revision already registered for task")
            source_id = str(uuid4())
            conn.execute(
                "INSERT INTO si_source_records "
                "(id,project_id,task_id,agent_run_id,recorded_by,source_kind,"
                "source_uri,source_revision,digest_sha256) "
                "VALUES(%s::uuid,%s,%s::uuid,%s::uuid,%s,%s,%s,%s,%s)",
                (source_id, project, task_id, run_id, actor, source_kind,
                 uri, revision, digest),
            )
            self._continuity_event(conn, task, actor, "SOURCE_REGISTERED",
                                   source_id, {"source_id": source_id,
                                               "run_id": run_id, "kind": source_kind})
            return {"source_id": source_id, "task_id": task_id,
                    "run_id": run_id, "trust": "SOURCE_LINKED_UNVERIFIED",
                    "source_revision": revision}

        return self._execute(
            project, actor, "source:write", "register_source", idem,
            {"task": task_id, "run": run_id, "v": expected_version,
             "kind": source_kind, "uri": uri, "rev": revision,
             "digest": digest, "lease_hash": lease_hash}, action,
        )

    def record_observation(self, project: str, actor: str, task_id: str,
                           run_id: str, expected_version: int, lease_token: str,
                           claim: str, source_ids: list[str], idem: str) -> dict:
        task_id = _uuid(task_id, "task id")
        run_id = _uuid(run_id, "run id")
        claim = _check_text(claim, "claim", 2000)
        lease_hash = _lease_fingerprint(lease_token)
        if not isinstance(source_ids, list) or not 1 <= len(source_ids) <= 10:
            raise ValueError("observation requires 1-10 source references")
        sources = sorted(_uuid(s, "source id") for s in source_ids)
        if len(set(sources)) != len(sources):
            raise ValueError("duplicate source references")

        def action(conn):
            task = self._working(conn, project, actor, task_id,
                                 expected_version, lease_token)
            self._owned_run(conn, project, actor, task_id, run_id)
            rows = conn.execute(
                "SELECT id FROM si_source_records "
                "WHERE project_id=%s AND task_id=%s::uuid AND id=ANY(%s::uuid[])",
                (project, task_id, sources),
            ).fetchall()
            if len(rows) != len(sources):
                raise Missing("source does not belong to this task/project")
            obs_id = str(uuid4())
            conn.execute(
                "INSERT INTO si_observations "
                "(id,project_id,task_id,agent_run_id,asserted_by,claim_text) "
                "VALUES(%s::uuid,%s,%s::uuid,%s::uuid,%s,%s)",
                (obs_id, project, task_id, run_id, actor, claim),
            )
            for source in sources:
                conn.execute(
                    "INSERT INTO si_observation_sources "
                    "(project_id,task_id,observation_id,source_id) "
                    "VALUES(%s,%s::uuid,%s::uuid,%s::uuid)",
                    (project, task_id, obs_id, source),
                )
            # Event intentionally contains only references, not untrusted claim text.
            self._continuity_event(conn, task, actor, "OBSERVATION_ASSERTED",
                                   obs_id, {"observation_id": obs_id,
                                            "run_id": run_id, "source_count": len(sources)})
            return {"observation_id": obs_id, "task_id": task_id,
                    "run_id": run_id, "trust_state": "ASSERTED",
                    "source_ids": sources, "task_version": expected_version}

        return self._execute(
            project, actor, "observation:write", "record_observation", idem,
            {"task": task_id, "run": run_id, "v": expected_version,
             "claim": claim, "sources": sources, "lease_hash": lease_hash}, action,
        )

    def list_observations(self, project: str, actor: str, task_id: str) -> dict:
        _valid_id(project, "project")
        _valid_id(actor, "actor")
        task_id = _uuid(task_id, "task id")
        with psycopg.connect(self.dsn, row_factory=dict_row, connect_timeout=10) as conn:
            # Read permissions are separate from write or task-execute grants.
            self._authorize(conn, project, actor, "task:read")
            self._authorize(conn, project, actor, "context:read")
            exists = conn.execute(
                "SELECT 1 FROM si_tasks WHERE project_id=%s AND id=%s::uuid",
                (project, task_id),
            ).fetchone()
            if not exists:
                raise Missing("task does not exist in this project")
            rows = conn.execute(
                "SELECT id,agent_run_id,asserted_by,claim_text,trust_state,created_at "
                "FROM si_observations WHERE project_id=%s AND task_id=%s::uuid "
                "ORDER BY created_at,id LIMIT 100",
                (project, task_id),
            ).fetchall()
            output = []
            for row in rows:
                source_rows = conn.execute(
                    "SELECT source_id FROM si_observation_sources "
                    "WHERE project_id=%s AND task_id=%s::uuid AND observation_id=%s::uuid "
                    "ORDER BY source_id",
                    (project, task_id, str(row["id"])),
                ).fetchall()
                output.append({
                    "observation_id": str(row["id"]), "agent_run_id": str(row["agent_run_id"]),
                    "asserted_by": row["asserted_by"], "claim": row["claim_text"],
                    "trust_state": row["trust_state"],
                    "created_at": row["created_at"].isoformat(),
                    "source_ids": [str(s["source_id"]) for s in source_rows],
                })
            return {"task_id": task_id, "observations": output,
                    "limit": 100, "truncated": len(rows) == 100}


    @staticmethod
    def _texts(values, name: str, minimum: int, maximum: int) -> list[str]:
        if not isinstance(values, list) or not minimum <= len(values) <= maximum:
            raise ValueError(f"{name}: invalid number of items")
        return [_check_text(value, name, 500) for value in values]

    def record_checkpoint(self, project: str, actor: str, task_id: str,
                          run_id: str, expected_version: int, lease_token: str,
                          expected_checkpoint_seq: int, summary: str,
                          next_actions: list[str], blockers: list[str],
                          observation_ids: list[str], idem: str) -> dict:
        """Append a checkpoint with CAS sequence and same-task observed references.

        Checkpoint claims and action suggestions stay ASSERTED, never approved.
        No task state/version transition, model inference, or Mem0 calls.
        """
        task_id = _uuid(task_id, "task id")
        run_id = _uuid(run_id, "run id")
        summary = _check_text(summary, "checkpoint summary", 2000)
        actions = self._texts(next_actions, "next_actions", 1, 12)
        blockers = self._texts(blockers, "blockers", 0, 12)
        if not isinstance(expected_checkpoint_seq, int) or isinstance(
            expected_checkpoint_seq, bool
        ) or expected_checkpoint_seq < 0:
            raise ValueError("invalid expected_checkpoint_seq")
        if not isinstance(observation_ids, list) or len(observation_ids) > 20:
            raise ValueError("checkpoint supports up to 20 observations")
        obs_ids = sorted(_uuid(x, "observation id") for x in observation_ids)
        if len(obs_ids) != len(set(obs_ids)):
            raise ValueError("duplicate observation reference")
        lease_hash = _lease_fingerprint(lease_token)

        def action(conn):
            task = self._working(conn, project, actor, task_id,
                                 expected_version, lease_token)
            self._authorize(conn, project, actor, "task:execute")
            self._authorize(conn, project, actor, "context:read")
            self._owned_run(conn, project, actor, task_id, run_id)
            current_seq = conn.execute(
                "SELECT COALESCE(MAX(checkpoint_seq),0) AS seq "
                "FROM si_task_checkpoints WHERE project_id=%s AND task_id=%s::uuid",
                (project, task_id),
            ).fetchone()["seq"]
            if current_seq != expected_checkpoint_seq:
                raise Conflict("stale checkpoint sequence")
            if obs_ids:
                matches = conn.execute(
                    "SELECT id FROM si_observations "
                    "WHERE project_id=%s AND task_id=%s::uuid "
                    "AND id=ANY(%s::uuid[])",
                    (project, task_id, obs_ids),
                ).fetchall()
                if len(matches) != len(obs_ids):
                    raise Missing("observation does not belong to this task")
            checkpoint_id = str(uuid4())
            seq = current_seq + 1
            conn.execute(
                "INSERT INTO si_task_checkpoints "
                "(id,project_id,task_id,agent_run_id,recorded_by,checkpoint_seq,"
                "task_version_recorded,summary,next_actions,blockers) "
                "VALUES(%s::uuid,%s,%s::uuid,%s::uuid,%s,%s,%s,%s,%s,%s)",
                (checkpoint_id, project, task_id, run_id, actor, seq,
                 expected_version, summary, Jsonb(actions), Jsonb(blockers)),
            )
            for obs in obs_ids:
                conn.execute(
                    "INSERT INTO si_checkpoint_observations "
                    "(project_id,task_id,checkpoint_id,observation_id) "
                    "VALUES(%s,%s::uuid,%s::uuid,%s::uuid)",
                    (project, task_id, checkpoint_id, obs),
                )
            self._continuity_event(
                conn, task, actor, "CHECKPOINT_RECORDED", checkpoint_id,
                {"checkpoint_id": checkpoint_id, "checkpoint_seq": seq,
                 "run_id": run_id, "observation_count": len(obs_ids)},
            )
            return {
                "checkpoint_id": checkpoint_id, "checkpoint_seq": seq,
                "task_id": task_id, "task_version": expected_version,
                "run_id": run_id, "trust_state": "ASSERTED",
                "observation_ids": obs_ids,
            }

        return self._execute(
            project, actor, "checkpoint:write", "record_checkpoint", idem,
            {"task": task_id, "run": run_id, "v": expected_version,
             "expected_seq": expected_checkpoint_seq, "summary": summary,
             "next_actions": actions, "blockers": blockers,
             "observation_ids": obs_ids, "lease_hash": lease_hash},
            action,
        )

    def resume_task(self, project: str, actor: str, task_id: str) -> dict:
        """Build a fresh read-only canonical snapshot; never mint a lease.

        Deliberately does not query Mem0 or trust arbitrary semantic results.
        Re-evaluates project grants for EACH request in a single DB snapshot.
        """
        _valid_id(project, "project")
        _valid_id(actor, "actor")
        task_id = _uuid(task_id, "task id")
        with psycopg.connect(self.dsn, row_factory=dict_row, connect_timeout=10) as conn:
            with conn.transaction():
                conn.execute(
                    "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"
                )
                self._authorize(conn, project, actor, "task:read")
                self._authorize(conn, project, actor, "context:read")
                task = conn.execute(
                    "SELECT id,project_id,title,status,version,acceptance_criteria,"
                    "updated_at FROM si_tasks WHERE project_id=%s AND id=%s::uuid",
                    (project, task_id),
                ).fetchone()
                if task is None:
                    raise Missing("task not found in project")
                latest = conn.execute(
                    "SELECT id,agent_run_id,recorded_by,checkpoint_seq,"
                    "task_version_recorded,summary,next_actions,blockers,"
                    "trust_state,created_at FROM si_task_checkpoints "
                    "WHERE project_id=%s AND task_id=%s::uuid "
                    "ORDER BY checkpoint_seq DESC LIMIT 1",
                    (project, task_id),
                ).fetchone()
                checkpoint = None
                if latest is not None:
                    linked = conn.execute(
                        "SELECT o.id,o.agent_run_id,o.asserted_by,o.claim_text,"
                        "o.trust_state FROM si_checkpoint_observations l "
                        "JOIN si_observations o ON "
                        "o.project_id=l.project_id AND o.task_id=l.task_id "
                        "AND o.id=l.observation_id "
                        "WHERE l.project_id=%s AND l.task_id=%s::uuid "
                        "AND l.checkpoint_id=%s::uuid ORDER BY o.created_at,o.id",
                        (project, task_id, str(latest["id"])),
                    ).fetchall()
                    observations = []
                    for obs in linked:
                        sources = conn.execute(
                            "SELECT s.id,s.source_kind,s.source_revision,"
                            "s.digest_sha256 FROM si_observation_sources l "
                            "JOIN si_source_records s ON "
                            "s.project_id=l.project_id AND s.task_id=l.task_id "
                            "AND s.id=l.source_id "
                            "WHERE l.project_id=%s AND l.task_id=%s::uuid "
                            "AND l.observation_id=%s::uuid ORDER BY s.id",
                            (project, task_id, str(obs["id"])),
                        ).fetchall()
                        observations.append({
                            "observation_id": str(obs["id"]),
                            "run_id": str(obs["agent_run_id"]),
                            "asserted_by": obs["asserted_by"],
                            "claim": obs["claim_text"],
                            "trust_state": obs["trust_state"],
                            "sources": [
                                {"source_id": str(s["id"]),
                                 "kind": s["source_kind"],
                                 "revision": s["source_revision"],
                                 "digest_sha256": s["digest_sha256"]}
                                for s in sources
                            ],
                        })
                    checkpoint = {
                        "checkpoint_id": str(latest["id"]),
                        "checkpoint_seq": latest["checkpoint_seq"],
                        "agent_run_id": str(latest["agent_run_id"]),
                        "recorded_by": latest["recorded_by"],
                        "task_version_recorded": latest["task_version_recorded"],
                        "summary": latest["summary"],
                        "next_actions": latest["next_actions"],
                        "blockers": latest["blockers"],
                        "trust_state": latest["trust_state"],
                        "created_at": latest["created_at"].isoformat(),
                        "observations": observations,
                    }
                h = conn.execute(
                    "SELECT id,status,from_principal_id,to_principal_id,"
                    "checkpoint_id,checkpoint_seq,checkpoint_task_version "
                    "FROM si_handoffs WHERE project_id=%s AND task_id=%s::uuid "
                    "ORDER BY offered_at DESC,id DESC LIMIT 1",
                    (project, task_id),
                ).fetchone()
                bound_id = str(h["checkpoint_id"]) if h and h["checkpoint_id"] else None
                handoff = ({
                    "handoff_id": str(h["id"]), "status": h["status"],
                    "from_principal_id": h["from_principal_id"],
                    "to_principal_id": h["to_principal_id"],
                    "checkpoint_binding": (
                        "BOUND_R1C" if bound_id else "LEGACY_UNBOUND"
                    ),
                    "checkpoint_id": bound_id,
                    "checkpoint_seq": h["checkpoint_seq"],
                    "checkpoint_task_version": h["checkpoint_task_version"],
                    "checkpoint_is_latest": (
                        checkpoint is not None
                        and bound_id is not None
                        and checkpoint["checkpoint_id"] == bound_id
                    ),
                } if h else None)
                # If B has added a later checkpoint, preserve the original
                # *offered* snapshot. Never silently substitute latest for bound.
                handoff_checkpoint = None
                if bound_id:
                    if checkpoint and checkpoint["checkpoint_id"] == bound_id:
                        handoff_checkpoint = checkpoint
                    else:
                        bound = conn.execute(
                            "SELECT id,checkpoint_seq,agent_run_id,recorded_by,"
                            "task_version_recorded,summary,next_actions,blockers,"
                            "trust_state,created_at FROM si_task_checkpoints "
                            "WHERE project_id=%s AND task_id=%s::uuid AND id=%s::uuid",
                            (project, task_id, bound_id),
                        ).fetchone()
                        if not bound:
                            raise Conflict("bound checkpoint no longer available")
                        linked_ids = conn.execute(
                            "SELECT observation_id FROM si_checkpoint_observations "
                            "WHERE project_id=%s AND task_id=%s::uuid "
                            "AND checkpoint_id=%s::uuid ORDER BY observation_id",
                            (project, task_id, bound_id),
                        ).fetchall()
                        handoff_checkpoint = {
                            "checkpoint_id": str(bound["id"]),
                            "checkpoint_seq": bound["checkpoint_seq"],
                            "agent_run_id": str(bound["agent_run_id"]),
                            "recorded_by": bound["recorded_by"],
                            "task_version_recorded": bound["task_version_recorded"],
                            "summary": bound["summary"],
                            "next_actions": bound["next_actions"],
                            "blockers": bound["blockers"],
                            "trust_state": bound["trust_state"],
                            "created_at": bound["created_at"].isoformat(),
                            "observation_ids": [str(x["observation_id"]) for x in linked_ids],
                            "detail": "BOUND_HISTORICAL_REF_NOT_CURRENT_LATEST",
                        }
                return {
                    "source_of_truth": "postgresql",
                    "project_id": project,
                    "task": {
                        "task_id": str(task["id"]), "title": task["title"],
                        "status": task["status"], "version": task["version"],
                        "acceptance_criteria": task["acceptance_criteria"],
                        "updated_at": task["updated_at"].isoformat(),
                    },
                    "snapshot_status": (
                        "CHECKPOINT_AVAILABLE" if checkpoint else "NO_CHECKPOINT"
                    ),
                    "checkpoint": checkpoint,
                    "last_handoff": handoff,
                    "handoff_checkpoint": handoff_checkpoint,
                    "memory_status": "NOT_QUERIED",
                    "verified_completion": False,
                    "read_only": True,
                    "lease_issued": False,
                    "checkpoint_version_matches_task": (
                        checkpoint is not None
                        and checkpoint["task_version_recorded"] == task["version"]
                    ),
                }
