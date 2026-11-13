"""R2 R1B real PostgreSQL + isolated provider tests (not production approval)."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import os
import unittest
from rightware_si.lab_boundary import require_disposable_postgres, is_disposable_postgres

import httpx
import psycopg
from fastapi.security import HTTPAuthorizationCredentials

from rightware_si.api_auth import resolve_principal
from rightware_si.core import AccessDenied, Conflict, WorkCore
from rightware_si.token_admin import issue_api_token
from rightware_si.verification_ledger import EvidenceLedger

_DSN=os.environ.get("RW_TEST_DATABASE_URL","")
_SAFE = is_disposable_postgres(_DSN, expected_user="rw")
_SHA="0c63b2f2d3d4cf00926752ab2c58d42ccbd64901"
_URL="https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43202560651"


def provider_record(**changes):
    record={
        "id":43202560651,
        "repository":{"id":1452533938,
                      "full_name":"rightware-corporations/rightware-shared-intelligence"},
        "head_repository":{"id":1452533938},
        "workflow_id":415280241,
        "run_attempt":1,
        "head_sha":_SHA,
        "status":"completed",
        "conclusion":"success",
        "event":"push",
    }
    return dict(record,**changes)


@unittest.skipUnless(_SAFE,"requires disposable local PostgreSQL /rw_test")
class VerificationLedgerLabTests(unittest.TestCase):
    def setUp(self):
        # Check again at use-time: PGHOSTADDR may change after module import.
        require_disposable_postgres(_DSN, expected_user="rw")
        with psycopg.connect(_DSN,autocommit=True) as conn:
            conn.execute("TRUNCATE si_organizations,si_principals RESTART IDENTITY CASCADE")
            conn.execute("INSERT INTO si_organizations(id) VALUES('r2lab'),('otherorg')")
            conn.execute("INSERT INTO si_projects(id,organization_id) VALUES"
                         "('alpha','r2lab'),('beta','otherorg')")
            conn.execute("INSERT INTO si_principals(id,principal_kind) VALUES"
                         "('worker','AGENT'),('verifier','SERVICE'),"
                         "('no-grant','SERVICE'),('operator','HUMAN'),('other','SERVICE')")
            perms={
                "worker":["task:create","task:manage","task:execute","task:read"],
                "verifier":["task:read","evidence:verify","evidence:read"],
                "no-grant":["task:read"],
            }
            for actor,grants in perms.items():
                for grant in grants:
                    conn.execute("INSERT INTO si_project_grants"
                                 "(project_id,principal_id,permission) VALUES('alpha',%s,%s)",
                                 (actor,grant))
            conn.execute("INSERT INTO si_project_grants"
                         "(project_id,principal_id,permission) VALUES"
                         "('beta','other','evidence:verify'),"
                         "('beta','other','task:read')")
        self.tokens={actor:issue_api_token(_DSN,actor,4)[1]
                     for actor in ("worker","verifier","no-grant","other")}
        self.core=WorkCore(_DSN)
        self.ledger=EvidenceLedger(_DSN)
        self.task=self.core.create_task("alpha","worker","Synthetic evidence-backed work",
            ["Expected workflow run must be completed successfully"],f"r2-create-{uuid4().hex[:8]}")
        self.task_id=self.task["task_id"]
        self.core.publish_task("alpha","worker",self.task_id,1,f"r2-publish-{uuid4().hex[:8]}")
        lease=self.core.claim_task("alpha","worker",self.task_id,2,
                                  f"r2-claim-{uuid4().hex[:8]}")["lease_token"]
        submitted=self.core.submit_result("alpha","worker",self.task_id,3,lease,
                                           _URL,f"r2-submit-{uuid4().hex[:8]}")
        self.assertEqual(submitted["status"],"IN_REVIEW")
        self.assertEqual(submitted["version"],4)
        self.evidence_id=submitted["evidence_id"]
        self.policy_id=self.seed_policy()

    def seed_policy(self,version=1,expected_sha=_SHA,created_by="operator",criteria_index=0):
        policy_id=str(uuid4())
        with psycopg.connect(_DSN) as conn:
            conn.execute(
                "INSERT INTO si_evidence_verification_policies"
                "(id,project_id,task_id,evidence_id,policy_version,criteria_index,"
                "repository_owner,repository_name,repository_id,workflow_id,run_id,"
                "run_attempt,expected_sha,expected_event,created_by)"
                " VALUES(%s::uuid,'alpha',%s::uuid,%s::uuid,%s,%s,"
                "'rightware-corporations','rightware-shared-intelligence',"
                "1452533938,415280241,43202560651,1,%s,'push',%s)",
                (policy_id,self.task_id,self.evidence_id,version,criteria_index,
                 expected_sha,created_by),
            )
        return policy_id

    def actor(self,name="verifier"):
        token=self.tokens[name]
        return resolve_principal(
            _DSN,HTTPAuthorizationCredentials(scheme="Bearer",credentials=token),
        )

    def mock(self,record=None,status=200,handler=None):
        if handler is None:
            def handler(request):
                return httpx.Response(status,json=record or provider_record())
        return httpx.Client(transport=httpx.MockTransport(handler))

    def check(self,client=None,actor="verifier",policy=None,key=None,version=4,project="alpha"):
        return self.ledger.verify_and_record(project,self.actor(actor),
            policy or self.policy_id,version,key or f"r2-attempt-{uuid4().hex[:9]}",
            client=client)

    def rows(self):
        with psycopg.connect(_DSN) as conn:
            return conn.execute(
                "SELECT result,reason_code,observation_channel FROM "
                "si_verification_attempts WHERE task_id=%s::uuid",(self.task_id,)
            ).fetchall()

    def test_01_success_is_append_only_and_never_done(self):
        with self.mock() as client:
            result=self.check(client)
        self.assertEqual(result["result"],"CHECKED_PASS")
        self.assertEqual(result["observation_channel"],"SIMULATED_TRANSPORT")
        self.assertFalse(result["task_approved"])
        self.assertEqual(result["review_decision"],"NOT_IMPLEMENTED_R2_R1B")
        task=self.core.get_task("alpha","worker",self.task_id)
        self.assertEqual(task["status"],"IN_REVIEW")
        self.assertEqual(task["version"],4)
        with psycopg.connect(_DSN) as conn:
            evidence=conn.execute("SELECT verification_state FROM si_evidence_refs "
                "WHERE id=%s::uuid",(self.evidence_id,)).fetchone()
            self.assertEqual(evidence[0],"REFERENCED")
            event=conn.execute(
                "SELECT event_type,payload FROM si_continuity_events "
                "WHERE task_id=%s::uuid AND event_type='EVIDENCE_CHECKED'",(self.task_id,)
            ).fetchone()
            self.assertEqual(event[0],"EVIDENCE_CHECKED")
            self.assertNotIn("token",str(event[1]).lower())

    def test_02_wrong_sha_persists_fail_without_status_change(self):
        with self.mock(provider_record(head_sha="f"*40)) as client:
            result=self.check(client)
        self.assertEqual(result["result"],"CHECKED_FAIL")
        self.assertEqual(result["reason_code"],"WRONG_SHA")
        self.assertEqual(self.core.get_task("alpha","worker",self.task_id)["status"],"IN_REVIEW")

    def test_03_api_error_persists_inconclusive(self):
        with self.mock(status=403) as client:
            result=self.check(client)
        self.assertEqual(result["result"],"INCONCLUSIVE")
        self.assertEqual(result["reason_code"],"PROVIDER_HTTP_UNAVAILABLE")

    def test_04_agent_cannot_verify_even_with_explicit_grant(self):
        with psycopg.connect(_DSN) as conn:
            conn.execute("INSERT INTO si_project_grants(project_id,principal_id,permission)"
                         " VALUES('alpha','worker','evidence:verify')")
        with self.mock() as client:
            with self.assertRaises(AccessDenied):
                self.check(client,actor="worker")
        self.assertEqual(self.rows(),[])

    def test_05_service_without_grant_is_denied(self):
        with self.mock() as client:
            with self.assertRaises(AccessDenied):
                self.check(client,actor="no-grant")
        self.assertEqual(self.rows(),[])

    def test_06_cross_project_policy_read_is_denied(self):
        with self.mock() as client:
            with self.assertRaises(Exception) as ctx:
                self.check(client,actor="other",project="beta")
        self.assertIn(type(ctx.exception).__name__,("Missing","AccessDenied"))
        self.assertEqual(self.rows(),[])

    def test_07_unmatched_evidence_url_fails_before_provider_fetch(self):
        with psycopg.connect(_DSN) as conn:
            conn.execute("UPDATE si_evidence_refs "
                         "SET uri='https://github.com/untrusted/other/actions/runs/1' "
                         "WHERE id=%s::uuid",(self.evidence_id,))
        called=[]
        def handler(request):
            called.append(str(request.url))
            return httpx.Response(200,json=provider_record())
        with self.mock(handler=handler) as client:
            with self.assertRaises(Conflict):
                self.check(client)
        self.assertEqual(called,[])
        self.assertEqual(self.rows(),[])

    def test_08_stale_task_version_fails(self):
        with self.mock() as client:
            with self.assertRaises(Conflict):
                self.check(client,version=3)
        self.assertEqual(self.rows(),[])

    def test_09_revoked_midflight_must_not_commit(self):
        def handler(request):
            with psycopg.connect(_DSN) as conn:
                conn.execute("DELETE FROM si_project_grants "
                             "WHERE project_id='alpha' AND principal_id='verifier' "
                             "AND permission='evidence:verify'")
            return httpx.Response(200,json=provider_record())
        with self.mock(handler=handler) as client:
            with self.assertRaises(AccessDenied):
                self.check(client)
        self.assertEqual(self.rows(),[])

    def test_10_retry_idempotently_replays_immutable_record_without_network(self):
        seen=[]
        def handler(request):
            seen.append(1)
            return httpx.Response(200,json=provider_record())
        with self.mock(handler=handler) as client:
            first=self.check(client,key="r2-fixed-key-100")
            second=self.check(client,key="r2-fixed-key-100")
        self.assertEqual(first,second)
        self.assertEqual(seen,[1])
        self.assertEqual(len(self.rows()),1)

    def test_11_reusing_key_with_other_policy_fails(self):
        with self.mock() as client:
            self.check(client,key="r2-fixed-key-101")
            another=self.seed_policy(version=2)
            with self.assertRaises(Conflict):
                self.check(client,policy=another,key="r2-fixed-key-101")
        self.assertEqual(len(self.rows()),1)

    def test_12_attempt_and_policy_are_database_immutable(self):
        with self.mock() as client:
            result=self.check(client)
        with psycopg.connect(_DSN) as conn:
            with self.assertRaises(psycopg.errors.CheckViolation):
                conn.execute("DELETE FROM si_verification_attempts WHERE id=%s::uuid",
                             (result["attempt_id"],))
            conn.rollback()
            with self.assertRaises(psycopg.errors.CheckViolation):
                conn.execute("UPDATE si_evidence_verification_policies "
                             "SET policy_version=2 WHERE id=%s::uuid",(self.policy_id,))

    def test_13_read_scoped_and_revoked_on_each_call(self):
        with self.mock() as client:
            self.check(client)
        results=self.ledger.list_attempts("alpha",self.actor(),self.task_id)
        self.assertEqual(len(results),1)
        self.assertEqual(results[0]["result"],"CHECKED_PASS")
        with self.assertRaises(AccessDenied):
            self.ledger.list_attempts("alpha",self.actor("no-grant"),self.task_id)
        with psycopg.connect(_DSN) as conn:
            conn.execute("DELETE FROM si_project_grants WHERE project_id='alpha' "
                         "AND principal_id='verifier' AND permission='evidence:read'")
        with self.assertRaises(AccessDenied):
            self.ledger.list_attempts("alpha",self.actor(),self.task_id)

    def test_14_verifier_cannot_verify_a_policy_it_authored(self):
        forged=self.seed_policy(version=2,created_by="verifier")
        with self.mock() as client:
            with self.assertRaises(AccessDenied):
                self.check(client,policy=forged)
        self.assertEqual(self.rows(),[])

    def test_15_policy_criterion_out_of_bounds_denied(self):
        forged=self.seed_policy(version=2,criteria_index=3)
        with self.mock() as client:
            with self.assertRaises(Conflict):
                self.check(client,policy=forged)
        self.assertEqual(self.rows(),[])

    def test_16_concurrent_distinct_attempts_are_append_only(self):
        def one(i):
            with self.mock() as client:
                return self.check(client,key=f"r2-parallel-{i:03d}")
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes=list(pool.map(one,[1,2]))
        self.assertEqual(len({r["attempt_id"] for r in outcomes}),2)
        self.assertEqual(len(self.rows()),2)
        self.assertEqual(self.core.get_task("alpha","worker",self.task_id)["status"],"IN_REVIEW")


if __name__=="__main__":
    unittest.main()
