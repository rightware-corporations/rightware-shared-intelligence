"""R2-R1B: isolated actual GitHub API -> verified ledger PostgreSQL smoke.

Refuses databases except disposable localhost:5432/rw_test and never touches
main, Jarvis, production databases or customer data. This script deliberately
TRUNCATES the synthetic test DB; never deploy to a non-lab environment.
"""
from __future__ import annotations

import os
from uuid import uuid4

import psycopg
from fastapi.security import HTTPAuthorizationCredentials

from rightware_si.api_auth import resolve_principal
from rightware_si.core import AccessDenied, WorkCore
from rightware_si.token_admin import issue_api_token
from rightware_si.verification_ledger import EvidenceLedger
from rightware_si.lab_boundary import require_disposable_postgres


SHA="0c63b2f2d3d4cf00926752ab2c58d42ccbd64901"
URL=("https://github.com/rightware-corporations/"
     "rightware-shared-intelligence/actions/runs/43202560651")


def require(condition: bool):
    if not condition:
        raise AssertionError("evidence ledger live gate mismatch")


def main() -> None:
    dsn=os.environ.get("RW_TEST_DATABASE_URL","")
    require_disposable_postgres(dsn, expected_user="rw")
    require(os.environ.get("RW_SI_DATABASE_URL")==dsn)
    require(bool(os.environ.get("GITHUB_TOKEN")))

    with psycopg.connect(dsn,autocommit=True) as conn:
        conn.execute("TRUNCATE si_organizations,si_principals RESTART IDENTITY CASCADE")
        conn.execute("INSERT INTO si_organizations(id) VALUES('r2-live-lab')")
        conn.execute("INSERT INTO si_projects(id,organization_id) "
                     "VALUES('alpha','r2-live-lab')")
        conn.execute("INSERT INTO si_principals(id,principal_kind) VALUES"
                     "('lab-agent','AGENT'),('lab-verifier','SERVICE'),('operator','HUMAN')")
        for perm in ("task:create","task:manage","task:execute","task:read"):
            conn.execute("INSERT INTO si_project_grants(project_id,principal_id,permission)"
                         " VALUES('alpha','lab-agent',%s)",(perm,))
        for perm in ("evidence:verify","task:read","evidence:read"):
            conn.execute("INSERT INTO si_project_grants(project_id,principal_id,permission)"
                         " VALUES('alpha','lab-verifier',%s)",(perm,))
    core=WorkCore(dsn)
    task=core.create_task("alpha","lab-agent","Live GitHub verified run (synthetic)",
                          ["Workflow run exact matching succeeds"],"r2-live-create-1")
    tid=task["task_id"]
    core.publish_task("alpha","lab-agent",tid,1,"r2-live-publish-1")
    claim=core.claim_task("alpha","lab-agent",tid,2,"r2-live-claim-1")
    evidence=core.submit_result("alpha","lab-agent",tid,3,claim["lease_token"],
                                URL,"r2-live-submit-1")
    require(evidence["status"]=="IN_REVIEW" and evidence["version"]==4)
    policy_id=str(uuid4())
    with psycopg.connect(dsn) as conn:
        conn.execute(
            "INSERT INTO si_evidence_verification_policies("
            "id,project_id,task_id,evidence_id,policy_version,criteria_index,"
            "repository_owner,repository_name,repository_id,workflow_id,run_id,"
            "run_attempt,expected_sha,expected_event,created_by)"
            " VALUES(%s::uuid,'alpha',%s::uuid,%s::uuid,1,0,"
            "'rightware-corporations','rightware-shared-intelligence',"
            "1452533938,415280241,43202560651,1,%s,'push','operator')",
            (policy_id,tid,evidence["evidence_id"],SHA),
        )
    raw_service_token=issue_api_token(dsn,"lab-verifier",1)[1]
    verifier=resolve_principal(dsn,HTTPAuthorizationCredentials(
        scheme="Bearer",credentials=raw_service_token,
    ))
    require(verifier=="lab-verifier")
    ledger=EvidenceLedger(dsn)
    record=ledger.verify_and_record(
        "alpha",verifier,policy_id,4,"r2-live-verify-1",
        github_token=os.environ["GITHUB_TOKEN"],
    )
    require(record["result"]=="CHECKED_PASS")
    require(record["observation_channel"]=="LIVE_HTTPS")
    require(record["reason_code"]=="EXPECTED_WORKFLOW_RUN_SUCCEEDED")
    require(record["review_decision"]=="NOT_IMPLEMENTED_R2_R1B")
    require(record["task_approved"] is False)
    duplicate=ledger.verify_and_record(
        "alpha",verifier,policy_id,4,"r2-live-verify-1",
        github_token=os.environ["GITHUB_TOKEN"],
    )
    require(duplicate["attempt_id"]==record["attempt_id"])
    require(core.get_task("alpha","lab-agent",tid)["status"]=="IN_REVIEW")
    scoped=ledger.list_attempts("alpha",verifier,tid)
    require(len(scoped)==1 and scoped[0]["attempt_id"]==record["attempt_id"])
    with psycopg.connect(dsn) as conn:
        rows=conn.execute(
            "SELECT verification_state FROM si_evidence_refs WHERE id=%s::uuid",
            (evidence["evidence_id"],),
        ).fetchall()
        require(len(rows)==1 and rows[0][0]=="REFERENCED")
        events=conn.execute(
            "SELECT id FROM si_continuity_events WHERE task_id=%s::uuid "
            "AND event_type='EVIDENCE_CHECKED'",
            (tid,),
        ).fetchall()
        require(len(events)==1)
        conn.execute("DELETE FROM si_project_grants "
                     "WHERE project_id='alpha' AND principal_id='lab-verifier' "
                     "AND permission='evidence:read'")
    try:
        ledger.list_attempts("alpha",verifier,tid)
    except AccessDenied:
        pass
    else:
        raise AssertionError("revoked evidence reader was not denied")

    print(
        "WORK03B_R2_R1B_LEDGER_LIVE_PASS "
        "provider=github_api result=CHECKED_PASS "
        "postgres_append_only=true independent_service=true "
        "scope_checked=true revoked_read_denied=true "
        "idempotent=true task_status=IN_REVIEW "
        "evidence_state=REFERENCED no_review=true no_done=true "
        "synthetic_lab=true"
    )


if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        # Never emit DB DSN, tokens, provider bodies or test secrets.
        print("WORK03B_R2_R1B_LEDGER_LIVE_FAIL "+type(exc).__name__)
        raise SystemExit(1) from None
