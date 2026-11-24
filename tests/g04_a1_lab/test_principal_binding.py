"""Synthetic-only principal binding, exercised with actual signed credentials."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import os
import unittest
from unittest.mock import patch

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from rightware_si.g04_a1_lab import (
    CredentialRejected, DirectorySnapshot, IdentityCandidate, PrincipalBinding,
    PROFILES, ResolvedPrincipal, Snapshot, SyntheticPrincipalResolver, TrustKey,
)

NOW = 2000000000
ENV = {"RW_SI_ENVIRONMENT": "lab", "RW_SI_ENABLE_G04_A1_LAB": "1"}


class PrincipalBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private = {k: rsa.generate_private_key(public_exponent=65537, key_size=2048)
                       for k in ("HUMAN", "AGENT", "SERVICE", "OTHER", "EXCHANGE")}
        cls.keys = tuple(TrustKey("syn-issuer", "syn-kid", k, cls.private[k].public_key())
                         for k in ("HUMAN", "AGENT", "SERVICE", "EXCHANGE")) + (
            TrustKey("syn-other", "syn-kid", "HUMAN", cls.private["OTHER"].public_key()),)
        cls.bindings = (
            PrincipalBinding("syn-issuer", "syn-human", "syn-p1", "HUMAN", True, NOW+120),
            PrincipalBinding("syn-other", "syn-human", "syn-p2", "HUMAN", True, NOW+120),
            PrincipalBinding("syn-issuer", "syn-agent", "syn-p3", "AGENT", True, NOW+120),
            PrincipalBinding("syn-issuer", "syn-service", "syn-p4", "SERVICE", True, NOW+120),
        )

    def setUp(self):
        env = patch.dict(os.environ, ENV)
        env.start()
        self.addCleanup(env.stop)
        self.now = NOW
        self.keys_snapshot = Snapshot(NOW-1, NOW+59, self.keys)
        self.directory = DirectorySnapshot(NOW-1, NOW+59, self.bindings)
        self.resolver = SyntheticPrincipalResolver(lambda: self.keys_snapshot,
                                                   lambda: self.directory, lambda: self.now)

    def token(self, kind="HUMAN", signing=None, **claims):
        data = dict(iss="syn-issuer", sub="syn-"+kind.lower(), aud=PROFILES[kind][1],
                    iat=NOW-5, nbf=NOW-5, exp=NOW+120, jti="syn-credential", gen=1)
        data.update(claims)
        return jwt.encode(data, self.private[signing or kind], algorithm="RS256",
                          headers={"typ": PROFILES[kind][0], "kid": "syn-kid"})

    def denied(self, token=None, kind="HUMAN"):
        if token is None:
            token = self.token()
        with self.assertRaisesRegex(CredentialRejected, "^synthetic credential rejected$") as ctx:
            self.resolver.resolve(token, kind)
        self.assertIsNone(ctx.exception.__cause__)

    def update(self, bindings):
        self.now += 1
        self.directory = DirectorySnapshot(self.now, self.now+59, tuple(bindings))

    def test_01_three_kinds_no_authority(self):
        for kind, principal in (("HUMAN","syn-p1"),("AGENT","syn-p3"),("SERVICE","syn-p4")):
            with self.subTest(kind=kind):
                result = self.resolver.resolve(self.token(kind), kind)
                self.assertIsInstance(result, ResolvedPrincipal)
                self.assertEqual(result.principal_id, principal)
                self.assertEqual(result.kind, kind)
                self.assertEqual(result.expires_at, NOW+59)
                self.assertFalse(hasattr(result, "permissions"))
                self.assertFalse(hasattr(result, "organization_id"))
                self.assertFalse(hasattr(result, "allows"))
                self.assertNotIn(principal, repr(result))

    def test_02_same_subject_distinct_issuers(self):
        a = self.resolver.resolve(self.token(), "HUMAN")
        b = self.resolver.resolve(self.token(signing="OTHER", iss="syn-other"), "HUMAN")
        self.assertEqual(a.subject, b.subject)
        self.assertNotEqual(a.principal_id, b.principal_id)
        self.denied(self.token(iss="syn-other"))

    def test_03_unbound_identity_denied(self):
        self.denied(self.token(sub="syn-unknown"))

    def test_04_no_forged_candidate_input(self):
        forged = IdentityCandidate("syn-issuer","syn-human","HUMAN","syn-forged",1,NOW+120)
        self.denied(forged)
        self.denied(ResolvedPrincipal("syn-p1","syn-issuer","syn-human","HUMAN",NOW+120))

    def test_05_no_type_elevation(self):
        self.denied(self.token("AGENT"), "HUMAN")
        self.denied(self.token("SERVICE"), "HUMAN")
        self.denied(self.token("AGENT", sub="syn-human"), "AGENT")

    def test_06_token_claims_cannot_choose_principal(self):
        for claims in (dict(principal_id="syn-p2"), dict(tenant="syn-tenant"),
                       dict(permissions=["task:approve"]), dict(role="HUMAN")):
            self.denied(self.token(**claims))

    def test_07_expired_or_inactive_binding(self):
        self.directory = replace(self.directory, bindings=(
            replace(self.bindings[0], active=False),)+self.bindings[1:])
        self.denied()
        self.directory = replace(self.directory, bindings=(
            replace(self.bindings[0], expires_at=NOW),)+self.bindings[1:])
        # New resolver isolates the expiry case from same-version rejection.
        self.resolver = SyntheticPrincipalResolver(lambda:self.keys_snapshot,
                                                    lambda:self.directory,lambda:self.now)
        self.denied()

    def test_08_duplicate_identity_denied(self):
        self.directory = replace(self.directory, bindings=self.bindings+(self.bindings[0],))
        self.denied()

    def test_09_duplicate_principal_denied(self):
        self.directory = replace(self.directory, bindings=self.bindings+(
            PrincipalBinding("syn-issuer","syn-new","syn-p1","HUMAN",True,NOW+120),))
        self.denied()

    def test_10_wrong_type_in_directory(self):
        self.directory = replace(self.directory, bindings=(
            replace(self.bindings[0],kind="AGENT"),)+self.bindings[1:])
        self.denied()

    def test_11_fresh_verification_after_revocation(self):
        token = self.token()
        self.resolver.resolve(token, "HUMAN")
        self.now += 1
        self.keys_snapshot = replace(self.keys_snapshot, observed_at=self.now,
                                     revoked=frozenset({("syn-issuer","syn-credential")}))
        self.denied(token)

    def test_12_stale_future_or_unavailable_directory(self):
        original = self.directory
        for value in (None, replace(original, observed_at=NOW+1),
                      replace(original, valid_until=NOW),
                      replace(original, valid_until=NOW+100)):
            self.directory = value
            self.denied()
        def unavailable():
            raise OSError("sensitive internal detail")
        self.resolver = SyntheticPrincipalResolver(lambda:self.keys_snapshot,
                                                    unavailable,lambda:self.now)
        self.denied()

    def test_13_no_snapshot_rollback_or_same_version_mutation(self):
        original = self.directory
        self.resolver.resolve(self.token(),"HUMAN")
        self.directory = replace(original,valid_until=NOW+58)
        self.denied()
        self.update(self.bindings)
        self.resolver.resolve(self.token(),"HUMAN")
        self.directory = original
        self.denied()

    def test_14_identity_rebinding_denied(self):
        self.resolver.resolve(self.token(),"HUMAN")
        self.update((replace(self.bindings[0],principal_id="syn-new"),)+self.bindings[1:])
        self.denied()

    def test_15_removed_mapping_cannot_return_or_be_reassigned(self):
        self.resolver.resolve(self.token(),"HUMAN")
        self.update(self.bindings[1:])
        self.denied()
        self.update(self.bindings)
        self.denied()
        self.update(self.bindings[1:]+(
            PrincipalBinding("syn-issuer","syn-new","syn-p1","HUMAN",True,NOW+120),))
        self.denied(self.token(sub="syn-new"))

    def test_16_inactive_mapping_cannot_reactivate(self):
        self.resolver.resolve(self.token(),"HUMAN")
        self.update((replace(self.bindings[0],active=False),)+self.bindings[1:])
        self.denied()
        self.update(self.bindings)
        self.denied()

    def test_17_exchange_is_not_principal_identity(self):
        self.denied(self.token("EXCHANGE"),"HUMAN")
        self.denied(self.token("EXCHANGE"),"EXCHANGE")

    def test_18_lab_guard_on_every_call(self):
        with patch.dict(os.environ,{"RW_SI_ENABLE_G04_A1_LAB":"0"}):
            self.denied()
            with self.assertRaises(CredentialRejected):
                SyntheticPrincipalResolver(lambda:self.keys_snapshot,
                                           lambda:self.directory,lambda:self.now)

    def test_19_concurrent_reads_stable(self):
        token = self.token()
        with ThreadPoolExecutor(max_workers=8) as pool:
            ids = list(pool.map(lambda _: self.resolver.resolve(token,"HUMAN").principal_id,
                                range(16)))
        self.assertEqual(set(ids),{"syn-p1"})

    def test_20_slow_directory_expires_before_return(self):
        def slow():
            self.now = NOW+59
            return self.directory
        self.resolver = SyntheticPrincipalResolver(lambda:self.keys_snapshot, slow, lambda:self.now)
        self.denied()

    def test_21_malformed_directory(self):
        original = self.directory
        for binding in (replace(self.bindings[0],principal_id="real-id"),
                        replace(self.bindings[0],active=1),
                        replace(self.bindings[0],expires_at=True),
                        replace(self.bindings[0],kind="ADMIN")):
            self.directory = replace(original,bindings=(binding,)+self.bindings[1:])
            self.denied()


if __name__ == "__main__":
    unittest.main()
