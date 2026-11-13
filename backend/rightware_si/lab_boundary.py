"""Fail-closed database boundary for disposable synthetic laboratory scripts."""
from __future__ import annotations

import ipaddress
import os
import socket
from typing import Mapping
from urllib.parse import urlsplit


def require_disposable_postgres(
    dsn: str, *, expected_user: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> None:
    """Reject query/env hostaddr routing, services and non-loopback targets.

    libpq can use hostaddr from a query or PGHOSTADDR even if URI host appears
    to be localhost. Never run TRUNCATE without this guard.
    """
    msg = "Refusing non-disposable PostgreSQL laboratory connection"
    if not isinstance(dsn, str) or not dsn:
        raise RuntimeError(msg)
    env = os.environ if environ is None else environ
    if any(env.get(name) for name in ("PGHOSTADDR", "PGSERVICE", "PGSERVICEFILE")):
        raise RuntimeError(msg)
    try:
        url = urlsplit(dsn)
        if not (url.scheme in ("postgres", "postgresql")
                and url.hostname in ("127.0.0.1", "localhost")
                and url.port == 5432 and url.path == "/rw_test"
                and bool(url.username) and not url.query and not url.fragment
                and (expected_user is None or url.username == expected_user)):
            raise RuntimeError(msg)
        if url.hostname == "localhost":
            candidates = socket.getaddrinfo("localhost", 5432,
                                            type=socket.SOCK_STREAM)
            if not candidates or any(
                    not ipaddress.ip_address(result[4][0]).is_loopback
                    for result in candidates):
                raise RuntimeError(msg)
    except (ValueError, TypeError, OSError, IndexError, AttributeError):
        raise RuntimeError(msg) from None
