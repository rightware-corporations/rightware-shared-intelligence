"""E1.1C review process safety; all submissions below are SYNTHETIC MOCKS.

These self-attested mock records are NOT human reviews and MUST NOT be
counted toward E1_DATA_READY. Only validation logic is under test.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from rightware_si.e1_01_data_eval import DataIntegrityError
from rightware_si.e1_03_review_protocol import (
    _cohen, _quadratic_weighted, assert_private_path,
    blank_submission, compare_submissions, make_packet,
    private_write_json, validate_submission,
)

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "docs" / "research" / "e1_02"


class E103ReviewProcessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = make_packet(DATASET)
        cls.blank = blank_submission(cls.packet)

    def mock(self, pseudonym="RV-MOCK-REVIEWER-A"):
        """Syntactically valid mock only, *not* semantically reviewed."""
        record = deepcopy(self.blank)
        record["reviewer_pseudonym"] = pseudonym
        record["independence_attested"] = True  # fictitious test fixture
        record["provisional_gold_not_consulted"] = True  # fictitious test
        record["submitted_at"] = "2026-11-24T08:00:00+02:00"
        record["review_status"] = "SUBMITTED_INDEPENDENT"
        for item in record["judgments"]:
            item["query_class"] = "UNANSWERABLE"
            for rating in item["ratings"]:
                rating["grade"] = 0
                rating["justification"] = "Test mock: unsupported in this fixture"
        return record

    def rejects(self, mutation):
        record = self.mock()
        mutation(record)
        with self.assertRaises(DataIntegrityError):
            validate_submission(record, self.packet)

    def test_01_packet_counts_and_no_eval(self):
        self.assertEqual((len(self.packet["documents"]),
                          len(self.packet["queries"])), (42, 24))
        self.assertFalse(any(x["split"] == "eval" for x in
                             self.packet["documents"] + self.packet["queries"]))

    def test_02_packet_does_not_expose_rule_labels_or_roles(self):
        for d in self.packet["documents"]:
            self.assertNotIn("role", d)
            self.assertNotIn("group_id", d)
        for q in self.packet["queries"]:
            self.assertNotIn("relevance", q)
            self.assertNotIn("kind", q)
        self.assertNotIn("RULE_PROVISIONAL_NOT_HUMAN", str(self.packet))

    def test_03_blank_templates_are_not_valid_reviews(self):
        with self.assertRaises(DataIntegrityError):
            validate_submission(self.blank, self.packet)

    def test_04_two_blanks_have_no_fake_reviewer_id(self):
        self.assertEqual(self.blank["reviewer_pseudonym"], "")
        self.assertFalse(self.blank["independence_attested"])

    def test_05_test_mock_schema_has_all_source_ratings(self):
        r = validate_submission(self.mock(), self.packet)
        self.assertEqual(r["query_count"], 24)
        self.assertEqual(r["rating_count"], 560)

    def test_06_same_reviewer_rejected_by_comparison(self):
        with self.assertRaises(DataIntegrityError):
            compare_submissions(self.mock(), self.mock(), self.packet)

    def test_07_mismatched_packet_hash_denied(self):
        self.rejects(lambda r: r.__setitem__("packet_sha256", "0"*64))

    def test_08_mismatched_dataset_hash_denied(self):
        self.rejects(lambda r: r["data_sha256"].__setitem__("documents", "0"*64))

    def test_09_attestation_missing_denied(self):
        self.rejects(lambda r: r.__setitem__("independence_attested", False))

    def test_10_review_status_not_submitted_denied(self):
        self.rejects(lambda r: r.__setitem__("review_status", "NOT_SUBMITTED"))

    def test_11_person_name_or_placeholder_disallowed(self):
        self.rejects(lambda r: r.__setitem__("reviewer_pseudonym", "John Doe"))

    def test_12_injected_eval_question_denied(self):
        self.rejects(lambda r: r["judgments"].append(
            {"query_id": "syn-e1b-water-q1",
             "query_class": "UNANSWERABLE", "ratings": []}))

    def test_13_missing_query_denied(self):
        self.rejects(lambda r: r["judgments"].pop())

    def test_14_missing_document_rating_denied(self):
        self.rejects(lambda r: r["judgments"][0]["ratings"].pop())

    def test_15_duplicate_document_rating_denied(self):
        def change(r):
            r["judgments"][0]["ratings"][0]["source_id"] = (
                r["judgments"][0]["ratings"][1]["source_id"])
        self.rejects(change)

    def test_16_out_of_scope_positive_rating_denied(self):
        def change(r):
            packet_doc = next(d for d in self.packet["documents"]
                              if d["split"] == "train"
                              and d["organization"] !=
                                  self.packet["queries"][0]["organization"])
            row = next(x for x in r["judgments"][0]["ratings"]
                       if x["source_id"] == packet_doc["source_id"])
            row.update(grade=3, evidence_quote=packet_doc["text"][:28])
        self.rejects(change)

    def test_17_expired_source_positive_rating_denied(self):
        def change(r):
            packet_doc = next(d for d in self.packet["documents"]
                              if d["split"] == "train"
                              and d["valid_until"] is not None)
            row = next(x for x in r["judgments"][0]["ratings"]
                       if x["source_id"] == packet_doc["source_id"])
            row.update(grade=3, evidence_quote=packet_doc["text"][:28])
        self.rejects(change)

    def test_18_unverified_source_positive_rating_denied(self):
        def change(r):
            d = next(x for x in self.packet["documents"]
                     if x["split"] == "train"
                     and x["authority"] == "UNVERIFIED_CLAIM")
            row = next(x for x in r["judgments"][0]["ratings"]
                       if x["source_id"] == d["source_id"])
            row.update(grade=3, evidence_quote=d["text"][:28])
        self.rejects(change)

    def test_19_invalid_evidence_span_denied(self):
        def change(r):
            row = next(x for x in r["judgments"][0]["ratings"] if
                       x["source_id"] == self.packet["documents"][0]["source_id"])
            row.update(grade=3, evidence_quote="SENTENCE THAT DOES NOT EXIST")
        self.rejects(change)

    def test_20_answerable_without_relevant_source_denied(self):
        self.rejects(lambda r: r["judgments"][0].__setitem__(
            "query_class", "ANSWERABLE"))

    def test_21_two_mock_reviews_never_approve_science(self):
        report = compare_submissions(
            self.mock(), self.mock("RV-MOCK-REVIEWER-B"), self.packet)
        self.assertFalse(report["adjudicated_gold"])
        self.assertFalse(report["independence_authenticated"])
        self.assertEqual(report["science_gate"], "REVIEW_REQUIRED")
        self.assertIsNone(report["class_cohen_kappa"])
        self.assertIsNone(report["rating_quadratic_weighted_kappa"])

    def test_22_agreement_examples_independent_of_reviews(self):
        self.assertAlmostEqual(_cohen(["A", "B", "A", "B"],
                                      ["A", "B", "B", "A"]), 0.0)
        self.assertIsNone(_quadratic_weighted([0, 0], [0, 0]))

    def test_23_export_path_blocked_outside_ignored_runtime(self):
        with self.assertRaises(DataIntegrityError):
            assert_private_path(ROOT / "docs" / "public_review.json", ROOT)

    def test_24_private_file_exclusive_create_prevents_overwrite(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".runtime") as tmp:
            target = Path(tmp) / "trial.json"
            private_write_json(target, {"mock":True}, ROOT)
            with self.assertRaises(FileExistsError):
                private_write_json(target, {"mock":False}, ROOT)

    def test_25_no_http_gateway_import(self):
        api = (ROOT / "backend" / "rightware_si" / "http_api.py").read_text(
            encoding="utf-8")
        self.assertNotIn("e1_03_review_protocol", api)


if __name__ == "__main__":
    unittest.main()
