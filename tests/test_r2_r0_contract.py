"""R2-R0 contract integrity gates, NOT executable EV-01..EV-16 verdicts.

A test passing here establishes only that the proposal and source fixture are
consistent and still unexecuted. It never calls GitHub verifier, Sigstore,
reviewer, LLM, Mem0 or an external effect.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "docs" / "work03b" / "R2_TRUST_CONTRACT_R0.json"
FIXTURE = ROOT / "docs" / "research" / "fixtures" / "SI_RD_03C_EVIDENCE_CASES_v1.jsonl"
POLICY = ROOT / "docs" / "work03b" / "R1C_SECURITY_POLICY_GATE_R0.md"
DESIGN = ROOT / "docs" / "work03b" / "R2_TRUST_CONTRACT_R0.md"
API = ROOT / "backend" / "rightware_si" / "http_api.py"


class R2DraftIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.draft = json.loads(DRAFT.read_text(encoding="utf-8"))
        cls.fixture = [
            json.loads(line) for line in FIXTURE.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_01_reference_design_not_a_claim_of_implementation(self):
        self.assertEqual(self.draft["status"], "DRAFT_OPERATOR_RATIFICATION_REQUIRED_NOT_IMPLEMENTED")
        self.assertEqual(self.draft["implemented_r2_routes"], 0)
        self.assertEqual(self.draft["phase"], "R2_R0_CONTRACT_ONLY")
        self.assertEqual(len(self.draft["proposed_routes"]), 2)
        self.assertTrue(all(x["state"] == "PROPOSED_UNIMPLEMENTED"
                            for x in self.draft["proposed_routes"]))

    def test_02_all_sixteen_oracle_contracts_match_original_and_are_unexecuted(self):
        self.assertEqual(len(self.fixture), 16)
        self.assertEqual(len(self.draft["oracle_references"]), 16)
        self.assertEqual(
            [x["id"] for x in self.fixture],
            [f"EV-{i:02}" for i in range(1, 17)]
        )
        by_id = {x["id"]: x for x in self.draft["oracle_references"]}
        self.assertEqual(len(by_id), 16)
        for fixture in self.fixture:
            with self.subTest(oracle_id=fixture["id"]):
                rec = by_id[fixture["id"]]
                self.assertTrue(fixture["synthetic"])
                self.assertFalse(fixture["executed"])
                self.assertTrue(rec["synthetic"])
                self.assertFalse(rec["executed"])
                self.assertEqual(rec["scenario"], fixture["scenario"])
                self.assertEqual(rec["expected_decision"], fixture["oracle"]["decision"])
                self.assertEqual(rec["expected_task_outcome"], fixture["oracle"]["task_outcome"])
                self.assertIsNone(rec["observed_decision"])
                self.assertIsNone(rec["observed_task_outcome"])
                self.assertEqual(rec["claim_status"], "SPECIFICATION_NOT_TEST_RESULT")
                self.assertTrue(rec["requires_real_verifier_or_policy_test"])

    def test_03_verification_never_auto_approves_and_assertion_stays_asserted(self):
        states = self.draft["state_separation"]
        self.assertEqual(states["assertion"]["current_value"], "ASSERTED")
        self.assertEqual(states["evidence_reference"]["current_value"], "REFERENCED")
        self.assertEqual(
            states["verification_result"]["future_values"],
            ["CHECKED_PASS", "CHECKED_FAIL", "INCONCLUSIVE"]
        )
        self.assertEqual(
            states["review_decision"]["future_values"],
            ["REVIEW_ACCEPTED", "REVIEW_REJECTED"]
        )
        inv = set(self.draft["invariants"])
        self.assertIn("NEVER_AUTO_DONE_FROM_GREEN_CI", inv)
        self.assertIn("APPROVED_ONLY_BY_AUTHORIZED_INDEPENDENT_REVIEW", inv)
        self.assertIn("REVOCATION_RECHECK_BEFORE_WRITE_AND_READ", inv)
        self.assertIn("NO_UNKNOWN_EXTERNAL_EFFECT_REEXECUTION", inv)

    def test_04_r0_historical_proposals_distinct_from_new_lab_route(self):
        module=ast.parse(API.read_text(encoding="utf-8"))
        actual=set()
        for node in ast.walk(module):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                        if (isinstance(dec.func.value, ast.Name)
                                and dec.func.value.id == "app"
                                and dec.args and isinstance(dec.args[0], ast.Constant)):
                            actual.add((dec.func.attr.upper(), dec.args[0].value))
        canonical=json.loads((ROOT/"docs"/"work03b"/"UC_CORE_01_CONTRACT.json").read_text(encoding="utf-8"))
        self.assertFalse(canonical["r2_r1c_lab"]["default_enabled"])
        self.assertFalse(canonical["r2_r1c_lab"]["release_approval"])
        for route in self.draft["proposed_routes"]:
            pair=(route["method"], route["path"])
            if route["path"].endswith("/verify"):
                # This R0 draft is historical; R1C added a gated LAB-only decorator later.
                self.assertIn(pair, actual)
                lab=next(x for x in canonical["future_routes"] if x["path"]==route["path"])
                self.assertEqual(lab["implementation"],
                                 "IMPLEMENTED_R2_R1C_LAB_FLAGGED_OFF_BY_DEFAULT")
            else:
                self.assertNotIn(pair, actual)

    def test_05_security_recommendations_not_mislabelled_official_decisions(self):
        policy = POLICY.read_text(encoding="utf-8")
        design = DESIGN.read_text(encoding="utf-8")
        for identifier in ("SEC-R1C-01", "SEC-R1C-02", "SEC-R1C-03", "SEC-R1C-04"):
            self.assertIn(identifier, policy)
        self.assertIn("OPERATOR RATIFICATION PENDING", policy)
        self.assertIn("DRAFT FOR OPERATOR RATIFICATION", design)
        self.assertIn("EV-01..EV-16 executed: 0", design)
        self.assertIn("R1C security decision register", design)

    def test_06_gate_order_and_original_acceptance_remains_pending(self):
        gate_ids=[g["id"] for g in self.draft["implementation_gates"]]
        self.assertEqual(gate_ids, ["R2-00","R2-01","R2-02","R2-03","R2-04","R2-05"])
        self.assertEqual(self.draft["implementation_gates"][0]["state"], "PENDING_OPERATOR")
        canonical=json.loads((ROOT/"docs"/"work03b"/"UC_CORE_01_CONTRACT.json").read_text(encoding="utf-8"))
        self.assertEqual(len(canonical["existing_routes"]),18)
        self.assertEqual(len(canonical["future_routes"]),3)
        self.assertTrue(all(x["final_acceptance"]=="PENDING_FULL_E2E"
                            for x in canonical["work01_acceptance"]))
        self.assertTrue(all(x["path"] in {y["path"] for y in canonical["future_routes"]}
                            for x in self.draft["proposed_routes"]))


if __name__ == "__main__":
    unittest.main()
