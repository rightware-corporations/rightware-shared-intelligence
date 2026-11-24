"""E1.1C/03B opaque ID security tests. All submissions are mock data."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import json
import unittest
from rightware_si.e1_01_data_eval import DataIntegrityError
from rightware_si.e1_03_review_protocol import make_packet,blank_submission
from rightware_si.e1_03_blind_alias import (
    issue_packets,audit_packets,compare_aliased,
)
ROOT=Path(__file__).resolve().parents[1]


class E103BOpaqueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=make_packet(ROOT/"docs"/"research"/"e1_02")

    def fresh(self):
        return issue_packets(self.original)

    @staticmethod
    def mock(pack,pseudo):
        r=blank_submission(pack)
        r.update(reviewer_pseudonym=pseudo,independence_attested=True,
                 provisional_gold_not_consulted=True,
                 submitted_at="2026-11-24T10:00:00+02:00",
                 review_status="SUBMITTED_INDEPENDENT")
        for q in r["judgments"]:
            q["query_class"]="UNANSWERABLE"
            for rating in q["ratings"]:
                rating.update(grade=0,
                    justification="Mock data for schema validation only")
        return r

    def test_01_counts_and_alias_namespaces(self):
        p,m=self.fresh()
        for slot in ("A","B"):
            self.assertEqual((len(p[slot]["documents"]),
                              len(p[slot]["queries"])),(42,24))
            self.assertTrue(all(d["source_id"].startswith("DOC-")
                                for d in p[slot]["documents"]))
            self.assertTrue(all(q["query_id"].startswith("QUE-")
                                for q in p[slot]["queries"]))

    def test_02_no_original_ids_in_packets(self):
        p,m=self.fresh()
        ids={d["source_id"] for d in self.original["documents"]}
        ids.update(q["query_id"] for q in self.original["queries"])
        for slot in ("A","B"):
            encoded=json.dumps(p[slot])
            self.assertFalse(any(x in encoded for x in ids))

    def test_03_independent_reviewer_alias_sets(self):
        p,m=self.fresh()
        for field in ("documents","queries"):
            k="source_id" if field=="documents" else "query_id"
            self.assertFalse({d[k] for d in p["A"][field]} &
                             {d[k] for d in p["B"][field]})

    def test_04_no_role_group_or_label_in_packets(self):
        p,m=self.fresh()
        for slot in ("A","B"):
            payload=json.dumps(p[slot])
            for term in ('"role"','"group_id"','"relevance"',
                         'labels_provisional','RULE_PROVISIONAL_NOT_HUMAN'):
                self.assertNotIn(term,payload)

    def test_05_mapping_is_separate_from_reviewers(self):
        p,m=self.fresh()
        self.assertIn("sources",m["slots"]["A"])
        self.assertNotIn('"sources"',json.dumps(p["A"]))
        self.assertEqual(set(m["slots"]["A"]["sources"].values()),
                         {d["source_id"] for d in self.original["documents"]})

    def test_06_no_eval_records_or_labels(self):
        p,m=self.fresh()
        for slot in ("A","B"):
            self.assertFalse(any(x["split"]=="eval"
                             for x in p[slot]["documents"]+p[slot]["queries"]))

    def test_07_modified_hash_rejected(self):
        p,m=self.fresh()
        m["slots"]["A"]["packet_sha256"]="0"*64
        with self.assertRaises(DataIntegrityError):
            audit_packets(self.original,p,m)

    def test_08_swapped_packets_rejected(self):
        p,m=self.fresh()
        with self.assertRaises(DataIntegrityError):
            audit_packets(self.original,{"A":p["B"],"B":p["A"]},m)

    def test_09_crosswalk_collision_rejected(self):
        p,m=self.fresh()
        qmap=m["slots"]["A"]["queries"]
        keys=list(qmap)
        qmap[keys[0]]=qmap[keys[1]]
        with self.assertRaises(DataIntegrityError):
            audit_packets(self.original,p,m)

    def test_10_mock_reconciliation_not_human_gold(self):
        p,m=self.fresh()
        result=compare_aliased(
            self.mock(p["A"],"RV-MOCK-A"),
            self.mock(p["B"],"RV-MOCK-B"),p,m,self.original)
        self.assertEqual(result["ratings_per_reviewer"],560)
        self.assertEqual(result["science_gate"],"REVIEW_REQUIRED")
        self.assertFalse(result["independence_authenticated"])
        self.assertFalse(result["adjudicated_gold"])

    def test_11_same_reviewer_rejected(self):
        p,m=self.fresh()
        with self.assertRaises(DataIntegrityError):
            compare_aliased(self.mock(p["A"],"RV-MOCK-X"),
                            self.mock(p["B"],"RV-MOCK-X"),p,m,self.original)

    def test_12_raw_original_id_submission_rejected(self):
        p,m=self.fresh()
        a=self.mock(p["A"],"RV-MOCK-A")
        a["judgments"][0]["ratings"][0]["source_id"]=(
            self.original["documents"][0]["source_id"])
        with self.assertRaises(DataIntegrityError):
            compare_aliased(a,self.mock(p["B"],"RV-MOCK-B"),
                            p,m,self.original)

    def test_13_no_http_api_import(self):
        api=(ROOT/"backend"/"rightware_si"/"http_api.py").read_text("utf-8")
        self.assertNotIn("e1_03_blind_alias",api)


if __name__=="__main__":
    unittest.main()
