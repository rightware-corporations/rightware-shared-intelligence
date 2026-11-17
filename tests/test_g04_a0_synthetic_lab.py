"""G04-A0 negative-first synthetic tests. These do NOT satisfy DB/E2E G04 oracles."""
from dataclasses import replace
from datetime import datetime,timedelta,timezone
from pathlib import Path
import os
import unittest
from unittest.mock import patch
from rightware_si.g04_a0_synthetic_policy import (
    G04A0LabPolicy,Claim,Principal,Membership,Resource,Grant,AUDIO,
)
DSN="postgresql://rw:synthetic@127.0.0.1:5432/rw_test"

class G04A0SyntheticTests(unittest.TestCase):
    def setUp(self):
        self.flags=patch.dict(os.environ,{
            "RW_SI_ENVIRONMENT":"lab",
            "RW_SI_ENABLE_G04_A0_SYNTHETIC_LAB":"1"})
        self.flags.start()
        self.addCleanup(self.flags.stop)
        self.now=datetime(2026,11,17,tzinfo=timezone.utc)
        self.future=self.now+timedelta(hours=1)
        self.claim=Claim("syn-issuer","syn-sub","rw-si-g04-a0-synthetic-only",
                         "HUMAN",self.future)
        self.person=(Principal("syn-alice","syn-issuer","syn-sub","HUMAN"),)
        self.member=(Membership("syn-alice","syn-org-a","syn-project-a",
                                True,self.future),)
        self.resources=(Resource("syn-task-a","syn-org-a","syn-project-a","SYNTHETIC"),
                        Resource("syn-task-b","syn-org-b","syn-project-b","SYNTHETIC"),
                        Resource("syn-task-c","syn-org-c","syn-project-c","SYNTHETIC"))
        self.grants=(Grant("syn-alice","syn-task-a","task:read",
                           "syn-purpose-work",True,self.future),)

    def policy(self, **kwargs):
        settings=dict(principals=self.person,memberships=self.member,
                      resources=self.resources,grants=self.grants)
        return G04A0LabPolicy(DSN,**(settings|kwargs))

    def ask(self, *, claim=None,policy=None,org="syn-org-a",
            project="syn-project-a",resource="syn-task-a",
            action="task:read",purpose="syn-purpose-work"):
        return (policy or self.policy()).allows(
            claim or self.claim,org,project,resource,action,purpose,now=self.now)

    def test_01_allows_exact_synthetic_scope(self): self.assertTrue(self.ask())
    def test_02_denies_other_organization(self):
        self.assertFalse(self.ask(org="syn-org-b"))
    def test_03_denies_other_project(self):
        self.assertFalse(self.ask(project="syn-project-b"))
    def test_04_denies_cross_tenant_resource(self):
        self.assertFalse(self.ask(resource="syn-task-b"))
        self.assertFalse(self.ask(resource="syn-task-c"))
    def test_05_denies_missing_membership(self):
        self.assertFalse(self.ask(policy=self.policy(memberships=())))
    def test_06_denies_revoked_membership(self):
        self.assertFalse(self.ask(policy=self.policy(
            memberships=(replace(self.member[0],active=False),))))
    def test_07_denies_expired_membership(self):
        self.assertFalse(self.ask(policy=self.policy(
            memberships=(replace(self.member[0],expires_at=self.now),))))
    def test_08_denies_missing_resource_grant(self):
        self.assertFalse(self.ask(policy=self.policy(grants=())))
    def test_09_denies_revoked_resource_grant(self):
        self.assertFalse(self.ask(policy=self.policy(
            grants=(replace(self.grants[0],active=False),))))
    def test_10_denies_other_purpose(self):
        self.assertFalse(self.ask(purpose="syn-purpose-export"))
    def test_11_denies_wrong_issuer(self):
        self.assertFalse(self.ask(claim=replace(self.claim,issuer="syn-foreign")))
    def test_12_denies_wrong_audience(self):
        self.assertFalse(self.ask(claim=replace(self.claim,audience="wrong")))
    def test_13_denies_expired_claim(self):
        self.assertFalse(self.ask(claim=replace(self.claim,expires_at=self.now)))
    def test_14_denies_service_impersonating_human(self):
        self.assertFalse(self.ask(claim=replace(self.claim,kind="SERVICE")))
    def test_15_denies_privileged_actions_even_with_grant(self):
        self.assertFalse(self.ask(action="policy:approve",policy=self.policy(
            grants=(replace(self.grants[0],action="policy:approve"),))))
        self.assertFalse(self.ask(action="task:mark_done"))
    def test_16_denies_private_resource_class(self):
        r=replace(self.resources[0],classification="PRIVATE")
        self.assertFalse(self.ask(policy=self.policy(
            resources=(r,*self.resources[1:]))))
    def test_17_fails_closed_without_lab_flag(self):
        with patch.dict(os.environ,{"RW_SI_ENABLE_G04_A0_SYNTHETIC_LAB":"0"}):
            with self.assertRaises(RuntimeError): self.policy()
    def test_18_fails_closed_for_remote_db_target(self):
        with self.assertRaises(RuntimeError):
            G04A0LabPolicy("postgresql://rw:x@example.org:5432/prod",
                principals=self.person,memberships=self.member,
                resources=self.resources,grants=self.grants)
    def test_19_denies_duplicate_issuer_subject_mapping(self):
        self.assertFalse(self.ask(policy=self.policy(
            principals=(self.person[0],self.person[0]))))
    def test_20_denies_conflicting_duplicate_grants(self):
        self.assertFalse(self.ask(policy=self.policy(
            grants=(self.grants[0],replace(self.grants[0],active=False)))))
    def test_21_gateway_is_not_wired_to_fake_claims(self):
        api=Path(__file__).resolve().parents[1]/"backend"/"rightware_si"/"http_api.py"
        self.assertNotIn("g04_a0_synthetic_policy",
                         api.read_text(encoding="utf-8"))

if __name__=="__main__": unittest.main()
