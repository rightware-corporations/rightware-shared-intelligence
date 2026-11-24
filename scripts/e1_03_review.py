"""RIGHTWARE E1.1C/03B: opaque reviewer packets, private local crosswalk."""
from __future__ import annotations
import argparse
from pathlib import Path
from rightware_si.e1_03_review_protocol import (
    assert_private_path, blank_submission, make_packet,
    private_load_json, private_write_json,
)
from rightware_si.e1_03_blind_alias import (
    issue_packets, audit_packets, compare_aliased,
)

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"docs"/"research"/"e1_02"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("self-check","export","compare"),
                   default="self-check")
    p.add_argument("--output-dir",default=".runtime/e1_03")
    p.add_argument("--a",default="")
    p.add_argument("--b",default="")
    args=p.parse_args()
    raw=make_packet(DATA)

    if args.mode=="self-check":
        packets,private=issue_packets(raw)
        audit_packets(raw,packets,private)
        print("E1_03B_OPAQUE_IDS_PASS reviewer_A_B_independent=true "
              "original_ids_exposed=false crosswalk_private=true "
              "eval_gold_exported=false actual_reviewers=0")
        print("E1_03_SCIENCE_GATE REVIEW_REQUIRED "
              "public_corpus_is_not_blind=true human_reviews=0")
        return

    out=assert_private_path(ROOT/args.output_dir,ROOT)
    if args.mode=="export":
        packets,private=issue_packets(raw)
        for slot in ("A","B"):
            private_write_json(out/("reviewer_"+slot)/"packet.json",
                               packets[slot],ROOT)
            private_write_json(out/("reviewer_"+slot)/"BLANK.json",
                               blank_submission(packets[slot]),ROOT)
        private_write_json(out/"CUSTODY_ONLY"/"PRIVATE_ALIAS_MAP.json",
                           private,ROOT)
        print("E1_03B_EXPORT_READY share_reviewer_folders_separately=true "
              "NEVER_share_CUSTODY_ONLY=true science_gate=REVIEW_REQUIRED")
        return

    if not args.a or not args.b:
        p.error("--mode compare requires --a and --b under ignored .runtime/")
    packets={slot:private_load_json(
        out/("reviewer_"+slot)/"packet.json",ROOT)
        for slot in ("A","B")}
    private=private_load_json(
        out/"CUSTODY_ONLY"/"PRIVATE_ALIAS_MAP.json",ROOT)
    a=private_load_json(ROOT/args.a,ROOT)
    b=private_load_json(ROOT/args.b,ROOT)
    summary=compare_aliased(a,b,packets,private,raw)
    private_write_json(out/"CUSTODY_ONLY"/"agreement_PRIVATE.json",summary,ROOT)
    print("E1_03B_SCHEMA_COMPARISON_PASS human_independence_unverified=true "
          "adjudicated_gold=false")


if __name__=="__main__":
    main()
