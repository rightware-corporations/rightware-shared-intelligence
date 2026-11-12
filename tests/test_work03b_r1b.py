"""WORK-03B R1B: real PostgreSQL REST checkpoint/resume tests on rw_test only.

These are lab assertions. They never demonstrate DONE verification, source-level
consent, arbitrary vendor history access or actual Jarvis production integration.
"""
from __future__ import annotations

import os
import unittest
from urllib.parse import urlsplit

import psycopg
from fastapi.testclient import TestClient

from rightware_si.http_api import create_app
from rightware_si.token_admin import issue_api_token, revoke_api_token

_DSN = os.environ.get("RW_TEST_DATABASE_URL", "")
_U = urlsplit(_DSN)
_SAFE = bool(_DSN and _U.path == "/rw_test"
             and _U.hostname in ("127.0.0.1", "localhost") and _U.port == 5432)


@unittest.skipUnless(_SAFE, "isolated local PostgreSQL rw_test required")
class CheckpointResumeTests(unittest.TestCase):
    def setUp(self):
        with psycopg.connect(_DSN, autocommit=True) as conn:
            conn.execute("TRUNCATE si_organizations,si_principals RESTART IDENTITY CASCADE")
            conn.execute("INSERT INTO si_organizations(id) VALUES('a-org'),('b-org')")
            conn.execute("INSERT INTO si_projects(id,organization_id) VALUES "
                         "('alpha','a-org'),('beta','b-org')")
            conn.execute("INSERT INTO si_principals(id,principal_kind) VALUES "
                         "('agent-a','AGENT'),('agent-b','AGENT'),('intruder','AGENT')")
            perms = {
                "agent-a": ("task:create","task:manage","task:execute","task:read",
                            "context:read","source:write","observation:write",
                            "checkpoint:write","handoff:offer"),
                "agent-b": ("task:execute","task:read","context:read",
                            "source:write","observation:write","checkpoint:write",
                            "handoff:accept"),
            }
            for actor, grants in perms.items():
                for perm in grants:
                    conn.execute("INSERT INTO si_project_grants "
                                 "(project_id,principal_id,permission) VALUES('alpha',%s,%s)",
                                 (actor,perm))
        self.tokens = {}
        self.token_ids = {}
        for actor in ("agent-a","agent-b","intruder"):
            tid, tok = issue_api_token(_DSN,actor,24)
            self.tokens[actor] = tok
            self.token_ids[actor] = tid
        self.client = TestClient(create_app(_DSN))
        self.serial = 0

    def h(self, actor="agent-a", idem=None):
        result={"Authorization":f"Bearer {self.tokens[actor]}"}
        if idem:
            result["Idempotency-Key"]=idem
        return result

    def post(self, path, data, actor="agent-a", idem=None):
        self.serial+=1
        return self.client.post(path,headers=self.h(actor,idem or f"r1b-idem-{self.serial:05d}"),
                                json=data)

    def seed(self):
        c=self.post("/v1/projects/alpha/tasks",
                    {"title":"Recover source-linked work",
                     "acceptance_criteria":["Do not claim completion without review"]})
        self.assertEqual(c.status_code,201,c.text)
        tid=c.json()["task_id"]
        p=self.post(f"/v1/projects/alpha/tasks/{tid}/publish",{"expected_version":1})
        self.assertEqual(p.status_code,200,p.text)
        claim=self.post(f"/v1/projects/alpha/tasks/{tid}/claim",{"expected_version":2})
        self.assertEqual(claim.status_code,200,claim.text)
        lease=claim.json()["lease_token"]
        run=self.post(f"/v1/projects/alpha/tasks/{tid}/runs",
                      {"expected_version":3,"lease_token":lease,"runtime_label":"synthetic-A"})
        self.assertEqual(run.status_code,201,run.text)
        runid=run.json()["run_id"]
        src=self.post("/v1/projects/alpha/sources",{
            "task_id":tid,"agent_run_id":runid,"expected_version":3,"lease_token":lease,
            "source_kind":"TOOL_RECEIPT","source_uri":"urn:rw:synthetic-pass",
            "source_revision":"runA"
        })
        self.assertEqual(src.status_code,201,src.text)
        obs=self.post("/v1/projects/alpha/observations",{
            "task_id":tid,"agent_run_id":runid,"expected_version":3,"lease_token":lease,
            "claim":"Tests reported by Agent A; not independently verified",
            "source_ids":[src.json()["source_id"]]
        })
        self.assertEqual(obs.status_code,201,obs.text)
        return tid,lease,runid,obs.json()["observation_id"],src.json()["source_id"]

    def checkpoint(self, tid, lease, runid, obsids, seq=0, actor="agent-a",
                   summary="Agent A finished preparation; independent review pending",
                   idem=None):
        return self.post(f"/v1/projects/alpha/tasks/{tid}/checkpoints",{
            "agent_run_id":runid,"expected_version":3 if actor=="agent-a" else 5,
            "lease_token":lease,"expected_checkpoint_seq":seq,
            "summary":summary,
            "next_actions":["Continue on staged synthetic dataset"],
            "blockers":["Independent verification pending"],
            "observation_ids":obsids
        },actor,idem)

    def resume(self, tid, actor="agent-a", project="alpha"):
        return self.client.get(f"/v1/projects/{project}/tasks/{tid}/resume",
                               headers=self.h(actor))

    def test_resume_before_checkpoint_is_explicit_and_readonly(self):
        tid,lease,runid,obs,src=self.seed()
        r=self.resume(tid)
        self.assertEqual(r.status_code,200,r.text)
        state=r.json()
        self.assertEqual(state["snapshot_status"],"NO_CHECKPOINT")
        self.assertIsNone(state["checkpoint"])
        self.assertEqual(state["memory_status"],"NOT_QUERIED")
        self.assertEqual((state["read_only"],state["lease_issued"]),(True,False))
        self.assertFalse(state["verified_completion"])

    def test_checkpoint_survives_new_read_and_never_mints_lease(self):
        tid,lease,runid,obs,src=self.seed()
        c=self.checkpoint(tid,lease,runid,[obs])
        self.assertEqual(c.status_code,201,c.text)
        self.assertEqual(c.json()["checkpoint_seq"],1)
        state=self.resume(tid).json()
        self.assertEqual(state["snapshot_status"],"CHECKPOINT_AVAILABLE")
        cp=state["checkpoint"]
        self.assertEqual(cp["checkpoint_id"],c.json()["checkpoint_id"])
        self.assertEqual(cp["trust_state"],"ASSERTED")
        self.assertEqual(cp["task_version_recorded"],3)
        self.assertTrue(state["checkpoint_version_matches_task"])
        self.assertEqual(cp["observations"][0]["sources"][0]["source_id"],src)
        self.assertEqual(cp["observations"][0]["trust_state"],"ASSERTED")
        self.assertEqual(state["task"]["version"],3)
        self.assertEqual(state["task"]["status"],"IN_PROGRESS")
        self.assertFalse(state["verified_completion"])
        self.assertNotIn("lease_token",str(state))
        self.assertNotIn(lease,str(state))
        self.assertEqual(state["memory_status"],"NOT_QUERIED")

    def test_sequence_cas_idempotency_and_new_checkpoint(self):
        tid,lease,runid,obs,src=self.seed()
        first=self.checkpoint(tid,lease,runid,[obs],idem="r1b-cp-first-0001")
        self.assertEqual(first.status_code,201,first.text)
        replay=self.checkpoint(tid,lease,runid,[obs],idem="r1b-cp-first-0001")
        self.assertEqual(replay.json(),first.json())
        stale=self.checkpoint(tid,lease,runid,[obs],seq=0,idem="r1b-cp-stale-0001")
        self.assertEqual(stale.status_code,409,stale.text)
        second=self.checkpoint(tid,lease,runid,[obs],seq=1,
                               summary="Revised pending work, still not verified")
        self.assertEqual(second.status_code,201,second.text)
        self.assertEqual(second.json()["checkpoint_seq"],2)
        state=self.resume(tid).json()
        self.assertEqual(state["checkpoint"]["checkpoint_seq"],2)
        self.assertEqual(state["task"]["version"],3)
        with psycopg.connect(_DSN) as conn:
            self.assertEqual(conn.execute(
                "SELECT count(*) FROM si_task_checkpoints WHERE task_id=%s::uuid",(tid,)
            ).fetchone()[0],2)
            events=conn.execute(
                "SELECT event_type,task_version,payload FROM si_continuity_events "
                "WHERE task_id=%s::uuid AND event_type='CHECKPOINT_RECORDED' ORDER BY id",
                (tid,)
            ).fetchall()
            self.assertEqual(len(events),2)
            self.assertEqual([x[1] for x in events],[3,3])
            self.assertNotIn(lease,str(events))

    def test_checkpoint_is_immutable_at_db_trigger_layer(self):
        tid,lease,runid,obs,src=self.seed()
        cp=self.checkpoint(tid,lease,runid,[obs]).json()["checkpoint_id"]
        with psycopg.connect(_DSN) as conn:
            with self.assertRaises(psycopg.errors.CheckViolation):
                conn.execute("UPDATE si_task_checkpoints SET summary='tampered' "
                             "WHERE id=%s::uuid",(cp,))
            conn.rollback()
            with self.assertRaises(psycopg.errors.CheckViolation):
                conn.execute("DELETE FROM si_task_checkpoints WHERE id=%s::uuid",(cp,))
            conn.rollback()
            with self.assertRaises(psycopg.errors.CheckViolation):
                conn.execute("DELETE FROM si_checkpoint_observations "
                             "WHERE checkpoint_id=%s::uuid",(cp,))
        self.assertEqual(self.resume(tid).json()["checkpoint"]["checkpoint_id"],cp)

    def test_cross_task_observation_cannot_be_linked(self):
        a,la,ra,oa,sa=self.seed()
        b,lb,rb,ob,sb=self.seed()
        res=self.checkpoint(b,lb,rb,[oa])
        self.assertEqual(res.status_code,404,res.text)
        self.assertEqual(self.resume(b).json()["snapshot_status"],"NO_CHECKPOINT")

    def test_scope_and_revocation_rechecked_on_each_resume(self):
        tid,lease,runid,obs,src=self.seed()
        self.assertEqual(self.checkpoint(tid,lease,runid,[obs]).status_code,201)
        self.assertEqual(self.resume(tid,actor="intruder").status_code,403)
        self.assertEqual(self.resume(tid,project="beta").status_code,403)
        with psycopg.connect(_DSN) as conn:
            conn.execute("DELETE FROM si_project_grants "
                         "WHERE project_id='alpha' AND principal_id='agent-a' "
                         "AND permission='context:read'")
        denied=self.resume(tid)
        self.assertEqual(denied.status_code,403,denied.text)
        self.assertNotIn("Agent A finished",denied.text)
        self.assertTrue(revoke_api_token(_DSN,self.token_ids["agent-a"]))
        self.assertEqual(self.resume(tid).status_code,401)

    def test_lease_and_run_bindings_prevent_stale_write_after_handoff(self):
        tid,lease,runid,obs,src=self.seed()
        cp=self.checkpoint(tid,lease,runid,[obs])
        self.assertEqual(cp.status_code,201,cp.text)
        offered=self.post(f"/v1/projects/alpha/tasks/{tid}/handoffs",{
            "to_principal_id":"agent-b","summary":"Checkpoint persisted and B may read",
            "expected_version":3,"lease_token":lease})
        self.assertEqual(offered.status_code,201,offered.text)
        stale=self.checkpoint(tid,lease,runid,[obs],seq=1)
        self.assertEqual(stale.status_code,409)
        b=self.post(f"/v1/projects/alpha/handoffs/{offered.json()['handoff_id']}/accept",
                    {"expected_version":4},actor="agent-b")
        self.assertEqual(b.status_code,200,b.text)
        state=self.resume(tid,"agent-b").json()
        self.assertEqual(state["last_handoff"]["status"],"ACCEPTED")
        self.assertEqual(state["last_handoff"]["checkpoint_binding"],"NOT_IMPLEMENTED_R1B")
        self.assertEqual(state["task"]["version"],5)
        self.assertEqual(state["checkpoint"]["task_version_recorded"],3)
        self.assertFalse(state["checkpoint_version_matches_task"])
        self.assertEqual(state["checkpoint"]["observations"][0]["asserted_by"],"agent-a")
        self.assertEqual(state["memory_status"],"NOT_QUERIED")
        self.assertFalse(state["verified_completion"])

    def test_checkpoint_validation_rejects_spoofed_approval_and_bad_payload(self):
        tid,lease,runid,obs,src=self.seed()
        payload={
            "agent_run_id":runid,"expected_version":3,"lease_token":lease,
            "expected_checkpoint_seq":0,"summary":"Approved",
            "next_actions":["continue"],"blockers":[],"observation_ids":[obs]
        }
        forged=self.post(f"/v1/projects/alpha/tasks/{tid}/checkpoints",
                         dict(payload,trust_state="APPROVED",actor_id="reviewer"))
        self.assertEqual(forged.status_code,422,forged.text)
        invalid=self.post(f"/v1/projects/alpha/tasks/{tid}/checkpoints",
                          dict(payload,next_actions=[]))
        self.assertEqual(invalid.status_code,422,invalid.text)
        wronglease=self.post(f"/v1/projects/alpha/tasks/{tid}/checkpoints",
                             dict(payload,lease_token="x"*32))
        self.assertEqual(wronglease.status_code,409,wronglease.text)
        with psycopg.connect(_DSN) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM si_task_checkpoints").fetchone()[0],0)

    def test_checkpoint_permission_revocation_blocks_write(self):
        tid,lease,runid,obs,src=self.seed()
        with psycopg.connect(_DSN) as conn:
            conn.execute("DELETE FROM si_project_grants WHERE project_id='alpha' "
                         "AND principal_id='agent-a' AND permission='checkpoint:write'")
        self.assertEqual(self.checkpoint(tid,lease,runid,[obs]).status_code,403)


if __name__=="__main__":
    unittest.main()
