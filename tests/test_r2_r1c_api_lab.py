"""R2 R1C LAB-only REST integration tests, synthetic disposable /rw_test.

MockTransport is injected only by the test harness into the internal ledger.
It MUST be labelled SIMULATED_TRANSPORT and never credited as LIVE_HTTPS.
"""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch
from uuid import uuid4

import httpx
import psycopg
from fastapi.testclient import TestClient

# Import the fixture module, not its unittest.TestCase class, so discovery
# runs the R1B 16 tests only in their original module.
import test_r2_r1b_ledger as r1b_fixture
from test_r2_r1b_ledger import _DSN, _SAFE, provider_record
from rightware_si.verification_ledger import EvidenceLedger


@unittest.skipUnless(_SAFE, "requires disposable loopback PostgreSQL /rw_test")
class R2R1CVerifiedHTTP(unittest.TestCase):
    def setUp(self):
        os.environ["RW_SI_DATABASE_URL"] = _DSN
        self.fixture = r1b_fixture.VerificationLedgerLabTests(
            "test_01_success_is_append_only_and_never_done"
        )
        self.fixture.setUp()
        from rightware_si.http_api import create_app
        with patch.dict(os.environ, {
            "RW_SI_ENVIRONMENT": "lab",
            "RW_SI_ENABLE_R2_R1C_LAB_API": "1",
        }):
            self.http = TestClient(create_app(_DSN))
        self.path = (
            f"/v1/projects/alpha/evidence/{self.fixture.evidence_id}/verify"
        )
        self.body = {
            "policy_id": self.fixture.policy_id,
            "expected_task_version": 4,
        }

    def request(self, *, actor="verifier", path=None, body=None, idem=None):
        headers = {"Idempotency-Key": idem or f"r2-rest-{uuid4().hex}"}
        if actor is not None:
            headers["Authorization"] = f"Bearer {self.fixture.tokens[actor]}"
        return self.http.post(
            path or self.path, json=self.body if body is None else body,
            headers=headers,
        )

    def fake_provider(self, response=None, status=200, on_fetch=None):
        real = EvidenceLedger.verify_and_record
        def shim(instance, project, actor, policy_id, version, idem, *,
                 expected_evidence_id=None, **kwargs):
            def handler(req):
                if on_fetch is not None:
                    on_fetch(req)
                return httpx.Response(status, json=response or provider_record())
            with httpx.Client(transport=httpx.MockTransport(handler)) as fake:
                return real(instance, project, actor, policy_id, version, idem,
                            expected_evidence_id=expected_evidence_id, client=fake)
        return patch.object(EvidenceLedger, "verify_and_record", autospec=True,
                            side_effect=shim)

    def test_01_flag_disabled_by_default(self):
        from rightware_si.http_api import create_app
        with patch.dict(os.environ, {"RW_SI_ENABLE_R2_R1C_LAB_API": "0"}):
            disabled = TestClient(create_app(_DSN))
        self.assertEqual(disabled.post(self.path, json=self.body).status_code, 404)

    def test_02_flag_rejects_non_lab_dsn(self):
        from rightware_si.http_api import create_app
        with patch.dict(os.environ, {
            "RW_SI_ENVIRONMENT": "lab",
            "RW_SI_ENABLE_R2_R1C_LAB_API": "1",
        }):
            with self.assertRaises(RuntimeError):
                create_app("postgresql://rw:xxx@example.com:5432/prod")

    def test_03_missing_bearer_401(self):
        self.assertEqual(self.request(actor=None).status_code, 401)
        self.assertEqual(self.fixture.rows(), [])

    def test_04_agent_even_with_verify_grant_403(self):
        with psycopg.connect(_DSN) as conn:
            conn.execute("INSERT INTO si_project_grants(project_id,principal_id,permission) "
                         "VALUES('alpha','worker','evidence:verify')")
        self.assertEqual(self.request(actor="worker").status_code, 403)
        self.assertEqual(self.fixture.rows(), [])

    def test_05_service_missing_grant_403(self):
        self.assertEqual(self.request(actor="no-grant").status_code, 403)
        self.assertEqual(self.fixture.rows(), [])

    def test_06_path_policy_mismatch_rejected_before_network(self):
        seen = []
        with self.fake_provider(on_fetch=lambda r: seen.append(r)):
            path = f"/v1/projects/alpha/evidence/{uuid4()}/verify"
            out = self.request(path=path)
        self.assertEqual(out.status_code, 409)
        self.assertEqual(seen, [])
        self.assertEqual(self.fixture.rows(), [])

    def test_07_missing_policy_404(self):
        out = self.request(body={"policy_id": str(uuid4()),
                                 "expected_task_version": 4})
        self.assertEqual(out.status_code, 404)
        self.assertEqual(self.fixture.rows(), [])

    def test_08_stale_task_version_409(self):
        out = self.request(body={"policy_id": self.fixture.policy_id,
                                 "expected_task_version": 3})
        self.assertEqual(out.status_code, 409)
        self.assertEqual(self.fixture.rows(), [])

    def test_09_synthetic_success_is_append_only_no_done(self):
        with self.fake_provider():
            out = self.request(idem="rest-lab-fixed-001")
        self.assertEqual(out.status_code, 200, out.text)
        data = out.json()
        self.assertEqual(data["result"], "CHECKED_PASS")
        self.assertEqual(data["observation_channel"], "SIMULATED_TRANSPORT")
        self.assertFalse(data["task_approved"])
        self.assertEqual(data["evidence_id"], self.fixture.evidence_id)
        self.assertEqual(len(self.fixture.rows()), 1)
        task = self.fixture.core.get_task("alpha", "worker", self.fixture.task_id)
        self.assertEqual(task["status"], "IN_REVIEW")

    def test_10_replay_does_not_refetch(self):
        seen = []
        with self.fake_provider(on_fetch=lambda r: seen.append(1)):
            first = self.request(idem="rest-lab-fixed-002")
            again = self.request(idem="rest-lab-fixed-002")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json(), again.json())
        self.assertEqual(seen, [1])
        self.assertEqual(len(self.fixture.rows()), 1)

    def test_11_provider_failure_is_inconclusive(self):
        with self.fake_provider(status=403):
            out = self.request()
        self.assertEqual(out.status_code, 200, out.text)
        self.assertEqual(out.json()["result"], "INCONCLUSIVE")
        self.assertEqual(out.json()["observation_channel"], "SIMULATED_TRANSPORT")

    def test_12_wrong_sha_returns_checked_fail(self):
        with self.fake_provider(response=provider_record(head_sha="f" * 40)):
            out = self.request()
        self.assertEqual(out.status_code, 200, out.text)
        self.assertEqual(out.json()["result"], "CHECKED_FAIL")
        self.assertFalse(out.json()["task_approved"])

    def test_13_reusing_idem_with_different_policy_409(self):
        with self.fake_provider():
            self.assertEqual(self.request(idem="rest-lab-fixed-003").status_code, 200)
            new_policy = self.fixture.seed_policy(version=2)
            out = self.request(
                idem="rest-lab-fixed-003",
                body={"policy_id": new_policy, "expected_task_version": 4},
            )
        self.assertEqual(out.status_code, 409)
        self.assertEqual(len(self.fixture.rows()), 1)

    def test_14_caller_identity_override_rejected_422(self):
        out = self.request(body={**self.body, "actor_id": "verifier"})
        self.assertEqual(out.status_code, 422)
        self.assertEqual(self.fixture.rows(), [])

    def test_15_cross_project_policy_not_found(self):
        path = f"/v1/projects/beta/evidence/{self.fixture.evidence_id}/verify"
        self.assertEqual(self.request(actor="other", path=path).status_code, 404)
        self.assertEqual(self.fixture.rows(), [])

    def test_16_revocation_midflight_denies_commit(self):
        def revoke(_):
            with psycopg.connect(_DSN) as conn:
                conn.execute("DELETE FROM si_project_grants "
                             "WHERE project_id='alpha' AND principal_id='verifier' "
                             "AND permission='evidence:verify'")
        with self.fake_provider(on_fetch=revoke):
            out = self.request()
        self.assertEqual(out.status_code, 403)
        self.assertEqual(self.fixture.rows(), [])


    def test_17_human_with_both_grants_denied(self):
        from rightware_si.token_admin import issue_api_token
        self.fixture.tokens["operator"] = issue_api_token(_DSN, "operator", 4)[1]
        with psycopg.connect(_DSN) as conn:
            for perm in ("task:read", "evidence:verify"):
                conn.execute("INSERT INTO si_project_grants "
                             "(project_id,principal_id,permission) "
                             "VALUES('alpha','operator',%s)", (perm,))
        seen = []
        with self.fake_provider(on_fetch=lambda r: seen.append(1)):
            out = self.request(actor="operator")
        self.assertEqual(out.status_code, 403)
        self.assertEqual(seen, [])
        self.assertEqual(self.fixture.rows(), [])

    def test_18_missing_task_read_grant_denied(self):
        with psycopg.connect(_DSN) as conn:
            conn.execute("DELETE FROM si_project_grants WHERE project_id='alpha' "
                         "AND principal_id='verifier' AND permission='task:read'")
        seen = []
        with self.fake_provider(on_fetch=lambda r: seen.append(1)):
            out = self.request()
        self.assertEqual(out.status_code, 403)
        self.assertEqual(seen, [])
        self.assertEqual(self.fixture.rows(), [])

    def test_19_other_task_evidence_cannot_borrow_first_policy(self):
        other = self.fixture.core.create_task(
            "alpha", "worker", "Unrelated task", ["Unrelated acceptance criterion"],
            f"cross-create-{uuid4().hex[:12]}")
        tid = other["task_id"]
        self.fixture.core.publish_task(
            "alpha", "worker", tid, 1, f"cross-pub-{uuid4().hex[:12]}")
        lease = self.fixture.core.claim_task(
            "alpha", "worker", tid, 2, f"cross-claim-{uuid4().hex[:12]}")["lease_token"]
        evidence = self.fixture.core.submit_result(
            "alpha", "worker", tid, 3, lease,
            r1b_fixture._URL, f"cross-submit-{uuid4().hex[:12]}")
        seen = []
        with self.fake_provider(on_fetch=lambda r: seen.append(1)):
            out = self.request(
                path=f"/v1/projects/alpha/evidence/{evidence['evidence_id']}/verify")
        self.assertEqual(out.status_code, 409)
        self.assertEqual(seen, [])
        self.assertEqual(self.fixture.rows(), [])

    def test_20_task_outside_in_review_cannot_be_verified(self):
        with psycopg.connect(_DSN) as conn:
            conn.execute("UPDATE si_tasks SET status='BLOCKED' "
                         "WHERE id=%s::uuid", (self.fixture.task_id,))
        seen = []
        with self.fake_provider(on_fetch=lambda r: seen.append(1)):
            out = self.request()
        self.assertEqual(out.status_code, 409)
        self.assertEqual(seen, [])
        self.assertEqual(self.fixture.rows(), [])

    def test_21_wrong_repository_id_is_checked_fail(self):
        record = provider_record(repository={
            "id": 987654321,
            "full_name": "rightware-corporations/rightware-shared-intelligence"})
        with self.fake_provider(response=record):
            out = self.request()
        self.assertEqual(out.status_code, 200, out.text)
        self.assertEqual(out.json()["result"], "CHECKED_FAIL")
        self.assertEqual(out.json()["reason_code"], "WRONG_REPOSITORY")
        self.assertFalse(out.json()["task_approved"])

    def test_22_wrong_workflow_id_is_checked_fail(self):
        with self.fake_provider(response=provider_record(workflow_id=999999)):
            out = self.request()
        self.assertEqual(out.status_code, 200, out.text)
        self.assertEqual(out.json()["reason_code"], "WRONG_WORKFLOW")
        self.assertEqual(out.json()["result"], "CHECKED_FAIL")

    def test_23_wrong_run_attempt_is_checked_fail(self):
        with self.fake_provider(response=provider_record(run_attempt=2)):
            out = self.request()
        self.assertEqual(out.status_code, 200, out.text)
        self.assertEqual(out.json()["reason_code"], "WRONG_RUN_ATTEMPT")
        self.assertEqual(out.json()["result"], "CHECKED_FAIL")

    def test_24_pending_workflow_is_inconclusive(self):
        with self.fake_provider(response=provider_record(status="queued", conclusion=None)):
            out = self.request()
        self.assertEqual(out.status_code, 200, out.text)
        self.assertEqual(out.json()["result"], "INCONCLUSIVE")
        self.assertEqual(out.json()["reason_code"], "WORKFLOW_NOT_COMPLETED")

    def test_25_provider_redirect_is_inconclusive(self):
        with self.fake_provider(status=302):
            out = self.request()
        self.assertEqual(out.status_code, 200, out.text)
        self.assertEqual(out.json()["result"], "INCONCLUSIVE")
        self.assertEqual(out.json()["reason_code"], "PROVIDER_REDIRECT_DENIED")

    def test_26_provider_network_timeout_is_inconclusive(self):
        def timeout(_):
            raise httpx.ReadTimeout("synthetic network timeout")
        with self.fake_provider(on_fetch=timeout):
            out = self.request()
        self.assertEqual(out.status_code, 200, out.text)
        self.assertEqual(out.json()["result"], "INCONCLUSIVE")
        self.assertEqual(out.json()["reason_code"], "PROVIDER_UNAVAILABLE")

    def test_27_idempotency_replay_with_stale_version_rejected(self):
        with self.fake_provider():
            first = self.request(idem="r1d-version-replay-001")
            self.assertEqual(first.status_code, 200, first.text)
            stale = self.request(
                idem="r1d-version-replay-001",
                body={"policy_id": self.fixture.policy_id, "expected_task_version": 3})
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(len(self.fixture.rows()), 1)

    def test_28_all_forbidden_request_controls_rejected(self):
        forbidden = ("principal_id", "github_token", "client", "source_url",
                     "observation_channel", "expected_head_sha", "repository_id",
                     "workflow_id", "task_status", "review_decision")
        for field in forbidden:
            with self.subTest(field=field):
                out = self.request(body={**self.body, field: "unauthorized"})
                self.assertEqual(out.status_code, 422)
        self.assertEqual(self.fixture.rows(), [])

    def test_29_ledger_db_outage_returns_sanitized_503(self):
        secret = "driver-password-should-never-appear"
        with patch.object(EvidenceLedger, "verify_and_record",
                          side_effect=psycopg.OperationalError(secret)):
            out = self.request()
        self.assertEqual(out.status_code, 503)
        self.assertNotIn(secret, out.text)
        self.assertNotIn(self.fixture.tokens["verifier"], out.text)
        self.assertEqual(self.fixture.rows(), [])

    def test_30_auth_db_outage_returns_sanitized_503(self):
        secret = "auth-db-secret-must-be-redacted"
        with patch("rightware_si.api_auth.resolve_principal",
                   side_effect=psycopg.OperationalError(secret)):
            out = self.request()
        self.assertEqual(out.status_code, 503)
        self.assertNotIn(secret, out.text)
        self.assertNotIn(self.fixture.tokens["verifier"], out.text)
        self.assertEqual(self.fixture.rows(), [])

    def test_31_invalid_idempotency_header_rejected_without_provider(self):
        seen = []
        with self.fake_provider(on_fetch=lambda r: seen.append(1)):
            out = self.request(idem="$$$$")
        self.assertEqual(out.status_code, 422)
        self.assertEqual(seen, [])
        self.assertEqual(self.fixture.rows(), [])

    def test_32_service_cannot_verify_policy_it_created(self):
        own = self.fixture.seed_policy(version=2, created_by="verifier")
        seen = []
        with self.fake_provider(on_fetch=lambda r: seen.append(1)):
            out = self.request(body={
                "policy_id": own, "expected_task_version": 4})
        self.assertEqual(out.status_code, 403)
        self.assertEqual(seen, [])
        self.assertEqual(self.fixture.rows(), [])

if __name__ == "__main__":
    unittest.main()
