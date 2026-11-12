"""WORK-03B R0: static contract consistency gates, NOT runtime functional acceptance."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs" / "work03b" / "UC_CORE_01_CONTRACT.json"
HTTP_PATH = ROOT / "backend" / "rightware_si" / "http_api.py"


def declared_routes_from_source() -> set[tuple[str, str]]:
    module = ast.parse(HTTP_PATH.read_text(encoding="utf-8"))
    routes: set[tuple[str, str]] = set()
    for node in ast.walk(module):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Attribute):
                continue
            if not isinstance(dec.func.value, ast.Name) or dec.func.value.id != "app":
                continue
            if dec.func.attr not in {"get", "post", "put", "delete", "patch"}:
                continue
            if dec.args and isinstance(dec.args[0], ast.Constant) and isinstance(dec.args[0].value, str):
                routes.add((dec.func.attr.upper(), dec.args[0].value))
    return routes


class ContractR0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_original_eighteen_ids_present_once_with_no_false_pass(self) -> None:
        records = self.contract["work01_acceptance"]
        ids = [x["id"] for x in records]
        self.assertEqual(ids, [f"M{i:02d}" for i in range(1, 19)])
        self.assertTrue(all(x["final_acceptance"] == "PENDING_FULL_E2E" for x in records))
        self.assertIn("SPEC_CONFLICT", {x["preexisting_coverage"] for x in records})

    def test_live_route_inventory_tracks_actual_decorators(self) -> None:
        actual = declared_routes_from_source()
        declared = self.contract["existing_routes"]
        pairs = [(x["method"], x["path"]) for x in declared]
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertEqual(len(pairs), 14)
        self.assertTrue(all(x["implementation"] in {"IMPLEMENTED_LAB", "IMPLEMENTED_R1A_LAB"} for x in declared))
        self.assertTrue(set(pairs).issubset(actual))

    def test_future_routes_not_misrepresented_as_live(self) -> None:
        actual = declared_routes_from_source()
        future = self.contract["future_routes"]
        self.assertEqual(len(future), 6)
        self.assertTrue(all(x["implementation"] == "PROPOSED_UNIMPLEMENTED" for x in future))
        self.assertFalse(any((x["method"], x["path"]) in actual for x in future))
        self.assertEqual(
            len({(x["method"], x["path"]) for x in future}), len(future)
        )

    def test_two_agent_journey_authority_and_monotonic_versions(self) -> None:
        steps = self.contract["journey"]
        self.assertEqual(len(steps), 14)
        self.assertEqual([x["id"] for x in steps], [f"S{i:02d}" for i in range(1, 15)])
        numbered = [(x["id"], x["expected_version"]) for x in steps if x["expected_version"] is not None]
        self.assertEqual([v for _, v in numbered], sorted([v for _, v in numbered]))
        self.assertEqual(next(x for x in steps if x["operation"] == "submit_result")["expected_state"], "IN_REVIEW")
        self.assertEqual(next(x for x in steps if x["operation"] == "accept_result")["actor"], "REVIEWER")
        self.assertEqual(next(x for x in steps if x["operation"] == "restart_process_and_resume")["actor"], "AGENT_B")
        self.assertEqual(self.contract["status"], "DRAFT_FOR_OPERATOR_RATIFICATION_PARTIAL_R1A_LAB")

    def test_r1a_routes_present_and_no_full_product_pass(self):
        r1a = [r for r in self.contract["existing_routes"]
               if r["implementation"] == "IMPLEMENTED_R1A_LAB"]
        self.assertEqual(len(r1a), 4)
        self.assertEqual(
            {r["permission"] for r in r1a},
            {"task:execute", "source:write", "observation:write",
             "task:read+context:read"},
        )
        self.assertEqual(
            next(x for x in self.contract["work01_acceptance"]
                 if x["id"] == "M02")["preexisting_coverage"],
            "R1A_LAB_PARTIAL",
        )
        self.assertTrue(all(
            x["final_acceptance"] == "PENDING_FULL_E2E"
            for x in self.contract["work01_acceptance"]
        ))

    def test_critical_policy_guards_present(self) -> None:
        inv = set(self.contract["invariants"])
        self.assertTrue({
            "NO_AUTHORITY_FROM_MEMORY", "NO_AGENT_SELF_APPROVAL",
            "SERVER_DERIVED_IDENTITY_SCOPE", "REAUTH_CONTEXT_ON_EVERY_READ",
            "NO_SECRET_REPLAY_FOR_LEASE_ISSUING_COMMANDS",
            "EXTERNAL_EFFECTS_REQUIRE_RECONCILIATION",
            "NO_CROSS_PROJECT_DATA",
        }.issubset(inv))
        self.assertEqual(self.contract["idempotency"]["secret_lease_issuance"], "CONFLICT_409_NO_RAW_TOKEN_REPLAY")
        self.assertEqual(self.contract["gates"]["critical_false_approvals"], 0)
        self.assertEqual(self.contract["gates"]["critical_unauthorized_disclosures"], 0)
        self.assertEqual(self.contract["gates"]["critical_duplicate_external_effects"], 0)


if __name__ == "__main__":
    unittest.main()
