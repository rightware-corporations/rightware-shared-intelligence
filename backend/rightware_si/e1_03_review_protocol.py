"""E1.1C: offline review protocol for RIGHTWARE synthetic E1.1B fixtures.

These are tooling contracts, not human evaluations, identities, signatures,
adjudicated gold, production authorization, or an independently blind test.
Never import into HTTP/MCP/Mem0; actual submissions remain in .runtime/.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re

from rightware_si.e1_01_data_eval import DataIntegrityError, _required, _when
from rightware_si.e1_02_quality import read_data, audit

SCHEMA = "rightware-e1c-independent-review-v1"
CLASSES = {
    "ANSWERABLE", "UNANSWERABLE", "FORBIDDEN_SCOPE",
    "TEMPORAL_INVALID", "AUTHORITY_CONFLICT",
}
DOC_FIELDS = (
    "source_id", "split", "organization", "project", "authority",
    "observed_at", "valid_from", "valid_until", "text",
)
QUERY_FIELDS = (
    "query_id", "split", "language", "organization", "project", "as_of", "text",
)
SUBMISSION_FIELDS = {
    "schema_version", "dataset_id", "data_sha256", "packet_sha256",
    "reviewer_pseudonym", "independence_attested",
    "provisional_gold_not_consulted", "submitted_at", "review_status",
    "judgments",
}
JUDGMENT_FIELDS = {"query_id", "query_class", "ratings"}
RATING_FIELDS = {"source_id", "grade", "justification", "evidence_quote"}
PSEUDONYM = re.compile(r"RV-[A-Za-z0-9_-]{3,32}\Z")


def _digest(obj: dict) -> str:
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    return sha256(blob).hexdigest()


def make_packet(dataset: Path) -> dict:
    docs, queries, provisional, manifest = read_data(dataset)
    audit(docs, queries, provisional, manifest)
    # Deliberately do not read from provisional labels to choose candidates.
    # No eval document, eval query or gold class is exported.
    packet = {
        "schema_version": SCHEMA,
        "dataset_id": manifest["dataset_id"],
        "data_sha256": {key: manifest["sha256"][key] for key in ("documents", "queries")},
        "status": "REVIEW_PACKET_NO_GOLD_TRAIN_DEV_ONLY",
        "documents": [
            {k: d[k] for k in DOC_FIELDS}
            for d in docs if d["split"] in ("train", "dev")
        ],
        "queries": [
            {k: q[k] for k in QUERY_FIELDS}
            for q in queries if q["split"] in ("train", "dev")
        ],
    }
    _required(len(packet["documents"]) == 42
              and len(packet["queries"]) == 24,
              "unexpected non-eval review packet size")
    _required(not any(row["split"] == "eval"
                      for row in packet["documents"] + packet["queries"]),
              "eval leakage into reviewer packet")
    return packet


def blank_submission(packet: dict) -> dict:
    documents = packet["documents"]
    return {
        "schema_version": SCHEMA,
        "dataset_id": packet["dataset_id"],
        "data_sha256": packet["data_sha256"].copy(),
        "packet_sha256": _digest(packet),
        "reviewer_pseudonym": "",
        "independence_attested": False,
        "provisional_gold_not_consulted": False,
        "submitted_at": "",
        "review_status": "NOT_SUBMITTED",
        "judgments": [
            {
                "query_id": q["query_id"],
                "query_class": "UNSET",
                "ratings": [
                    {
                        "source_id": d["source_id"], "grade": None,
                        "justification": "", "evidence_quote": "",
                    }
                    for d in documents if d["split"] == q["split"]
                ],
            }
            for q in packet["queries"]
        ],
    }


def _eligible(q: dict, d: dict) -> bool:
    when = _when(q["as_of"])
    return (q["organization"] == d["organization"]
            and q["project"] == d["project"]
            and d["authority"] == "OFFICIAL_SOURCE"
            and _when(d["valid_from"]) <= when
            and _when(d["observed_at"]) <= when
            and (d["valid_until"] is None
                 or when < _when(d["valid_until"])))


def validate_submission(submission: dict, packet: dict) -> dict:
    _required(isinstance(submission, dict)
              and set(submission) == SUBMISSION_FIELDS,
              "submission schema/fields invalid")
    _required(submission["schema_version"] == SCHEMA
              and submission["dataset_id"] == packet["dataset_id"]
              and submission["data_sha256"] == packet["data_sha256"]
              and submission["packet_sha256"] == _digest(packet),
              "submission does not match pinned packet/dataset")
    reviewer = submission["reviewer_pseudonym"]
    _required(isinstance(reviewer, str)
              and PSEUDONYM.fullmatch(reviewer) is not None,
              "reviewer pseudonym must be RV-... (not a human identity proof)")
    _required(submission["independence_attested"] is True
              and submission["provisional_gold_not_consulted"] is True
              and submission["review_status"] == "SUBMITTED_INDEPENDENT",
              "incomplete or unsigned self-attestation")
    _when(submission["submitted_at"])
    judgments = submission["judgments"]
    _required(isinstance(judgments, list), "judgments must be array")
    expected_q = {q["query_id"]: q for q in packet["queries"]}
    _required(len(judgments) == len(expected_q)
              and all(isinstance(j, dict) for j in judgments),
              "review must cover exactly train/dev questions")
    by_q: dict[str, dict] = {}
    docs_by_split = {
        s: {d["source_id"]: d for d in packet["documents"]
            if d["split"] == s}
        for s in ("train", "dev")
    }
    for j in judgments:
        _required(set(j) == JUDGMENT_FIELDS, "judgment fields invalid")
        qid = j["query_id"]
        _required(isinstance(qid, str)
                  and qid in expected_q and qid not in by_q,
                  "missing, duplicate or injected eval query")
        q = expected_q[qid]
        _required(j["query_class"] in CLASSES,
                  "query class must be independently annotated")
        ratings = j["ratings"]
        _required(isinstance(ratings, list)
                  and len(ratings) == len(docs_by_split[q["split"]]),
                  "each query must rate every source in its split")
        rated: dict[str, int] = {}
        high_grades = 0
        for rating in ratings:
            _required(isinstance(rating, dict)
                      and set(rating) == RATING_FIELDS,
                      "invalid rating fields")
            sid = rating["source_id"]
            _required(isinstance(sid, str)
                      and sid in docs_by_split[q["split"]]
                      and sid not in rated,
                      "duplicate or out-of-split document")
            grade, explanation, quote = (
                rating["grade"], rating["justification"],
                rating["evidence_quote"],
            )
            _required(type(grade) is int and grade in (0, 1, 2, 3),
                      "invalid rating grade")
            _required(isinstance(explanation, str)
                      and len(explanation.strip()) >= 10
                      and isinstance(quote, str),
                      "review explanation/evidence missing")
            d = docs_by_split[q["split"]][sid]
            if grade:
                _required(_eligible(q, d),
                          "unauthorized/stale/unverified positive rating")
                _required(len(quote.strip()) >= 6 and quote in d["text"],
                          "positive grade must quote a literal evidence span")
            else:
                _required(not quote, "grade 0 cannot cite positive support")
            high_grades += int(grade >= 2)
            rated[sid] = grade
        _required(set(rated) == set(docs_by_split[q["split"]]),
                  "incomplete document coverage")
        if j["query_class"] == "ANSWERABLE":
            _required(high_grades > 0, "answerable without supporting evidence")
        elif j["query_class"] in (
            "UNANSWERABLE", "FORBIDDEN_SCOPE", "TEMPORAL_INVALID"
        ):
            _required(high_grades == 0,
                      "negative class contradicts supported positive grade")
        else:
            _required(high_grades >= 2,
                      "authority conflict needs at least two candidate sources")
        by_q[qid] = {
            "class": j["query_class"],
            "grades": rated,
        }
    _required(set(by_q) == set(expected_q), "query review coverage incomplete")
    return {"pseudonym": reviewer, "judgments": by_q,
            "query_count": len(by_q),
            "rating_count": sum(len(v["grades"]) for v in by_q.values())}


def _cohen(a: list[str], b: list[str]) -> float | None:
    _required(len(a) == len(b) and bool(a), "invalid agreement arrays")
    n = len(a)
    p0 = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    chance = sum(ca[k] * cb[k] for k in ca.keys() | cb.keys()) / (n * n)
    return None if 1 - chance < 1e-12 else round((p0 - chance) / (1 - chance), 6)


def _quadratic_weighted(a: list[int], b: list[int]) -> float | None:
    _required(len(a) == len(b) and bool(a), "invalid ordinal rating arrays")
    n = len(a)
    ca, cb = Counter(a), Counter(b)
    observed = sum((x - y) ** 2 for x, y in zip(a, b)) / n
    expected = sum(ca[i] * cb[j] * (i - j) ** 2
                   for i in range(4) for j in range(4)) / (n * n)
    return None if expected < 1e-12 else round(1 - observed / expected, 6)


def compare_submissions(a: dict, b: dict, packet: dict) -> dict:
    first = validate_submission(a, packet)
    second = validate_submission(b, packet)
    _required(first["pseudonym"] != second["pseudonym"],
              "two submissions cannot share one reviewer pseudonym")
    ids = sorted(first["judgments"])
    classes_a = [first["judgments"][qid]["class"] for qid in ids]
    classes_b = [second["judgments"][qid]["class"] for qid in ids]
    ratings_a, ratings_b = [], []
    disagreeing_queries = []
    for qid in ids:
        x, y = first["judgments"][qid], second["judgments"][qid]
        if x["class"] != y["class"] or x["grades"] != y["grades"]:
            disagreeing_queries.append(qid)
        for sid in sorted(x["grades"]):
            ratings_a.append(x["grades"][sid])
            ratings_b.append(y["grades"][sid])
    return {
        "status": "TECHNICAL_REVIEW_VALIDATION_ONLY_NOT_HUMAN_IDENTITY_PROOF",
        "dataset_id": packet["dataset_id"],
        "packet_sha256": _digest(packet),
        "review_count": 2,
        "query_count": len(ids),
        "ratings_per_reviewer": len(ratings_a),
        "class_exact_agreement": round(
            sum(a == b for a, b in zip(classes_a, classes_b)) / len(ids), 6),
        "class_cohen_kappa": _cohen(classes_a, classes_b),
        "rating_exact_agreement": round(
            sum(a == b for a, b in zip(ratings_a, ratings_b)) / len(ratings_a),
            6),
        "rating_quadratic_weighted_kappa": _quadratic_weighted(
            ratings_a, ratings_b),
        "disagreement_query_count": len(disagreeing_queries),
        "disagreement_query_ids": disagreeing_queries,
        "adjudicated_gold": False,
        "independence_authenticated": False,
        "science_gate": "REVIEW_REQUIRED",
    }


def assert_private_path(path: Path, repo_root: Path) -> Path:
    """Never export packets, identities, or reviewed labels to tracked Git."""
    resolved = Path(path).resolve()
    private_root = (Path(repo_root).resolve() / ".runtime").resolve()
    _required(resolved.is_relative_to(private_root)
              and resolved != private_root,
              "review output/input MUST be under ignored .runtime/")
    return resolved


def private_write_json(path: Path, payload: dict, repo_root: Path) -> None:
    approved = assert_private_path(path, repo_root)
    approved.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create: do not silently overwrite an existing reviewer record.
    with approved.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False,
                  sort_keys=True, indent=2)
        handle.write("\n")


def private_load_json(path: Path, repo_root: Path) -> dict:
    approved = assert_private_path(path, repo_root)
    _required(approved.stat().st_size < 5_000_000,
              "review file unexpectedly large")
    return json.loads(approved.read_text(encoding="utf-8"))
