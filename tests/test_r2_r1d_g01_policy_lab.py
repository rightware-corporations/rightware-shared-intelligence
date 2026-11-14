"""G01 policy event journal in a synthetic disposable PostgreSQL lab."""
from __future__ import annotations
import os
import multiprocessing
import time
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


def _g01_verify_in_separate_process(dsn, service_bearer, policy_id,
                                    entered_provider, provider_resume, out):
    """Real separate Python process; provider response is SIMULATED only."""
    import httpx
    from fastapi.security import HTTPAuthorizationCredentials
    from rightware_si.api_auth import resolve_principal
    from rightware_si.verification_ledger import EvidenceLedger
    from test_r2_r1b_ledger import provider_record

    try:
        actor = resolve_principal(
            dsn, HTTPAuthorizationCredentials(
                scheme="Bearer", credentials=service_bearer))
        def provider(request):
            entered_provider.set()
            if not provider_resume.wait(timeout=25):
                raise RuntimeError("parent did not release synthetic provider")
            return httpx.Response(200, json=provider_record())
        with httpx.Client(transport=httpx.MockTransport(provider)) as client:
            EvidenceLedger(dsn).verify_and_record(
                "alpha", actor, policy_id, 4, "g01-multiprocess-verify-001",
                client=client)
    except Conflict:
        out.put(("VERIFY_REJECTED_AFTER_REVOKE", os.getpid()))
    except Exception as exc:
        out.put(("VERIFY_UNEXPECTED_" + type(exc).__name__, os.getpid()))
    else:
        out.put(("VERIFY_UNSAFE_ACCEPT", os.getpid()))


