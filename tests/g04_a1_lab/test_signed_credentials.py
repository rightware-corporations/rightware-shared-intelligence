"""Real RSA cryptographic tests with ephemeral keys; no real identity or network."""
import ast
import base64
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import json
import os
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

import jwt
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes

from rightware_si.g04_a1_lab import (
    CredentialRejected, IdentityCandidate, PROFILES, Snapshot,
    SyntheticVerifier, TrustKey,
)

ROOT = Path(__file__).resolve().parents[2]
NOW = 2000000000
ENV = {"RW_SI_ENVIRONMENT": "lab", "RW_SI_ENABLE_G04_A1_LAB": "1"}


def b64(value):
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


class G04A1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private = {p: rsa.generate_private_key(public_exponent=65537, key_size=2048)
                       for p in (*PROFILES, "OTHER")}
        cls.keys = tuple(TrustKey("syn-issuer", "syn-kid", p, cls.private[p].public_key())
                         for p in PROFILES) + (
            TrustKey("syn-other", "syn-kid", "HUMAN", cls.private["OTHER"].public_key()),)

    def setUp(self):
        self.env = patch.dict(os.environ, ENV)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.now = NOW
        self.snapshot = Snapshot(NOW - 1, NOW + 59, self.keys)
        self.verifier = SyntheticVerifier(lambda: self.snapshot, lambda: self.now)

    def claims(self, profile="HUMAN", **changes):
        values = dict(iss="syn-issuer", sub="syn-subject", aud=PROFILES[profile][1],
                      iat=NOW-5, nbf=NOW-5, exp=NOW+120, jti="syn-id", gen=1)
        values.update(changes)
        return values

    def token(self, profile="HUMAN", key=None, header=None, **changes):
        headers = dict(typ=PROFILES[profile][0], kid="syn-kid")
        headers.update(header or {})
        return jwt.encode(self.claims(profile, **changes), key or self.private[profile],
                          algorithm="RS256", headers=headers)

    def denied(self, token, kind="HUMAN", verifier=None):
        with self.assertRaisesRegex(CredentialRejected, "^synthetic credential rejected$") as ctx:
            (verifier or self.verifier).verify(token, kind)
        self.assertIsNone(ctx.exception.__cause__)

    def test_01_valid_three_profiles(self):
        for profile in ("HUMAN", "AGENT", "SERVICE"):
            with self.subTest(profile=profile):
                result = self.verifier.verify(self.token(profile), profile)
                self.assertIsInstance(result, IdentityCandidate)
                self.assertEqual(result.kind, profile)
                self.assertFalse(hasattr(result, "allows"))
                self.assertFalse(hasattr(result, "permissions"))
                self.assertNotIn("syn-subject", repr(result))

    def test_02_wrong_expected_profile(self):
        for profile in ("AGENT", "SERVICE"):
            self.denied(self.token(profile))

    def test_03_tampered_payload_and_signature(self):
        parts = self.token().split(".")
        for index in (1, 2):
            changed = parts[:]
            if index == 1:
                changed[1] = b64(json.dumps(self.claims(sub="syn-attacker")).encode())
            else:
                changed[2] = ("A" if parts[2][0] != "A" else "B") + parts[2][1:]
            self.denied(".".join(changed))

    def test_04_wrong_signing_key(self):
        self.denied(self.token(key=self.private["OTHER"]))

    def test_05_none_and_hmac_confusion(self):
        h = {"typ": PROFILES["HUMAN"][0], "kid": "syn-kid"}
        self.denied(jwt.encode(self.claims(), "", algorithm="none", headers=h))
        self.denied(jwt.encode(self.claims(), b"x"*32, algorithm="HS256", headers=h))

    def test_06_unknown_issuer_and_kid(self):
        self.denied(self.token(iss="syn-unknown"))
        self.denied(self.token(header={"kid": "syn-unknown"}))

    def test_07_cross_issuer_same_subject_kid(self):
        first = self.verifier.verify(self.token(), "HUMAN")
        second = self.verifier.verify(self.token(key=self.private["OTHER"], iss="syn-other"), "HUMAN")
        self.assertEqual(first.subject, second.subject)
        self.assertNotEqual(first.issuer, second.issuer)
        self.denied(self.token(iss="syn-other"))

    def test_08_wrong_audience_or_type(self):
        for value in ("syn-other", [PROFILES["HUMAN"][1]], None):
            self.denied(self.token(aud=value))
        self.denied(self.token(header={"typ": "JWT"}))

    def test_09_missing_claims(self):
        for name in self.claims():
            claims = self.claims()
            del claims[name]
            token = jwt.encode(claims, self.private["HUMAN"], algorithm="RS256",
                               headers={"typ": PROFILES["HUMAN"][0], "kid": "syn-kid"})
            self.denied(token)

    def test_10_temporal_boundaries(self):
        for kwargs in (dict(exp=NOW), dict(nbf=NOW+1), dict(iat=NOW+1),
                       dict(exp=NOW+301), dict(nbf=NOW-6),
                       dict(iat=True), dict(exp=str(NOW+120)), dict(nbf=1.5)):
            with self.subTest(kwargs=kwargs):
                self.denied(self.token(**kwargs))

    def test_11_invalid_identifiers_and_generation(self):
        for kwargs in (dict(sub="real-user"), dict(sub="syn-"), dict(jti=""),
                       dict(gen=True), dict(gen=0), dict(gen=2), dict(iss=["syn-issuer"])):
            self.denied(self.token(**kwargs))

    def test_12_extra_privileged_claims(self):
        for kwargs in (dict(role="HUMAN"), dict(tenant="syn-tenant"), dict(scope="policy:approve"),
                       dict(project="syn-project"), dict(permissions=["DONE"])):
            self.denied(self.token(**kwargs))

    def test_13_untrusted_headers_never_fetch(self):
        with patch.object(socket, "create_connection", side_effect=AssertionError("network")) as net:
            for extra in ({"jku": "https://invalid.example/key"}, {"x5u": "https://invalid.example"},
                          {"jwk": {}}, {"crit": ["unknown"]}, {"cty": "JWT"}):
                self.denied(self.token(header=extra))
            self.verifier.verify(self.token(), "HUMAN")
            net.assert_not_called()

    def test_14_duplicate_json_members(self):
        header = b64(b'{"alg":"RS256","alg":"RS256","typ":"rw-syn-human-id+jwt","kid":"syn-kid"}')
        normal = self.token().split(".")
        payload = json.dumps(self.claims()).rstrip("}") + ',"sub":"syn-subject"}'
        for h, p in ((header, normal[1]), (normal[0], b64(payload.encode()))):
            data = (h+"."+p).encode("ascii")
            sig = self.private["HUMAN"].sign(data, padding.PKCS1v15(), hashes.SHA256())
            self.denied(h+"."+p+"."+b64(sig))

    def test_15_malformed_and_oversized_tokens(self):
        for value in (None, "", "a.b", "a.b.c.d", "a.=.c", "é.b.c", "x"*8193,
                      self.token()+"=", "e30.e30.A"):
            self.denied(value)

    def test_16_revocation_and_reusable_token(self):
        token = self.token()
        self.verifier.verify(token, "HUMAN")
        self.verifier.verify(token, "HUMAN")
        self.snapshot = replace(self.snapshot, observed_at=NOW,
                                revoked=frozenset({("syn-issuer", "syn-id")}))
        self.denied(token)
        self.verifier.verify(self.token(jti="syn-next"), "HUMAN")

    def test_17_generation_rotation(self):
        token = self.token()
        self.verifier.verify(token, "HUMAN")
        new = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.snapshot = replace(self.snapshot, observed_at=NOW,
                                keys=(replace(self.keys[0], public_key=new.public_key(), generation=2),)
                                + self.keys[1:])
        self.denied(token)
        self.verifier.verify(self.token(key=new, gen=2), "HUMAN")
        self.denied(self.token(key=new, gen=1))

    def test_18_stale_future_and_unavailable_snapshot(self):
        for snapshot in (replace(self.snapshot, observed_at=NOW-100, valid_until=NOW-40),
                         replace(self.snapshot, observed_at=NOW+1),
                         replace(self.snapshot, valid_until=NOW),
                         None):
            self.snapshot = snapshot
            self.denied(self.token())
            self.snapshot = Snapshot(NOW-1, NOW+59, self.keys)
        def unavailable():
            raise OSError("secret dependency detail")
        self.denied(self.token(), verifier=SyntheticVerifier(unavailable, lambda: NOW))

    def test_19_snapshot_rollback_and_revocation_rollback(self):
        first = self.snapshot
        self.verifier.verify(self.token(), "HUMAN")
        self.snapshot = replace(first, observed_at=NOW,
                                revoked=frozenset({("syn-issuer", "syn-id")}))
        self.denied(self.token())
        self.snapshot = first
        self.denied(self.token(jti="syn-other-id"))
        self.now += 1
        self.snapshot = replace(first, observed_at=self.now, valid_until=NOW+59)
        self.denied(self.token(jti="syn-other-id"))

    def test_20_ambiguous_and_shared_keys(self):
        for keys in (self.keys+(self.keys[0],),
                     self.keys+(TrustKey("syn-alt", "syn-alt", "HUMAN", self.keys[0].public_key),)):
            self.snapshot = replace(self.snapshot, keys=keys)
            self.denied(self.token())

    def test_21_weak_key_rejected(self):
        weak = rsa.generate_private_key(public_exponent=65537, key_size=1024)
        self.snapshot = replace(self.snapshot, keys=(replace(self.keys[0], public_key=weak.public_key()),)
                                +self.keys[1:])
        self.denied(self.token())

    def test_22_exchange_one_time_and_type_separation(self):
        receipt = self.token("EXCHANGE")
        self.denied(receipt)
        with self.assertRaises(CredentialRejected):
            self.verifier.consume_exchange(self.token())
        self.verifier.consume_exchange(receipt)
        with self.assertRaises(CredentialRejected):
            self.verifier.consume_exchange(receipt)

    def test_23_concurrent_exchange_only_one(self):
        receipt = self.token("EXCHANGE")
        def consume(_):
            try:
                self.verifier.consume_exchange(receipt)
                return True
            except CredentialRejected:
                return False
        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(consume, range(16))), 1)

    def test_24_lab_flag_required_at_init_and_use(self):
        with patch.dict(os.environ, {"RW_SI_ENABLE_G04_A1_LAB": "0"}):
            with self.assertRaises(CredentialRejected):
                SyntheticVerifier(lambda: self.snapshot, lambda: self.now)
            self.denied(self.token())

    def test_25_clock_rollback(self):
        self.verifier.verify(self.token(), "HUMAN")
        self.now -= 1
        self.denied(self.token())

    def test_26_no_runtime_wiring(self):
        for path in (ROOT/"backend/rightware_si").rglob("*.py"):
            if path.name == "g04_a1_lab.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertFalse(any("g04_a1_lab" in alias.name for alias in node.names))
                if isinstance(node, ast.ImportFrom):
                    self.assertNotIn("g04_a1_lab", node.module or "")
                    self.assertFalse(any("g04_a1_lab" in alias.name for alias in node.names))


if __name__ == "__main__":
    unittest.main()
