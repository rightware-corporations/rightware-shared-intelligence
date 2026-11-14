"""G01-12: native PostgreSQL logical backup + restore of synthetic lab evidence.

Runs ONLY after dedicated G03 LAB CI smoke. Uses an ephemeral separate DB.
No production connections, no private source records, no backup upload.
The archive is temporary and deleted; no secrets are printed.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from rightware_si.core import Conflict
from rightware_si.lab_boundary import require_disposable_postgres
from rightware_si.policy_lifecycle import PolicyLifecycle


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError("G01 logical restore: " + message)


def snapshot(dsn: str) -> dict:
    """Data-equivalence oracle; no tokens or provider bodies are returned."""
    with psycopg.connect(dsn, row_factory=dict_row, connect_timeout=10) as conn:
        policy = conn.execute(
            "SELECT id::text AS id, project_id, task_id::text AS task_id, "
            "evidence_id::text AS evidence_id, created_by, policy_version "
            "FROM si_evidence_verification_policies ORDER BY id"
        ).fetchall()
        events = conn.execute(
            "SELECT id::text AS id, sequence, project_id, task_id::text AS task_id, "
            "policy_id::text AS policy_id, event_type, actor_id, "
            "idempotency_key, valid_until, reason_code, recorded_at "
            "FROM si_policy_lifecycle_events ORDER BY sequence"
        ).fetchall()
        attempts = conn.execute(
            "SELECT id::text AS id, policy_id::text AS policy_id, "
            "task_id::text AS task_id, verified_by, idempotency_key, "
            "result, reason_code, observation_channel "
            "FROM si_verification_attempts ORDER BY id"
        ).fetchall()
        tasks = conn.execute(
            "SELECT id::text AS id, project_id, status, version "
            "FROM si_tasks ORDER BY id"
        ).fetchall()
        refs = conn.execute(
            "SELECT id::text AS id, project_id, verification_state "
            "FROM si_evidence_refs ORDER BY id"
        ).fetchall()
    return {
        "policies": policy, "events": events,
        "attempts": attempts, "tasks": tasks, "evidence": refs,
    }


def native_postgres_tool(command: str, dsn: str, backup_dir: Path,
                         archive: str, destination: str | None = None) -> None:
    """Run vendor postgres:16 tools, suppressing stdout and error details."""
    uri = urlsplit(dsn)
    environment = dict(os.environ)
    environment["PGPASSWORD"] = unquote(uri.password or "")
    container = [
        "docker", "run", "--rm", "--network", "host",
        "--volume", f"{backup_dir}:/backup", "--env", "PGPASSWORD",
        "postgres:16",
    ]
    common = ["--host", "127.0.0.1", "--port", "5432",
              "--username", "rw", "--no-owner", "--no-acl"]
    if command == "pg_dump":
        args = ["pg_dump", *common, "--format", "custom",
                "--dbname", "rw_test", "--file", "/backup/" + archive]
    elif command == "pg_restore" and destination is not None:
        require(destination.startswith("rw_g01_restore_"), "invalid target")
        args = ["pg_restore", *common, "--exit-on-error",
                "--dbname", destination, "/backup/" + archive]
    else:
        raise ValueError("unsupported PostgreSQL restore operation")
    try:
        result = subprocess.run(
            [*container, *args], env=environment,
            capture_output=True, text=True, timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise RuntimeError("isolated native PostgreSQL tool unavailable") from None
    if result.returncode != 0:
        # Do not print vendor diagnostics: credentials are deliberately masked.
        raise RuntimeError(f"isolated {command} failed (exit {result.returncode})")


def main() -> None:
    dsn = os.environ.get("RW_TEST_DATABASE_URL", "")
    # All destructive operations are behind the same strict loopback guard.
    require_disposable_postgres(dsn, expected_user="rw")
    require(dsn == os.environ.get("RW_SI_DATABASE_URL"), "DSN mismatch")
    require(os.environ.get("RW_SI_ENVIRONMENT") == "lab", "not a lab")
    require(os.environ.get("RW_SI_ENABLE_R2_R1C_LAB_API") == "1",
            "R2 LAB flag missing")
    require(os.environ.get("RW_SI_ENABLE_R2_G01_LAB_POLICY") == "1",
            "G01 LAB flag missing")

    original = snapshot(dsn)
    require(len(original["policies"]) == 1, "G03 policy fixture not present")
    require([x["event_type"] for x in original["events"]] ==
            ["PROPOSED", "ACTIVATED", "DISABLED"],
            "G03 must have one terminal disabled lifecycle")
    require(len(original["attempts"]) == 1 and
            original["attempts"][0]["result"] == "CHECKED_PASS" and
            original["attempts"][0]["observation_channel"] == "LIVE_HTTPS",
            "LIVE G03 check not present")
    require(len(original["tasks"]) == 1 and
            original["tasks"][0]["status"] == "IN_REVIEW", "task must not be DONE")
    require(len(original["evidence"]) == 1 and
            original["evidence"][0]["verification_state"] == "REFERENCED",
            "evidence must remain REFERENCED")

    # Construct the administrative URL only after validating the exact test
    # DSN. The target DB name is generated by this process, not user input.
    admin_dsn = dsn[:-len("/rw_test")] + "/postgres"
    target = "rw_g01_restore_" + uuid4().hex[:10]
    restored_dsn = dsn[:-len("/rw_test")] + "/" + target
    created = False
    try:
        with tempfile.TemporaryDirectory(prefix="rw-g01-restore-") as folder:
            archive = "synthetic-g01.archive"
            backup_dir = Path(folder)
            native_postgres_tool("pg_dump", dsn, backup_dir, archive)
            require((backup_dir / archive).is_file() and
                    (backup_dir / archive).stat().st_size > 1000,
                    "native archive missing or empty")

            with psycopg.connect(admin_dsn, autocommit=True,
                                 connect_timeout=10) as admin:
                existing = admin.execute(
                    "SELECT 1 FROM pg_database WHERE datname=%s",
                    (target,)).fetchone()
                require(existing is None, "restore target already exists")
                admin.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target)))
                created = True

            native_postgres_tool(
                "pg_restore", dsn, backup_dir, archive, destination=target)
            restored = snapshot(restored_dsn)
            require(restored == original, "restored policy/evidence differs")

            policy = original["policies"][0]
            with psycopg.connect(restored_dsn, row_factory=dict_row,
                                 connect_timeout=10) as conn:
                try:
                    PolicyLifecycle.require_active(
                        conn, policy["project_id"], policy["id"])
                except Conflict:
                    pass
                else:
                    raise AssertionError(
                        "G01 restore erroneously activated a revoked policy")

            with psycopg.connect(restored_dsn, connect_timeout=10) as conn:
                try:
                    conn.execute(
                        "DELETE FROM si_policy_lifecycle_events "
                        "WHERE policy_id=%s::uuid", (policy["id"],))
                except psycopg.errors.CheckViolation:
                    pass
                else:
                    raise AssertionError(
                        "G01 restored append-only trigger not enforced")
    finally:
        if created:
            # Only drop the random database created by this invocation.
            # No DROP against rw_test or any preexisting database.
            with psycopg.connect(admin_dsn, autocommit=True,
                                 connect_timeout=10) as admin:
                admin.execute(
                    sql.SQL("DROP DATABASE {}").format(sql.Identifier(target)))

    print(
        "WORK03B_R2_R1D_G01_NATIVE_RESTORE_PASS "
        "native_pg_dump=true native_pg_restore=true "
        "separate_ephemeral_database=true full_archive=true "
        "events_immutable=true revocation_survives_restore=true "
        "live_provider_attempt_preserved=true task_in_review=true "
        "target_cleaned=true synthetic_only=true no_done=true"
    )


if __name__ == "__main__":
    main()
