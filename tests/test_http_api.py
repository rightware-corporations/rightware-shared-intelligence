"""WORK-02B real PostgreSQL + FastAPI bearer integration tests.

Only runs against a disposable database whose path is exactly /rw_test.
Never point RW_TEST_DATABASE_URL at a production/other project database.
"""
from __future__ import annotations

import hashlib
import os
from urllib.parse import urlsplit
from uuid import uuid4
import unittest

import psycopg
from fastapi.testclient import TestClient

from rightware_si.http_api import create_app
from rightware_si.token_admin import issue_api_token, revoke_api_token

_DSN = os.environ.get("RW_TEST_DATABASE_URL", "")
_SAFE = bool(_DSN and urlsplit(_DSN).path == "/rw_test")


@unittest.skipUnless(_SAFE, "requires explicitly isolated PostgreSQL /rw_test")
class Work02BApiTests(unittest.TestCase):
    def setUp(self):
        self.dsn = _DSN
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            conn.execute("TRUNCATE si_organizations,si_principals RESTART IDENTITY CASCADE")
            conn.execute("INSERT INTO si_organizations(id) VALUES ('rightware')")
            conn.execute("INSERT INTO si_projects(id,organization_id) VALUES "
                         "('alpha','rightware'),('beta','rightware')")
            conn.execute("INSERT INTO si_principals(id,principal_kind) VALUES "
                         "('agent-a','AGENT'),('agent-b','AGENT'),('intruder','AGENT')")
            for principal, permissions in {
                "agent-a": ["task:create", "task:manage", "task:execute", "task:read",
                            "handoff:offer", "audit:read"],
                "agent-b": ["task:read", "task:execute", "handoff:accept", "audit:read"],
            }.items():
                for perm in permissions:
                    conn.execute(
                        "INSERT INTO si_project_grants(project_id,principal_id,permission) "
                        "VALUES('alpha',%s,%s)", (principal,perm))
        self.keys = {}
        self.ids = {}
        for principal in ("agent-a","agent-b","intruder"):
            token_id, token = issue_api_token(self.dsn,principal,24)
            self.ids[principal] = token_id
            self.keys[principal] = token
        self.client = TestClient(create_app(self.dsn))

    def h(self, actor="agent-a", idem=None):
        d={"Authorization":f"Bearer {self.keys[actor]}"}
        if idem:
            d["Idempotency-Key"]=idem
        return d

    def create(self):
        res=self.client.post("/v1/projects/alpha/tasks",
            headers=self.h(idem="create-0001"),
            json={"title":"Integrate context", "acceptance_criteria":["Pass scoped tests"]})
        self.assertEqual(res.status_code,201,res.text)
        return res.json()

    def running(self):
        a=self.create()
        tid=a["task_id"]
        self.assertEqual(self.client.post(
            f"/v1/projects/alpha/tasks/{tid}/publish",
            headers=self.h(idem="publish-0001"),json={"expected_version":1}
        ).status_code,200)
        res=self.client.post(
            f"/v1/projects/alpha/tasks/{tid}/claim",
            headers=self.h(idem="claim-0001"),json={"expected_version":2}
        )
        self.assertEqual(res.status_code,200,res.text)
        return res.json()

    def test_no_anonymous_or_invalid_bearer(self):
        self.assertEqual(self.client.get("/v1/projects/alpha/tasks/"+str(uuid4())).status_code,401)
        self.assertEqual(self.client.post(
            "/v1/projects/alpha/tasks",json={"title":"X","acceptance_criteria":["Y"]},
            headers={"Authorization":"Bearer invalid","Idempotency-Key":"deny-0001"},
        ).status_code,401)

    def test_authenticated_actor_cannot_be_spoofed_in_body(self):
        res=self.client.post("/v1/projects/alpha/tasks",
            headers=self.h("intruder",idem="deny-0001"),
            json={"title":"X","acceptance_criteria":["Y"],"actor":"agent-a"})
        self.assertEqual(res.status_code,422)
        res2=self.client.post("/v1/projects/alpha/tasks",
            headers=self.h("intruder",idem="deny-0002"),
            json={"title":"X","acceptance_criteria":["Y"]})
        self.assertEqual(res2.status_code,403)

    def test_token_revocation_is_immediate(self):
        t=self.create()
        self.assertTrue(revoke_api_token(self.dsn,self.ids["agent-a"]))
        res=self.client.get(f"/v1/projects/alpha/tasks/{t['task_id']}",
                            headers=self.h())
        self.assertEqual(res.status_code,401)

    def test_token_expiry_is_respected(self):
        t=self.create()
        with psycopg.connect(self.dsn) as conn:
            conn.execute("UPDATE si_api_tokens SET expires_at=now()-interval '1 second' "
                         "WHERE id=%s::uuid",(self.ids["agent-a"],))
        self.assertEqual(self.client.get(
            f"/v1/projects/alpha/tasks/{t['task_id']}",headers=self.h()
        ).status_code,401)

    def test_project_scope_enforced_in_api(self):
        t=self.create()
        res=self.client.get(f"/v1/projects/beta/tasks/{t['task_id']}",headers=self.h())
        self.assertEqual(res.status_code,403)
        self.assertEqual(self.client.get(
            f"/v1/projects/alpha/tasks/{t['task_id']}",headers=self.h("intruder")
        ).status_code,403)

    def test_rest_handoff_two_distinct_principals(self):
        a=self.running()
        tid=a["task_id"]
        offered=self.client.post(
            f"/v1/projects/alpha/tasks/{tid}/handoffs",
            headers=self.h(idem="offer-0001"),
            json={"to_principal_id":"agent-b","summary":"Tests still needed",
                  "lease_token":a["lease_token"],"expected_version":3}
        )
        self.assertEqual(offered.status_code,201,offered.text)
        o=offered.json()
        self.assertEqual(o["status"],"BLOCKED")
        denied=self.client.post(
            f"/v1/projects/alpha/handoffs/{o['handoff_id']}/accept",
            headers=self.h(idem="source-accept-0001"),
            json={"expected_version":4},
        )
        self.assertEqual(denied.status_code,403)
        accepted=self.client.post(
            f"/v1/projects/alpha/handoffs/{o['handoff_id']}/accept",
            headers=self.h("agent-b",idem="accept-0001"),
            json={"expected_version":4},
        )
        self.assertEqual(accepted.status_code,200,accepted.text)
        b=accepted.json()
        self.assertEqual(b["status"],"IN_PROGRESS")
        self.assertEqual(b["version"],5)
        res=self.client.post(
            f"/v1/projects/alpha/tasks/{tid}/submit",
            headers=self.h("agent-b",idem="submit-0001"),
            json={"expected_version":5,"lease_token":b["lease_token"],
                  "evidence_url":"https://github.com/example/repo/commit/abc123"}
        )
        self.assertEqual(res.status_code,200,res.text)
        self.assertEqual(res.json()["status"],"IN_REVIEW")
        self.assertEqual(res.json()["verification_state"],"REFERENCED")
        events=self.client.get(
            f"/v1/projects/alpha/tasks/{tid}/events",
            headers=self.h("agent-b")
        )
        self.assertEqual(events.status_code,200,events.text)
        self.assertEqual(len(events.json()["events"]),6)
        # No attempt to claim DONE or verified.

    def test_api_idempotency_and_stale_version(self):
        created=self.create()
        same=self.client.post("/v1/projects/alpha/tasks",
            headers=self.h(idem="create-0001"),
            json={"title":"Integrate context","acceptance_criteria":["Pass scoped tests"]})
        self.assertEqual(same.status_code,201)
        self.assertEqual(same.json(),created)
        changed=self.client.post("/v1/projects/alpha/tasks",
            headers=self.h(idem="create-0001"),
            json={"title":"Another task","acceptance_criteria":["Pass scoped tests"]})
        self.assertEqual(changed.status_code,409)
        tid=created["task_id"]
        done=self.client.post(
            f"/v1/projects/alpha/tasks/{tid}/publish",
            headers=self.h(idem="publish-0002"),json={"expected_version":1})
        self.assertEqual(done.status_code,200)
        stale=self.client.post(
            f"/v1/projects/alpha/tasks/{tid}/publish",
            headers=self.h(idem="publish-0003"),json={"expected_version":1})
        self.assertEqual(stale.status_code,409)

    def test_malformed_evidence_does_not_mutate_task(self):
        a=self.running()
        tid=a["task_id"]
        resp=self.client.post(
            f"/v1/projects/alpha/tasks/{tid}/submit",
            headers=self.h(idem="bad-evidence-0001"),
            json={"expected_version":3,"lease_token":a["lease_token"],
                  "evidence_url":"http://example.com/not-proof"}
        )
        self.assertEqual(resp.status_code,422)
        row=self.client.get(f"/v1/projects/alpha/tasks/{tid}",headers=self.h())
        self.assertEqual(row.json()["status"],"IN_PROGRESS")

    def test_error_response_does_not_disclose_token(self):
        a=self.create()
        res=self.client.post(
            f"/v1/projects/alpha/tasks/{a['task_id']}/claim",
            headers=self.h(idem="claim-invalid-0001"),json={"expected_version":1}
        )
        self.assertEqual(res.status_code,409)
        self.assertNotIn(self.keys["agent-a"],res.text)
        self.assertEqual(res.headers["cache-control"],"no-store")


if __name__=="__main__":
    unittest.main()
