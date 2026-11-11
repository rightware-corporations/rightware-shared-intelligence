"""WORK-02C local service API shape tests with FAKE Mem0 engine.

These do not assert real Mem0 embedding accuracy or self-hosted runtime.
"""
from __future__ import annotations
import unittest

from fastapi.testclient import TestClient
from rightware_si.mem0_local_service import create_mem0_lab_app

KEY = "local-only-synthetic-secret-" + "x" * 45


class FakeMem0:
    def __init__(self):
        self.memories=[]
        self.calls=[]

    def add(self,**kwargs):
        self.calls.append(("add",kwargs))
        self.memories.append(kwargs)
        return {"results":[{"id":"mem01","memory":kwargs["messages"][0]["content"],
                             "event":"ADD"}]}

    def search(self,**kwargs):
        self.calls.append(("search",kwargs))
        return {"results":[{
            "id":"mem01","memory":"Synthetic authorized note",
            "user_id":kwargs["filters"]["user_id"],
            "metadata":{"rw_kind":"note"},
        }]}


class ShimTests(unittest.TestCase):
    def setUp(self):
        self.fake=FakeMem0()
        self.client=TestClient(create_mem0_lab_app(self.fake,api_key=KEY))
        self.headers={"X-API-Key":KEY}

    def test_authentication_required(self):
        r=self.client.post("/search",json={"query":"test","filters":{"user_id":"rw:org:alpha"}})
        self.assertEqual(r.status_code,401)
        self.assertEqual(self.fake.calls,[])

    def test_scoped_infer_false_write(self):
        data={"messages":[{"role":"user","content":"synthetic non-secret"}],
              "user_id":"rw:org:alpha","agent_id":"agent-a",
              "metadata":{"rw_source":"synthetic"},"infer":False}
        r=self.client.post("/memories",headers=self.headers,json=data)
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(self.fake.calls[0][1]["infer"],False)
        data["infer"]=True
        self.assertEqual(self.client.post("/memories",headers=self.headers,json=data).status_code,422)

    def test_scope_required_in_search(self):
        r=self.client.post("/search",headers=self.headers,
            json={"query":"project","filters":{"user_id":"rw:org:alpha"},"top_k":3})
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()["results"][0]["user_id"],"rw:org:alpha")
        self.assertEqual(self.client.post("/search",headers=self.headers,
            json={"query":"project","filters":{"user_id":"cross-project"}}).status_code,422)
        self.assertEqual(self.client.post("/search",headers=self.headers,
            json={"query":"project","filters":{"user_id":"rw:org:alpha","agent_id":"x"}}).status_code,422)

    def test_bad_key_denied(self):
        self.assertEqual(self.client.post("/search",
            headers={"X-API-Key":"wrong"},json={"query":"test",
            "filters":{"user_id":"rw:org:alpha"}}).status_code,401)


if __name__=="__main__":
    unittest.main()
