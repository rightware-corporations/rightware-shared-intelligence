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
MAX_KEY_HISTORY = 256
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
        self._key_history = {}
        self._fingerprint_history = {}

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
        # Remember retired keys across intermediate snapshots. A removed
        # issuer/kid/profile is never reintroduced in this verifier instance;
        # rotation after removal must use a fresh kid and fresh public key.
        active_before = ({k for k, _, _ in self._last_snapshot[2]}
                         if self._last_snapshot is not None else set())
        history = dict(self._key_history)
        used = dict(self._fingerprint_history)
        for lookup, key in index.items():
            fingerprint = key.public_key.public_numbers()
            prior = history.get(lookup)
            if prior is not None:
                generation, previous_key = prior
                if (lookup not in active_before or key.generation < generation
                        or (key.generation == generation and fingerprint != previous_key)):
                    reject()
            if fingerprint in used and (used[fingerprint] != lookup
                                        or (prior is not None and fingerprint != prior[1])):
                reject()
            history[lookup] = (key.generation, fingerprint)
            used[fingerprint] = lookup
        if len(history) > MAX_KEY_HISTORY or len(used) > MAX_KEY_HISTORY:
            reject()
        self._key_history = history
        self._fingerprint_history = used
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


# G04-A1-LAB-02: identity resolution only. This is an in-memory experiment,
# not a production directory, account link, membership grant or permission.
MAX_BINDINGS = 256


@dataclass(frozen=True)
class PrincipalBinding:
    issuer: str = field(repr=False)
    subject: str = field(repr=False)
    principal_id: str = field(repr=False)
    kind: str
    active: bool
    expires_at: int


@dataclass(frozen=True)
class DirectorySnapshot:
    observed_at: int
    valid_until: int
    bindings: tuple[PrincipalBinding, ...] = field(repr=False)


@dataclass(frozen=True)
class ResolvedPrincipal:
    principal_id: str = field(repr=False)
    issuer: str = field(repr=False)
    subject: str = field(repr=False)
    kind: str
    expires_at: int
    status: str = field(default="RESOLVED_SYNTHETIC_PRINCIPAL", init=False)


class SyntheticPrincipalResolver:
    """Bind a fresh verified token to one explicit synthetic principal.

    Construct the verifier here; do not accept caller-supplied IdentityCandidate
    objects. Both callbacks and the clock are trusted laboratory dependencies,
    not request data. This result conveys no membership or authorization.
    """
    def __init__(self, key_snapshot: Callable[[], Snapshot],
                 directory_snapshot: Callable[[], DirectorySnapshot],
                 clock: Callable[[], int]):
        if not enabled() or not callable(directory_snapshot) or not callable(clock):
            reject()
        self._verifier = SyntheticVerifier(key_snapshot, clock)
        self._directory = directory_snapshot
        self._clock = clock
        self._lock = Lock()
        self._last_now = None
        self._last_directory = None
        self._history = {}
        self._principal_history = {}

    def resolve(self, token: str, expected_kind: str) -> ResolvedPrincipal:
        try:
            with self._lock:
                return self._resolve(token, expected_kind)
        except Exception:
            pass
        raise CredentialRejected("synthetic credential rejected") from None

    def _resolve(self, token, expected_kind):
        if not enabled() or type(expected_kind) is not str or expected_kind not in KINDS:
            reject()
        # Obtain a freshly verified result, never trust cached candidate objects.
        identity = self._verifier.verify(token, expected_kind)
        now = self._clock()
        if (not number(now) or now >= identity.expires_at
                or (self._last_now is not None and now < self._last_now)):
            reject()
        self._last_now = now
        snapshot = self._directory()
        if (type(snapshot) is not DirectorySnapshot
                or not number(snapshot.observed_at) or not number(snapshot.valid_until)
                or not (snapshot.observed_at <= now < snapshot.valid_until
                        <= snapshot.observed_at + MAX_SNAPSHOT_AGE)
                or type(snapshot.bindings) is not tuple
                or len(snapshot.bindings) > MAX_BINDINGS):
            reject()
        index, ids = {}, set()
        for binding in snapshot.bindings:
            if (type(binding) is not PrincipalBinding
                    or not all(ident(v) for v in
                               (binding.issuer, binding.subject, binding.principal_id))
                    or binding.kind not in KINDS
                    or type(binding.active) is not bool
                    or not number(binding.expires_at)):
                reject()
            key = (binding.issuer, binding.subject)
            if key in index or binding.principal_id in ids:
                reject()
            index[key] = binding
            ids.add(binding.principal_id)

        # Same-version mutation or snapshot rollback is not permitted.
        stamp = (snapshot.observed_at, snapshot.valid_until,
                 frozenset(index.items()))
        previous = self._last_directory
        if previous is not None:
            if stamp[0] < previous[0] or (stamp[0] == previous[0] and stamp != previous):
                reject()
        previous_active = ({k for k, _ in previous[2]} if previous else set())
        history = dict(self._history)
        principal_history = dict(self._principal_history)
        for key, binding in index.items():
            old = history.get(key)
            if old is not None:
                if (key not in previous_active or old.principal_id != binding.principal_id
                        or old.kind != binding.kind or (not old.active and binding.active)):
                    reject()
            owner = principal_history.get(binding.principal_id)
            if owner is not None and owner != key:
                reject()
            history[key] = binding
            principal_history[binding.principal_id] = key
        if len(history) > MAX_BINDINGS or len(principal_history) > MAX_BINDINGS:
            reject()
        self._history = history
        self._principal_history = principal_history
        self._last_directory = stamp

        match = index.get((identity.issuer, identity.subject))
        if match is None or match.kind != identity.kind or not match.active:
            reject()
        # A second clock check covers slow directory callbacks; it does not
        # claim atomic cross-store revocation or distributed consistency.
        end = self._clock()
        if (not number(end) or end < now or end >= snapshot.valid_until
                or end >= match.expires_at or end >= identity.expires_at):
            reject()
        self._last_now = end
        return ResolvedPrincipal(match.principal_id, identity.issuer,
                                 identity.subject, identity.kind,
                                 min(identity.expires_at, match.expires_at,
                                     snapshot.valid_until))
