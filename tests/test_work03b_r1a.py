"""WORK-03B R1A: real disposable PostgreSQL + bearer REST integration.

Never run on production or on Jarvis/PULSE databases. These are R1A lab
assertions only; checkpoint/resume, verifier and DONE remain out of scope.
"""
from __future__ import annotations

import os
from rightware_si.lab_boundary import require_disposable_postgres, is_disposable_postgres
from uuid import uuid4
import unittest

import psycopg
from fastapi.testclient import TestClient

from rightware_si.http_api import create_app
from rightware_si.token_admin import issue_api_token, revoke_api_token

_DSN = os.environ.get("RW_TEST_DATABASE_URL", "")
_SAFE = is_disposable_postgres(_DSN, expected_user="rw")


@unittest.skipUnless(_SAFE, "requires disposable local PostgreSQL /rw_test")
class Work03BR1ATests(unittest.TestCase):
    def setUp(self):
        # Check again at use-time: PGHOSTADDR may change after module import.
        require_disposable_postgres(_DSN, expected_user="rw")
        with psycopg.connect(_DSN, autocommit=True) as conn:
            conn.execute("TRUNCATE si_organizations,si_principals RESTART IDENTITY CASCADE")
            conn.execute("INSERT INTO si_organizations(id) VALUES('rw-synthetic'),('separate')")
            conn.execute(
                "INSERT INTO si_projects(id,organization_id) VALUES"
                "('alpha','rw-synthetic'),('beta','separate')"
            )
            conn.execute(
                "INSERT INTO si_principals(id,principal_kind) VALUES"
                "('agent-a','AGENT'),('agent-b','AGENT'),"
                "('reviewer','HUMAN'),('intruder','AGENT')"
            )
            grants = {
                "agent-a": (
                    "task:create", "task:manage", "task:execute", "task:read",
                    "context:read", "audit:read", "handoff:offer",
                    "source:write", "observation:write"
                ),
                "agent-b": (
                    "task:read", "task:execute", "context:read",
                    "handoff:accept", "source:write", "observation:write"
                ),
                "reviewer": ("task:read",),
            }
            for actor, permissions in grants.items():
                for permission in permissions:
                    conn.execute(
                        "INSERT INTO si_project_grants(project_id,principal_id,permission) "
                        "VALUES('alpha',%s,%s)", (actor, permission),
                    )
        self.tokens = {}
        self.token_ids = {}
        for actor in ("agent-a", "agent-b", "reviewer", "intruder"):
            token_id, token = issue_api_token(_DSN, actor, 24)
            self.token_ids[actor] = token_id
            self.tokens[actor] = token
        self.client = TestClient(create_app(_DSN))
        self.sequence = 0

    def headers(self, actor="agent-a", idem=None):
        h = {"Authorization": f"Bearer {self.tokens[actor]}"}
        if idem:
            h["Idempotency-Key"] = idem
        return h

    def send(self, path, body, actor="agent-a", idem=None):
        self.sequence += 1
        idem = idem or f"r1a-idem-{self.sequence:05d}"
        return self.client.post(path, json=body, headers=self.headers(actor, idem))

    def running(self):
        created = self.send(
            "/v1/projects/alpha/tasks",
            {"title": "R1A synthetic continuity work",
             "acceptance_criteria": ["Observation is source-linked and unverified"]},
        )
        self.assertEqual(created.status_code, 201, created.text)
        task_id = created.json()["task_id"]
        published = self.send(
            f"/v1/projects/alpha/tasks/{task_id}/publish",
            {"expected_version": 1},
        )
        self.assertEqual(published.status_code, 200, published.text)
        claim = self.send(
            f"/v1/projects/alpha/tasks/{task_id}/claim",
            {"expected_version": 2},
        )
        self.assertEqual(claim.status_code, 200, claim.text)
        return task_id, claim.json()["lease_token"]

    def run_start(self, task_id, lease, version=3, actor="agent-a", idem=None):
        res = self.send(
            f"/v1/projects/alpha/tasks/{task_id}/runs",
            {"expected_version": version, "lease_token": lease,
             "runtime_label": "synthetic-ci-agent"},
            actor=actor, idem=idem,
        )
        self.assertEqual(res.status_code, 201, res.text)
        return res.json()

    def source(self, task_id, run_id, lease, version=3, actor="agent-a",
               kind="GIT_REF", uri="https://github.com/rightware-corporations/rightware-shared-intelligence/commit/abc123",
               idem=None):
        res = self.send(
            "/v1/projects/alpha/sources",
            {"task_id": task_id, "agent_run_id": run_id,
             "expected_version": version, "lease_token": lease,
             "source_kind": kind, "source_uri": uri,
             "source_revision": "abc123"},
            actor=actor, idem=idem,
        )
        self.assertEqual(res.status_code, 201, res.text)
        return res.json()

    def observation(self, task_id, run_id, lease, source_ids,
                    version=3, actor="agent-a", claim="Unit tests are written",
                    idem=None):
        return self.send(
            "/v1/projects/alpha/observations",
            {"task_id": task_id, "agent_run_id": run_id,
             "expected_version": version, "lease_token": lease,
             "claim": claim, "source_ids": source_ids},
            actor=actor, idem=idem,
        )

    def test_end_to_end_source_linked_assertion_keeps_task_version(self):
        task, lease = self.running()
        run = self.run_start(task, lease)
        self.assertEqual(run["actor_id"], "agent-a")
        self.assertTrue(run["correlation_id"])
        source = self.source(task, run["run_id"], lease)
        self.assertEqual(source["trust"], "SOURCE_LINKED_UNVERIFIED")
        obs = self.observation(task, run["run_id"], lease, [source["source_id"]])
        self.assertEqual(obs.status_code, 201, obs.text)
        self.assertEqual(obs.json()["trust_state"], "ASSERTED")
        get = self.client.get(
            f"/v1/projects/alpha/tasks/{task}/observations",
            headers=self.headers(),
        )
        self.assertEqual(get.status_code, 200, get.text)
        records = get.json()["observations"]
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["asserted_by"], "agent-a")
        self.assertEqual(records[0]["source_ids"], [source["source_id"]])
        self.assertEqual(records[0]["trust_state"], "ASSERTED")
        task_state = self.client.get(
            f"/v1/projects/alpha/tasks/{task}", headers=self.headers(),
        ).json()
        self.assertEqual((task_state["status"], task_state["version"]), ("IN_PROGRESS", 3))
        with psycopg.connect(_DSN) as conn:
            events = conn.execute(
                "SELECT event_type,task_version,payload FROM si_continuity_events "
                "WHERE project_id='alpha' AND task_id=%s::uuid ORDER BY id",
                (task,),
            ).fetchall()
            self.assertEqual([x[0] for x in events],
                             ["AGENT_RUN_STARTED", "SOURCE_REGISTERED", "OBSERVATION_ASSERTED"])
            self.assertEqual([x[1] for x in events], [3, 3, 3])
            self.assertNotIn(lease, str(events))
            self.assertNotIn("Unit tests are written", str(events))
            row = conn.execute(
                "SELECT trust_state FROM si_observations WHERE id=%s::uuid",
                (obs.json()["observation_id"],),
            ).fetchone()
            self.assertEqual(row[0], "ASSERTED")

    def test_run_requires_current_lease_and_version(self):
        task, lease = self.running()
        bad = self.send(
            f"/v1/projects/alpha/tasks/{task}/runs",
            {"expected_version": 2, "lease_token": lease,
             "runtime_label": "synthetic"},
        )
        self.assertEqual(bad.status_code, 409)
        bad_token = self.send(
            f"/v1/projects/alpha/tasks/{task}/runs",
            {"expected_version": 3, "lease_token": "x" * 32,
             "runtime_label": "synthetic"},
        )
        self.assertEqual(bad_token.status_code, 409)
        with psycopg.connect(_DSN) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM si_agent_runs").fetchone()[0], 0)

    def test_idempotent_run_source_observation_and_conflict(self):
        task, lease = self.running()
        path = f"/v1/projects/alpha/tasks/{task}/runs"
        body = {"expected_version": 3, "lease_token": lease,
                "runtime_label": "synthetic-ci-agent"}
        one = self.send(path, body, idem="run-replay-0001")
        two = self.send(path, body, idem="run-replay-0001")
        self.assertEqual(one.status_code, 201, one.text)
        self.assertEqual(two.json(), one.json())
        bad = self.send(path, dict(body, runtime_label="other"), idem="run-replay-0001")
        self.assertEqual(bad.status_code, 409)
        second = self.send(path, body, idem="run-new-0001")
        self.assertEqual(second.status_code, 409)
        source = self.source(task, one.json()["run_id"], lease, idem="source-replay-0001")
        source_body = {
            "task_id": task, "agent_run_id": one.json()["run_id"], "expected_version": 3,
            "lease_token": lease, "source_kind": "GIT_REF",
            "source_uri": "https://github.com/rightware-corporations/rightware-shared-intelligence/commit/abc123",
            "source_revision": "abc123"
        }
        same_source = self.send("/v1/projects/alpha/sources", source_body,
                                idem="source-replay-0001")
        self.assertEqual(same_source.json(), source)
        obs = self.observation(task, one.json()["run_id"], lease, [source["source_id"]],
                               idem="obs-replay-0001")
        self.assertEqual(obs.status_code, 201, obs.text)
        same_obs = self.observation(task, one.json()["run_id"], lease,
                                    [source["source_id"]], idem="obs-replay-0001")
        self.assertEqual(obs.json(), same_obs.json())
        with psycopg.connect(_DSN) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM si_agent_runs").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT count(*) FROM si_source_records").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT count(*) FROM si_observations").fetchone()[0], 1)

    def test_cross_project_and_read_permissions(self):
        task, lease = self.running()
        run = self.run_start(task, lease)
        source = self.source(task, run["run_id"], lease)
        self.assertEqual(self.observation(
            task, run["run_id"], lease, [source["source_id"]]
        ).status_code, 201)
        base = f"/v1/projects/alpha/tasks/{task}/observations"
        for actor in ("intruder", "reviewer"):
            r = self.client.get(base, headers=self.headers(actor))
            self.assertEqual(r.status_code, 403, r.text)
            self.assertNotIn("Unit tests are written", r.text)
        beta = self.client.get(
            f"/v1/projects/beta/tasks/{task}/observations",
            headers=self.headers(),
        )
        self.assertEqual(beta.status_code, 403)
        spoof = self.send(
            "/v1/projects/alpha/observations",
            {"task_id": task, "agent_run_id": run["run_id"],
             "expected_version": 3, "lease_token": lease,
             "claim": "Fake approved", "source_ids": [source["source_id"]],
             "actor_id": "reviewer", "trust_state": "APPROVED"},
        )
        self.assertEqual(spoof.status_code, 422)
        with psycopg.connect(_DSN) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM si_observations").fetchone()[0], 1)

    def test_permission_revocation_blocks_new_writes_and_reads(self):
        task, lease = self.running()
        run = self.run_start(task, lease)
        with psycopg.connect(_DSN) as conn:
            conn.execute(
                "DELETE FROM si_project_grants WHERE project_id='alpha' "
                "AND principal_id='agent-a' AND permission='source:write'"
            )
        denied = self.send(
            "/v1/projects/alpha/sources",
            {"task_id": task, "agent_run_id": run["run_id"],
             "expected_version": 3, "lease_token": lease,
             "source_kind": "GIT_REF",
             "source_uri": "https://github.com/example/repo/commit/abc",
             "source_revision": "abc"},
        )
        self.assertEqual(denied.status_code, 403)
        self.assertTrue(revoke_api_token(_DSN, self.token_ids["agent-a"]))
        self.assertEqual(
            self.client.get(
                f"/v1/projects/alpha/tasks/{task}/observations",
                headers=self.headers()
            ).status_code, 401
        )

    def test_source_must_belong_to_same_task_and_run(self):
        task1, lease1 = self.running()
        run1 = self.run_start(task1, lease1)
        source = self.source(task1, run1["run_id"], lease1)
        task2, lease2 = self.running()
        run2 = self.run_start(task2, lease2)
        invalid = self.observation(
            task2, run2["run_id"], lease2, [source["source_id"]]
        )
        self.assertEqual(invalid.status_code, 404, invalid.text)
        wrong_run = self.observation(
            task2, run1["run_id"], lease2, [source["source_id"]]
        )
        self.assertEqual(wrong_run.status_code, 404, wrong_run.text)
        with psycopg.connect(_DSN) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM si_observations").fetchone()[0], 0)

    def test_handoff_revokes_agent_a_write_and_b_can_start_new_run(self):
        task, lease = self.running()
        run = self.run_start(task, lease)
        source = self.source(task, run["run_id"], lease)
        offered = self.send(
            f"/v1/projects/alpha/tasks/{task}/handoffs",
            {"expected_version": 3, "lease_token": lease, "to_principal_id": "agent-b",
             "summary": "Synthetic source registered; checkpoint is not implemented"},
        )
        self.assertEqual(offered.status_code, 201, offered.text)
        stale = self.observation(
            task, run["run_id"], lease, [source["source_id"]], version=4
        )
        self.assertEqual(stale.status_code, 409, stale.text)
        accepted = self.send(
            f"/v1/projects/alpha/handoffs/{offered.json()['handoff_id']}/accept",
            {"expected_version": 4}, actor="agent-b",
        )
        self.assertEqual(accepted.status_code, 200, accepted.text)
        token_b = accepted.json()["lease_token"]
        run_b = self.run_start(task, token_b, version=5, actor="agent-b")
        self.assertEqual(run_b["actor_id"], "agent-b")
        b_source = self.source(
            task, run_b["run_id"], token_b, version=5, actor="agent-b",
            kind="TOOL_RECEIPT", uri="urn:rw:tool-receipt-001",
        )
        b_obs = self.observation(
            task, run_b["run_id"], token_b, [b_source["source_id"]],
            version=5, actor="agent-b", claim="B continued on a new lease"
        )
        self.assertEqual(b_obs.status_code, 201, b_obs.text)
        self.assertEqual(
            self.client.get(
                f"/v1/projects/alpha/tasks/{task}", headers=self.headers("agent-b")
            ).json()["version"], 5
        )
        self.assertEqual(
            self.client.get(
                f"/v1/projects/alpha/tasks/{task}/observations",
                headers=self.headers("agent-b")
            ).json()["observations"][0]["asserted_by"], "agent-b"
        )

    def test_invalid_source_and_unverified_status_fails_closed(self):
        task, lease = self.running()
        run = self.run_start(task, lease)
        base = {"task_id": task, "agent_run_id": run["run_id"],
                "expected_version": 3, "lease_token": lease,
                "source_kind": "GIT_REF", "source_revision": "abc123"}
        invalid = self.send(
            "/v1/projects/alpha/sources",
            dict(base, source_uri="http://127.0.0.1/secret"),
        )
        self.assertEqual(invalid.status_code, 422)
        invalid_digest = self.send(
            "/v1/projects/alpha/sources",
            dict(base, source_uri="https://github.com/example/repo", digest_sha256="xyz"),
        )
        self.assertEqual(invalid_digest.status_code, 422)
        invalid_claim = self.send(
            "/v1/projects/alpha/observations",
            {"task_id": task, "agent_run_id": run["run_id"],
             "expected_version": 3, "lease_token": lease,
             "claim": "I approved everything", "source_ids": [],
             "trust_state": "APPROVED"},
        )
        self.assertEqual(invalid_claim.status_code, 422)
        with psycopg.connect(_DSN) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM si_source_records").fetchone()[0], 0)
            self.assertEqual(conn.execute("SELECT count(*) FROM si_observations").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
