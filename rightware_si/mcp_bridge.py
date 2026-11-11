"""WORK-02B read-only MCP 2.x stdio adapter.

The MCP client launches this program locally. It never exposes an unauthenticated
HTTP MCP port. It calls the *same authenticated REST API* used by other clients
and therefore receives the same grant checks and task states.

Required environment:
  RW_SI_API_URL=http://127.0.0.1:8890
  RW_SI_API_TOKEN=<high entropy token issued for this single client>
MCP is READ-ONLY by design in WORK-02B; no handoff mutations are exposed.
"""
from __future__ import annotations

import os
from urllib.parse import quote, urlsplit

import httpx
from mcp.server import MCPServer


mcp = MCPServer("RIGHTWARE Shared Intelligence — WORK-02B read-only")


def _base_url() -> str:
    url = os.environ.get("RW_SI_API_URL", "")
    parsed = urlsplit(url)
    loopback = parsed.hostname in ("127.0.0.1", "localhost", "::1")
    if (
        not parsed.netloc
        or parsed.username
        or parsed.password
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
        or (parsed.scheme != "https" and not (parsed.scheme == "http" and loopback))
    ):
        raise RuntimeError("RW_SI_API_URL must be an HTTPS origin or local loopback HTTP")
    return url.rstrip("/")


def _read_api(path: str) -> dict:
    token = os.environ.get("RW_SI_API_TOKEN", "")
    if not token.startswith("rwsi_") or len(token) < 45:
        raise RuntimeError("MCP bridge credential not configured")
    if not path.startswith("/v1/projects/"):
        raise ValueError("unsupported route")
    # no redirects, no proxy environment, no raw API response in an error
    try:
        with httpx.Client(timeout=8.0, follow_redirects=False, trust_env=False) as client:
            response = client.get(_base_url() + path, headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            raise RuntimeError(f"Shared Intelligence REST request failed: HTTP {response.status_code}")
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("Unexpected REST response format")
        return data
    except (httpx.HTTPError, ValueError) as exc:
        raise RuntimeError(f"Shared Intelligence connection failed ({type(exc).__name__})") from None


def _segment(identifier: str) -> str:
    if not isinstance(identifier, str) or not identifier or len(identifier) > 128:
        raise ValueError("invalid identifier")
    # URL encoding protects route construction; REST handles UUID and auth checks.
    return quote(identifier, safe="")


@mcp.tool()
def get_task(project_id: str, task_id: str) -> dict:
    """Read an authorized project's canonical task status and version."""
    return _read_api(f"/v1/projects/{_segment(project_id)}/tasks/{_segment(task_id)}")


@mcp.tool()
def get_task_events(project_id: str, task_id: str) -> dict:
    """Read an authorized project's task event history; no mutation."""
    return _read_api(f"/v1/projects/{_segment(project_id)}/tasks/{_segment(task_id)}/events")


if __name__ == "__main__":
    mcp.run(transport="stdio")
