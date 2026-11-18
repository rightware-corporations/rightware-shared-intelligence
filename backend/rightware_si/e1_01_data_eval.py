"""RIGHTWARE E1.1: independent *synthetic* evaluation data audit.

This is research scaffolding, not a production data source or a tested ML
ranker. The gold labels in the repo are synthetic/rule-derived, NOT blind.
Never mix this dataset with the sealed SI-RD challenge or train on its key.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from hashlib import sha256
import json
from math import log2
from pathlib import Path
from statistics import mean
from typing import Any

from rightware_si.experimental_engine_e0 import Query, Source, decide

SPLITS = ("train", "dev", "test")
CATEGORIES = {"ANSWERABLE", "UNANSWERABLE", "FORBIDDEN_SCOPE"}
AUTHORITIES = {"VERIFIED_LEDGER", "OFFICIAL_SOURCE", "OBSERVATION", "UNVERIFIED_CLAIM"}
ROLES = {"primary","secondary","historical","unverified","distractor","foreign","other-project"}
EXPECTED_COUNTS = {
    "train": {"families": 6, "documents": 42, "queries": 30},
    "dev": {"families": 3, "documents": 21, "queries": 15},
    "test": {"families": 3, "documents": 21, "queries": 15},
}


class DataIntegrityError(ValueError):
    pass


def _required(condition: bool, explanation: str) -> None:
    if not condition:
        raise DataIntegrityError(explanation)


def _when(value: str) -> datetime:
    _required(isinstance(value, str), "datetime must be string")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DataIntegrityError("invalid timestamp") from exc
    _required(result.tzinfo is not None and result.utcoffset() is not None,
              "timezone must be explicit")
    return result


def _jsonl(data: bytes) -> list[dict[str, Any]]:
    _required(data.endswith(b"\n"), "jsonl must end in newline")
    rows = []
    for line in data.decode("utf-8").splitlines():
        _required(bool(line.strip()), "empty JSONL line")
        row = json.loads(line)
        _required(isinstance(row, dict), "expected JSON object")
        rows.append(row)
    return rows


def read_fixture(root: Path) -> tuple[list[dict], list[dict], dict]:
    root = Path(root)
    raw_documents = (root / "documents.jsonl").read_bytes()
    raw_queries = (root / "queries.jsonl").read_bytes()
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    _required(manifest.get("schema_version") == "rightware-e1-01-v1",
              "unexpected dataset schema")
    _required(manifest.get("review_status") == "REVIEW_REQUIRED"
              and manifest.get("real_data") is False
              and manifest.get("ranker_trained") is False,
              "research-only classification missing")
    for label, data in (("documents", raw_documents), ("queries", raw_queries)):
        _required(sha256(data).hexdigest() == manifest["sha256"][label],
                  label + " content SHA-256 mismatch")
    documents, queries = _jsonl(raw_documents), _jsonl(raw_queries)
    audit_records(documents, queries, manifest)
    return documents, queries, manifest


def audit_records(documents: list[dict], queries: list[dict], manifest: dict) -> None:
    _required(len(documents) == 84 and len(queries) == 60, "record counts changed")
    doc_ids = [d.get("source_id") for d in documents]
    query_ids = [q.get("query_id") for q in queries]
    _required(len(doc_ids) == len(set(doc_ids)), "source id collision")
    _required(len(query_ids) == len(set(query_ids)), "query id collision")
    doc_index = {d["source_id"]: d for d in documents}
    groups: dict[str, set[str]] = {split: set() for split in SPLITS}
    projects: dict[str, set[str]] = {split: set() for split in SPLITS}
    text_hash_by_split: dict[str, set[str]] = {split: set() for split in SPLITS}
    query_hash_by_split: dict[str, set[str]] = {split: set() for split in SPLITS}
    language_by_group: dict[str, str] = {}

    for d in documents:
        split = d.get("split")
        _required(split in SPLITS, "invalid document split")
        _required(d.get("group_id", "").startswith("syn-e1-family-")
                  and d.get("source_id", "").startswith("syn-e1-")
                  and d.get("project", "").startswith("syn-")
                  and d.get("organization", "").startswith("syn-"),
                  "non-synthetic document identifier")
        _required(d.get("role") in ROLES and d.get("authority") in AUTHORITIES,
                  "unknown role or authority")
        _required(isinstance(d.get("text"), str) and len(d["text"]) >= 25,
                  "invalid source text")
        observed, start = _when(d["observed_at"]), _when(d["valid_from"])
        end = _when(d["valid_until"]) if d.get("valid_until") else None
        _required(end is None or end > start, "invalid source validity")
        _required(observed >= start, "observed before valid-from")
        groups[split].add(d["group_id"])
        projects[split].add(d["project"])
        signature = sha256(d["text"].casefold().encode("utf-8")).hexdigest()
        _required(signature not in text_hash_by_split[split],
                  "duplicate source text in same split")
        text_hash_by_split[split].add(signature)

    _required(all(not groups[a] & groups[b] and
                  not projects[a] & projects[b] and
                  not text_hash_by_split[a] & text_hash_by_split[b]
                  for i, a in enumerate(SPLITS) for b in SPLITS[i+1:]),
              "train/dev/test group/project/exact text leakage")

    by_group: dict[str, list[dict]] = {}
    for d in documents:
        by_group.setdefault(d["group_id"], []).append(d)
    for group, docs in by_group.items():
        _required(len(docs) == 7 and {d["role"] for d in docs} == ROLES,
                  "each family must have 7 distinct source roles")
        main = next(d for d in docs if d["role"] == "primary")
        _required(all(d["split"] == main["split"] for d in docs),
                  "family split crossed")
        for d in docs:
            if d["role"] == "foreign":
                _required(d["organization"] != main["organization"]
                          and d["project"] == main["project"],
                          "foreign distractor not actually foreign")
            elif d["role"] == "other-project":
                _required(d["organization"] == main["organization"]
                          and d["project"] != main["project"],
                          "different-project distractor invalid")
            else:
                _required(d["organization"] == main["organization"]
                          and d["project"] == main["project"],
                          "authorized family source mis-scoped")

    kind_by_split = {s: Counter() for s in SPLITS}
    languages = Counter()
    for q in queries:
        split,group = q.get("split"),q.get("group_id")
        _required(split in SPLITS and group in groups[split],
                  "query group missing or split leakage")
        docs = by_group[group]
        main = next(d for d in docs if d["role"] == "primary")
        _required(q.get("organization") == main["organization"]
                  and q.get("project") == main["project"],
                  "query organization/project mismatch")
        _required(q.get("language") in ("PT", "EN")
                  and q.get("kind") in CATEGORIES
                  and q.get("expected_mode") in ("ABSTAIN", "EVIDENCE_CANDIDATE"),
                  "invalid query classification")
        _required(isinstance(q.get("text"), str) and len(q["text"]) >= 20,
                  "invalid query text")
        _when(q["as_of"])
        signature = sha256(q["text"].casefold().encode("utf-8")).hexdigest()
        _required(signature not in query_hash_by_split[split],
                  "duplicated query in split")
        query_hash_by_split[split].add(signature)
        _required(group not in language_by_group
                  or language_by_group[group] == q["language"],
                  "language mismatch inside group")
        language_by_group[group] = q["language"]
        grades = q.get("relevance")
        _required(isinstance(grades, dict), "relevance must be JSON mapping")
        if q["kind"] == "ANSWERABLE":
            _required(bool(grades) and q["expected_mode"] == "EVIDENCE_CANDIDATE",
                      "missing positive grade")
        else:
            _required(not grades and q["expected_mode"] == "ABSTAIN",
                      "negative query gold must be empty")
        for source_id, grade in grades.items():
            _required(source_id in doc_index and type(grade) is int
                      and 1 <= grade <= 3, "invalid gold source or label")
            doc = doc_index[source_id]
            _required(doc["split"] == split and doc["group_id"] == group
                      and doc["organization"] == q["organization"]
                      and doc["project"] == q["project"]
                      and doc["authority"] == "OFFICIAL_SOURCE",
                      "gold points outside authorized official scope")
            t = _when(q["as_of"])
            _required(_when(doc["observed_at"]) <= t
                      and _when(doc["valid_from"]) <= t
                      and (not doc["valid_until"]
                           or t < _when(doc["valid_until"])),
                      "gold source is stale/not-yet-published")
        kind_by_split[split][q["kind"]] += 1

    _required(all(not query_hash_by_split[a] & query_hash_by_split[b]
                  for i,a in enumerate(SPLITS) for b in SPLITS[i+1:]),
              "duplicate query across train/dev/test")
    for split in SPLITS:
        expected = EXPECTED_COUNTS[split]
        _required(len(groups[split]) == expected["families"] and
                  sum(d["split"] == split for d in documents) == expected["documents"] and
                  sum(q["split"] == split for q in queries) == expected["queries"],
                  split + " wrong expected counts")
        _required(kind_by_split[split]["ANSWERABLE"] == expected["families"] * 3
                  and kind_by_split[split]["UNANSWERABLE"] == expected["families"]
                  and kind_by_split[split]["FORBIDDEN_SCOPE"] == expected["families"],
                  "missing negative or positive strata")
    for group, language in language_by_group.items():
        languages[language] += 1
    _required(languages == {"PT": 6, "EN": 6},
              "PT/EN group balance unexpectedly changed")
    _required(manifest.get("counts") == {
        "documents":84,"queries":60,"families":12,
        "languages":{"PT":6,"EN":6},"splits":EXPECTED_COUNTS
    }, "manifest count mismatch")


def _metrics(ranked_ids: list[str], relevance: dict[str, int]) -> dict[str, float]:
    """One query's standard retrieval measures, relevant iff grade > 0."""
    if not relevance:
        return {}
    first = next((rank for rank, source_id in enumerate(ranked_ids[:5], 1)
                  if relevance.get(source_id, 0) > 0), None)
    dcg = sum((2**relevance.get(source_id, 0) - 1) / log2(rank + 1)
              for rank, source_id in enumerate(ranked_ids[:5], 1))
    ideal = sum((2**grade-1)/log2(rank+1)
                for rank, grade in enumerate(sorted(relevance.values(), reverse=True)[:5], 1))
    return {
        "hit@1":float(first is not None and first <= 1),
        "hit@2":float(first is not None and first <= 2),
        "hit@5":float(first is not None and first <= 5),
        "mrr@5":(1/first if first is not None else 0.0),
        "ndcg@5":(dcg/ideal if ideal else 0.0)
    }


