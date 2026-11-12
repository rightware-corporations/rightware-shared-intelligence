"""R2 R1C lab contract gates. Static lint ONLY, not REST/DB E2E."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/work03b/R2_R1C_REST_VERIFY_CONTRACT_R0.json"
GATEWAY = ROOT / "backend/rightware_si/http_api.py"
LEDGER = ROOT / "backend/rightware_si/verification_ledger.py"
PROVIDER = ROOT / "backend/rightware_si/evidence_github.py"

class R2R1CContractGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.gateway_src = GATEWAY.read_text(encoding="utf-8")
        cls.ledger_src = LEDGER.read_text(encoding="utf-8")
        cls.provider_src = PROVIDER.read_text(encoding="utf-8")
        cls.gateway_ast = ast.parse(cls.gateway_src)
        cls.ledger_ast = ast.parse(cls.ledger_src)

    def test_01_still_draft_no_runtime(self):
        self.assertEqual(self.spec["status"], "SEC_PRINCIPLES_RATIFIED_LAB_IMPLEMENTATION_CI_PENDING")
        self.assertTrue(self.spec["runtime"]["lab_route_implemented"])
        self.assertFalse(self.spec["authorization"]["operator_ratified"])
        self.assertFalse(self.spec["runtime"]["route_enabled"])
        self.assertFalse(self.spec["runtime"]["auto_done"])

    def test_02_canonical_endpoint(self):
        api = self.spec["api"]
        self.assertEqual(api["method"], "POST")
        self.assertEqual(api["path"], "/v1/projects/{project_id}/evidence/{evidence_id}/verify")
        self.assertEqual(api["response_http_status"], 200)

    def test_03_independent_service_only(self):
        a = self.spec["authorization"]
        self.assertEqual(a["principal_source"], "server_resolved_bearer")
        self.assertEqual(a["allowed_principal_kinds"], ["SERVICE"])
        self.assertEqual(set(a["required_grants"]), {"evidence:verify", "task:read"})
        self.assertTrue(a["reject_task_creator"] and a["reject_evidence_submitter"] and a["reject_policy_author"])

    def test_04_no_caller_auth_overrides(self):
        req = self.spec["api"]["request"]
        self.assertEqual(set(req["path_fields"]), {"project_id", "evidence_id"})
        self.assertEqual(set(req["body_fields"]), {"policy_id", "expected_task_version"})
        self.assertEqual(req["required_header"], "Idempotency-Key")
        self.assertTrue({"actor_id", "github_token", "client", "source_url", "observation_channel"}.issubset(set(req["forbidden_body_fields"])))
        self.assertFalse(set(req["forbidden_body_fields"]) & set(req["body_fields"]))

    def test_05_evidence_id_binding_gap_recorded(self):
        b = self.spec["binding"]
        self.assertTrue(b["require_path_evidence_policy_match_before_network"])
        self.assertTrue(b["require_recheck_after_network"])
        self.assertEqual(b["required_future_ledger_argument"], "expected_evidence_id")
        cls = next(n for n in self.ledger_ast.body if isinstance(n, ast.ClassDef) and n.name == "EvidenceLedger")
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "verify_and_record")
        args = {a.arg for a in method.args.args}
        self.assertIn("policy_id", args)
        self.assertIn("expected_evidence_id", {a.arg for a in method.args.kwonlyargs})

    def test_06_no_verify_or_review_public_route(self):
        routes = set()
        for fn in ast.walk(self.gateway_ast):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for d in fn.decorator_list:
                if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.args:
                    if d.func.attr in {"post", "get", "put", "patch", "delete"} and isinstance(d.args[0], ast.Constant):
                        routes.add(str(d.args[0].value))
        self.assertIn(self.spec["api"]["path"], routes)
        self.assertNotIn("/v1/projects/{project_id}/tasks/{task_id}/review", routes)

    def test_07_checked_never_done(self):
        s = self.spec["safety"]
        self.assertEqual(set(s["verification_results"]), {"CHECKED_PASS", "CHECKED_FAIL", "INCONCLUSIVE"})
        self.assertEqual(s["task_status_after_any_result"], "IN_REVIEW")
        self.assertEqual(s["evidence_status_after_any_result"], "REFERENCED")
        self.assertFalse(s["may_write_review_decision"] or s["may_update_agent_assertion"])

    def test_08_fixed_provider_channel(self):
        p = self.spec["provider"]
        self.assertEqual(p["kind"], "GITHUB_WORKFLOW_RUN")
        self.assertEqual(p["network_target_source"], "trusted_pinned_policy_only")
        self.assertEqual(p["live_channel"], "LIVE_HTTPS")
        self.assertIn("follow_redirects=False", self.provider_src)
        self.assertIn("trust_env=False", self.provider_src)
        self.assertIn("SIMULATED_TRANSPORT", self.ledger_src)

    def test_09_http_error_map(self):
        self.assertEqual(self.spec["api"]["error_http_status"], {
            "unauthenticated": 401, "unauthorized": 403, "not_found": 404,
            "state_conflict": 409, "invalid_request": 422, "service_unavailable": 503})
        self.assertEqual(self.spec["provider"]["provider_failure_result"], "INCONCLUSIVE")

    def test_10_negative_cases_are_only_specs(self):
        ids = {c["id"] for c in self.spec["acceptance_cases"]}
        self.assertTrue({f"API-NEG-{i:02d}" for i in range(1, 17)}.issubset(ids))
        self.assertTrue(all(c["execution"] == "NOT_EXECUTED" for c in self.spec["acceptance_cases"]))

    def test_11_operator_gates_pending(self):
        g = self.spec["required_operator_gates"]
        self.assertEqual({x["id"] for x in g},
            {"SEC-R1C-01","SEC-R1C-02","SEC-R1C-03","SEC-R1C-04","R2-PROVIDER","R2-IDENTITY","R2-PRIVACY"})
        for item in g:
            expected = ("PRINCIPLE_RATIFIED_IMPLEMENTATION_PENDING"
                        if item["id"].startswith("SEC-R1C-") else "NOT_RATIFIED")
            self.assertEqual(item["status"], expected)

if __name__ == "__main__":
    unittest.main()
