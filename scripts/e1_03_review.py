"""E1.1C offline synthetic-only review packet and agreement CLI.

No reviewer submissions exist in CI. Nothing here adjudicates gold.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rightware_si.e1_03_review_protocol import (
    assert_private_path, blank_submission, compare_submissions,
    make_packet, private_load_json, private_write_json,
)

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "docs" / "research" / "e1_02"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("self-check", "export", "compare"),
                        default="self-check")
    parser.add_argument("--output-dir", default=".runtime/e1_03")
    parser.add_argument("--a", default="")
    parser.add_argument("--b", default="")
    args = parser.parse_args()
    packet = make_packet(DATASET)
    template = blank_submission(packet)

    if args.mode == "self-check":
        assert not any(q["split"] == "eval" for q in packet["queries"])
        assert not any(k in str(packet) for k in (
            "RULE_PROVISIONAL_NOT_HUMAN", "source_relevance",
            "expected_mode", "labels_provisional"
        ))
        print("E1_03_REVIEW_CONTRACT_PASS source_docs=42 questions=24 "
              "provisional_gold_exported=false eval_exported=false "
              "real_reviewers=0 adjudicated_gold=false")
        print("E1_03_SCIENCE_GATE REVIEW_REQUIRED independent_human_reviews=0 "
              "evaluator_gold=uncollected no_model_trained=true")
        return

    out = assert_private_path(ROOT / args.output_dir, ROOT)
    if args.mode == "export":
        private_write_json(out / "review_packet.json", packet, ROOT)
        for slot in ("A", "B"):
            private_write_json(out / ("review_" + slot + "_BLANK.json"),
                               template, ROOT)
        print("E1_03_REVIEW_PACKETS_EXPORTED train_dev_only=true "
              "slots=A,B no_human_review_implied=true "
              "directory=.runtime/e1_03")
        return

    if not args.a or not args.b:
        parser.error("--mode compare requires --a and --b inside .runtime/")
    a = private_load_json(ROOT / args.a, ROOT)
    b = private_load_json(ROOT / args.b, ROOT)
    report = compare_submissions(a, b, packet)
    private_write_json(out / "agreement_PRIVATE.json", report, ROOT)
    print("E1_03_SUBMISSION_SCHEMA_CHECK_PASS "
          "identity_independence_not_cryptographically_proven=true "
          "adjudicated_gold=false science_gate=REVIEW_REQUIRED")


if __name__ == "__main__":
    main()
