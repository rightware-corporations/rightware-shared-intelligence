"""E1.1B synthetic dataset quality checks; not production or model validation.

The held-out eval queries intentionally have NO gold labels. Publishing the
queries and documents is NOT the same as an independently blinded benchmark.
Rule-authored labels in train/dev are provisional until human adjudication.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata

from rightware_si.e1_01_data_eval import DataIntegrityError, _required, _when
from rightware_si.experimental_engine_e0 import Query, Source, decide

SPLITS=("train","dev","eval")
ROLES={"current","adjacent","expired","unverified","foreign","other_project","distractor"}
COUNTS={"train":(4,28,16,16),"dev":(2,14,8,8),"eval":(2,14,8,0)}


def _load_lines(blob: bytes) -> list[dict]:
    _required(blob.endswith(b"\n"),"file must end with newline")
    result=[json.loads(line) for line in blob.decode("utf-8").splitlines()]
    _required(all(isinstance(row,dict) for row in result),"JSONL objects only")
    return result


def read_data(root: Path) -> tuple[list[dict],list[dict],list[dict],dict]:
    raw={}
    for filename in ("documents","queries","labels_provisional"):
        raw[filename]=(Path(root)/(filename+".jsonl")).read_bytes()
    manifest=json.loads((Path(root)/"manifest.json").read_text(encoding="utf-8"))
    _required(manifest.get("schema_version")=="rightware-e1b-quality-v1"
              and manifest.get("review_status")=="INDEPENDENT_REVIEW_REQUIRED"
              and manifest.get("independent_human_annotators")==0
              and manifest.get("real_data") is False
              and manifest.get("trained_ranker") is False,"bad research provenance")
    for name,blob in raw.items():
        _required(sha256(blob).hexdigest()==manifest["sha256"][name],
                  name+" SHA-256 mismatch")
    documents,queries,labels=(_load_lines(raw[name]) for name in
                               ("documents","queries","labels_provisional"))
    return documents,queries,labels,manifest


def _shingles(s: str, n: int = 4) -> set[tuple[str,...]]:
    word=unicodedata.normalize("NFKD",s.casefold())
    word="".join(ch for ch in word if not unicodedata.combining(ch))
    toks=re.findall(r"[a-z0-9]+",word)
    return {tuple(toks[i:i+n]) for i in range(max(0,len(toks)-n+1))}


def similarity(a: str,b: str) -> float:
    left,right=_shingles(a),_shingles(b)
    return len(left & right)/len(left | right) if left or right else 0.0


def audit(documents: list[dict],queries: list[dict],labels: list[dict],
          manifest: dict) -> dict:
    _required(len(documents)==56 and len(queries)==32 and len(labels)==24,
              "unexpected fixture size")
    _required(manifest["counts"]["documents"]==56 and
              manifest["counts"]["queries"]==32 and
              manifest["counts"]["labels_provisional"]==24,
              "manifest counts mismatch")
    sources={d["source_id"]:d for d in documents}
    qmap={q["query_id"]:q for q in queries}
    _required(len(sources)==len(documents) and len(qmap)==len(queries),
              "duplicate source or query ids")
    groups={s:set() for s in SPLITS}
    by_group={}
    for d in documents:
        split=d["split"]
        _required(split in SPLITS and d["role"] in ROLES
                  and d["source_id"].startswith("syn-e1b-")
                  and d["group_id"].startswith("syn-e1b-group-")
                  and d["organization"].startswith("syn-")
                  and d["project"].startswith("syn-")
                  and isinstance(d["text"],str) and len(d["text"])>=60,
                  "invalid synthetic document")
        _required(_when(d["valid_from"])<=_when(d["observed_at"]),
                  "source observed before validity start")
        if d["valid_until"] is not None:
            _required(_when(d["valid_until"])>_when(d["valid_from"]),
                      "invalid validity range")
        groups[split].add(d["group_id"])
        by_group.setdefault(d["group_id"],[]).append(d)
    _required(all(not groups[a]&groups[b]
                  for i,a in enumerate(SPLITS) for b in SPLITS[i+1:]),
              "group leakage across splits")
    for group,ds in by_group.items():
        _required(len(ds)==7 and {d["role"] for d in ds}==ROLES,
                  "incomplete group source roles")
        key=next(d for d in ds if d["role"]=="current")
        for d in ds:
            _required(d["split"]==key["split"],"cross split source family")
            if d["role"]=="foreign":
                _required(d["organization"]!=key["organization"]
                          and d["project"]==key["project"],
                          "invalid foreign control")
            elif d["role"]=="other_project":
                _required(d["organization"]==key["organization"]
                          and d["project"]!=key["project"],
                          "invalid other-project control")
            else:
                _required(d["organization"]==key["organization"]
                          and d["project"]==key["project"],
                          "authorized source wrong scope")
            if d["role"]=="unverified":
                _required(d["authority"]=="UNVERIFIED_CLAIM",
                          "unverified document promoted")
            else:
                _required(d["authority"]=="OFFICIAL_SOURCE",
                          "unexpected asserted authority")
        _required(key["role"]=="current","missing current source")
    for split,(ng,nd,nq,nl) in COUNTS.items():
        _required(len(groups[split])==ng and
                  sum(d["split"]==split for d in documents)==nd and
                  sum(q["split"]==split for q in queries)==nq and
                  sum(l["split"]==split for l in labels)==nl,
                  "split counters mismatch")
        # Several independent topics must genuinely COMPETE in one project.
        authorized={d["project"] for d in documents
                    if d["split"]==split and d["role"]=="current"}
        _required(len(authorized)==1 and len(groups[split])>1,
                  "per-family project partition makes retrieval too easy")
    for q in queries:
        _required(q["split"] in SPLITS and q["group_id"] in groups[q["split"]]
                  and q["query_id"].startswith("syn-e1b-")
                  and q["organization"].startswith("syn-")
                  and q["project"].startswith("syn-")
                  and q["language"] in ("PT","EN")
                  and isinstance(q["text"],str) and len(q["text"])>=30,
                  "invalid query scope or shape")
        ds=by_group[q["group_id"]]
        current=next(d for d in ds if d["role"]=="current")
        _required(q["organization"]==current["organization"]
                  and q["project"]==current["project"],"query mismatched project")
        _when(q["as_of"])
    labelmap={}
    for label in labels:
        qid=label["query_id"]
        _required(qid in qmap and qid not in labelmap,"duplicate/orphan label")
        q=qmap[qid]
        _required(q["split"] in ("train","dev") and
                  q["split"]==label["split"] and
                  label["review_state"]=="RULE_PROVISIONAL_NOT_HUMAN",
                  "eval label leak or forged review")
        grades=label["relevance"]
        _required(isinstance(grades,dict),"bad relevance mapping")
        for sid,score in grades.items():
            _required(sid in sources and type(score) is int and 1<=score<=3,
                      "invalid graded label")
            d=sources[sid]
            _required(d["group_id"]==q["group_id"] and
                      d["split"]==q["split"] and
                      d["organization"]==q["organization"] and
                      d["project"]==q["project"] and
                      d["role"] in ("current","adjacent") and
                      d["authority"]=="OFFICIAL_SOURCE",
                      "gold points to forbidden, stale or unverified item")
            at=_when(q["as_of"])
            _required(_when(d["observed_at"])<=at and
                      _when(d["valid_from"])<=at and
                      (d["valid_until"] is None or at<_when(d["valid_until"])),
                      "gold source not valid at query time")
        labelmap[qid]=label
    _required(set(labelmap)=={q["query_id"] for q in queries
                               if q["split"]!="eval"},
              "train/dev query missing provisional label")
    _required(all(q["query_id"] not in labelmap for q in queries
                  if q["split"]=="eval"),"eval gold must not exist")
    for name,items in (("source",documents),("query",queries)):
        for i,row in enumerate(items):
            for other in items[i+1:]:
                if row["split"]!=other["split"]:
                    _required(similarity(row["text"],other["text"])<0.65,
                              name+" near-duplicate leakage across splits")
    return {"documents":len(documents),"queries":len(queries),
            "labels_provisional":len(labels),"eval_unlabeled":8,
            "families":len(by_group),"independent_reviewers":0,
            "cross_split_near_duplicate_threshold":0.65,
            "shared_projects_per_split":True,
            "status":"ENGINEERING_PASS_SCIENCE_REVIEW_REQUIRED"}


def e0_development_diagnostic(documents: list[dict], queries: list[dict],
                               labels: list[dict]) -> dict:
    """No evaluation of unlabeled eval split, no threshold fitting."""
    lmap={row["query_id"]:row for row in labels}
    result={}
    for split in ("train","dev"):
        ds=[Source(d["source_id"],d["organization"],d["project"],d["text"],
                   d["authority"],_when(d["observed_at"]),_when(d["valid_from"]),
                   _when(d["valid_until"]) if d["valid_until"] else None)
            for d in documents if d["split"]==split]
        approved={d.source_id:d for d in ds}
        npositive=negative=hit=emitted=0
        for row in queries:
            if row["split"]!=split: continue
            label=lmap[row["query_id"]]
            decision=decide(Query(row["organization"],row["project"],row["text"],
                                  _when(row["as_of"]),limit=5),ds,trusted_scope=True)
            ids=[c.source_id for c in decision.candidates]
            _required(all(sid in approved
                          and approved[sid].organization==row["organization"]
                          and approved[sid].project==row["project"] for sid in ids),
                      "foreign source leaked by E0 evaluator")
            if label["relevance"]:
                npositive+=1
                hit+=int(bool(ids) and ids[0] in label["relevance"])
            else:
                negative+=1
                emitted+=int(decision.status=="EVIDENCE_CANDIDATE")
        result[split]={"positive_queries":npositive,"negative_queries":negative,
                       "hit_at_1_count":hit,"negative_candidate_emissions":emitted,
                       "foreign_ids":0}
    return result
