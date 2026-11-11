"""Offline, trusted-operator API token issuer/revoker for WORK-02B.

Only run with a DATABASE_URL on an isolated administration machine. There is no
remote token issuance API. Generated secret is printed exactly once to stdout.
"""
from __future__ import annotations

import argparse
from datetime import timedelta
import hashlib
import os
import secrets
from uuid import uuid4

import psycopg


def issue_api_token(dsn: str, principal: str, ttl_hours: int = 24) -> tuple[str, str]:
    if not 1 <= ttl_hours <= 720:
        raise ValueError("ttl_hours must be between 1 and 720")
    raw = "rwsi_" + secrets.token_urlsafe(40)
    digest = hashlib.sha256(raw.encode("ascii")).hexdigest()
    token_id = str(uuid4())
    with psycopg.connect(dsn) as conn:
        row = conn.execute("SELECT 1 FROM si_principals WHERE id=%s", (principal,)).fetchone()
        if row is None:
            raise ValueError("principal does not exist; create and grant it first")
        conn.execute(
            "INSERT INTO si_api_tokens(id,principal_id,secret_sha256,expires_at) "
            "VALUES (%s::uuid,%s,%s,now()+(%s * interval '1 hour'))",
            (token_id, principal, digest, ttl_hours),
        )
    return token_id, raw


def revoke_api_token(dsn: str, token_id: str) -> bool:
    from uuid import UUID
    UUID(token_id)
    with psycopg.connect(dsn) as conn:
        cur = conn.execute(
            "UPDATE si_api_tokens SET revoked_at=now() "
            "WHERE id=%s::uuid AND revoked_at IS NULL",
            (token_id,),
        )
        return cur.rowcount == 1


def main() -> None:
    parser = argparse.ArgumentParser(description="WORK-02B local API-key administration")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("issue")
    add.add_argument("--principal", required=True)
    add.add_argument("--ttl-hours", type=int, default=24)
    revoke = sub.add_parser("revoke")
    revoke.add_argument("--id", required=True)
    args = parser.parse_args()
    dsn = os.environ.get("RW_SI_DATABASE_URL")
    if not dsn:
        parser.error("RW_SI_DATABASE_URL environment variable required")
    if args.command == "issue":
        token_id, secret = issue_api_token(dsn, args.principal, args.ttl_hours)
        print(f"token_id={token_id}")
        print(f"token={secret}")
        print("Store the token in a secrets manager. It cannot be displayed again.")
    else:
        print("revoked" if revoke_api_token(dsn, args.id) else "not_found_or_already_revoked")


if __name__ == "__main__":
    main()
