"""ENG-E1-02 quality and unlabelled eval data safety checks."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import unittest

from rightware_si.e1_01_data_eval import DataIntegrityError
from rightware_si.e1_02_quality import read_data, audit, similarity, e0_development_diagnostic

ROOT=Path(__file__).resolve().parents[1]/"docs"/"research"/"e1_02"


class E102QualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs,cls.queries,cls.labels,cls.manifest=read_data(ROOT)
        cls.profile=audit(cls.docs,cls.queries,cls.labels,cls.manifest)

    def mutate_fail(self,mutator):
        d,q,l,m=deepcopy((self.docs,self.queries,self.labels,self.manifest))
        mutator(d,q,l,m)
        with self.assertRaises(DataIntegrityError):
            audit(d,q,l,m)

    def test_01_counts_and_unlabeled_eval(self):
        self.assertEqual((len(self.docs),len(self.queries),len(self.labels)),(56,32,24))
        self.assertEqual(self.profile["eval_unlabeled"],8)

    def test_02_human_review_absent_not_falsified(self):
        self.assertEqual(self.manifest["review_status"],"INDEPENDENT_REVIEW_REQUIRED")
        self.assertEqual(self.profile["independent_reviewers"],0)

    def test_03_two_languages_in_all_splits(self):
        for split in ("train","dev","eval"):
            self.assertEqual({q["language"] for q in self.queries if q["split"]==split},
                             {"PT","EN"})

    def test_04_competing_subjects_share_project_in_split(self):
        for split in ("train","dev","eval"):
            self.assertEqual(len({d["project"] for d in self.docs
                                  if d["split"]==split and d["role"]=="current"}),1)

    def test_05_exact_duplicate_text_in_other_split_rejected(self):
        self.mutate_fail(lambda d,q,l,m:d[28].__setitem__("text",d[0]["text"]))

    def test_06_semantic_near_duplicate_with_changed_punctuation_rejected(self):
        def patch(d,q,l,m):
            d[28]["text"]=d[0]["text"].replace(".", "; ").replace(",", " ")
        self.mutate_fail(patch)

    def test_07_query_near_duplicate_across_splits_rejected(self):
        self.mutate_fail(lambda d,q,l,m:q[16].__setitem__("text",q[0]["text"]))

    def test_08_eval_label_injected_rejected(self):
        def patch(d,q,l,m):
            l.append(dict(query_id=q[-1]["query_id"],split="eval",
                          review_state="RULE_PROVISIONAL_NOT_HUMAN",relevance={}))
        self.mutate_fail(patch)

    def test_09_rule_label_claiming_human_review_rejected(self):
        self.mutate_fail(lambda d,q,l,m:l[0].__setitem__("review_state","INDEPENDENT_PASS"))

    def test_10_cross_project_label_rejected(self):
        target=next(d for d in self.docs if d["role"]=="other_project")
        self.mutate_fail(lambda d,q,l,m:l[0].__setitem__(
            "relevance",{target["source_id"]:3}))

    def test_11_foreign_gold_rejected(self):
        target=next(d for d in self.docs if d["role"]=="foreign")
        self.mutate_fail(lambda d,q,l,m:l[0].__setitem__(
            "relevance",{target["source_id"]:3}))

    def test_12_unverified_gold_rejected(self):
        target=next(d for d in self.docs if d["role"]=="unverified")
        self.mutate_fail(lambda d,q,l,m:l[0].__setitem__(
            "relevance",{target["source_id"]:3}))

    def test_13_expired_gold_rejected(self):
        target=next(d for d in self.docs if d["role"]=="expired")
        self.mutate_fail(lambda d,q,l,m:l[0].__setitem__(
            "relevance",{target["source_id"]:3}))

    def test_14_cross_group_source_mismatch_rejected(self):
        target=next(d for d in self.docs if d["group_id"]!=self.queries[0]["group_id"]
                    and d["role"]=="current")
        self.mutate_fail(lambda d,q,l,m:l[0].__setitem__(
            "relevance",{target["source_id"]:3}))

    def test_15_all_provisional_labels_mapped(self):
        self.assertEqual({q["query_id"] for q in self.queries if q["split"]!="eval"},
                         {l["query_id"] for l in self.labels})

    def test_16_all_eval_queries_unlabeled(self):
        eval_ids={q["query_id"] for q in self.queries if q["split"]=="eval"}
        self.assertFalse(eval_ids & {l["query_id"] for l in self.labels})

    def test_17_e0_diagnostic_reproducible(self):
        r=e0_development_diagnostic(self.docs,self.queries,self.labels)
        self.assertEqual(r,e0_development_diagnostic(self.docs,self.queries,self.labels))
        self.assertNotIn("eval",r)

    def test_18_e0_does_not_expose_foreign_source(self):
        r=e0_development_diagnostic(self.docs,self.queries,self.labels)
        self.assertEqual([v["foreign_ids"] for v in r.values()],[0,0])

    def test_19_cross_split_shingle_similarity_bounded(self):
        self.assertLess(similarity(self.docs[0]["text"],self.docs[-1]["text"]),.65)

    def test_20_no_new_production_import(self):
        api=(Path(__file__).resolve().parents[1]/"backend"/
             "rightware_si"/"http_api.py").read_text(encoding="utf-8")
        self.assertNotIn("e1_02_quality",api)


if __name__=="__main__":
    unittest.main()
