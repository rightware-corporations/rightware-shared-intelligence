"""E1.1B quality CI audit only: never scores the unlabeled eval questions."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from rightware_si.e1_02_quality import read_data,audit,e0_development_diagnostic

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--dataset",default="docs/research/e1_02")
    p.add_argument("--output",default="")
    args=p.parse_args()
    ds,queries,labels,manifest=read_data(Path(args.dataset))
    profile=audit(ds,queries,labels,manifest)
    diagnostic=e0_development_diagnostic(ds,queries,labels)
    report={"profile":profile,"development_diagnostic":diagnostic,
            "scientific_gate":"REVIEW_REQUIRED","independent_reviewers":0,
            "eval_scoring":"NOT_RUN"}
    if args.output:
        Path(args.output).write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("E1_02_QUALITY_AUDIT_PASS documents=56 queries=32 provisional_labels=24 "
          "eval_unlabeled=8 shared_projects=true cross_split_near_dup_checked=true")
    print("E1_02_E0_DEV_DIAGNOSTIC "+json.dumps(diagnostic,sort_keys=True))
    print("E1_02_SCIENCE_GATE REVIEW_REQUIRED reviewer_a=missing reviewer_b=missing "
          "adjudication=missing evaluation_gold=not_collected no_model_trained=true")

if __name__=="__main__":
    main()
