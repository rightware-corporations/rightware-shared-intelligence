"""R2 R1D G03: LIVE GitHub via authenticated SERVICE-only REST to Postgres LAB.

Destructive synthetic database setup. This script REFUSES all DB targets except
postgresql://...@localhost:5432/rw_test with RW_SI_ENVIRONMENT=lab.
Uses a server-only GitHub Actions token; neither bearer nor provider token
is placed in a JSON request, URL, persisted record, or output.
"""
from __future__ import annotations

import os
from uuid import uuid4

import psycopg
from fastapi.testclient import TestClient

from rightware_si.core import WorkCore
from rightware_si.http_api import create_app
from rightware_si.token_admin import issue_api_token
from rightware_si.lab_boundary import require_disposable_postgres

LIVE_SHA = "0c63b2f2d3d4cf00926752ab2c58d42ccbd64901"
LIVE_URL = ("https://github.com/rightware-corporations/"
            "rightware-shared-intelligence/actions/runs/43202560651")


def require(ok: bool) -> None:
    if not ok:
        raise AssertionError("R2 R1D lab HTTP real-provider gate did not match")


def main() -> None:
    dsn = os.environ.get("RW_TEST_DATABASE_URL", "")
    # No network, database, or destructive action occurs before the guard.
    require_disposable_postgres(dsn, expected_user="rw")
    require(dsn == os.environ.get("RW_SI_DATABASE_URL"))
    require(os.environ.get("RW_SI_ENVIRONMENT") == "lab")
    require(os.environ.get("RW_SI_ENABLE_R2_R1C_LAB_API") == "1")
    require(bool(os.environ.get("RW_SI_GITHUB_PROVIDER_TOKEN")))

    # No real users, tasks, agents, private repositories or arbitrary URLs.
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("TRUNCATE si_organizations,si_principals RESTART IDENTITY CASCADE")
        conn.execute("INSERT INTO si_organizations(id) VALUES('r1d-http-live-lab')")
        conn.execute("INSERT INTO si_projects(id,organization_id) "
                     "VALUES('alpha','r1d-http-live-lab')")
        conn.execute("INSERT INTO si_principals(id,principal_kind) VALUES"
                     "('lab-agent','AGENT'),('lab-verifier','SERVICE'),"
                     "('operator','HUMAN')")
        for perm in ("task:create", "task:manage", "task:execute", "task:read"):
            conn.execute("INSERT INTO si_project_grants "
                         "(project_id,principal_id,permission) "
                         "VALUES('alpha','lab-agent',%s)", (perm,))
        for perm in ("evidence:verify", "task:read", "evidence:read"):
            conn.execute("INSERT INTO si_project_grants "
                         "(project_id,principal_id,permission) "
                         "VALUES('alpha','lab-verifier',%s)", (perm,))

    core = WorkCore(dsn)
    task = core.create_task(
        "alpha", "lab-agent", "R1D lab live GitHub-through-REST (synthetic)",
        ["Exact workflow run must succeed"], "r1d-http-create-0001")
    task_id = task["task_id"]
    core.publish_task("alpha", "lab-agent", task_id, 1, "r1d-http-publish-0001")
    claim = core.claim_task("alpha", "lab-agent", task_id, 2, "r1d-http-claim-0001")
    evidence = core.submit_result(
        "alpha", "lab-agent", task_id, 3, claim["lease_token"],
        LIVE_URL, "r1d-http-submit-0001")
    require(evidence["version"] == 4 and evidence["status"] == "IN_REVIEW")

    policy_id = str(uuid4())
    with psycopg.connect(dsn) as conn:
        conn.execute(
            "INSERT INTO si_evidence_verification_policies("
            "id,project_id,task_id,evidence_id,policy_version,criteria_index,"
            "repository_owner,repository_name,repository_id,workflow_id,run_id,"
            "run_attempt,expected_sha,expected_event,created_by)"
            " VALUES(%s::uuid,'alpha',%s::uuid,%s::uuid,1,0,"
            "'rightware-corporations','rightware-shared-intelligence',"
            "1452533938,415280241,43202560651,1,%s,'push','operator')",
            (policy_id, task_id, evidence["evidence_id"], LIVE_SHA))

    service_token = issue_api_token(dsn, "lab-verifier", 1)[1]
    app = create_app(dsn)
    route = (f"/v1/projects/alpha/evidence/"
             f"{evidence['evidence_id']}/verify")
    headers = {
        "Authorization": f"Bearer {service_token}",
        "Idempotency-Key": "r1d-http-live-verify-0001",
    }
    body = {"policy_id": policy_id, "expected_task_version": 4}
    with TestClient(app) as http:
        first = http.post(route, json=body, headers=headers)
        require(first.status_code == 200)
        outcome = first.json()
        require(outcome["result"] == "CHECKED_PASS")
        require(outcome["reason_code"] == "EXPECTED_WORKFLOW_RUN_SUCCEEDED")
        require(outcome["observation_channel"] == "LIVE_HTTPS")
        require(outcome["verified_by"] == "lab-verifier")
        require(outcome["task_approved"] is False)
        require(outcome["review_decision"] == "NOT_IMPLEMENTED_R2_R1B")
        require(outcome["evidence_id"] == evidence["evidence_id"])
        require(outcome["policy_id"] == policy_id)
        duplicate = http.post(route, json=body, headers=headers)
        require(duplicate.status_code == 200)
        require(duplicate.json()["attempt_id"] == outcome["attempt_id"])

        with psycopg.connect(dsn) as conn:
            a = conn.execute("SELECT result,observation_channel FROM "
                             "si_verification_attempts "
                             "WHERE project_id='alpha' AND task_id=%s::uuid",
                             (task_id,)).fetchall()
            e = conn.execute("SELECT verification_state FROM si_evidence_refs "
                             "WHERE id=%s::uuid", (evidence["evidence_id"],)).fetchone()
            ev = conn.execute("SELECT count(*) FROM si_continuity_events "
                              "WHERE task_id=%s::uuid AND event_type='EVIDENCE_CHECKED'",
                              (task_id,)).fetchone()[0]
            require(len(a) == 1 and a[0] == ("CHECKED_PASS", "LIVE_HTTPS"))
            require(e[0] == "REFERENCED" and ev == 1)
            conn.execute("DELETE FROM si_project_grants "
                         "WHERE project_id='alpha' AND principal_id='lab-verifier' "
                         "AND permission='evidence:verify'")
        revoked = http.post(route, json=body, headers=headers)
        require(revoked.status_code == 403)

    require(core.get_task("alpha", "lab-agent", task_id)["status"] == "IN_REVIEW")
    # Never print provider token, bearer credential, DSN, or raw provider JSON.
    print("WORK03B_R2_R1D_LAB_HTTP_GITHUB_LIVE_PASS "
          "transport=GitHub_API_HTTPS provider_live=true "
          "bearer_service=true pinned_policy=true postgres_append_only=true "
          "same_key_replay=true permission_revocation_denied=true "
          "evidence_state=REFERENCED task_state=IN_REVIEW "
          "no_review=true no_done=true synthetic_lab=true")


if __name__ == "__main__":
    main()
