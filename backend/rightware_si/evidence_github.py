"""R2-R1A EXPERIMENT: constrained GitHub Workflow Run evidence verifier.

Pure, bounded, non-authoritative check. Does not write SQL, expose REST/MCP
endpoints, modify tasks, fetch arbitrary URLs, run tools, check cryptographic
attestations or authorize DONE. Fake transports prove logic, not authenticity.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

import httpx

_SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_MAX_BODY = 32768
CHECKED_PASS = "CHECKED_PASS"
CHECKED_FAIL = "CHECKED_FAIL"
INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class GithubRunPolicy:
    owner: str
    repository: str
    repository_id: int
    workflow_id: int
    head_sha: str
    run_id: int
    run_attempt: int = 1
    event: str = "push"

    def __post_init__(self) -> None:
        for name, value in (("owner", self.owner), ("repository", self.repository)):
            if not isinstance(value, str) or not _SLUG.fullmatch(value):
                raise ValueError(f"unsafe GitHub {name}")
        for name in ("repository_id", "workflow_id", "run_id", "run_attempt"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"invalid {name}")
        if not isinstance(self.head_sha, str) or not _SHA40.fullmatch(self.head_sha):
            raise ValueError("full lowercase 40-hex commit SHA required")
        if self.event not in {"push", "pull_request", "workflow_dispatch"}:
            raise ValueError("unapproved GitHub event")

    @property
    def repository_full_name(self) -> str:
        return f"{self.owner}/{self.repository}"

    @property
    def fixed_api_url(self) -> str:
        # Never reuse any caller-provided URL, redirect or HTML link as a target.
        return (f"https://api.github.com/repos/{self.owner}/{self.repository}"
                f"/actions/runs/{self.run_id}")


@dataclass(frozen=True)
class GithubCheck:
    decision: str
    reason: str
    source_type: str
    run_id: int | None = None
    repository_id: int | None = None
    workflow_id: int | None = None
    head_sha: str | None = None
    run_attempt: int | None = None
    task_approved: bool = False
    state_authoritative: bool = False

    def __post_init__(self) -> None:
        if self.decision not in {CHECKED_PASS, CHECKED_FAIL, INCONCLUSIVE}:
            raise ValueError("invalid verification decision")
        if self.task_approved or self.state_authoritative:
            raise ValueError("external evidence must never approve a task")


def _result(decision: str, reason: str, policy: GithubRunPolicy,
            record: dict[str, Any] | None = None) -> GithubCheck:
    record = record or {}
    def posint(key: str) -> int | None:
        value = record.get(key)
        return (value if isinstance(value, int) and not isinstance(value, bool)
                and value > 0 else None)
    repository = record.get("repository")
    repo_id = repository.get("id") if isinstance(repository, dict) else None
    head_sha = record.get("head_sha")
    return GithubCheck(
        decision=decision, reason=reason, source_type="GITHUB_WORKFLOW_RUN",
        run_id=posint("id"),
        repository_id=repo_id if isinstance(repo_id, int) and not isinstance(repo_id, bool) else None,
        workflow_id=posint("workflow_id"),
        head_sha=head_sha if isinstance(head_sha, str) and _SHA40.fullmatch(head_sha) else None,
        run_attempt=posint("run_attempt"),
    )


def check_github_record(policy: GithubRunPolicy, record: object) -> GithubCheck:
    """Only exact GitHub run identity, completed success, and allowed origin PASS.

    A mismatch is CHECKED_FAIL; missing/pending/unavailable is INCONCLUSIVE.
    The authenticity of input still depends on a real trusted provider channel.
    """
    if not isinstance(record, dict):
        return _result(INCONCLUSIVE, "MALFORMED_PROVIDER_RECORD", policy)
    required = ("id", "repository", "workflow_id", "head_sha",
                "run_attempt", "status", "conclusion", "event")
    if any(key not in record for key in required):
        return _result(INCONCLUSIVE, "INCOMPLETE_PROVIDER_RECORD", policy)
    repository = record["repository"]
    if not isinstance(repository, dict) or not isinstance(repository.get("id"), int):
        return _result(INCONCLUSIVE, "INVALID_PROVIDER_REPOSITORY", policy, record)
    if isinstance(repository.get("id"), bool) or not isinstance(repository.get("full_name"), str):
        return _result(INCONCLUSIVE, "INVALID_PROVIDER_REPOSITORY", policy, record)
    for key in ("id", "workflow_id", "run_attempt"):
        value = record[key]
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            return _result(INCONCLUSIVE, "INVALID_PROVIDER_IDENTITY_FIELD", policy, record)
    if not isinstance(record["head_sha"], str) or not _SHA40.fullmatch(record["head_sha"]):
        return _result(INCONCLUSIVE, "INVALID_PROVIDER_SHA", policy, record)
    if not isinstance(record["event"], str):
        return _result(INCONCLUSIVE, "INVALID_PROVIDER_EVENT", policy, record)
    expected = (
        (record["id"], policy.run_id, "WRONG_RUN"),
        (repository["id"], policy.repository_id, "WRONG_REPOSITORY"),
        (repository["full_name"], policy.repository_full_name, "WRONG_REPOSITORY_NAME"),
        (record["workflow_id"], policy.workflow_id, "WRONG_WORKFLOW"),
        (record["run_attempt"], policy.run_attempt, "WRONG_RUN_ATTEMPT"),
        (record["head_sha"], policy.head_sha, "WRONG_SHA"),
        (record["event"], policy.event, "WRONG_EVENT"),
    )
    for observed, wanted, reason in expected:
        if observed != wanted:
            return _result(CHECKED_FAIL, reason, policy, record)
    head_repository = record.get("head_repository")
    if not isinstance(head_repository, dict):
        return _result(INCONCLUSIVE, "MISSING_HEAD_REPOSITORY", policy, record)
    if head_repository.get("id") != policy.repository_id:
        return _result(CHECKED_FAIL, "UNTRUSTED_HEAD_REPOSITORY", policy, record)
    if record["status"] != "completed":
        return _result(INCONCLUSIVE, "WORKFLOW_NOT_COMPLETED", policy, record)
    if record["conclusion"] is None:
        return _result(INCONCLUSIVE, "WORKFLOW_NO_CONCLUSION", policy, record)
    if record["conclusion"] != "success":
        return _result(CHECKED_FAIL, "WORKFLOW_NOT_SUCCESSFUL", policy, record)
    return _result(CHECKED_PASS, "EXPECTED_WORKFLOW_RUN_SUCCEEDED", policy, record)


def check_non_api_source(source_kind: str) -> GithubCheck:
    """Screenshots, LLM prose, pasted logs and links are untrusted."""
    if not isinstance(source_kind, str):
        raise ValueError("source kind required")
    return GithubCheck(INCONCLUSIVE, "UNTRUSTED_SOURCE_NOT_PROVIDER_API",
                       source_type="UNTRUSTED_MEDIA")


def verify_github_run(policy: GithubRunPolicy, *,
                      client: httpx.Client | None = None,
                      token: str | None = None) -> GithubCheck:
    """Exactly one fixed-host GET, never redirects, caller URLs or proxy env.

    Real API TLS and identity are needed for actual provider validation.
    Tests can inject MockTransport but cannot claim provider authenticity.
    """
    own = client is None
    if own:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "rightware-si-r2-r1a-lab",
        }
        if token:
            if not isinstance(token, str) or "\r" in token or "\n" in token:
                raise ValueError("invalid API credential")
            headers["Authorization"] = f"Bearer {token}"
        client = httpx.Client(headers=headers, timeout=httpx.Timeout(6.0),
                              follow_redirects=False, trust_env=False)
    try:
        try:
            response = client.get(policy.fixed_api_url, headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }, follow_redirects=False)
        except httpx.RequestError:
            return _result(INCONCLUSIVE, "PROVIDER_UNAVAILABLE", policy)
        if response.status_code != 200:
            if 300 <= response.status_code < 400:
                return _result(INCONCLUSIVE, "PROVIDER_REDIRECT_DENIED", policy)
            return _result(INCONCLUSIVE, "PROVIDER_HTTP_UNAVAILABLE", policy)
        if len(response.content) > _MAX_BODY:
            return _result(INCONCLUSIVE, "PROVIDER_RESPONSE_TOO_LARGE", policy)
        if "json" not in response.headers.get("content-type", "").lower():
            return _result(INCONCLUSIVE, "PROVIDER_NOT_JSON", policy)
        try:
            data = response.json()
        except ValueError:
            return _result(INCONCLUSIVE, "PROVIDER_JSON_INVALID", policy)
        return check_github_record(policy, data)
    finally:
        if own:
            client.close()
