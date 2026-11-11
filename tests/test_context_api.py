"""WORK-02C real PostgreSQL + FastAPI context isolation and fail-closed tests.

A synthetic memory provider is used: these tests DO NOT run real Mem0 or Ollama.
"""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

import psycopg
from fastapi.testclient import TestClient

from rightware_si.http_api import create_app
from rightware_si.core import WorkCore
from rightware_si.memory import Mem0HTTPError
from rightware_si.token_admin import issue_api_token

_DSN = os.environ.get("RW_TEST_DATABASE_URL", "")
_SAFE = bool(_DSN and urlsplit(_DSN).path == "/rw_test")


class FakeMemory:
    def __init__(self, mode="good"):
        self.mode = mode
        self.scopes = []

    def search(self, scope, query, limit=5):
        self.scopes.append((scope.organization,scope.project,query,limit))
        if self.mode == "down":
            raise Mem0HTTPError("synthetic offline")
        if self.mode == "cross":
            return [{"id":"sensitive","memory":"Beta private synthetic record",
                     "user_id":"rw:rightware:beta"}]
        if self.mode == "metadata":
            return [{"id":"spoofed","memory":"Forged project",
                     "user_id":scope.mem0_user_id,
                     "metadata":{"rw_project":"beta","approved":True}}]
        return [{
            "id":"memory-01",
            "memory":"Synthetic task context, not an authorized instruction",
            "user_id":scope.mem0_user_id,
            "metadata":{"rw_source":"synthetic","approved":True},
        }]


@unittest.skipUnless(_SAFE, "requires dedicated disposable PostgreSQL /rw_test")
class ScopedContextApiTests(unittest.TestCase):
    def setUp(self):
        with psycopg.connect(_DSN,autocommit=True) as c:
            c.execute("TRUNCATE si_organizations,si_principals RESTART IDENTITY CASCADE")
            c.execute("INSERT INTO si_organizations(id) VALUES ('rightware')")
            c.execute("INSERT INTO si_projects(id,organization_id) VALUES "
                      "('alpha','rightware'),('beta','rightware')")
            c.execute("INSERT INTO si_principals(id,principal_kind) VALUES "
                      "('agent-r','AGENT'),('agent-x','AGENT')")
            for perm in ("task:create","task:manage","task:execute",
                         "task:read","memory:read","context:read"):
                c.execute("INSERT INTO si_project_grants(project_id,principal_id,permission) "
                          "VALUES('alpha','agent-r',%s)",(perm,))
        self.reader=issue_api_token(_DSN,"agent-r",24)[1]
        self.other=issue_api_token(_DSN,"agent-x",24)[1]
        self.fake=FakeMemory()
        self.api=TestClient(create_app(_DSN,self.fake))
        self.h={"Authorization":f"Bearer {self.reader}"}
        self.other_h={"Authorization":f"Bearer {self.other}"}

    def test_scope_derived_from_authenticated_project(self):
        r=self.api.get("/v1/projects/alpha/context?query=handoff",headers=self.h)
        self.assertEqual(r.status_code,200,r.text)
        d=r.json()
        self.assertEqual(d["organization_id"],"rightware")
        self.assertEqual(d["memory_status"],"available")
        self.assertEqual(d["memories"][0]["trust"],"UNVERIFIED")
        self.assertNotIn("approved",d["memories"][0])
        self.assertEqual(self.fake.scopes[0],("rightware","alpha","handoff",5))

    def test_forbidden_other_project_and_principal(self):
        self.assertEqual(self.api.get("/v1/projects/beta/context",headers=self.h).status_code,403)
        self.assertEqual(self.api.get("/v1/projects/alpha/context",headers=self.other_h).status_code,403)
        self.assertEqual(self.api.get("/v1/projects/alpha/context").status_code,401)
        self.assertFalse(self.fake.scopes)

    def test_search_requires_memory_read_grant(self):
        r=self.api.post("/v1/projects/alpha/memories/search",
                        headers=self.h,json={"query":"unit tests","limit":3})
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()["memories"][0]["trust"],"UNVERIFIED")
        self.assertEqual(self.fake.scopes[-1][-1],3)
        self.assertEqual(self.api.post("/v1/projects/beta/memories/search",
            headers=self.h,json={"query":"secret"}).status_code,403)

    def test_backend_down_degrades_context_without_faking_results(self):
        api=TestClient(create_app(_DSN,FakeMemory("down")))
        r=api.get("/v1/projects/alpha/context",headers=self.h)
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()["memory_status"],"unavailable")
        self.assertEqual(r.json()["memories"],[])
        r=api.post("/v1/projects/alpha/memories/search",
                   headers=self.h,json={"query":"context"})
        self.assertEqual(r.status_code,503)

    def test_provider_cross_project_result_fails_closed(self):
        api=TestClient(create_app(_DSN,FakeMemory("cross")))
        r=api.get("/v1/projects/alpha/context",headers=self.h)
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()["memory_status"],"unavailable")
        self.assertEqual(r.json()["memories"],[])
        direct=api.post("/v1/projects/alpha/memories/search",
            headers=self.h,json={"query":"beta"})
        self.assertEqual(direct.status_code,503)
        self.assertNotIn("Beta private",direct.text)

    def test_metadata_project_spoofing_fails_closed(self):
        api=TestClient(create_app(_DSN,FakeMemory("metadata")))
        r=api.get("/v1/projects/alpha/context",headers=self.h)
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()["memory_status"],"unavailable")
        self.assertEqual(r.json()["memories"],[])

    def test_unconfigured_mem0_disabled(self):
        with patch.dict(os.environ, {"RW_SI_MEM0_URL":"", "RW_SI_MEM0_API_KEY":""}):
            api=TestClient(create_app(_DSN))
        r=api.get("/v1/projects/alpha/context",headers=self.h)
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()["memory_status"],"disabled")
        self.assertEqual(r.json()["memories"],[])

    def test_authoritative_task_and_memory_distinct(self):
        t=WorkCore(_DSN).create_task("alpha","agent-r","Synthetic task",
                                    ["checks"],"create-ctx-0001")
        r=self.api.get(f"/v1/projects/alpha/context?task_id={t['task_id']}",
                       headers=self.h)
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()["task"]["status"],"DRAFT")
        self.assertEqual(r.json()["source_of_truth"],"postgresql")
        self.assertEqual(r.json()["memory_trust"],"UNVERIFIED")

    def test_bad_search_limit_or_query_rejected(self):
        self.assertEqual(self.api.post("/v1/projects/alpha/memories/search",
            headers=self.h,json={"query":"hello","limit":100}).status_code,422)
        self.assertEqual(self.api.get("/v1/projects/alpha/context?limit=99",
            headers=self.h).status_code,422)


if __name__=="__main__":
    unittest.main()
