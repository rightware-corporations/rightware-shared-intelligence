"""EXPERIMENTAL Mem0 REST adapter. Not a multi-tenant authorization boundary.

Mem0 provides memory persistence and retrieval. This adapter adds project
naming, a typed handoff claim, and defensive response scope checks. It does
not turn agent statements into verified facts or approved task states.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_ALLOWED_KINDS = frozenset({"note", "observation", "handoff_claim"})


def _validate_id(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"{label} must be 1-64 safe identifier characters")
    return value


@dataclass(frozen=True, slots=True)
class MemoryScope:
    organization: str
    project: str

    def __post_init__(self) -> None:
        _validate_id(self.organization, "organization")
        _validate_id(self.project, "project")

    @property
    def mem0_user_id(self) -> str:
        # A namespace convention, NOT authorization. Enforce external policy.
        return f"rw:{self.organization}:{self.project}"


@dataclass(frozen=True, slots=True)
class HandoffClaim:
    task_id: str
    agent_id: str
    summary: str
    evidence_url: str | None = None

    def __post_init__(self) -> None:
        _validate_id(self.task_id, "task_id")
        _validate_id(self.agent_id, "agent_id")
        if not isinstance(self.summary, str) or not self.summary.strip() or len(self.summary) > 8000:
            raise ValueError("summary must have 1-8000 nonblank characters")
        if self.evidence_url is not None:
            parsed = urlparse(self.evidence_url)
            if parsed.scheme != "https" or not parsed.hostname:
                raise ValueError("evidence_url must be an absolute HTTPS URL")
            if parsed.username or parsed.password or parsed.fragment:
                raise ValueError("evidence_url cannot contain credentials or fragment")


class Mem0HTTPError(RuntimeError):
    """Transport or remote service error; does not echo credentials or payload."""


class MemoryScopeError(RuntimeError):
    """Upstream returned a memory from an unexpected or absent project scope."""


class Mem0HTTPClient:
    """Thin Mem0 self-hosted HTTP client.

    API key must belong to a trusted service account. Do not expose this class
    directly as a public multi-tenant API or accept arbitrary scope from users.
    """

    def __init__(self, base_url: str, api_key: str, *, timeout: float = 10.0) -> None:
        parsed = urlparse(base_url)
        loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
        if parsed.scheme != "https" and not (parsed.scheme == "http" and loopback):
            raise ValueError("Mem0 HTTP must use HTTPS, except local loopback")
        if not parsed.netloc or parsed.username or parsed.password or parsed.path.strip("/") or parsed.query or parsed.fragment:
            raise ValueError("base_url must be an origin without path, query or credentials")
        if not api_key or len(api_key) < 16:
            raise ValueError("api_key must be non-empty and at least 16 characters")
        if timeout <= 0 or timeout > 120:
            raise ValueError("timeout must be in (0,120]")
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if path not in {"/memories", "/search"}:
            raise ValueError("unsupported Mem0 path")
        req = Request(
            self._base_url + path,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json", "X-API-Key": self._api_key},
        )
        try:
            with urlopen(req, timeout=self._timeout) as response:
                data = json.loads(response.read(2_000_000).decode("utf-8"))
        except HTTPError as exc:
            raise Mem0HTTPError(f"Mem0 HTTP status {exc.code}") from None
        except (URLError, TimeoutError, OSError, ValueError, UnicodeError) as exc:
            raise Mem0HTTPError(f"Mem0 request failed ({type(exc).__name__})") from None
        if not isinstance(data, dict):
            raise Mem0HTTPError("Mem0 response is not a JSON object")
        return data


class SharedMemory:
    """Project-scoped adapter for a *trusted internal caller*.

    Scope access is enforced outside this layer. In production a gateway must
    derive organization/project from the authenticated principal.
    """

    def __init__(self, http_client: Mem0HTTPClient) -> None:
        self._http = http_client

    def add(
        self, scope: MemoryScope, agent_id: str, text: str, *,
        kind: str = "note", source: str | None = None,
    ) -> dict[str, Any]:
        _validate_id(agent_id, "agent_id")
        if kind not in _ALLOWED_KINDS:
            raise ValueError("unsupported memory kind")
        if not isinstance(text, str) or not text.strip() or len(text) > 10_000:
            raise ValueError("memory text must have 1-10000 nonblank characters")
        meta = {
            "rw_organization": scope.organization,
            "rw_project": scope.project,
            "rw_kind": kind,
            "rw_claim_state": "unverified",
            "rw_created_utc": datetime.now(timezone.utc).isoformat(),
        }
        if source:
            if len(source) > 512:
                raise ValueError("source too long")
            meta["rw_source"] = source
        return self._http.post("/memories", {
            "messages": [{"role": "user", "content": text}],
            "user_id": scope.mem0_user_id,
            "agent_id": agent_id,
            "metadata": meta,
            # Disables automatic fact extraction. Embedding still requires a model.
            "infer": False,
        })

    def handoff(self, scope: MemoryScope, claim: HandoffClaim) -> dict[str, Any]:
        event_id = str(uuid4())
        text = (
            f"Task: {claim.task_id}\nAgent: {claim.agent_id}\n"
            f"Handoff assertion (not independently verified): {claim.summary.strip()}"
        )
        return self.add(
            scope, claim.agent_id, text, kind="handoff_claim",
            source=claim.evidence_url or f"handoff:{event_id}",
        )

    def search(self, scope: MemoryScope, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
        if not isinstance(query, str) or not query.strip() or len(query) > 2000:
            raise ValueError("query must have 1-2000 nonblank characters")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 20:
            raise ValueError("limit must be an integer between 1 and 20")
        response = self._http.post("/search", {
            "query": query,
            "filters": {"user_id": scope.mem0_user_id},
            "top_k": limit,
        })
        rows = response.get("results")
        if not isinstance(rows, list):
            raise Mem0HTTPError("Mem0 response missing results list")
        for row in rows:
            if not isinstance(row, dict) or row.get("user_id") != scope.mem0_user_id:
                raise MemoryScopeError("Mem0 returned missing or cross-project scope")
        return rows