def evaluate(documents: list[dict], queries: list[dict], manifest: dict) -> dict:
    audit_records(documents, queries, manifest)
    result = {"dataset_id":manifest["dataset_id"],
              "data_sha256":manifest["sha256"].copy(),
              "classification":"SYNTHETIC_DIAGNOSTIC_NOT_MODEL_SCIENCE",
              "model":"E0_BM25_PUBLIC_BASELINE", "splits":{}}
    for split in SPLITS:
        sources = [d for d in documents if d["split"] == split]
        query_rows = [q for q in queries if q["split"] == split]
        source_ids = {d["source_id"] for d in sources}
        by_id = {d["source_id"]: d for d in sources}
        engine_sources = [Source(
            source_id=d["source_id"],organization=d["organization"],
            project=d["project"],text=d["text"],authority=d["authority"],
            observed_at=_when(d["observed_at"]),valid_from=_when(d["valid_from"]),
            valid_until=_when(d["valid_until"]) if d["valid_until"] else None
        ) for d in sources]
        retrieval = []
        negatives = 0
        emitted_on_negative = 0
        scoped_denials = 0
        for q in query_rows:
            r = decide(Query(q["organization"],q["project"],q["text"],
                             _when(q["as_of"]),limit=5),engine_sources,
                       trusted_scope=True)
            ids = [item.source_id for item in r.candidates]
            _required(len(ids) == len(set(ids)), "duplicate output IDs")
            _required(all(sid in source_ids and
                          by_id[sid]["organization"] == q["organization"] and
                          by_id[sid]["project"] == q["project"]
                          for sid in ids),
                      "CRITICAL: cross-scope returned source ID")
            if q["kind"] == "ANSWERABLE":
                retrieval.append(_metrics(ids,q["relevance"]))
            else:
                negatives += 1
                emitted_on_negative += int(r.status == "EVIDENCE_CANDIDATE")
            scoped_denials += len(ids)
        _required(bool(retrieval), "missing retrieval positives")
        result["splits"][split] = {
            "documents":len(sources),"queries":len(query_rows),
            "answerable":len(retrieval),"negative_queries":negatives,
            "negative_evidence_candidate_emissions":emitted_on_negative,
            "returned_scoped_ids":scoped_denials,
            "foreign_ids_returned":0,
            "retrieval":{metric:round(mean(row[metric] for row in retrieval),6)
                         for metric in ("hit@1","hit@2","hit@5","mrr@5","ndcg@5")}
        }
    return result
