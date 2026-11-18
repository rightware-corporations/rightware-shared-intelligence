"""Offline scientific E0 tests. NEVER a vendor comparison or production proof."""
from dataclasses import replace
from datetime import datetime, timezone, timedelta
import unittest

from rightware_si.experimental_engine_e0 import Query, Source, decide


class RightwareIntelligenceE0Tests(unittest.TestCase):
    def setUp(self):
        self.t = datetime(2026, 11, 18, 10, tzinfo=timezone.utc)
        self.base = Source(
            "syn-id-a", "syn-org-rw", "syn-project-alpha",
            "Relatório de continuidade operacional validado para o motor RIGHTWARE",
            "VERIFIED_LEDGER", self.t - timedelta(days=2),
            self.t - timedelta(days=3), None, "syn-status", "syn-ready")
        self.foreign = Source(
            "syn-secret-b", "syn-org-b", "syn-project-beta",
            "Relatório de continuidade operacional validado para o motor RIGHTWARE",
            "OFFICIAL_SOURCE", self.t - timedelta(days=2),
            self.t - timedelta(days=3))
        self.q = Query("syn-org-rw", "syn-project-alpha",
                       "continuidade operacional RIGHTWARE", self.t)

    def run_engine(self, sources=None, q=None, trusted_scope=True):
        return decide(q or self.q, sources if sources is not None
                      else [self.base,self.foreign], trusted_scope=trusted_scope)

    def test_01_single_authorized_source_is_candidate(self):
        out=self.run_engine()
        self.assertEqual(out.status,"EVIDENCE_CANDIDATE")
        self.assertEqual([x.source_id for x in out.candidates],["syn-id-a"])

    def test_02_no_trusted_scope_is_denied_without_leak(self):
        out=self.run_engine(trusted_scope=False)
        self.assertEqual(out.status,"DENY")
        self.assertEqual(out.candidates,())

    def test_03_only_foreign_source_abstains_without_source_id(self):
        out=self.run_engine([self.foreign])
        self.assertEqual(out.status,"ABSTAIN")
        self.assertEqual(out.candidates,())

    def test_04_other_project_in_same_org_is_never_retrieved(self):
        r=replace(self.base,source_id="syn-other-project",
                  project="syn-project-other")
        out=self.run_engine([r])
        self.assertEqual(out.candidates,())

    def test_05_future_observation_does_not_answer_at_old_date(self):
        future=replace(self.base,observed_at=self.t+timedelta(seconds=1))
        self.assertEqual(self.run_engine([future]).status,"ABSTAIN")

    def test_06_valid_from_after_query_excludes_record(self):
        future=replace(self.base,valid_from=self.t+timedelta(seconds=1))
        self.assertEqual(self.run_engine([future]).status,"ABSTAIN")

    def test_07_expired_validity_excludes_record(self):
        old=replace(self.base,valid_until=self.t)
        self.assertEqual(self.run_engine([old]).status,"ABSTAIN")

    def test_08_unverified_only_must_abstain(self):
        candidate=replace(self.base,authority="UNVERIFIED_CLAIM")
        out=self.run_engine([candidate])
        self.assertEqual(out.status,"ABSTAIN")
        self.assertEqual(out.reason,"UNVERIFIED_ONLY")

    def test_09_unverified_contradiction_not_authoritative(self):
        other=replace(self.base,source_id="syn-other",authority="UNVERIFIED_CLAIM",
                      claim_value="syn-not-ready")
        self.assertEqual(self.run_engine([self.base,other]).status,
                         "EVIDENCE_CANDIDATE")

    def test_10_conflicting_official_sources_never_silenced_by_topk(self):
        other=replace(self.base,source_id="syn-official",authority="OFFICIAL_SOURCE",
                      claim_value="syn-not-ready")
        out=self.run_engine([self.base,other],
                            q=replace(self.q,limit=1))
        self.assertEqual(out.status,"CONFLICT")
        self.assertEqual(len(out.candidates),1)

    def test_11_identical_verified_claims_not_marked_conflict(self):
        other=replace(self.base,source_id="syn-official",authority="OFFICIAL_SOURCE")
        self.assertEqual(self.run_engine([self.base,other]).status,
                         "EVIDENCE_CANDIDATE")

    def test_12_query_without_evidence_abstains(self):
        out=self.run_engine(q=replace(self.q,text="xylophone outlier 9933"))
        self.assertEqual(out.status,"ABSTAIN")

    def test_13_portuguese_accents_normalized(self):
        source=replace(self.base,text="Evidência auditável de governação")
        q=replace(self.q,text="evidencia governacao")
        self.assertEqual(self.run_engine([source],q=q).status,"EVIDENCE_CANDIDATE")

    def test_14_duplicate_source_ids_fail_closed(self):
        self.assertEqual(self.run_engine([self.base,self.base]).status,"ABSTAIN")

    def test_15_invalid_authority_tag_fail_closed(self):
        source=replace(self.base,authority="USER_SAYS_VERIFIED")
        self.assertEqual(self.run_engine([source]).status,"ABSTAIN")

    def test_16_invalid_claim_without_value_fail_closed(self):
        source=replace(self.base,claim_value=None)
        self.assertEqual(self.run_engine([source]).status,"ABSTAIN")

    def test_17_observational_only_is_not_proof(self):
        source=replace(self.base,authority="OBSERVATION")
        self.assertEqual(self.run_engine([source]).status,"ABSTAIN")

    def test_18_bm25_ranking_deterministic(self):
        s=replace(self.base,source_id="syn-id-b")
        a=self.run_engine([self.base,s]).candidates
        b=self.run_engine([s,self.base]).candidates
        self.assertEqual(a,b)

    def test_19_topk_respected(self):
        s=replace(self.base,source_id="syn-id-b")
        out=self.run_engine([self.base,s],q=replace(self.q,limit=1))
        self.assertEqual(len(out.candidates),1)

    def test_20_wrong_tenant_query_never_finds_source(self):
        q=replace(self.q,organization="syn-org-c")
        out=self.run_engine(q=q)
        self.assertEqual(out.candidates,())

    def test_21_naive_datetime_is_rejected(self):
        q=replace(self.q,as_of=datetime(2026,11,18))
        self.assertEqual(self.run_engine(q=q).status,"ABSTAIN")

    def test_22_not_a_public_gateway_dependency(self):
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]/"backend"/"rightware_si"
        for file in ("http_api.py","memory.py","context_service.py","verification_ledger.py"):
            self.assertNotIn("experimental_engine_e0",
                             (root/file).read_text(encoding="utf-8"))

if __name__=="__main__":
    unittest.main()
