"""WORK-02B bearer credential verification — local experimental gateway.

Token identity is cryptographic and separate from descriptive agent_id in memory.
A trusted operator issues tokens offline; public API has no token-issuance route.
"""
from __future__ import annotations

import hashlib
import re

import psycopg
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from psycopg.rows import dict_row


_TOKEN_PATTERN = re.compile(r"^rwsi_[A-Za-z0-9_-]{40,100}$")
_bearer = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Invalid or expired bearer credential",
        headers={"WWW-Authenticate": "Bearer"},
    )


def resolve_principal(
    dsn: str, credentials: HTTPAuthorizationCredentials | None,
) -> str:
    """Look up a high-entropy token hash; do not log or return the credential."""
    if (
        credentials is None
        or credentials.scheme.lower() != "bearer"
        or not _TOKEN_PATTERN.fullmatch(credentials.credentials)
    ):
        raise _unauthorized()
    digest = hashlib.sha256(credentials.credentials.encode("ascii")).hexdigest()
    with psycopg.connect(dsn, row_factory=dict_row, connect_timeout=10) as conn:
        row = conn.execute(
            "SELECT t.principal_id FROM si_api_tokens AS t "
            "JOIN si_principals AS p ON p.id=t.principal_id "
            "WHERE t.secret_sha256=%s AND t.revoked_at IS NULL AND t.expires_at>now()",
            (digest,),
        ).fetchone()
    if row is None:
        raise _unauthorized()
    return row["principal_id"]


def make_principal_dependency(dsn: str):
    """Create a FastAPI dependency bound to one explicitly configured database."""
    def principal(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    ) -> str:
        return resolve_principal(dsn, credentials)
    return principal
