"""E1.1C/03C structural conflict annotation tests; NEVER human gold."""
from copy import deepcopy
from pathlib import Path
import unittest
from rightware_si.e1_01_data_eval import DataIntegrityError
from rightware_si.e1_03_review_protocol import (
    SCHEMA_V2, blank_submission, validate_submission, make_packet,
)
from rightware_si.e1_03_blind_alias import issue_packets, compare_aliased, audit_packets
ROOT = Path(__file__).resolve().parents[1]


class E103ConflictTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = make_packet(ROOT / "docs/research/e1_02")

    def setUp(self):
        self.packets, self.custody = issue_packets(self.raw)

    def mock(self, slot):
        p = self.packets[slot]
        record = blank_submission(p)
        record.update(reviewer_pseudonym="RV-MOCK-" + slot,
                      independence_attested=True, provisional_gold_not_consulted=True,
                      submitted_at="2026-11-24T12:00:00+02:00",
                      review_status="SUBMITTED_INDEPENDENT")
        for j in record["judgments"]:
            j["query_class"] = "UNANSWERABLE"
            for r in j["ratings"]:
                r.update(grade=0, justification="Synthetic test only, no human annotation")
        maps = self.custody["slots"][slot]
        invq = {v:k for k,v in maps["queries"].items()}
        invd = {v:k for k,v in maps["sources"].items()}
        qid = invq["syn-e1b-registry-q1"]
        official = invd["syn-e1b-registry-d1"]
        opposing = invd["syn-e1b-registry-d4"]
        j = next(x for x in record["judgments"] if x["query_id"] == qid)
        d = {x["source_id"]:x for x in p["documents"]}
        r = next(x for x in j["ratings"] if x["source_id"] == official)
        r.update(grade=3, evidence_quote=d[official]["text"])
        j["query_class"] = "AUTHORITY_CONFLICT"
        j["conflict_claims"] = [dict(official_source_id=official,
            opposing_source_id=opposing, opposing_quote=d[opposing]["text"],
            rationale="Mock structural contradiction annotation, not adjudicated truth")]
        return record, j, d, invd

    def rejects(self, change):
        r,j,d,ids = self.mock("A")
        change(r,j,d,ids)
        with self.assertRaises(DataIntegrityError):
            validate_submission(r,self.packets["A"])

    def test_01_versioned_opaque_packets(self):
        self.assertEqual(self.packets["A"]["schema_version"], SCHEMA_V2)
        self.assertIn("conflict_claims", blank_submission(self.packets["B"])["judgments"][0])

    def test_02_official_vs_unverified_is_representable(self):
        r,j,d,ids = self.mock("A")
        result = validate_submission(r,self.packets["A"])
        item = result["judgments"][j["query_id"]]
        self.assertEqual(item["grades"][ids["syn-e1b-registry-d4"]],0)
        self.assertEqual(len(item["conflict_pairs"]),1)

    def test_03_missing_explicit_pair_rejected(self):
        self.rejects(lambda r,j,d,i:j.update(conflict_claims=[]))

    def test_04_unverified_cannot_get_support_grade(self):
        def change(r,j,d,i):
            sid=i["syn-e1b-registry-d4"]
            next(x for x in j["ratings"] if x["source_id"]==sid).update(
                grade=3,evidence_quote=d[sid]["text"])
        self.rejects(change)

    def test_05_forged_quote_rejected(self):
        self.rejects(lambda r,j,d,i:j["conflict_claims"][0].update(
            opposing_quote="NONEXISTENT EVIDENCE"))

    def test_06_foreign_opponent_rejected(self):
        def change(r,j,d,i):
            sid=i["syn-e1b-registry-d5"]
            j["conflict_claims"][0].update(opposing_source_id=sid,
                                           opposing_quote=d[sid]["text"])
        self.rejects(change)

    def test_07_expired_opponent_rejected(self):
        def change(r,j,d,i):
            sid=i["syn-e1b-registry-d3"]
            j["conflict_claims"][0].update(opposing_source_id=sid,
                                           opposing_quote=d[sid]["text"])
        self.rejects(change)

    def test_08_other_project_opponent_rejected(self):
        def change(r,j,d,i):
            sid=i["syn-e1b-registry-d6"]
            j["conflict_claims"][0].update(opposing_source_id=sid,
                                           opposing_quote=d[sid]["text"])
        self.rejects(change)

    def test_09_nonconflict_class_cannot_carry_pair(self):
        self.rejects(lambda r,j,d,i:j.update(query_class="ANSWERABLE"))

    def test_10_duplicate_pair_rejected(self):
        self.rejects(lambda r,j,d,i:j["conflict_claims"].append(
            deepcopy(j["conflict_claims"][0])))

    def test_11_official_anchor_required(self):
        self.rejects(lambda r,j,d,i:j["conflict_claims"][0].update(
            official_source_id=i["syn-e1b-registry-d4"]))

    def test_12_schema_downgrade_rejected(self):
        self.rejects(lambda r,j,d,i:r.update(schema_version="rightware-e1c-independent-review-v1"))

    def test_13_cross_reviewer_conflict_pairs_reconciled(self):
        a,_,_,_=self.mock("A")
        b,_,_,_=self.mock("B")
        result=compare_aliased(a,b,self.packets,self.custody,self.raw)
        self.assertEqual(result["conflict_pair_disagreement_queries"],0)
        self.assertFalse(result["adjudicated_gold"])
        self.assertEqual(result["science_gate"],"REVIEW_REQUIRED")

    def test_14_conflict_disagreement_is_counted(self):
        a,_,_,_=self.mock("A")
        b,j,_,_=self.mock("B")
        j.update(query_class="ANSWERABLE",conflict_claims=[])
        result=compare_aliased(a,b,self.packets,self.custody,self.raw)
        self.assertEqual(result["conflict_pair_disagreement_queries"],1)
        self.assertEqual(result["disagreement_count"],1)

    def test_15_legacy_map_not_accepted_by_new_runner(self):
        self.custody["schema"]="rightware-e1-03b-opaque-map-v1"
        with self.assertRaises(DataIntegrityError):
            audit_packets(self.raw,self.packets,self.custody)
