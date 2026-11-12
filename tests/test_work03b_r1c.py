"""WORK-03B R1C: real PostgreSQL/REST tests of bound handoff and fenced rekey.

Disposable localhost:5432/rw_test only. Tests assert actual transaction outcomes,
not speculative security/cryptographic assurances or complete UC-CORE-01.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import os
import unittest
from urllib.parse import urlsplit
from uuid import uuid4

import psycopg
from fastapi.testclient import TestClient

from rightware_si.http_api import create_app
from rightware_si.token_admin import issue_api_token

_DSN=os.getenv("RW_TEST_DATABASE_URL","")
_U=urlsplit(_DSN)
_SAFE=bool(_DSN and _U.path=="/rw_test"
           and _U.hostname in ("localhost","127.0.0.1") and _U.port==5432)


@unittest.skipUnless(_SAFE, "requires disposable local PostgreSQL /rw_test")
class HandoffFencingTests(unittest.TestCase):
    def setUp(self):
        with psycopg.connect(_DSN,autocommit=True) as conn:
            conn.execute("TRUNCATE si_organizations,si_principals RESTART IDENTITY CASCADE")
            conn.execute("INSERT INTO si_organizations(id) VALUES('r1c-a'),('r1c-b')")
            conn.execute("INSERT INTO si_projects(id,organization_id) VALUES "
                         "('alpha','r1c-a'),('beta','r1c-b')")
            conn.execute("INSERT INTO si_principals(id,principal_kind) VALUES "
                         "('agent-a','AGENT'),('agent-b','AGENT'),('intruder','AGENT')")
            grants={
                "agent-a":("task:create","task:manage","task:execute","task:read",
                           "context:read","source:write","observation:write",
                           "checkpoint:write","handoff:offer","task:recover"),
                "agent-b":("task:execute","task:read","context:read",
                           "checkpoint:write","handoff:accept","task:recover"),
            }
            for actor,perms in grants.items():
                for permission in perms:
                    conn.execute("INSERT INTO si_project_grants "
                                 "(project_id,principal_id,permission) "
                                 "VALUES('alpha',%s,%s)",(actor,permission))
        self.tokens={actor:issue_api_token(_DSN,actor,24)[1]
                     for actor in ("agent-a","agent-b","intruder")}
        self.client=TestClient(create_app(_DSN))
        self.n=0

    def auth(self,actor="agent-a",idem=None):
        head={"Authorization":f"Bearer {self.tokens[actor]}"}
        if idem:
            head["Idempotency-Key"]=idem
        return head

    def post(self,path,data,actor="agent-a",idem=None):
        self.n+=1
        return self.client.post(path,json=data,
            headers=self.auth(actor,idem or f"r1c-auto-{self.n:05d}"))

    def get(self,path,actor="agent-a"):
        return self.client.get(path,headers=self.auth(actor))

    def task(self):
        created=self.post("/v1/projects/alpha/tasks",{
            "title":"R1C synthetic checkpoint bound handoff",
            "acceptance_criteria":["Only a reviewed result may be DONE"],
        })
        self.assertEqual(created.status_code,201,created.text)
        task=created.json()["task_id"]
        pub=self.post(f"/v1/projects/alpha/tasks/{task}/publish",
                      {"expected_version":1})
        self.assertEqual(pub.status_code,200,pub.text)
        claim=self.post(f"/v1/projects/alpha/tasks/{task}/claim",
                        {"expected_version":2})
        self.assertEqual(claim.status_code,200,claim.text)
        return task,claim.json()["lease_token"],claim.json()["lease_generation"]

    def task_with_checkpoint(self):
        tid,lease,generation=self.task()
        run=self.post(f"/v1/projects/alpha/tasks/{tid}/runs",{
            "expected_version":3,"lease_token":lease,
            "runtime_label":"r1c-agent-a",
        })
        self.assertEqual(run.status_code,201,run.text)
        runid=run.json()["run_id"]
        source=self.post("/v1/projects/alpha/sources",{
            "task_id":tid,"agent_run_id":runid,"expected_version":3,
            "lease_token":lease,"source_kind":"TOOL_RECEIPT",
            "source_uri":"urn:rw:r1c-synthetic-receipt","source_revision":"v1",
        })
        self.assertEqual(source.status_code,201,source.text)
        observation=self.post("/v1/projects/alpha/observations",{
            "task_id":tid,"agent_run_id":runid,"expected_version":3,
            "lease_token":lease,"claim":"Executor says fixture passed, still ASSERTED",
            "source_ids":[source.json()["source_id"]],
        })
        self.assertEqual(observation.status_code,201,observation.text)
        cp=self.post(f"/v1/projects/alpha/tasks/{tid}/checkpoints",{
            "agent_run_id":runid,"expected_version":3,"lease_token":lease,
            "expected_checkpoint_seq":0,
            "summary":"First immutable R1C handoff checkpoint",
            "next_actions":["Independently verify receipt"],"blockers":["Review pending"],
            "observation_ids":[observation.json()["observation_id"]],
        })
        self.assertEqual(cp.status_code,201,cp.text)
        return {"task":tid,"lease":lease,"generation":generation,
                "run":runid,"cp":cp.json()["checkpoint_id"],"seq":1}

    def offer(self,seed,cp=None,seq=None,actor="agent-a",idem=None):
        body={"expected_version":3,"lease_token":seed["lease"],
              "to_principal_id":"agent-b","summary":"Bound checkpoint handoff"}
        if cp is not None:
            body["checkpoint_id"]=cp
        if seq is not None:
            body["expected_checkpoint_seq"]=seq
        return self.post(f"/v1/projects/alpha/tasks/{seed['task']}/handoffs",
                         body,actor,idem)

    def accepted(self,seed):
        offered=self.offer(seed,seed["cp"],seed["seq"])
        self.assertEqual(offered.status_code,201,offered.text)
        a=self.post(
            f"/v1/projects/alpha/handoffs/{offered.json()['handoff_id']}/accept",
            {"expected_version":4},actor="agent-b",
        )
        self.assertEqual(a.status_code,200,a.text)
        return offered.json(),a.json()

    def test_handoff_binds_exact_checkpoint_and_increments_generation(self):
        seed=self.task_with_checkpoint()
        offered,accepted=self.accepted(seed)
        self.assertEqual(offered["checkpoint_id"],seed["cp"])
        self.assertEqual(offered["checkpoint_seq"],1)
        self.assertEqual(offered["checkpoint_binding"],"BOUND_R1C")
        self.assertEqual(accepted["checkpoint_id"],seed["cp"])
        self.assertGreater(accepted["lease_generation"],seed["generation"])
        resume=self.get(f"/v1/projects/alpha/tasks/{seed['task']}/resume",
                        actor="agent-b")
        self.assertEqual(resume.status_code,200,resume.text)
        snapshot=resume.json()
        self.assertEqual(snapshot["last_handoff"]["checkpoint_id"],seed["cp"])
        self.assertTrue(snapshot["last_handoff"]["checkpoint_is_latest"])
        self.assertEqual(snapshot["handoff_checkpoint"]["checkpoint_id"],seed["cp"])
        self.assertEqual(snapshot["checkpoint"]["trust_state"],"ASSERTED")
        self.assertFalse(snapshot["verified_completion"])
        self.assertFalse(snapshot["checkpoint_version_matches_task"])
        self.assertNotIn(seed["lease"],str(snapshot))
        old=self.post(f"/v1/projects/alpha/tasks/{seed['task']}/checkpoints",{
            "agent_run_id":seed["run"],"expected_version":5,
            "expected_checkpoint_seq":1,"lease_token":seed["lease"],
            "summary":"Stale writer","next_actions":["unsafe"],
        })
        self.assertEqual(old.status_code,409)

    def test_requires_explicit_current_checkpoint_when_one_exists(self):
        seed=self.task_with_checkpoint()
        self.assertEqual(self.offer(seed).status_code,409)
        self.assertEqual(self.offer(seed,seed["cp"],2).status_code,409)
        self.assertEqual(self.offer(seed,str(uuid4()),1).status_code,409)
        self.assertEqual(self.offer(seed,seed["cp"]).status_code,422)
        good=self.offer(seed,seed["cp"],seed["seq"])
        self.assertEqual(good.status_code,201,good.text)
        self.assertEqual(good.json()["checkpoint_id"],seed["cp"])

    def test_latest_checkpoint_cas_rejects_stale_binding(self):
        seed=self.task_with_checkpoint()
        second=self.post(f"/v1/projects/alpha/tasks/{seed['task']}/checkpoints",{
            "agent_run_id":seed["run"],"expected_version":3,
            "lease_token":seed["lease"],"expected_checkpoint_seq":1,
            "summary":"New current checkpoint",
            "next_actions":["Review later"],"observation_ids":[],
        })
        self.assertEqual(second.status_code,201,second.text)
        stale=self.offer(seed,seed["cp"],1)
        self.assertEqual(stale.status_code,409)
        newer=self.offer(seed,second.json()["checkpoint_id"],2)
        self.assertEqual(newer.status_code,201,newer.text)

    def test_db_rejects_checkpoint_rebinding_and_forged_version(self):
        seed=self.task_with_checkpoint()
        offered=self.offer(seed,seed["cp"],1)
        self.assertEqual(offered.status_code,201,offered.text)
        with psycopg.connect(_DSN) as conn:
            with self.assertRaises(psycopg.errors.CheckViolation):
                conn.execute("UPDATE si_handoffs SET checkpoint_id=NULL,"
                             "checkpoint_seq=NULL,checkpoint_task_version=NULL "
                             "WHERE id=%s::uuid",(offered.json()["handoff_id"],))
            conn.rollback()
            # DB validates a checkpoint's stored version/sequence on INSERT.
            with self.assertRaises(psycopg.errors.CheckViolation):
                conn.execute(
                    "INSERT INTO si_handoffs"
                    "(id,project_id,task_id,from_principal_id,to_principal_id,"
                    "summary,status,checkpoint_id,checkpoint_seq,checkpoint_task_version)"
                    " VALUES(%s::uuid,'alpha',%s::uuid,'agent-a','agent-b',"
                    "'bad metadata','OFFERED',%s::uuid,99,999)",
                    (str(uuid4()),seed["task"],seed["cp"]),
                )

    def test_recovery_only_holder_with_explicit_permission(self):
        seed=self.task_with_checkpoint()
        status=self.get(f"/v1/projects/alpha/tasks/{seed['task']}/lease-status")
        self.assertEqual(status.status_code,200,status.text)
        self.assertEqual(status.json()["lease_generation"],seed["generation"])
        self.assertFalse(status.json()["token_recoverable"])
        denied=self.get(f"/v1/projects/alpha/tasks/{seed['task']}/lease-status",
                        actor="agent-b")
        self.assertEqual(denied.status_code,403)
        intruder=self.post(f"/v1/projects/alpha/tasks/{seed['task']}/lease-recovery",{
            "expected_version":3,"expected_generation":seed["generation"],
        },actor="intruder")
        self.assertEqual(intruder.status_code,403)
        with psycopg.connect(_DSN) as conn:
            conn.execute("DELETE FROM si_project_grants WHERE project_id='alpha' "
                         "AND principal_id='agent-a' AND permission='task:recover'")
        no_grant=self.post(f"/v1/projects/alpha/tasks/{seed['task']}/lease-recovery",{
            "expected_version":3,"expected_generation":seed["generation"],
        })
        self.assertEqual(no_grant.status_code,403)

    def test_lost_response_rekeys_and_does_not_store_secret(self):
        seed=self.task_with_checkpoint()
        path=f"/v1/projects/alpha/tasks/{seed['task']}/lease-recovery"
        payload={"expected_version":3,"expected_generation":seed["generation"]}
        rec=self.post(path,payload,idem="r1c-recover-once-0001")
        self.assertEqual(rec.status_code,200,rec.text)
        recovered=rec.json()
        self.assertTrue(recovered["recovered"])
        self.assertGreater(recovered["lease_generation"],seed["generation"])
        self.assertNotEqual(recovered["lease_token"],seed["lease"])
        self.assertEqual(self.post(path,payload,idem="r1c-recover-once-0001").status_code,409)
        self.assertEqual(self.post(path,payload,idem="r1c-recover-stale-0001").status_code,409)
        with psycopg.connect(_DSN) as conn:
            row=conn.execute(
                "SELECT response FROM si_idempotency WHERE "
                "project_id='alpha' AND principal_id='agent-a' "
                "AND action='recover_lease' AND idem_key='r1c-recover-once-0001'"
            ).fetchone()
            self.assertNotIn("lease_token",row[0])
            self.assertNotIn(recovered["lease_token"],str(row[0]))
            ev=conn.execute(
                "SELECT payload FROM si_continuity_events "
                "WHERE task_id=%s::uuid AND event_type='LEASE_REKEYED'",(seed["task"],)
            ).fetchall()
            self.assertEqual(len(ev),1)
            self.assertNotIn(recovered["lease_token"],str(ev))
            self.assertEqual(ev[0][0]["new_generation"],recovered["lease_generation"])
        self.assertEqual(self.offer(seed,seed["cp"],1).status_code,409)
        seed["lease"]=recovered["lease_token"]
        self.assertEqual(self.offer(seed,seed["cp"],1).status_code,201)

    def test_expired_lease_can_be_rekeyed_by_same_holder(self):
        seed=self.task_with_checkpoint()
        with psycopg.connect(_DSN) as conn:
            conn.execute("UPDATE si_task_leases "
                         "SET expires_at=now()-interval '1 second' "
                         "WHERE task_id=%s::uuid",(seed["task"],))
        expired=self.offer(seed,seed["cp"],1)
        self.assertEqual(expired.status_code,409)
        status=self.get(f"/v1/projects/alpha/tasks/{seed['task']}/lease-status")
        self.assertEqual(status.status_code,200,status.text)
        self.assertFalse(status.json()["lease_valid"])
        recovered=self.post(f"/v1/projects/alpha/tasks/{seed['task']}/lease-recovery",{
            "expected_version":3,"expected_generation":seed["generation"],
        })
        self.assertEqual(recovered.status_code,200,recovered.text)
        seed["lease"]=recovered.json()["lease_token"]
        self.assertEqual(self.offer(seed,seed["cp"],1).status_code,201)

    def test_generation_never_regresses_after_handoff_and_recovery(self):
        seed=self.task_with_checkpoint()
        generation=seed["generation"]
        for i in range(3):
            r=self.post(f"/v1/projects/alpha/tasks/{seed['task']}/lease-recovery",{
                "expected_version":3,"expected_generation":generation,
            })
            self.assertEqual(r.status_code,200,r.text)
            seed["lease"]=r.json()["lease_token"]
            self.assertGreater(r.json()["lease_generation"],generation)
            generation=r.json()["lease_generation"]
        offered,accepted=self.accepted(seed)
        self.assertGreater(accepted["lease_generation"],generation)
        status=self.get(f"/v1/projects/alpha/tasks/{seed['task']}/lease-status",
                        actor="agent-b")
        self.assertEqual(status.json()["lease_generation"],accepted["lease_generation"])
        r2=self.post(f"/v1/projects/alpha/tasks/{seed['task']}/lease-recovery",{
            "expected_version":5,"expected_generation":accepted["lease_generation"],
        },actor="agent-b")
        self.assertEqual(r2.status_code,200,r2.text)
        self.assertGreater(r2.json()["lease_generation"],accepted["lease_generation"])

    def test_accepted_handoff_lost_secret_is_recoverable_only_by_b(self):
        seed=self.task_with_checkpoint()
        _,accepted=self.accepted(seed)
        tid=seed["task"]
        attempted=self.post(f"/v1/projects/alpha/tasks/{tid}/lease-recovery",{
            "expected_version":5,
            "expected_generation":accepted["lease_generation"],
        })
        self.assertEqual(attempted.status_code,403,attempted.text)
        b_status=self.get(f"/v1/projects/alpha/tasks/{tid}/lease-status",actor="agent-b")
        self.assertEqual(b_status.status_code,200,b_status.text)
        tokenb=self.post(f"/v1/projects/alpha/tasks/{tid}/lease-recovery",{
            "expected_version":5,
            "expected_generation":b_status.json()["lease_generation"],
        },actor="agent-b")
        self.assertEqual(tokenb.status_code,200,tokenb.text)
        self.assertNotEqual(tokenb.json()["lease_token"],accepted["lease_token"])
        self.assertEqual(tokenb.json()["version"],5)
        with psycopg.connect(_DSN) as conn:
            stored=conn.execute("SELECT token_hash FROM si_task_leases "
                                "WHERE task_id=%s::uuid",(tid,)).fetchone()[0]
        self.assertNotEqual(stored,tokenb.json()["lease_token"])

    def test_new_checkpoint_preserves_original_offered_snapshot(self):
        seed=self.task_with_checkpoint()
        _,accepted=self.accepted(seed)
        runb=self.post(f"/v1/projects/alpha/tasks/{seed['task']}/runs",{
            "expected_version":5,"lease_token":accepted["lease_token"],
            "runtime_label":"r1c-agent-b",
        },actor="agent-b")
        self.assertEqual(runb.status_code,201,runb.text)
        cpb=self.post(f"/v1/projects/alpha/tasks/{seed['task']}/checkpoints",{
            "agent_run_id":runb.json()["run_id"],
            "expected_version":5,"lease_token":accepted["lease_token"],
            "expected_checkpoint_seq":1,
            "summary":"B continuation superseded latest checkpoint",
            "next_actions":["Further verification"],
            "observation_ids":[],
        },actor="agent-b")
        self.assertEqual(cpb.status_code,201,cpb.text)
        snapshot=self.get(f"/v1/projects/alpha/tasks/{seed['task']}/resume",
                          actor="agent-b")
        self.assertEqual(snapshot.status_code,200,snapshot.text)
        data=snapshot.json()
        self.assertEqual(data["checkpoint"]["checkpoint_id"],cpb.json()["checkpoint_id"])
        self.assertFalse(data["last_handoff"]["checkpoint_is_latest"])
        self.assertEqual(data["handoff_checkpoint"]["checkpoint_id"],seed["cp"])
        self.assertEqual(data["handoff_checkpoint"]["checkpoint_seq"],1)
        self.assertEqual(data["handoff_checkpoint"]["trust_state"],"ASSERTED")
        self.assertEqual(data["handoff_checkpoint"]["summary"],
                         "First immutable R1C handoff checkpoint")

    def test_concurrent_recovery_one_winner_one_conflict(self):
        seed=self.task_with_checkpoint()
        path=f"/v1/projects/alpha/tasks/{seed['task']}/lease-recovery"
        payload={"expected_version":3,"expected_generation":seed["generation"]}
        def run_recovery(i):
            with TestClient(create_app(_DSN)) as client:
                r=client.post(path,headers=self.auth(
                    "agent-a",f"r1c-race-{i:05d}"),json=payload)
                return r.status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses=list(pool.map(run_recovery,[1,2]))
        self.assertEqual(sorted(statuses),[200,409])
        state=self.get(f"/v1/projects/alpha/tasks/{seed['task']}/lease-status")
        self.assertGreater(state.json()["lease_generation"],seed["generation"])

    def test_legacy_without_checkpoint_is_explicit_unbound(self):
        tid,lease,_=self.task()
        body={"task":tid,"lease":lease}
        res=self.offer(body)
        self.assertEqual(res.status_code,201,res.text)
        self.assertEqual(res.json()["checkpoint_binding"],"LEGACY_UNBOUND")
        self.assertIsNone(res.json()["checkpoint_id"])


if __name__=="__main__":
    unittest.main()
