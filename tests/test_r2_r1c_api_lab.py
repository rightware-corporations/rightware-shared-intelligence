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

if __name__ == "__main__":
    unittest.main()
