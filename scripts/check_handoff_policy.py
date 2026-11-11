"""Check both durable handoff files were updated in every new develop commit.

Run at start of each develop CI. This verifies presence, not factual accuracy.
The reviewer must still validate provenance and test evidence.
"""
from __future__ import annotations

import os
import subprocess
import sys

REQUIRED = frozenset(("docs/HANDOFF.md", "docs/HANDOFF_MASTER.md"))


def missing_handoffs(paths):
    return REQUIRED.difference(set(paths))


def git(*args):
    return subprocess.check_output(("git", *args), text=True).strip()


def main():
    head = os.environ.get("GITHUB_SHA") or git("rev-parse", "HEAD")
    before = os.environ.get("GITHUB_EVENT_BEFORE", "")
    if not before or set(before) == {"0"}:
        before = head + "^"
    # A branch force-push/rebase can make the before SHA unreachable.
    # Reject rather than quietly claim complete audit coverage.
    try:
        git("merge-base", "--is-ancestor", before, head)
    except subprocess.CalledProcessError:
        print("HANDOFF_POLICY_FAIL: non-fast-forward or missing base; manual review required")
        return 1
    commits = git("rev-list", "--reverse", f"{before}..{head}").splitlines()
    if not commits:
        print("HANDOFF_POLICY_NO_NEW_COMMITS")
        return 0
    failures = []
    for commit in commits:
        changed = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()
        absent = missing_handoffs(changed)
        if absent:
            failures.append((commit[:12], sorted(absent)))
    if failures:
        for commit, absent in failures:
            print(f"HANDOFF_POLICY_FAIL commit={commit} missing={','.join(absent)}")
        return 1
    print(f"HANDOFF_POLICY_PASS audited_commits={len(commits)} both_files_updated=true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
