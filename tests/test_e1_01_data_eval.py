"""ENG-E1-01 independent synthetic dataset integrity and evaluator tests."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import tempfile
import unittest

from rightware_si.e1_01_data_eval import (
    DataIntegrityError, _metrics, audit_records, evaluate, read_fixture
)

ROOT=Path(__file__).resolve().parents[1]/"docs"/"research"/"e1_01"


class E101DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs,cls.queries,cls.manifest=read_fixture(ROOT)

    def clone(self):
        return deepcopy(self.docs),deepcopy(self.queries),deepcopy(self.manifest)

    def rejects(self,change):
        docs,queries,manifest=self.clone()
        change(docs,queries,manifest)
        with self.assertRaises(DataIntegrityError):
            audit_records(docs,queries,manifest)

    def test_01_fixture_integrity_and_expected_counts(self):
        self.assertEqual((len(self.docs),len(self.queries)),(84,60))

    def test_02_split_counts(self):
        for split,expected in (("train",(42,30)),("dev",(21,15)),("test",(21,15))):
            self.assertEqual((
                sum(d["split"]==split for d in self.docs),
                sum(q["split"]==split for q in self.queries)),expected)

    def test_03_sha256_manifest_detects_modified_dataset(self):
        with tempfile.TemporaryDirectory() as temp:
            for name in ("documents.jsonl","queries.jsonl","manifest.json"):
                (Path(temp)/name).write_bytes((ROOT/name).read_bytes())
            p=Path(temp)/"documents.jsonl"
            p.write_bytes(p.read_bytes().replace(b"checkpoint",b"checkpointX",1))
            with self.assertRaises(DataIntegrityError):
                read_fixture(Path(temp))

    def test_04_source_id_collision_denied(self):
        self.rejects(lambda d,q,m:d[1].__setitem__("source_id",d[0]["source_id"]))

    def test_05_group_split_leakage_denied(self):
        self.rejects(lambda d,q,m:d[0].__setitem__("split","test"))

    def test_06_project_split_leakage_denied(self):
        self.rejects(lambda d,q,m:d[0].__setitem__("project","syn-e1-project-anchors"))

    def test_07_language_mismatch_denied(self):
        self.rejects(lambda d,q,m:q[0].__setitem__("language","EN"))

    def test_08_missing_label_rejected_for_answerable(self):
        self.rejects(lambda d,q,m:q[0].__setitem__("relevance",{}))

    def test_09_negative_query_cannot_have_positive_gold(self):
        idx=next(i for i,v in enumerate(self.queries) if v["kind"]=="UNANSWERABLE")
        self.rejects(lambda d,q,m:q[idx].__setitem__("relevance",{
            d[0]["source_id"]:3}))

    def test_10_foreign_source_cannot_be_gold(self):
        foreign=next(d for d in self.docs if d["role"]=="foreign")
        self.rejects(lambda d,q,m:q[0].__setitem__("relevance",{
            foreign["source_id"]:3}))

    def test_11_expired_source_cannot_be_gold(self):
        old=next(d for d in self.docs if d["role"]=="historical")
        self.rejects(lambda d,q,m:q[0].__setitem__("relevance",{
            old["source_id"]:3}))

    def test_12_unverified_source_cannot_be_positive_gold(self):
        bogus=next(d for d in self.docs if d["role"]=="unverified")
        self.rejects(lambda d,q,m:q[0].__setitem__("relevance",{
            bogus["source_id"]:3}))

    def test_13_ambiguous_project_org_denied(self):
        self.rejects(lambda d,q,m:q[0].__setitem__("organization","syn-org-external"))

    def test_14_query_duplicate_denied(self):
        self.rejects(lambda d,q,m:q[1].__setitem__("query_id",q[0]["query_id"]))

    def test_15_naive_timestamp_denied(self):
        self.rejects(lambda d,q,m:q[0].__setitem__("as_of","2026-11-18T12:00:00"))

    def test_16_dataset_evaluation_deterministic(self):
        a=evaluate(self.docs,self.queries,self.manifest)
        b=evaluate(self.docs,self.queries,self.manifest)
        self.assertEqual(json.dumps(a,sort_keys=True),json.dumps(b,sort_keys=True))
        self.assertEqual(a["classification"],"SYNTHETIC_DIAGNOSTIC_NOT_MODEL_SCIENCE")

    def test_17_e0_never_returns_foreign_source_ids(self):
        result=evaluate(self.docs,self.queries,self.manifest)
        self.assertTrue(all(s["foreign_ids_returned"]==0 for s in result["splits"].values()))

    def test_18_scoring_known_example(self):
        m=_metrics(["syn-a","syn-b"],{"syn-b":3})
        self.assertEqual(m["hit@1"],0.0)
        self.assertEqual(m["hit@2"],1.0)
        self.assertAlmostEqual(m["mrr@5"],0.5)
        self.assertAlmostEqual(m["ndcg@5"],1/1.584962500721156)

    def test_19_unanswerable_excluded_from_retrieval_denominator(self):
        m=evaluate(self.docs,self.queries,self.manifest)
        self.assertEqual(sum(x["answerable"] for x in m["splits"].values()),36)
        self.assertEqual(sum(x["negative_queries"] for x in m["splits"].values()),24)

    def test_20_experimental_fixture_not_blind_or_human_reviewed(self):
        self.assertEqual(self.manifest["review_status"],"REVIEW_REQUIRED")
        self.assertIn("not independently human",self.manifest["label_provenance"])
        self.assertFalse(self.manifest["ranker_trained"])

    def test_21_live_api_does_not_import_data_evaluator(self):
        api=(Path(__file__).resolve().parents[1]/"backend"/
             "rightware_si"/"http_api.py").read_text(encoding="utf-8")
        self.assertNotIn("e1_01_data_eval",api)

    def test_22_manifest_hashes_well_formed(self):
        for digest in self.manifest["sha256"].values():
            self.assertEqual(len(digest),64)
            self.assertTrue(all(ch in "0123456789abcdef" for ch in digest))

    def test_23_foreign_and_cross_project_distractors_present(self):
        self.assertEqual(sum(d["role"]=="foreign" for d in self.docs),12)
        self.assertEqual(sum(d["role"]=="other-project" for d in self.docs),12)

    def test_24_executed_example_never_claims_trained_rightware_ranker(self):
        out=evaluate(self.docs,self.queries,self.manifest)
        self.assertEqual(out["model"],"E0_BM25_PUBLIC_BASELINE")
        self.assertNotIn("RW-R1",json.dumps(out))


if __name__=="__main__":
    unittest.main()
