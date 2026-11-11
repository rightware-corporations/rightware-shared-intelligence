"""WORK-02C: authenticated, project-scoped contextual read model.

PostgreSQL is authoritative. Mem0 supplies unverified semantic candidates.
This module never promotes model text to verified tasks or decisions.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from rightware_si.core import AccessDenied, Missing, WorkCore
from rightware_si.memory import MemoryScope, MemoryScopeError, Mem0HTTPError


class SemanticUnavailable(RuntimeError):
    """Semantic backend disabled or unavailable; authoritative data remains readable."""


class ScopedContextReader:
    def __init__(self, dsn: str, memory: Any | None = None) -> None:
        self._dsn = dsn
        self._memory = memory

    def _scope(self, project: str, principal: str, permission: str) -> MemoryScope:
        # Never accept an organization or Mem0 user_id from a client.
        with psycopg.connect(self._dsn, row_factory=dict_row, connect_timeout=10) as conn:
            WorkCore._authorize(conn, project, principal, permission)
            row = conn.execute(
                "SELECT organization_id FROM si_projects WHERE id=%s", (project,),
            ).fetchone()
        if row is None:
            raise Missing("project not found")
        return MemoryScope(row["organization_id"], project)

    @staticmethod
    def _safe_rows(rows: list[dict]) -> list[dict]:
        # Mem0 content is UNTRUSTED. Do not copy arbitrary upstream metadata,
        # user/agent identities or arbitrary score/trust assertions into clients.
        safe = []
        for row in rows:
            metadata = row.get("metadata")
            if not isinstance(metadata, dict):
                metadata = {}
            source = metadata.get("rw_source")
            if not isinstance(source, str) or len(source) > 512:
                source = None
            raw_text = row.get("memory")
            if not isinstance(raw_text, str):
                continue
            safe.append({
                "id": str(row.get("id", ""))[:128],
                "text": raw_text[:3000],
                "source_ref": source,
                "trust": "UNVERIFIED",
                "kind": "semantic_memory",
            })
        return safe

    def _search(self, scope: MemoryScope, query: str, limit: int) -> list[dict]:
        if self._memory is None:
            raise SemanticUnavailable("semantic memory is disabled")
        if not isinstance(query, str) or not query.strip() or len(query) > 2000:
            raise ValueError("query must contain 1-2000 characters")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 10:
            raise ValueError("limit must be 1-10")
        try:
            rows = self._memory.search(scope, query, limit=limit)
        except (Mem0HTTPError, MemoryScopeError, OSError) as exc:
            # Never expose upstream payloads, credentials, raw memory or URL.
            raise SemanticUnavailable("semantic memory backend unavailable") from None
        if not isinstance(rows, list):
            raise SemanticUnavailable("unexpected memory backend response")
        for row in rows:
            if not isinstance(row, dict) or row.get("user_id") != scope.mem0_user_id:
                # Defence in depth: do not rely solely on provider-side filtering.
                raise SemanticUnavailable("memory returned outside authorized scope")
            meta = row.get("metadata")
            if isinstance(meta, dict) and (
                ("rw_organization" in meta and meta["rw_organization"] != scope.organization)
                or ("rw_project" in meta and meta["rw_project"] != scope.project)
            ):
                raise SemanticUnavailable("memory metadata violates project scope")
        return self._safe_rows(rows)

    def search(self, project: str, principal: str, query: str, limit: int = 5) -> dict:
        scope = self._scope(project, principal, "memory:read")
        return {
            "project_id": project,
            "organization_id": scope.organization,
            "memory_status": "available",
            "memories": self._search(scope, query, limit),
        }

    def context(self, project: str, principal: str, query: str,
                task_id: str | None = None, limit: int = 5) -> dict:
        scope = self._scope(project, principal, "context:read")
        task = None
        if task_id is not None:
            # Authoritative task data is always queried from PostgreSQL.
            task = WorkCore(self._dsn).get_task(project, principal, str(UUID(task_id)))
        try:
            memories = self._search(scope, query, limit)
            status = "available"
        except SemanticUnavailable:
            memories = []
            status = "unavailable" if self._memory is not None else "disabled"
        return {
            "project_id": project,
            "organization_id": scope.organization,
            "task": task,
            "memory_status": status,
            "memories": memories,
            "memory_trust": "UNVERIFIED",
            "source_of_truth": "postgresql",
        }
