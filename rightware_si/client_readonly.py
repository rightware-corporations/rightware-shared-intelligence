"""Standalone opt-in read-only compatibility probe; NOT integrated into Jarvis.

The Jarvis repository is not imported, installed, or modified.
"""
from __future__ import annotations

import os
import sys
from urllib.parse import quote, urlsplit
from uuid import UUID

import httpx


def read_task(project: str, task_id: str, *, api_url: str, token: str) -> dict:
    host = urlsplit(api_url)
    if (
        host.scheme != "https"
        and not (host.scheme == "http" and host.hostname in ("127.0.0.1","localhost","::1"))
    ):
        raise ValueError("API endpoint must use HTTPS or local loopback")
    if host.path not in ("","/") or host.query or host.fragment or host.username:
        raise ValueError("API URL must be an origin")
    if not token.startswith("rwsi_") or len(token) < 45:
        raise ValueError("read-only token required")
    if len(project) > 64 or not project or not all(c.isalnum() or c in "._-" for c in project):
        raise ValueError("invalid project")
    path = f"/v1/projects/{quote(project,safe='')}/tasks/{UUID(task_id)}"
    with httpx.Client(trust_env=False,timeout=3.0,follow_redirects=False) as client:
        response=client.get(api_url.rstrip("/") + path,
                            headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        raise RuntimeError(f"Shared Intelligence read unavailable (HTTP {response.status_code})")
    result = response.json()
    if not isinstance(result,dict) or result.get("status") not in {
        "DRAFT","READY","IN_PROGRESS","BLOCKED","IN_REVIEW","DONE","CANCELLED"
    }:
        raise RuntimeError("Unrecognized remote task response")
    return {"task_id":str(result["id"]),"status":result["status"],
            "version":result["version"]}


def main():
    import argparse
    p=argparse.ArgumentParser(description="Standalone read-only pilot: no Jarvis writes")
    p.add_argument("--project",required=True)
    p.add_argument("--task-id",required=True)
    args=p.parse_args()
    try:
        value=read_task(args.project,args.task_id,
            api_url=os.environ["RW_SI_API_URL"],
            token=os.environ["RW_SI_API_TOKEN"])
        print(f"task_id={value['task_id']} status={value['status']} version={value['version']}")
    except (KeyError,ValueError,RuntimeError,httpx.HTTPError) as e:
        print(f"Compatibility probe failed ({type(e).__name__})",file=sys.stderr)
        raise SystemExit(1) from None


if __name__=="__main__":
    main()
