"""E1.1C/03B: reviewer-specific opaque IDs and PRIVATE reconciliation.

Original corpus and provisional labels are PUBLIC. Opaque aliases mitigate
ordinal ID leakage but cannot establish a truly blind scientific benchmark.
Never give PRIVATE_ALIAS_MAP.json to a reviewer or commit local files.
"""
from __future__ import annotations
from copy import deepcopy
import json
import secrets
import random
from rightware_si.e1_01_data_eval import _required
from rightware_si.e1_03_review_protocol import (
    _digest, _cohen, _quadratic_weighted, validate_submission,
)

SCHEMA="rightware-e1-03b-opaque-map-v1"


def issue_packets(original: dict) -> tuple[dict, dict]:
    _required(len(original["documents"])==42 and len(original["queries"])==24,
              "unexpected raw research packet")
    all_aliases=set()
    packets={}
    custody={"schema":SCHEMA,"base_sha256":_digest(original),
             "dataset_id":original["dataset_id"],"slots":{},
             "status":"PRIVATE_MAPPING_NEVER_SHARE"}
    rng=random.SystemRandom()
    for slot in ("A","B"):
        def aliases(items,field,prefix):
            mapping={}
            for row in items:
                while True:
                    alias=prefix+"-"+secrets.token_urlsafe(20)
                    if alias not in all_aliases:
                        all_aliases.add(alias)
                        break
                mapping[alias]=row[field]
            return mapping
        dm=aliases(original["documents"],"source_id","DOC")
        qm=aliases(original["queries"],"query_id","QUE")
        reverse_d={v:k for k,v in dm.items()}
        reverse_q={v:k for k,v in qm.items()}
        documents=[{**d,"source_id":reverse_d[d["source_id"]]}
                   for d in original["documents"]]
        queries=[{**q,"query_id":reverse_q[q["query_id"]]}
                 for q in original["queries"]]
        rng.shuffle(documents)
        rng.shuffle(queries)
        packet={
            "schema_version":original["schema_version"],
            "dataset_id":original["dataset_id"],
            "data_sha256":deepcopy(original["data_sha256"]),
            "review_slot":slot,
            "status":"REVIEWER_OPAQUE_TRAIN_DEV_NO_GOLD",
            "documents":documents,"queries":queries
        }
        packets[slot]=packet
        custody["slots"][slot]={
            "packet_sha256":_digest(packet),
            "sources":dm,"queries":qm
        }
    audit_packets(original,packets,custody)
    return packets,custody


def audit_packets(original:dict,packets:dict,custody:dict)->None:
    _required(custody.get("schema")==SCHEMA
              and custody.get("base_sha256")==_digest(original)
              and set(packets)=={"A","B"}
              and set(custody.get("slots",{}))=={"A","B"},
              "custody manifest mismatched")
    originals={"sources":{d["source_id"]:d for d in original["documents"]},
               "queries":{q["query_id"]:q for q in original["queries"]}}
    orig_ids=set(originals["sources"])|set(originals["queries"])
    seen=set()
    for slot in ("A","B"):
        pack=packets[slot]
        mapping=custody["slots"][slot]
        source_index={d["source_id"]:d for d in pack["documents"]}
        query_index={q["query_id"]:q for q in pack["queries"]}
        _required(pack.get("review_slot")==slot
                  and pack.get("status")=="REVIEWER_OPAQUE_TRAIN_DEV_NO_GOLD"
                  and pack.get("data_sha256")==original["data_sha256"]
                  and mapping["packet_sha256"]==_digest(pack),
                  "reviewer packet hash/scope mismatched")
        for key,fields,id_key,prefix,index in (
            ("sources","documents","source_id","DOC",source_index),
            ("queries","queries","query_id","QUE",query_index)
        ):
            alias_map=mapping[key]
            _required(len(alias_map)==len(originals[key])
                      and set(alias_map)==set(index)
                      and set(alias_map.values())==set(originals[key]),
                      "incomplete or duplicated aliases")
            for alias,old in alias_map.items():
                _required(alias.startswith(prefix+"-") and len(alias)>20
                          and alias not in seen and alias not in orig_ids,
                          "predictable/colliding alias")
                seen.add(alias)
                expected={k:v for k,v in originals[key][old].items()
                          if k!=id_key}
                found={k:v for k,v in index[alias].items() if k!=id_key}
                _required(found==expected,"aliased metadata changed")
        _required(len(source_index)==42 and len(query_index)==24,
                  "review packet count changed")
        _required(all(d["split"]!="eval" for d in pack["documents"])
                  and all(q["split"]!="eval" for q in pack["queries"]),
                  "evaluation split leaked")
        encoded=json.dumps(pack,ensure_ascii=False)
        _required(not any(sid in encoded for sid in orig_ids),
                  "raw ID exposed to reviewer")
        _required(not any(k in encoded for k in
             ('"role"','"group_id"','"relevance"',
              "labels_provisional","RULE_PROVISIONAL_NOT_HUMAN",
              '"sources"','"queries_to_original"')),
              "label/crosswalk metadata in reviewer packet")


def compare_aliased(a:dict,b:dict,packets:dict,custody:dict,raw:dict)->dict:
    audit_packets(raw,packets,custody)
    va=validate_submission(a,packets["A"])
    vb=validate_submission(b,packets["B"])
    _required(va["pseudonym"]!=vb["pseudonym"],
              "same reviewer pseudonym")
    def canonical(validation,slot):
        sm=custody["slots"][slot]["sources"]
        qm=custody["slots"][slot]["queries"]
        return {qm[alias]:{"class":record["class"],
                 "grades":{sm[sid]:v for sid,v in record["grades"].items()}}
                for alias,record in validation["judgments"].items()}
    x,y=canonical(va,"A"),canonical(vb,"B")
    _required(set(x)==set(y) and len(x)==24,"reviewed different question sets")
    classes_a,classes_b,grades_a,grades_b=[],[],[],[]
    disagreements=0
    for qid in sorted(x):
        p,r=x[qid],y[qid]
        _required(set(p["grades"])==set(r["grades"]),
                  "document coverage differs")
        classes_a.append(p["class"])
        classes_b.append(r["class"])
        disagreements+=int(p!=r)
        for sid in sorted(p["grades"]):
            grades_a.append(p["grades"][sid])
            grades_b.append(r["grades"][sid])
    _required(len(grades_a)==560,"incomplete review ratings")
    return {
        "status":"SCHEMA_VERIFIED_HUMAN_INDEPENDENCE_NOT_AUTHENTICATED",
        "reviewers_claimed":2,"query_count":24,
        "ratings_per_reviewer":560,
        "class_agreement":round(sum(a==b for a,b in zip(classes_a,classes_b))/24,6),
        "class_cohen_kappa":_cohen(classes_a,classes_b),
        "rating_agreement":round(sum(a==b for a,b in zip(grades_a,grades_b))/560,6),
        "rating_weighted_kappa":_quadratic_weighted(grades_a,grades_b),
        "disagreement_count":disagreements,
        "independence_authenticated":False,"adjudicated_gold":False,
        "science_gate":"REVIEW_REQUIRED"
    }
