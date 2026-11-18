"""RIGHTWARE Intelligence Engine E0: a strictly offline, research-only reference.

This is not a trained RIGHTWARE ML model, a trusted authorization gateway,
a source truth oracle, or an end-user answer generator. All metadata is
synthetic and supplied by the experiment fixture; it must NEVER be accepted
from untrusted HTTP, MCP or Mem0 callers. Do not import into production paths.

Purpose: independently own and instrument candidate retrieval, time/scope
filtering, provenance decisions and abstention before scientific evaluation.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from math import log
import re
import unicodedata
from typing import Sequence

AUTHORITATIVE = frozenset({"VERIFIED_LEDGER", "OFFICIAL_SOURCE"})
KINDS = AUTHORITATIVE | {"OBSERVATION", "UNVERIFIED_CLAIM"}
STATES = frozenset({"DENY", "ABSTAIN", "CONFLICT", "EVIDENCE_CANDIDATE"})


def _terms(value: str) -> list[str]:
    plain = unicodedata.normalize("NFKD", value.casefold())
    plain = "".join(ch for ch in plain if not unicodedata.combining(ch))
    return re.findall(r"[a-z0-9]+", plain)


def _aware(value: datetime) -> bool:
    return isinstance(value, datetime) and value.tzinfo is not None and value.utcoffset() is not None


@dataclass(frozen=True, slots=True)
class Source:
    source_id: str
    organization: str
    project: str
    text: str
    authority: str
    observed_at: datetime
    valid_from: datetime
    valid_until: datetime | None = None
    claim_key: str | None = None
    claim_value: str | None = None


@dataclass(frozen=True, slots=True)
class Query:
    organization: str
    project: str
    text: str
    as_of: datetime
    limit: int = 5


@dataclass(frozen=True, slots=True)
class Candidate:
    source_id: str
    authority: str
    lexical_score: float


@dataclass(frozen=True, slots=True)
class RetrievalDecision:
    status: str
    candidates: tuple[Candidate, ...]
    reason: str
    # Does not certify that any proposed natural-language answer is correct.


def decide(query: Query, records: Sequence[Source],
           *, trusted_scope: bool) -> RetrievalDecision:
    """Fail closed; search only the pre-authorized synthetic corpus.

    The caller in this offline experiment owns the trusted_scope assertion.
    A real gateway must *derive* authorization cryptographically and from DB;
    this function must not be published as an endpoint.
    """
    if not trusted_scope:
        return RetrievalDecision("DENY", (), "NO_AUTHORIZATION")

    if (not isinstance(query, Query) or not _aware(query.as_of)
            or not isinstance(query.organization, str)
            or not isinstance(query.project, str)
            or not query.organization.startswith("syn-")
            or not query.project.startswith("syn-")
            or not isinstance(query.text, str)
            or not query.text.strip()
            or not isinstance(query.limit, int)
            or isinstance(query.limit, bool)
            or not 1 <= query.limit <= 10):
        return RetrievalDecision("ABSTAIN", (), "INVALID_SYNTHETIC_QUERY")

    # Scope BEFORE ranking. Foreign source IDs and scores never enter output.
    scoped = [
        r for r in records
        if (isinstance(r, Source)
            and r.organization == query.organization
            and r.project == query.project)
    ]
    if (any(not r.source_id.startswith("syn-") or not r.text.strip()
            or r.authority not in KINDS or not _aware(r.observed_at)
            or not _aware(r.valid_from)
            or (r.valid_until is not None and not _aware(r.valid_until))
            or (r.claim_key is None) != (r.claim_value is None)
            for r in scoped)
            or len({r.source_id for r in scoped}) != len(scoped)):
        return RetrievalDecision("ABSTAIN", (), "INVALID_SYNTHETIC_CORPUS")

    eligible = [
        r for r in scoped
        if r.observed_at <= query.as_of
        and r.valid_from <= query.as_of
        and (r.valid_until is None or query.as_of < r.valid_until)
    ]
    if not eligible:
        return RetrievalDecision("ABSTAIN", (), "NO_VALID_EVIDENCE")

    qterms = set(_terms(query.text))
    if not qterms:
        return RetrievalDecision("ABSTAIN", (), "NO_SEARCH_TOKENS")
    counts = [Counter(_terms(r.text)) for r in eligible]
    lengths = [sum(v.values()) for v in counts]
    average_length = sum(lengths) / len(lengths)
    if average_length == 0:
        return RetrievalDecision("ABSTAIN", (), "NO_SEARCHABLE_TEXT")

    # BM25 is an openly known research baseline, NOT claimed as proprietary.
    # The engine's differentiation hypothesis is the governed evidence layer.
    scores: list[tuple[Source, float]] = []
    for row, frequencies, length in zip(eligible, counts, lengths):
        score = 0.0
        for token in qterms:
            tf = frequencies[token]
            if tf == 0:
                continue
            df = sum(1 for other in counts if other[token] > 0)
            idf = log(1.0 + (len(eligible) - df + 0.5) / (df + 0.5))
            score += idf * (tf * 2.2) / (
                tf + 1.2 * (1 - 0.75 + 0.75 * length / average_length))
        if score > 0:
            scores.append((row, score))

    scores.sort(key=lambda item: (-item[1], item[0].source_id))
    candidates = tuple(Candidate(r.source_id, r.authority, round(score, 8))
                       for r, score in scores[:query.limit])
    if not candidates:
        return RetrievalDecision("ABSTAIN", (), "NO_RELEVANT_EVIDENCE")

    trusted = [(r, score) for r, score in scores if r.authority in AUTHORITATIVE]
    if not trusted:
        return RetrievalDecision("ABSTAIN", candidates, "UNVERIFIED_ONLY")

    # Contradictory authoritative claims anywhere in the relevant scoped set
    # must not be concealed by top-k clipping.
    by_claim: dict[str, set[str]] = {}
    for r, _ in trusted:
        if r.claim_key is not None:
            by_claim.setdefault(r.claim_key, set()).add(r.claim_value or "")
    if any(len(values) > 1 for values in by_claim.values()):
        return RetrievalDecision("CONFLICT", candidates, "AUTHORITATIVE_CONFLICT")

    # EVIDENCE_CANDIDATE is NOT an answer and never advances task to DONE.
    return RetrievalDecision("EVIDENCE_CANDIDATE", candidates,
                             "RETRIEVAL_NOT_FACT_VERIFICATION")
