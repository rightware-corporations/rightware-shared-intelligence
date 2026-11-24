"""G04-A1-LAB-01: offline synthetic credential verification, never authorization.

No IdP, network, database, real principals, runtime wiring or persistent keys.
The caller supplies trusted synthetic configuration, clock and snapshot, never
request claims. A verified candidate confers no permission or human assurance.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass, field
import json
import os
import re
from threading import Lock
from typing import Callable

import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

KINDS = ("HUMAN", "AGENT", "SERVICE")
PROFILES = {
    "HUMAN": ("rw-syn-human-id+jwt", "rw-syn-human"),
    "AGENT": ("rw-syn-agent-at+jwt", "rw-syn-agent"),
    "SERVICE": ("rw-syn-service-at+jwt", "rw-syn-service"),
    "EXCHANGE": ("rw-syn-exchange+jwt", "rw-syn-exchange"),
}
MAX_TOKEN = 8192
MAX_TTL = 300
MAX_SNAPSHOT_AGE = 60
MAX_REPLAY = 4096
IDENTIFIER = re.compile(r"syn-[A-Za-z0-9_-]{1,64}\Z", re.ASCII)
SEGMENT = re.compile(r"[A-Za-z0-9_-]+\Z", re.ASCII)
FIELDS = {"iss", "sub", "aud", "iat", "nbf", "exp", "jti", "gen"}
HEADERS = {"alg", "typ", "kid"}


class CredentialRejected(Exception):
    """Deliberately constant public error; no token, key or claims in message."""


def reject():
    raise CredentialRejected("synthetic credential rejected")


def enabled():
    return (os.environ.get("RW_SI_ENVIRONMENT") == "lab"
            and os.environ.get("RW_SI_ENABLE_G04_A1_LAB") == "1")


def ident(value):
    return type(value) is str and IDENTIFIER.fullmatch(value) is not None


def number(value):
    return type(value) is int and 0 <= value <= 2**53 - 1


def strict_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            reject()
        result[key] = value
    return result


def invalid_constant(_):
    reject()


def unpack(segment):
    if not SEGMENT.fullmatch(segment):
        reject()
    raw = base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4))
    if base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=") != segment:
        reject()
    return raw


def json_object(segment):
    value = json.loads(unpack(segment).decode("utf-8"),
                       object_pairs_hook=strict_pairs,
                       parse_constant=invalid_constant)
    if type(value) is not dict:
        reject()
    return value


@dataclass(frozen=True)
class TrustKey:
    issuer: str
    kid: str
    profile: str
    public_key: RSAPublicKey = field(repr=False)
    generation: int = 1


@dataclass(frozen=True)
class Snapshot:
    observed_at: int
    valid_until: int
    keys: tuple[TrustKey, ...] = field(repr=False)
    revoked: frozenset[tuple[str, str]] = field(default_factory=frozenset, repr=False)


@dataclass(frozen=True)
class IdentityCandidate:
    issuer: str = field(repr=False)
    subject: str = field(repr=False)
    kind: str
    credential_id: str = field(repr=False)
    generation: int
    expires_at: int
    # Never used as a capability. Constructible data, not an authority object.
    status: str = field(default="VERIFIED_SYNTHETIC_IDENTITY_CANDIDATE", init=False)


class SyntheticVerifier:
    """Single-instance, fail-closed laboratory verifier; not a session service.

    Snapshot callback is a trusted in-memory lab dependency. No remote discovery.
    Replay prevention applies only to EXCHANGE receipts, not reusable credentials.
    """
    def __init__(self, snapshot: Callable[[], Snapshot], clock: Callable[[], int]):
        if not enabled() or not callable(snapshot) or not callable(clock):
            reject()
        self._snapshot = snapshot
        self._clock = clock
        self._lock = Lock()
        self._consumed = {}
        self._last_now = None
        self._last_snapshot = None

    def verify(self, token: str, expected_kind: str) -> IdentityCandidate:
        if expected_kind not in KINDS:
            reject()
        return self._check(token, expected_kind)

    def consume_exchange(self, token: str) -> IdentityCandidate:
        return self._check(token, "EXCHANGE")

    def _check(self, token, profile):
        # Normalize all malformed input and dependency failures without exception
        # chaining or logging potentially sensitive token text.
        try:
            with self._lock:
                return self._locked(token, profile)
        except Exception:
            pass
        raise CredentialRejected("synthetic credential rejected") from None

    def _locked(self, token, profile):
        if not enabled() or type(token) is not str or len(token) > MAX_TOKEN:
            reject()
        if not token.isascii():
            reject()
        parts = token.split(".")
        if len(parts) != 3:
            reject()
        header, claims = json_object(parts[0]), json_object(parts[1])
        unpack(parts[2])
        typ, audience = PROFILES[profile]
        if (set(header) != HEADERS or header["alg"] != "RS256"
                or header["typ"] != typ or not ident(header["kid"])):
            reject()
        if (set(claims) != FIELDS or claims["aud"] != audience
                or not all(ident(claims[k]) for k in ("iss", "sub", "jti"))
                or not all(number(claims[k]) for k in ("iat", "nbf", "exp", "gen"))
                or claims["gen"] < 1):
            reject()

        now = self._clock()
        if not number(now) or (self._last_now is not None and now < self._last_now):
            reject()
        self._last_now = now
        if not (claims["iat"] <= claims["nbf"] <= now < claims["exp"]
                and 0 < claims["exp"] - claims["iat"] <= MAX_TTL):
            reject()

        snap = self._snapshot()
        if (type(snap) is not Snapshot or not number(snap.observed_at)
                or not number(snap.valid_until)
                or not (snap.observed_at <= now < snap.valid_until
                        <= snap.observed_at + MAX_SNAPSHOT_AGE)
                or type(snap.keys) is not tuple or not (1 <= len(snap.keys) <= 64)
                or type(snap.revoked) is not frozenset):
            reject()
        if any(type(pair) is not tuple or len(pair) != 2
               or not all(ident(v) for v in pair) for pair in snap.revoked):
            reject()

        index = {}
        fingerprints = set()
        for key in snap.keys:
            if (type(key) is not TrustKey or not ident(key.issuer)
                    or not ident(key.kid) or key.profile not in PROFILES
                    or not number(key.generation) or key.generation < 1
                    or not isinstance(key.public_key, RSAPublicKey)
                    or key.public_key.key_size < 2048):
                reject()
            lookup = (key.issuer, key.kid, key.profile)
            fingerprint = key.public_key.public_numbers()
            # One signing key per issuer/kid/profile. No shared trust roots.
            if lookup in index or fingerprint in fingerprints:
                reject()
            index[lookup] = key
            fingerprints.add(fingerprint)

        # Reject snapshot rollback and same-version changes. This is an in-memory
        # laboratory invariant, not a distributed revocation consistency proof.
        stamp = (snap.observed_at, snap.valid_until,
                 frozenset((k, v.generation, v.public_key.public_numbers())
                           for k, v in index.items()), snap.revoked)
        if self._last_snapshot is not None:
            previous = self._last_snapshot
            if stamp[0] < previous[0] or (stamp[0] == previous[0] and stamp != previous):
                reject()
            if not previous[3].issubset(snap.revoked):
                reject()
            old_keys = {k: (g, n) for k, g, n in previous[2]}
            for k, v in index.items():
                if k in old_keys:
                    g, n = old_keys[k]
                    if v.generation < g or (v.generation == g and v.public_key.public_numbers() != n):
                        reject()
        self._last_snapshot = stamp

        key = index.get((claims["iss"], header["kid"], profile))
        if key is None or key.generation != claims["gen"]:
            reject()
        if (claims["iss"], claims["jti"]) in snap.revoked:
            reject()

        # JOSE implementation performs actual RS256 signature verification.
        # Temporal checks above use the trusted synthetic clock, not wall time.
        # Fixed strict schema/audience and issuer are rechecked by the library.
        verified = jwt.decode(
            token, key.public_key, algorithms=["RS256"],
            audience=audience, issuer=key.issuer,
            options={"require": sorted(FIELDS), "strict_aud": True,
                     "verify_exp": False, "verify_nbf": False,
                     "verify_iat": False},
        )
        if verified != claims:
            reject()

        if profile == "EXCHANGE":
            self._consumed = {k: expiry for k, expiry in self._consumed.items()
                              if expiry > now}
            receipt = (claims["iss"], claims["jti"])
            if receipt in self._consumed or len(self._consumed) >= MAX_REPLAY:
                reject()
            self._consumed[receipt] = claims["exp"]

        return IdentityCandidate(claims["iss"], claims["sub"], profile,
                                 claims["jti"], claims["gen"], claims["exp"])
