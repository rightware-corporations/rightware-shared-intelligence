"""G01 policy event journal in a synthetic disposable PostgreSQL lab."""
from __future__ import annotations
import os
import unittest
from unittest.mock import patch
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row
import test_r2_r1b_ledger as fixture
from test_r2_r1b_ledger import _DSN,_SAFE
from rightware_si.core import AccessDenied, Conflict, Missing
from rightware_si.policy_lifecycle import PolicyLifecycle
from rightware_si.token_admin import issue_api_token

@unittest.skipUnless(_SAFE,"requires isolated rw_test")
class G01LifecycleLabTests(unittest.TestCase):
    def setUp(self):
        self.old=fixture.VerificationLedgerLabTests(
            "test_01_success_is_append_only_and_never_done")
        self.old.setUp()
        self.flags=patch.dict(os.environ,{
            "RW_SI_ENVIRONMENT":"lab","RW_SI_ENABLE_R2_R1C_LAB_API":"1",
            "RW_SI_ENABLE_R2_G01_LAB_POLICY":"1"})
        self.flags.start()
        self.addCleanup(self.flags.stop)
        with psycopg.connect(_DSN) as conn:
            conn.execute("INSERT INTO si_principals(id,principal_kind) VALUES"
                         "('approver','HUMAN'),('disabler','HUMAN')")
            for who,perm in (
                ("operator","policy:propose"),
                ("approver","policy:approve"),
                ("approver","policy:disable"),
                ("disabler","policy:disable")):
                conn.execute("INSERT INTO si_project_grants "
                             "(project_id,principal_id,permission) "
                             "VALUES('alpha',%s,%s)",(who,perm))
        self.op=issue_api_token(_DSN,"operator",1)[1]
        self.ap=issue_api_token(_DSN,"approver",1)[1]
        self.dis=issue_api_token(_DSN,"disabler",1)[1]
        self.life=PolicyLifecycle(_DSN)

    def proposed(self):
        return self.life.propose("alpha",self.op,self.old.policy_id,
                                 "g01-prop-"+uuid4().hex[:12])

    def active(self):
        p=self.proposed()
        a=self.life.approve("alpha",self.ap,self.old.policy_id,
            "g01-appr-"+uuid4().hex[:12],p["sequence"])
        return p,a

    def test_01_unapproved_denied(self):
        with psycopg.connect(_DSN,row_factory=dict_row) as conn:
            with self.assertRaises(Conflict):
                self.life.require_active(conn,"alpha",self.old.policy_id)

    def test_02_independent_two_human_activation_and_seven_day_window(self):
        self.active()
        with psycopg.connect(_DSN,row_factory=dict_row) as conn:
            self.life.require_active(conn,"alpha",self.old.policy_id)
            a=conn.execute("SELECT recorded_at,valid_until FROM "
                "si_policy_lifecycle_events WHERE event_type='ACTIVATED'").fetchone()
        delta=(a["valid_until"]-a["recorded_at"]).total_seconds()
        self.assertTrue(604790 < delta < 604810)

    def test_03_service_cannot_approve_even_with_grant(self):
        p=self.proposed()
        with psycopg.connect(_DSN) as conn:
            conn.execute("INSERT INTO si_project_grants "
                         "(project_id,principal_id,permission) "
                         "VALUES('alpha','verifier','policy:approve')")
        with self.assertRaises(AccessDenied):
            self.life.approve("alpha",self.old.tokens["verifier"],
                              self.old.policy_id,"g01-unauth-service-001",p["sequence"])

    def test_04_policy_author_cannot_self_approve(self):
        p=self.proposed()
        with psycopg.connect(_DSN) as conn:
            conn.execute("INSERT INTO si_project_grants "
                         "(project_id,principal_id,permission) "
                         "VALUES('alpha','operator','policy:approve')")
        with self.assertRaises(AccessDenied):
            self.life.approve("alpha",self.op,self.old.policy_id,
                              "g01-author-approve-001",p["sequence"])

    def test_05_disable_is_terminal_and_preserves_history(self):
        _,a=self.active()
        self.life.disable("alpha",self.dis,self.old.policy_id,
            "g01-disable-001",a["sequence"],"PILOT_REVOKE")
        with psycopg.connect(_DSN,row_factory=dict_row) as conn:
            with self.assertRaises(Conflict):
                self.life.require_active(conn,"alpha",self.old.policy_id)
            count=conn.execute("SELECT count(*) FROM si_policy_lifecycle_events").fetchone()[0]
        self.assertEqual(count,3)

    def test_06_superseded_policy_cannot_activate_successor_automatically(self):
        _,a=self.active()
        successor=self.old.seed_policy(version=2)
        self.life.supersede("alpha",self.ap,self.old.policy_id,successor,
            "g01-supersede-001",a["sequence"])
        with psycopg.connect(_DSN,row_factory=dict_row) as conn:
            with self.assertRaises(Conflict):
                self.life.require_active(conn,"alpha",successor)
            with self.assertRaises(Conflict):
                self.life.require_active(conn,"alpha",self.old.policy_id)

    def test_07_stale_generation_rejected(self):
        p=self.proposed()
        with self.assertRaises(Conflict):
            self.life.approve("alpha",self.ap,self.old.policy_id,
                              "g01-stale-approve-001",0)
        self.life.approve("alpha",self.ap,self.old.policy_id,
                          "g01-stale-approve-001",p["sequence"])

    def test_08_append_only_sql_update_delete_rejected(self):
        self.active()
        with psycopg.connect(_DSN) as conn:
            with self.assertRaises(psycopg.errors.CheckViolation):
                conn.execute("DELETE FROM si_policy_lifecycle_events "
                             "WHERE policy_id=%s::uuid",(self.old.policy_id,))
        with psycopg.connect(_DSN) as conn:
            with self.assertRaises(psycopg.errors.CheckViolation):
                conn.execute("UPDATE si_policy_lifecycle_events SET "
                             "event_type='DISABLED' WHERE policy_id=%s::uuid",
                             (self.old.policy_id,))

if __name__=="__main__":
    unittest.main()
