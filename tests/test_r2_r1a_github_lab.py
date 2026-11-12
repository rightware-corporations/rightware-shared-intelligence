"""R2-R1A actual adapter behavior tests (provider records are synthetic).

EV-01..EV-07 execute the actual check code with mocked GitHub responses,
NOT a cryptographically verified GitHub provider. Source research JSONL remains
unchanged, with executed=false (it is a specification, not a result journal).
"""
from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import unittest

import httpx

from rightware_si.evidence_github import (
    CHECKED_FAIL, CHECKED_PASS, INCONCLUSIVE, GithubRunPolicy,
    check_github_record, check_non_api_source, verify_github_run,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/research/fixtures/SI_RD_03C_EVIDENCE_CASES_v1.jsonl"
BASE_SHA = "0c63b2f2d3d4cf00926752ab2c58d42ccbd64901"
REPO_ID = 1452533938
WORKFLOW_ID = 415280241
RUN_ID = 43202560651


def policy(**changes):
    return replace(GithubRunPolicy(
        owner="rightware-corporations",
        repository="rightware-shared-intelligence",
        repository_id=REPO_ID,
        workflow_id=WORKFLOW_ID,
        run_id=RUN_ID,
        run_attempt=1,
        head_sha=BASE_SHA,
        event="push",
    ), **changes)


def provider_record(**changes):
    record = {
        "id": RUN_ID,
        "repository": {
            "id": REPO_ID,
            "full_name": "rightware-corporations/rightware-shared-intelligence",
        },
        "head_repository": {"id": REPO_ID},
        "workflow_id": WORKFLOW_ID,
        "run_attempt": 1,
        "head_sha": BASE_SHA,
        "status": "completed",
        "conclusion": "success",
        "event": "push",
        "html_url": "https://github.com/synthetic/run/only-display",
    }
    return dict(record, **changes)


class GithubVerifierLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = {x["id"]: x for x in (
            json.loads(line) for line in FIXTURE.read_text().splitlines()
            if line.strip()
        )}

    def check_oracle(self, oracle_id, result):
        original = self.oracle[oracle_id]
        self.assertEqual(result.decision, original["oracle"]["decision"])
        self.assertFalse(result.task_approved)
        self.assertFalse(result.state_authoritative)
        self.assertFalse(original["executed"])

    def test_ev01_exact_record_checked_pass_but_not_done(self):
        self.check_oracle("EV-01", check_github_record(policy(), provider_record()))

    def test_ev02_wrong_commit_checked_fail(self):
        self.check_oracle("EV-02", check_github_record(
            policy(), provider_record(head_sha="f"*40)
        ))

    def test_ev03_wrong_repository_checked_fail(self):
        record = provider_record(repository={"id": REPO_ID+1,"full_name":
            "malicious-org/repository"})
        self.check_oracle("EV-03", check_github_record(policy(), record))

    def test_ev04_wrong_workflow_checked_fail(self):
        self.check_oracle("EV-04", check_github_record(
            policy(), provider_record(workflow_id=WORKFLOW_ID+1)
        ))

    def test_ev05_pending_is_inconclusive(self):
        self.check_oracle("EV-05", check_github_record(
            policy(), provider_record(status="in_progress", conclusion=None)
        ))

    def test_ev06_external_api_down_is_inconclusive(self):
        def down(request):
            raise httpx.ConnectError("synthetic connection unavailable", request=request)
        with httpx.Client(transport=httpx.MockTransport(down)) as client:
            result = verify_github_run(policy(), client=client)
        self.check_oracle("EV-06", result)
        self.assertEqual(result.reason, "PROVIDER_UNAVAILABLE")

    def test_ev07_screenshot_is_inconclusive(self):
        result = check_non_api_source("SCREENSHOT")
        self.check_oracle("EV-07", result)
        self.assertEqual(result.source_type, "UNTRUSTED_MEDIA")

    def test_trusted_path_ignores_fake_user_html_url_and_redirects(self):
        observed = []
        def handler(request):
            observed.append(str(request.url))
            return httpx.Response(200, json=provider_record(
                html_url="http://127.0.0.1:4444/internal",
            ))
        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            result = verify_github_run(policy(), client=client)
        self.assertEqual(result.decision, CHECKED_PASS)
        self.assertEqual(observed, [policy().fixed_api_url])
        self.assertNotIn("127.0.0.1", str(observed))

    def test_cross_repository_wrong_name_and_fork_rejected(self):
        self.assertEqual(
            check_github_record(policy(),provider_record(repository={
                "id":REPO_ID,"full_name":"other/repo",
            })).reason,"WRONG_REPOSITORY_NAME"
        )
        self.assertEqual(
            check_github_record(policy(),provider_record(
                head_repository={"id":REPO_ID+1}
            )).reason,"UNTRUSTED_HEAD_REPOSITORY"
        )

    def test_run_attempt_and_event_strict(self):
        self.assertEqual(
            check_github_record(policy(), provider_record(run_attempt=2)).reason,
            "WRONG_RUN_ATTEMPT",
        )
        self.assertEqual(
            check_github_record(policy(), provider_record(event="pull_request")).reason,
            "WRONG_EVENT",
        )

    def test_workflow_failed_not_promoted(self):
        result=check_github_record(policy(),provider_record(conclusion="failure"))
        self.assertEqual(result.decision,CHECKED_FAIL)
        self.assertEqual(result.reason,"WORKFLOW_NOT_SUCCESSFUL")

    def test_redirect_malformed_json_and_unauthorized_fail_closed(self):
        for status,response in (
            (302,httpx.Response(302,headers={"location":"http://localhost/secret"})),
            (403,httpx.Response(403,json={"message":"rate limited"})),
            (200,httpx.Response(200,content=b"{bad",headers={"content-type":"application/json"})),
            (200,httpx.Response(200,text="fake green screenshot")),
        ):
            with self.subTest(status=status,body=response.content[:12]):
                with httpx.Client(transport=httpx.MockTransport(
                    lambda request: response
                )) as client:
                    res=verify_github_run(policy(),client=client)
                self.assertEqual(res.decision,INCONCLUSIVE)
                self.assertFalse(res.task_approved)

    def test_malformed_provider_record_is_inconclusive(self):
        for fake in (
            None,{}, {"id":1},
            provider_record(head_sha="not-a-full-sha"),
            provider_record(repository={"id": True,"full_name":"rightware-corporations/rightware-shared-intelligence"}),
            provider_record(id=True),
        ):
            with self.subTest(fake=repr(fake)[:45]):
                self.assertEqual(check_github_record(policy(),fake).decision,
                                 INCONCLUSIVE)

    def test_invalid_input_cannot_construct_arbitrary_api_target(self):
        for bad in (
            {"owner":"https://127.0.0.1"},
            {"repository":"../../secret"},
            {"repository_id":0},
            {"workflow_id":False},
            {"head_sha":"deadbeef"},
            {"run_id":-1},
            {"run_attempt":0},
            {"event":"repository_dispatch"},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    policy(**bad)

    def test_provider_response_body_size_is_limited(self):
        with httpx.Client(transport=httpx.MockTransport(
            lambda req: httpx.Response(
                200,content=b"x"*40000,headers={"content-type":"application/json"}
            )
        )) as client:
            result=verify_github_run(policy(),client=client)
        self.assertEqual(result.decision,INCONCLUSIVE)
        self.assertEqual(result.reason,"PROVIDER_RESPONSE_TOO_LARGE")


if __name__=="__main__":
    unittest.main()
