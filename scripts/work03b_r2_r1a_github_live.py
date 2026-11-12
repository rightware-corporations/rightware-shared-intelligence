"""Live, bounded GitHub workflow-run read-only smoke, no task status mutation.

Uses a previously *observed completed* synthetic CI run in this repository.
One real HTTPS response is checked by the actual R2-R1A adapter. The four
positive/negative checks must not be described as enterprise acceptance,
cryptographic attestations, proof of all criteria, or EV-08..EV-16.
"""
from __future__ import annotations

from dataclasses import replace
import os

from rightware_si.evidence_github import (
    CHECKED_PASS, CHECKED_FAIL, GithubRunPolicy, verify_github_run,
)

# These identifiers were observed from GitHub Actions run 43202560651 at
# R2-R0 checkpoint; never derive these from a model's prose or screenshots.
BASE = GithubRunPolicy(
    owner="rightware-corporations",
    repository="rightware-shared-intelligence",
    repository_id=1452533938,
    workflow_id=415280241,
    head_sha="0c63b2f2d3d4cf00926752ab2c58d42ccbd64901",
    run_id=43202560651,
    run_attempt=1,
    event="push",
)


def validate_live() -> None:
    token = os.environ.get("GITHUB_TOKEN") or None
    decisions = (
        ("EV-01", BASE, CHECKED_PASS, "EXPECTED_WORKFLOW_RUN_SUCCEEDED"),
        ("EV-02", replace(BASE, head_sha="f"*40), CHECKED_FAIL, "WRONG_SHA"),
        ("EV-03", replace(BASE, repository_id=BASE.repository_id+1),
         CHECKED_FAIL, "WRONG_REPOSITORY"),
        ("EV-04", replace(BASE, workflow_id=BASE.workflow_id+1),
         CHECKED_FAIL, "WRONG_WORKFLOW"),
    )
    # Live provider API on a fixed endpoint, exactly one request per policy.
    # Enforce each check rather than counting tests from an input JSON fixture.
    for identifier, policy, expected, reason in decisions:
        result = verify_github_run(policy, token=token)
        if result.decision != expected or result.reason != reason:
            raise AssertionError(
                f"{identifier} provider check did not match expected live outcome "
                f"(reason={result.reason}, decision={result.decision})"
            )
        if result.task_approved or result.state_authoritative:
            raise AssertionError("GitHub run evidence cannot approve task")
        print(f"R2_R1A_{identifier}_LIVE_PASS "
              f"observed={result.decision} task_approved=false "
              f"provider=github_workflow_run")
    print("WORK03B_R2_R1A_GITHUB_LIVE_PASS "
          "run_id=43202560651 repo_id=1452533938 "
          "workflow_id=415280241 attempt=1 "
          "provider_live=true task_done=false "
          "evidence_records_persisted=false review_not_implemented=true")


if __name__ == "__main__":
    try:
        validate_live()
    except (AssertionError, ValueError) as exc:
        # Never log tokens, API response bodies, or arbitrary untrusted text.
        print("WORK03B_R2_R1A_GITHUB_LIVE_FAIL "
              f"kind={type(exc).__name__}")
        raise SystemExit(1) from None
