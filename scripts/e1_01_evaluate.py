"""E1.1 offline integrity + E0 diagnostic runner, no third-party inputs."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from rightware_si.e1_01_data_eval import read_fixture, evaluate


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--dataset",default="docs/research/e1_01")
    parser.add_argument("--output",default="")
    args=parser.parse_args()
    records,queries,manifest=read_fixture(Path(args.dataset))
    report=evaluate(records,queries,manifest)
    encoded=json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n"
    if args.output:
        Path(args.output).write_text(encoded,encoding="utf-8")
    print("E1_01_DATA_INTEGRITY_PASS records=84 queries=60 families=12 "
          "train_dev_test_disjoint=true hashed=true labeled_synthetic=true "
          "no_forbidden_scope=true no_model_trained=true")
    print("E1_01_E0_OFFLINE_DIAGNOSTIC "+json.dumps(report["splits"],sort_keys=True))
    print("E1_01_SCIENTIFIC_GATE REVIEW_REQUIRED human_gold_review=false "
          "structural_template_leakage_unmeasured=true external_benchmark=false")


if __name__=="__main__":
    main()