def _g01_disable_in_separate_process(dsn, disabler_bearer, policy_id,
                                     expected_sequence, out):
    """Separate PostgreSQL client and transaction; no test-process DB reuse."""
    try:
        life = PolicyLifecycle(dsn)
        result = life.disable(
            "alpha", disabler_bearer, policy_id, "g01-multiprocess-disable-001",
            expected_sequence, "PILOT_REVOKE")
        if result["event_type"] != "DISABLED":
            raise AssertionError("no DISABLED lifecycle event")
    except Exception as exc:
        out.put(("DISABLE_UNEXPECTED_" + type(exc).__name__, os.getpid()))
    else:
        out.put(("DISABLE_COMMITTED", os.getpid()))

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
            count=conn.execute("SELECT count(*) AS n FROM si_policy_lifecycle_events").fetchone()["n"]
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


    def test_09_verifier_rejects_unapproved_before_github(self):
        import httpx
        seen=[]
        def handle(request):
            seen.append(1)
            return httpx.Response(200)
        with self.old.mock(handler=handle) as client:
            with self.assertRaises(Conflict):
                self.old.check(client)
        self.assertEqual(seen,[])
        self.assertEqual(self.old.rows(),[])

    def test_10_active_policy_verifies_and_idempotent_replay(self):
        self.active()
        with self.old.mock() as client:
            first=self.old.check(client,key="g01-replay-verify-001")
            second=self.old.check(client,key="g01-replay-verify-001")
        self.assertEqual(first["attempt_id"],second["attempt_id"])
        self.assertEqual(first["result"],"CHECKED_PASS")
        self.assertEqual(len(self.old.rows()),1)

    def test_11_disable_blocks_replay_after_prior_success(self):
        _,a=self.active()
        with self.old.mock() as client:
            first=self.old.check(client,key="g01-revoke-check-001")
            self.life.disable("alpha",self.dis,self.old.policy_id,
                "g01-revoke-after-success-001",a["sequence"],"PILOT_REVOKE")
            with self.assertRaises(Conflict):
                self.old.check(client,key="g01-revoke-check-001")
        self.assertEqual(first["result"],"CHECKED_PASS")
        self.assertEqual(len(self.old.rows()),1)

    def test_12_disable_during_provider_call_blocks_commit(self):
        import httpx
        from test_r2_r1b_ledger import provider_record
        _,a=self.active()
        def handle(request):
            self.life.disable("alpha",self.dis,self.old.policy_id,
                "g01-midflight-revoke-001",a["sequence"],"PILOT_REVOKE")
            return httpx.Response(200,json=provider_record())
        with self.old.mock(handler=handle) as client:
            with self.assertRaises(Conflict):
                self.old.check(client,key="g01-midflight-check-001")
        self.assertEqual(self.old.rows(),[])

    def test_13_expired_db_clock_denies_before_network(self):
        import httpx
        self.proposed()
        # A test-only historical fixture; callers cannot inject timestamps
        # through the authenticated policy lifecycle administration service.
        with psycopg.connect(_DSN) as conn:
            conn.execute("INSERT INTO si_policy_lifecycle_events "
                "(id,project_id,task_id,evidence_id,policy_id,event_type,"
                "actor_id,idempotency_key,valid_until) VALUES("
                "%s::uuid,'alpha',%s::uuid,%s::uuid,%s::uuid,"
                "'ACTIVATED','approver','g01-test-expired-seed-001',"
                "clock_timestamp()-interval '1 second')",
                (str(uuid4()),self.old.task_id,self.old.evidence_id,
                 self.old.policy_id))
        hits=[]
        def handle(req):
            hits.append(1)
            return httpx.Response(200)
        with self.old.mock(handler=handle) as client:
            with self.assertRaises(Conflict):
                self.old.check(client)
        self.assertEqual(hits,[])
        self.assertEqual(self.old.rows(),[])

    def test_14_legacy_compatibility_is_flagged_and_not_implicit(self):
        with self.assertRaises(Conflict):
            with self.old.mock() as client:
                self.old.check(client,key="g01-rejected-legacy-001")
        with patch.dict(os.environ,{"RW_SI_ENABLE_R2_G01_LAB_POLICY":"0"}):
            with self.old.mock() as client:
                success=self.old.check(client,key="g01-legacy-only-001")
        self.assertEqual(success["result"],"CHECKED_PASS")
        with self.old.mock() as client:
            with self.assertRaises(Conflict):
                self.old.check(client,key="g01-legacy-only-001")


    def test_15_reused_disable_idempotency_cannot_change_reason(self):
        _, active = self.active()
        original_key = "g01-disable-reason-once-001"
        result = self.life.disable(
            "alpha", self.dis, self.old.policy_id, original_key,
            active["sequence"], "PILOT_REVOKE")
        self.assertFalse(result["replayed"])
        with self.assertRaises(Conflict):
            self.life.disable(
                "alpha", self.dis, self.old.policy_id, original_key,
                active["sequence"], "DIFFERENT_REASON")

    def test_16_reused_supersession_idempotency_cannot_swap_successor(self):
        _, active = self.active()
        successor_a = self.old.seed_policy(version=2)
        successor_b = self.old.seed_policy(version=3)
        key = "g01-supersede-bound-001"
        saved = self.life.supersede(
            "alpha", self.ap, self.old.policy_id, successor_a,
            key, active["sequence"])
        self.assertEqual(saved["event_type"], "SUPERSEDED")
        with self.assertRaises(Conflict):
            self.life.supersede(
                "alpha", self.ap, self.old.policy_id, successor_b,
                key, active["sequence"])

    def test_17_reused_approval_key_cannot_change_expected_generation(self):
        proposed = self.proposed()
        key = "g01-approval-generation-001"
        self.life.approve(
            "alpha", self.ap, self.old.policy_id, key, proposed["sequence"])
        with self.assertRaises(Conflict):
            self.life.approve(
                "alpha", self.ap, self.old.policy_id, key, 0)

    def test_18_proposal_key_cannot_replay_after_terminal_disable(self):
        proposed = self.proposed()
        active = self.life.approve(
            "alpha", self.ap, self.old.policy_id, "g01-terminal-approve-001",
            proposed["sequence"])
        self.life.disable(
            "alpha", self.dis, self.old.policy_id, "g01-terminal-disable-001",
            active["sequence"])
        with self.assertRaises(Conflict):
            self.life.propose(
                "alpha", self.op, self.old.policy_id,
                "g01-terminal-proposal-original", 0)
        # A genuinely old idempotent proposal key must also fail closed.
        with psycopg.connect(_DSN) as conn:
            old_proposal_key = conn.execute(
                "SELECT idempotency_key FROM si_policy_lifecycle_events "
                "WHERE policy_id=%s::uuid AND event_type='PROPOSED'",
                (self.old.policy_id,)).fetchone()[0]
        with self.assertRaises(Conflict):
            self.life.propose(
                "alpha", self.op, self.old.policy_id, old_proposal_key, 0)

    def test_19_cross_organization_human_cannot_propose_foreign_policy(self):
        with psycopg.connect(_DSN) as conn:
            conn.execute(
                "INSERT INTO si_principals(id,principal_kind) "
                "VALUES('foreign-policy-human','HUMAN')")
            conn.execute(
                "INSERT INTO si_project_grants(project_id,principal_id,permission) "
                "VALUES('beta','foreign-policy-human','policy:propose')")
        foreign_bearer = issue_api_token(_DSN, "foreign-policy-human", 1)[1]
        with self.assertRaises(Missing):
            self.life.propose(
                "beta", foreign_bearer, self.old.policy_id,
                "g01-foreign-project-propose-001")
        with self.assertRaises(AccessDenied):
            self.life.propose(
                "alpha", foreign_bearer, self.old.policy_id,
                "g01-foreign-scope-propose-001")
        with psycopg.connect(_DSN) as conn:
            count = conn.execute(
                "SELECT count(*) FROM si_policy_lifecycle_events").fetchone()[0]
        self.assertEqual(count, 0)

    def test_20_expiry_during_provider_call_aborts_append(self):
        import httpx
        from test_r2_r1b_ledger import provider_record
        self.proposed()
        # Synthetic DB fixture only. An actual HUMAN approval always uses
        # the server-fixed seven-day expiry and cannot choose a short period.
        with psycopg.connect(_DSN) as conn:
            conn.execute(
                "INSERT INTO si_policy_lifecycle_events "
                "(id,project_id,task_id,evidence_id,policy_id,event_type,"
                "actor_id,idempotency_key,valid_until) VALUES("
                "%s::uuid,'alpha',%s::uuid,%s::uuid,%s::uuid,"
                "'ACTIVATED','approver','g01-expire-during-get-001',"
                "clock_timestamp()+interval '2 seconds')",
                (str(uuid4()), self.old.task_id, self.old.evidence_id,
                 self.old.policy_id))
        fetched = []
        def slow_provider(request):
            fetched.append(True)
            time.sleep(2.35)
            return httpx.Response(200, json=provider_record())
        with self.old.mock(handler=slow_provider) as client:
            with self.assertRaises(Conflict):
                self.old.check(client, key="g01-midflight-expiry-check-001")
        self.assertEqual(len(fetched), 1)
        self.assertEqual(self.old.rows(), [])

    def test_21_independent_processes_revoke_during_provider_fetch(self):
        _, approved = self.active()
        context = multiprocessing.get_context("spawn")
        entered_provider = context.Event()
        release_provider = context.Event()
        results = context.Queue()
        verify = context.Process(
            target=_g01_verify_in_separate_process,
            args=(_DSN, self.old.tokens["verifier"], self.old.policy_id,
                  entered_provider, release_provider, results))
        disable = context.Process(
            target=_g01_disable_in_separate_process,
            args=(_DSN, self.dis, self.old.policy_id,
                  approved["sequence"], results))
        try:
            verify.start()
            self.assertTrue(
                entered_provider.wait(timeout=25),
                "verifier never reached the simulated provider")
            disable.start()
            disable.join(timeout=25)
            self.assertEqual(disable.exitcode, 0)
            release_provider.set()
            verify.join(timeout=25)
            self.assertEqual(verify.exitcode, 0)
            observations = [results.get(timeout=8), results.get(timeout=8)]
            self.assertEqual(
                {item[0] for item in observations},
                {"DISABLE_COMMITTED", "VERIFY_REJECTED_AFTER_REVOKE"})
            self.assertEqual(len({item[1] for item in observations}), 2)
            self.assertNotIn(os.getpid(), {item[1] for item in observations})
            self.assertEqual(self.old.rows(), [])
        finally:
            release_provider.set()
            for child in (disable, verify):
                if child.is_alive():
                    child.terminate()
                    child.join(timeout=5)
            results.close()

    def test_22_exact_disable_retry_remains_idempotent(self):
        _, active = self.active()
        key = "g01-disable-exact-retry-001"
        first = self.life.disable(
            "alpha", self.dis, self.old.policy_id, key,
            active["sequence"], "PILOT_REVOKE")
        again = self.life.disable(
            "alpha", self.dis, self.old.policy_id, key,
            active["sequence"], "PILOT_REVOKE")
        self.assertEqual(first["event_id"], again["event_id"])
        self.assertTrue(again["replayed"])
        with psycopg.connect(_DSN) as conn:
            row = conn.execute(
                "SELECT count(*) FROM si_policy_lifecycle_events "
                "WHERE event_type='DISABLED'").fetchone()[0]
        self.assertEqual(row, 1)

if __name__=="__main__":
    unittest.main()
