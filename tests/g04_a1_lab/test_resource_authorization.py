"""G04-A1-LAB-04: actual synthetic RSA verification and resource policy decisions."""
from dataclasses import replace
import os
import unittest
from unittest.mock import patch

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from rightware_si.g04_a1_lab import (
    DirectorySnapshot, Organization, OrganizationMembership, PrincipalBinding,
    Project, ProjectMembership, PROFILES, ResourceDecision, ResourceGrant,
    ResourcePolicySnapshot, ResourceRecord, ScopeSnapshot, ScopedPrincipal,
    Snapshot, SyntheticResourceAuthorizer, TrustKey,
)

NOW = 2000000000
ENV = {"RW_SI_ENVIRONMENT":"lab","RW_SI_ENABLE_G04_A1_LAB":"1"}
WORK = "syn-purpose-work"
AUDIT = "syn-purpose-audit"


class ResourceAuthorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private = rsa.generate_private_key(public_exponent=65537,key_size=2048)
        cls.key = TrustKey("syn-issuer","syn-key","AGENT",cls.private.public_key())

    def setUp(self):
        guard = patch.dict(os.environ,ENV)
        guard.start()
        self.addCleanup(guard.stop)
        self.now = NOW
        self.keys = Snapshot(NOW-1,NOW+59,(self.key,))
        self.directory = DirectorySnapshot(NOW-1,NOW+59,(
            PrincipalBinding("syn-issuer","syn-agent","syn-p1","AGENT",True,NOW+120),
            PrincipalBinding("syn-issuer","syn-other-agent","syn-p2","AGENT",True,NOW+120)))
        self.scope = ScopeSnapshot(NOW-1,NOW+59,
            (Organization("syn-rw",True),Organization("syn-other",True),Organization("syn-third",True)),
            (Project("syn-alpha","syn-rw",True),Project("syn-beta","syn-rw",True),
             Project("syn-gamma","syn-other",True),Project("syn-delta","syn-third",True)),
            (OrganizationMembership("syn-p1","syn-rw",True,NOW+120),
             OrganizationMembership("syn-p2","syn-rw",True,NOW+120)),
            (ProjectMembership("syn-p1","syn-alpha",True,NOW+120),
             ProjectMembership("syn-p2","syn-alpha",True,NOW+120)))
        self.policy = ResourcePolicySnapshot(NOW-1,NOW+59,(
            ResourceRecord("syn-task","syn-rw","syn-alpha","TASK","SYNTHETIC",True),
            ResourceRecord("syn-memory","syn-rw","syn-alpha","MEMORY","SYNTHETIC",True),
            ResourceRecord("syn-evidence","syn-rw","syn-alpha","EVIDENCE","SYNTHETIC",True),
            ResourceRecord("syn-other-task","syn-rw","syn-beta","TASK","SYNTHETIC",True),
            ResourceRecord("syn-foreign","syn-other","syn-gamma","TASK","SYNTHETIC",True),
            ResourceRecord("syn-third-task","syn-third","syn-delta","TASK","SYNTHETIC",True)),(
            ResourceGrant("syn-p1","syn-task","task:read",WORK,True,NOW+120),
            ResourceGrant("syn-p1","syn-task","task:write",WORK,True,NOW+120),
            ResourceGrant("syn-p1","syn-memory","memory:read",WORK,True,NOW+120),
            ResourceGrant("syn-p2","syn-evidence","evidence:read",AUDIT,True,NOW+120),
            ResourceGrant("syn-p1","syn-other-task","task:read",WORK,True,NOW+120),
            ResourceGrant("syn-p1","syn-foreign","task:read",WORK,True,NOW+120),
            ResourceGrant("syn-p1","syn-third-task","task:read",WORK,True,NOW+120)))
        self.make()

    def make(self,provider=None,scope=None):
        self.authorizer = SyntheticResourceAuthorizer(
            lambda:self.keys,lambda:self.directory,scope or (lambda:self.scope),
            provider or (lambda:self.policy),lambda:self.now)

    def token(self,subject="syn-agent",**extra):
        claims = dict(iss="syn-issuer",sub=subject,aud=PROFILES["AGENT"][1],
                      iat=NOW-5,nbf=NOW-5,exp=NOW+120,jti="syn-credential",gen=1)
        claims.update(extra)
        return jwt.encode(claims,self.private,algorithm="RS256",
                          headers={"typ":PROFILES["AGENT"][0],"kid":"syn-key"})

    def evaluate(self,resource="syn-task",action="task:read",purpose=WORK,
                 subject="syn-agent",org="syn-rw",project="syn-alpha",token=None,kind="AGENT"):
        return self.authorizer.evaluate(self.token(subject) if token is None else token,
                                        kind,org,project,resource,action,purpose)

    def deny(self,**kwargs):
        self.assertEqual(self.evaluate(**kwargs),ResourceDecision(False,"DENY_SYNTHETIC"))

    def change(self,**kwargs):
        self.now += 1
        self.policy = replace(self.policy,observed_at=self.now,valid_until=self.now+59,**kwargs)

    def test_01_exact_allowed_actions(self):
        for resource,action in (("syn-task","task:read"),("syn-task","task:write"),
                                ("syn-memory","memory:read")):
            result = self.evaluate(resource,action)
            self.assertEqual(result,ResourceDecision(True,"ALLOW_SYNTHETIC_EVALUATION_ONLY",NOW+59))
            self.assertFalse(hasattr(result,"token"))
            self.assertFalse(hasattr(result,"payload"))

    def test_02_membership_without_resource_grant(self):
        self.deny(subject="syn-other-agent")
        self.deny(resource="syn-evidence",action="evidence:read",purpose=AUDIT)

    def test_03_distinct_agent_grant_and_purpose(self):
        self.assertTrue(self.evaluate("syn-evidence","evidence:read",AUDIT,
                                      "syn-other-agent").allowed)
        self.deny(resource="syn-evidence",action="evidence:read",subject="syn-other-agent")

    def test_04_cross_project_even_with_grant(self):
        self.deny(resource="syn-other-task")
        self.deny(resource="syn-other-task",project="syn-beta")

    def test_05_two_adversary_orgs_even_with_grant(self):
        for resource,org,project in (("syn-foreign","syn-other","syn-gamma"),
                                     ("syn-third-task","syn-third","syn-delta")):
            self.deny(resource=resource)
            self.deny(resource=resource,org=org,project=project)

    def test_06_exact_action_and_purpose(self):
        self.deny(action="memory:read")
        self.deny(purpose=AUDIT)
        self.deny(purpose="syn-purpose-unknown")

    def test_07_privileged_or_wildcard_action_never_allowed(self):
        for action in ("task:approve","task:DONE","task:delete","source:ingest","*","task:*"):
            self.deny(action=action)

    def test_08_unknown_and_real_ids_same_denial(self):
        for resource in ("syn-unknown","real-resource","*"):
            self.deny(resource=resource)

    def test_09_forged_identity_or_scope_not_accepted(self):
        self.deny(token=ScopedPrincipal("syn-p1","syn-rw","syn-alpha","AGENT",NOW+30))
        self.deny(token=self.token(principal_id="syn-p1"))
        self.deny(kind="HUMAN")

    def test_10_inactive_resource(self):
        self.policy=replace(self.policy,resources=(replace(self.policy.resources[0],active=False),)
                            +self.policy.resources[1:])
        self.deny()

    def test_11_expired_inactive_grant(self):
        original=self.policy
        for fields in ({"active":False},{"expires_at":NOW}):
            self.policy=replace(original,grants=(replace(original.grants[0],**fields),)+original.grants[1:])
            self.make()
            self.deny()

    def test_12_duplicate_resource_or_grant(self):
        original=self.policy
        for key in ("resources","grants"):
            rows=getattr(original,key)
            self.policy=replace(original,**{key:rows+(rows[0],)})
            self.make()
            self.deny()

    def test_13_orphan_or_invalid_grant(self):
        original=self.policy
        for fields in ({"resource_id":"syn-missing"},{"action":"task:approve"},{"active":1}):
            self.policy=replace(original,grants=(replace(original.grants[0],**fields),)+original.grants[1:])
            self.make()
            self.deny()

    def test_14_non_synthetic_classification(self):
        self.policy=replace(self.policy,resources=(replace(self.policy.resources[0],classification="PRIVATE"),)
                            +self.policy.resources[1:])
        self.deny()

    def test_15_stale_future_invalid_policy_and_outage(self):
        original=self.policy
        for candidate in (None,replace(original,observed_at=NOW+1),
                          replace(original,valid_until=NOW),replace(original,valid_until=NOW+100)):
            self.policy=candidate
            self.make()
            self.deny()
        def unavailable():
            raise RuntimeError("internal secret")
        self.make(unavailable)
        self.deny()

    def test_16_policy_rollback_same_version(self):
        first=self.policy
        self.assertTrue(self.evaluate().allowed)
        self.policy=replace(first,valid_until=NOW+58)
        self.deny()
        self.policy=first
        self.change()
        self.assertTrue(self.evaluate().allowed)
        self.policy=first
        self.deny()

    def test_17_resource_cannot_move_project(self):
        self.assertTrue(self.evaluate().allowed)
        self.change(resources=(replace(self.policy.resources[0],project_id="syn-beta"),)
                    +self.policy.resources[1:])
        self.deny()

    def test_18_revoked_grant_cannot_reactivate(self):
        original=self.policy.grants
        self.assertTrue(self.evaluate().allowed)
        self.change(grants=(replace(original[0],active=False),)+original[1:])
        self.deny()
        self.change(grants=original)
        self.deny()

    def test_19_removed_grant_cannot_return(self):
        original=self.policy.grants
        self.assertTrue(self.evaluate().allowed)
        self.change(grants=original[1:])
        self.deny()
        self.change(grants=original)
        self.deny()

    def test_20_revocation_during_policy_callback(self):
        def revoke():
            self.now+=1
            self.keys=replace(self.keys,observed_at=self.now,
                              revoked=frozenset({("syn-issuer","syn-credential")}))
            return self.policy
        self.make(revoke)
        self.deny()

    def test_21_membership_revocation_during_policy_callback(self):
        def revoke():
            self.now+=1
            self.scope=replace(self.scope,observed_at=self.now,
                project_memberships=(replace(self.scope.project_memberships[0],active=False),)
                +self.scope.project_memberships[1:])
            return self.policy
        self.make(revoke)
        self.deny()

    def test_22_policy_change_during_recheck(self):
        calls=0
        def changed():
            nonlocal calls
            calls+=1
            if calls==2:
                self.change(grants=(replace(self.policy.grants[0],active=False),)+self.policy.grants[1:])
            return self.policy
        self.make(changed)
        self.deny()

    def test_23_grant_expiry_caps_result(self):
        self.policy=replace(self.policy,grants=(replace(self.policy.grants[0],expires_at=NOW+7),)
                            +self.policy.grants[1:])
        self.assertEqual(self.evaluate().valid_until,NOW+7)

    def test_24_lab_guard_on_use(self):
        with patch.dict(os.environ,{"RW_SI_ENABLE_G04_A1_LAB":"0"}):
            self.deny()

    def test_25_policy_capacity(self):
        self.policy=replace(self.policy,resources=tuple(
            ResourceRecord("syn-r"+str(i),"syn-rw","syn-alpha","TASK","SYNTHETIC",True)
            for i in range(257)),grants=())
        self.deny()


if __name__=="__main__":
    unittest.main()
