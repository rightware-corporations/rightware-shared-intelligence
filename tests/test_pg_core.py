"""WORK-02A real PostgreSQL integration tests on disposable synthetic database.

Tests intentionally do not run unless RW_TEST_DATABASE_URL points to a
dedicated database ending in /rw_test. They never connect to Jarvis/PULSE.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import os
import unittest
from urllib.parse import urlsplit

try:
    import psycopg
    from rightware_si.core import AccessDenied, Conflict, InvalidTransition, WorkCore
except ImportError:
    psycopg = None


_DSN = os.environ.get("RW_TEST_DATABASE_URL", "")
_SAFE = bool(_DSN and urlsplit(_DSN).path == "/rw_test")


@unittest.skipUnless(psycopg is not None and _SAFE,
                     "real Postgres tests require RW_TEST_DATABASE_URL ending /rw_test")
class PostgresCoreTests(unittest.TestCase):
    def setUp(self):
        self.dsn = _DSN
        self.core = WorkCore(self.dsn)
        # THIS IS A DISPOSABLE INTEGRATION TEST DATABASE ONLY.
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            conn.execute("TRUNCATE si_organizations,si_principals RESTART IDENTITY CASCADE")
            conn.execute("INSERT INTO si_organizations(id) VALUES ('rightware')")
            conn.execute(
                "INSERT INTO si_projects(id,organization_id) VALUES "
                "('alpha','rightware'),('beta','rightware')"
            )
            conn.execute(
                "INSERT INTO si_principals(id,principal_kind) VALUES "
                "('agent-a','AGENT'),('agent-b','AGENT'),"
                "('reviewer','HUMAN'),('intruder','AGENT')"
            )
            grants = {
                "agent-a": ["task:create","task:manage","task:execute",
                            "task:read","handoff:offer","audit:read"],
                "agent-b": ["task:execute","task:read","handoff:accept","audit:read"],
                "reviewer": ["task:read","audit:read"],
            }
            for actor, permissions in grants.items():
                for permission in permissions:
                    conn.execute(
                        "INSERT INTO si_project_grants(project_id,principal_id,permission) "
                        "VALUES (%s,%s,%s)", ("alpha",actor,permission),
                    )

    def make_draft(self):
        return self.core.create_task("alpha","agent-a","Implement memory bridge",
                                     ["Validates source identifiers"],"create-0001")

    def make_running(self):
        t=self.make_draft()
        t=self.core.publish_task("alpha","agent-a",t["task_id"],1,"publish-0001")
        claimed=self.core.claim_task("alpha","agent-a",t["task_id"],2,"claim-0001")
        return claimed

    def handoff(self):
        c=self.make_running()
        offer=self.core.offer_handoff(
            "alpha","agent-a",c["task_id"],"agent-b",
            "Bridge implemented; tests pending",c["lease_token"],3,"offer-0001")
        return c,offer

    def test_create_publish_claim_is_versioned(self):
        a=self.make_running()
        self.assertEqual((a["status"],a["version"]),("IN_PROGRESS",3))
        current=self.core.get_task("alpha","agent-a",a["task_id"])
        self.assertEqual(current["version"],3)
        events=self.core.task_events("alpha","agent-a",a["task_id"])
        self.assertEqual([e["task_version"] for e in events],[1,2,3])

    def test_idempotency_and_reuse_conflict(self):
        one=self.make_draft()
        two=self.make_draft()
        self.assertEqual(one,two)
        with self.assertRaises(Conflict):
            self.core.create_task("alpha","agent-a","Changed",
                                  ["Validates source identifiers"],"create-0001")

    def test_stale_expected_version_rejected(self):
        a=self.make_running()
        with self.assertRaises(Conflict):
            self.core.publish_task("alpha","agent-a",a["task_id"],1,"publish-stale")
        self.assertEqual(self.core.get_task("alpha","agent-a",a["task_id"])["version"],3)

    def test_scope_requires_server_side_grant(self):
        with self.assertRaises(AccessDenied):
            self.core.create_task("beta","agent-a","Unpermitted",["No"],"create-beta")
        with self.assertRaises(AccessDenied):
            self.core.get_task("alpha","intruder",self.make_draft()["task_id"])

    def test_handoff_transfers_exclusive_lease(self):
        a,off=self.handoff()
        self.assertEqual(off["status"],"BLOCKED")
        b=self.core.accept_handoff("alpha","agent-b",off["handoff_id"],4,"accept-0001")
        self.assertEqual((b["status"],b["version"]),("IN_PROGRESS",5))
        with self.assertRaises(Conflict):
            self.core.submit_result("alpha","agent-a",a["task_id"],5,
                                    a["lease_token"],
                                    "https://github.com/example/repo/commit/123",
                                    "submit-old")
        result=self.core.submit_result(
            "alpha","agent-b",a["task_id"],5,b["lease_token"],
            "https://github.com/example/repo/commit/123","submit-new")
        self.assertEqual((result["status"],result["version"]),("IN_REVIEW",6))
        self.assertEqual(result["verification_state"],"REFERENCED")
        self.assertEqual(len(self.core.task_events("alpha","agent-a",a["task_id"])),6)

    def test_lease_secrets_never_persist_in_idempotency(self):
        a=self.make_running()
        with psycopg.connect(self.dsn) as conn:
            row=conn.execute(
                "SELECT response FROM si_idempotency WHERE "
                "project_id='alpha' AND principal_id='agent-a' "
                "AND action='claim_task' AND idem_key='claim-0001'"
            ).fetchone()
        self.assertNotIn("lease_token",row[0])
        self.assertEqual(row[0]["status"],"IN_PROGRESS")
        # One-time lease credential cannot be reconstructed from a DB read
        # or re-issued through a duplicate idempotency key.
        with self.assertRaises(Conflict):
            self.core.claim_task("alpha","agent-a",a["task_id"],2,"claim-0001")
        with psycopg.connect(self.dsn) as conn:
            row=conn.execute(
                "SELECT response FROM si_idempotency WHERE "
                "project_id='alpha' AND principal_id='agent-a' "
                "AND action='claim_task' AND idem_key='claim-0001'"
            ).fetchone()
        self.assertNotIn("lease_token",row[0])

    def test_accepted_handoff_secret_not_replayable(self):
        _,off=self.handoff()
        result=self.core.accept_handoff(
            "alpha","agent-b",off["handoff_id"],4,"accept-0001"
        )
        self.assertIn("lease_token",result)
        with psycopg.connect(self.dsn) as conn:
            row=conn.execute(
                "SELECT response FROM si_idempotency WHERE "
                "project_id='alpha' AND principal_id='agent-b' "
                "AND action='accept_handoff' AND idem_key='accept-0001'"
            ).fetchone()
        self.assertNotIn("lease_token",row[0])
        with self.assertRaises(Conflict):
            self.core.accept_handoff(
                "alpha","agent-b",off["handoff_id"],4,"accept-0001"
            )

    def test_handoff_other_principal_denied(self):
        _,off=self.handoff()
        with self.assertRaises(AccessDenied):
            self.core.accept_handoff("alpha","intruder",off["handoff_id"],4,"intruder-1")
        with self.assertRaises(AccessDenied):
            self.core.accept_handoff("alpha","agent-a",off["handoff_id"],4,"source-1")

    def test_no_direct_done_or_unverified_success(self):
        a=self.make_running()
        with self.assertRaises(ValueError):
            self.core.submit_result("alpha","agent-a",a["task_id"],3,
                                    a["lease_token"],"http://example.com",
                                    "submit-insecure")
        self.assertEqual(self.core.get_task("alpha","agent-a",a["task_id"])["status"],
                         "IN_PROGRESS")

    def test_concurrent_handoff_acceptance_has_one_winner(self):
        a,off=self.handoff()
        def accept(k):
            try:
                return self.core.accept_handoff(
                    "alpha","agent-b",off["handoff_id"],4,"accept-parallel-"+k)
            except Conflict:
                return "CONFLICT"
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(accept,["a","b"]))
        self.assertEqual(sum(isinstance(x,dict) for x in results),1)
        self.assertEqual(results.count("CONFLICT"),1)
        self.assertEqual(self.core.get_task("alpha","agent-b",a["task_id"])["version"],5)


if __name__ == "__main__":
    unittest.main()
