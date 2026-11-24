"""G04-A1-LAB-03: signed identities and explicit synthetic scope; no resource rights."""
from dataclasses import replace
import os
import unittest
from unittest.mock import patch

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from rightware_si.g04_a1_lab import (
    CredentialRejected, DirectorySnapshot, Organization, OrganizationMembership,
    PrincipalBinding, Project, ProjectMembership, PROFILES, ScopeSnapshot,
    ScopedPrincipal, Snapshot, SyntheticScopeResolver, TrustKey,
)

NOW = 2000000000
ENV = {"RW_SI_ENVIRONMENT":"lab","RW_SI_ENABLE_G04_A1_LAB":"1"}


class ScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private = {k:rsa.generate_private_key(public_exponent=65537,key_size=2048)
                       for k in ("AGENT","SERVICE","HUMAN")}
        cls.keys = tuple(TrustKey("syn-issuer","syn-key",k,p.public_key())
                         for k,p in cls.private.items())

    def setUp(self):
        guard = patch.dict(os.environ,ENV)
        guard.start()
        self.addCleanup(guard.stop)
        self.now = NOW
        self.key_snap = Snapshot(NOW-1,NOW+59,self.keys)
        self.directory = DirectorySnapshot(NOW-1,NOW+59,(
            PrincipalBinding("syn-issuer","syn-agent","syn-p1","AGENT",True,NOW+120),
            PrincipalBinding("syn-issuer","syn-service","syn-p2","SERVICE",True,NOW+120),
            PrincipalBinding("syn-issuer","syn-human","syn-p3","HUMAN",True,NOW+120)))
        self.scope = ScopeSnapshot(NOW-1,NOW+59,
            (Organization("syn-rw",True),Organization("syn-other",True),Organization("syn-third",True)),
            (Project("syn-alpha","syn-rw",True),Project("syn-beta","syn-rw",True),
             Project("syn-gamma","syn-other",True),Project("syn-delta","syn-third",True)),
            (OrganizationMembership("syn-p1","syn-rw",True,NOW+120),
             OrganizationMembership("syn-p1","syn-other",True,NOW+120),
             OrganizationMembership("syn-p2","syn-rw",True,NOW+120),
             OrganizationMembership("syn-p3","syn-third",True,NOW+120)),
            (ProjectMembership("syn-p1","syn-alpha",True,NOW+120),
             ProjectMembership("syn-p1","syn-gamma",True,NOW+120),
             ProjectMembership("syn-p2","syn-beta",True,NOW+120),
             ProjectMembership("syn-p3","syn-delta",True,NOW+120)))
        self.make_resolver()

    def make_resolver(self, provider=None):
        self.resolver = SyntheticScopeResolver(lambda:self.key_snap,lambda:self.directory,
                                                provider or (lambda:self.scope),lambda:self.now)

    def token(self, kind="AGENT", **extra):
        data = dict(iss="syn-issuer",sub="syn-"+kind.lower(),aud=PROFILES[kind][1],
                    iat=NOW-5,nbf=NOW-5,exp=NOW+120,jti="syn-credential",gen=1)
        data.update(extra)
        return jwt.encode(data,self.private[kind],algorithm="RS256",
                          headers={"typ":PROFILES[kind][0],"kid":"syn-key"})

    def resolve(self, org="syn-rw", project="syn-alpha", kind="AGENT", token=None):
        return self.resolver.resolve(self.token(kind) if token is None else token,kind,org,project)

    def denied(self, org="syn-rw", project="syn-alpha", kind="AGENT", token=None):
        with self.assertRaisesRegex(CredentialRejected,"^synthetic credential rejected$"):
            self.resolve(org,project,kind,token)

    def change(self, **kwargs):
        self.now += 1
        self.scope = replace(self.scope, observed_at=self.now,valid_until=self.now+59,**kwargs)

    def test_01_explicit_scope_no_resource_rights(self):
        result = self.resolve()
        self.assertIsInstance(result,ScopedPrincipal)
        self.assertEqual((result.principal_id,result.organization_id,result.project_id),
                         ("syn-p1","syn-rw","syn-alpha"))
        self.assertEqual(result.expires_at,NOW+59)
        for field in ("permissions","allows","resource_id","role"):
            self.assertFalse(hasattr(result,field))

    def test_02_multi_org_requires_explicit_selection(self):
        self.assertEqual(self.resolve("syn-other","syn-gamma").organization_id,"syn-other")
        self.denied("syn-rw","syn-gamma")
        self.denied("syn-other","syn-alpha")

    def test_03_cross_project_denied(self):
        self.denied("syn-rw","syn-beta")
        self.denied("syn-third","syn-delta")

    def test_04_distinct_agents_and_human(self):
        self.assertEqual(self.resolve("syn-rw","syn-beta","SERVICE").principal_id,"syn-p2")
        self.assertEqual(self.resolve("syn-third","syn-delta","HUMAN").principal_id,"syn-p3")
        self.denied(kind="SERVICE")
        self.denied(kind="HUMAN")

    def test_05_claims_cannot_grant_scope(self):
        self.denied(token=self.token(organization_id="syn-rw",project_id="syn-alpha"))

    def test_06_forged_context_denied(self):
        self.denied(token=ScopedPrincipal("syn-p1","syn-rw","syn-alpha","AGENT",NOW+30))

    def test_07_unknown_and_real_ids_denied(self):
        self.denied("syn-missing","syn-alpha")
        self.denied("syn-rw","syn-missing")
        self.denied("real-org","syn-alpha")

    def test_08_inactive_organization_or_project(self):
        original=self.scope
        for key in ("organizations","projects"):
            rows=getattr(original,key)
            self.scope=replace(original,**{key:(replace(rows[0],active=False),)+rows[1:]})
            self.make_resolver()
            self.denied()

    def test_09_expired_or_inactive_membership(self):
        original=self.scope
        for key in ("organization_memberships","project_memberships"):
            rows=getattr(original,key)
            for fields in ({"active":False},{"expires_at":NOW}):
                self.scope=replace(original,**{key:(replace(rows[0],**fields),)+rows[1:]})
                self.make_resolver()
                self.denied()

    def test_10_duplicate_rows_fail_closed(self):
        original=self.scope
        for key in ("organizations","projects","organization_memberships","project_memberships"):
            rows=getattr(original,key)
            self.scope=replace(original,**{key:rows+(rows[0],)})
            self.make_resolver()
            self.denied()

    def test_11_orphan_project_denied(self):
        self.scope=replace(self.scope,projects=(replace(self.scope.projects[0],organization_id="syn-missing"),)+self.scope.projects[1:])
        self.denied()

    def test_12_project_membership_needs_org_membership(self):
        self.scope=replace(self.scope,organization_memberships=self.scope.organization_memberships[1:])
        self.denied()

    def test_13_scope_snapshot_outage_stale_future(self):
        original=self.scope
        for snap in (None,replace(original,observed_at=NOW+1),replace(original,valid_until=NOW),
                     replace(original,valid_until=NOW+100)):
            self.scope=snap
            self.make_resolver()
            self.denied()
        def unavailable():
            raise OSError("private fixture detail")
        self.make_resolver(unavailable)
        self.denied()

    def test_14_same_version_mutation_and_rollback(self):
        first=self.scope
        self.resolve()
        self.scope=replace(first,valid_until=NOW+58)
        self.denied()
        self.scope=first
        self.change()
        self.resolve()
        self.scope=first
        self.denied()

    def test_15_project_cannot_move_org(self):
        self.resolve()
        self.change(projects=(replace(self.scope.projects[0],organization_id="syn-other"),)+self.scope.projects[1:])
        self.denied("syn-other","syn-alpha")

    def test_16_removed_or_revoked_project_membership_cannot_return(self):
        original=self.scope.project_memberships
        self.resolve()
        self.change(project_memberships=original[1:])
        self.denied()
        self.change(project_memberships=original)
        self.denied()

    def test_17_inactive_org_membership_cannot_reactivate(self):
        original=self.scope.organization_memberships
        self.resolve()
        self.change(organization_memberships=(replace(original[0],active=False),)+original[1:])
        self.denied()
        self.change(organization_memberships=original)
        self.denied()

    def test_18_credential_revocation_during_scope_callback(self):
        def revoke():
            self.now+=1
            self.key_snap=replace(self.key_snap,observed_at=self.now,
                                  revoked=frozenset({("syn-issuer","syn-credential")}))
            return self.scope
        self.make_resolver(revoke)
        self.denied()

    def test_19_directory_revocation_during_scope_callback(self):
        def revoke():
            self.now+=1
            self.directory=replace(self.directory,observed_at=self.now,
                                   bindings=(replace(self.directory.bindings[0],active=False),)+self.directory.bindings[1:])
            return self.scope
        self.make_resolver(revoke)
        self.denied()

    def test_20_key_snapshot_expires_during_directory_callback(self):
        def slow():
            self.now=NOW+59
            return replace(self.directory,observed_at=self.now,valid_until=self.now+59)
        resolver=SyntheticScopeResolver(lambda:self.key_snap,slow,lambda:self.scope,lambda:self.now)
        with self.assertRaises(CredentialRejected):
            resolver.resolve(self.token(),"AGENT","syn-rw","syn-alpha")

    def test_21_membership_expiry_caps_context(self):
        self.scope=replace(self.scope,project_memberships=(
            replace(self.scope.project_memberships[0],expires_at=NOW+7),)+self.scope.project_memberships[1:])
        self.assertEqual(self.resolve().expires_at,NOW+7)

    def test_22_guard_on_each_call(self):
        with patch.dict(os.environ,{"RW_SI_ENABLE_G04_A1_LAB":"0"}):
            self.denied()

    def test_23_non_boolean_status_rejected(self):
        self.scope=replace(self.scope,organizations=(replace(self.scope.organizations[0],active=1),)+self.scope.organizations[1:])
        self.denied()


if __name__=="__main__":
    unittest.main()
