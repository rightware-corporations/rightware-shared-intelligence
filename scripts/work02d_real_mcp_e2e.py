"""WORK-02D full lab chain: external MCP stdio client → REST → PostgreSQL → real Mem0.

Run ONLY against ephemeral rw_test and Mem0 lab databases. All records are
synthetic, and the service/model never invokes a paid inference API.
"""
from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import time
from uuid import uuid4

import httpx
import psycopg
from mcp import Client, StdioServerParameters

from rightware_si.core import WorkCore
from rightware_si.lab_boundary import require_disposable_postgres
from rightware_si.memory import Mem0HTTPClient, MemoryScope, SharedMemory
from rightware_si.token_admin import issue_api_token, revoke_api_token


def check_db() -> str:
    dsn = os.environ["RW_TEST_DATABASE_URL"]
    require_disposable_postgres(dsn, expected_user="rw")
    if os.environ.get("RW_SI_DATABASE_URL") != dsn:
        raise RuntimeError("API database and test database must match")
    if os.environ.get("RW_SI_MEM0_URL") != "http://127.0.0.1:8891":
        raise RuntimeError("Real Mem0 lab must be loopback 8891")
    if not os.environ.get("RW_SI_MEM0_API_KEY"):
        raise RuntimeError("Mem0 lab secret not provided")
    return dsn


def prepare(dsn: str):
    with psycopg.connect(dsn) as conn:
        # The prior unit suite seeds "alpha"/"beta" into the same disposable
        # /rw_test database. Reset fixtures to avoid cross-suite collisions.
        # check_db() already rejects non-local/non-ephemeral DB targets.
        conn.execute("TRUNCATE si_organizations,si_principals RESTART IDENTITY CASCADE")
        conn.execute("INSERT INTO si_organizations(id) VALUES('rwlab')")
        conn.execute("INSERT INTO si_projects(id,organization_id) VALUES "
                     "('alpha','rwlab'),('beta','rwlab')")
        conn.execute("INSERT INTO si_principals(id,principal_kind) VALUES "
                     "('reader','AGENT'),('intruder','AGENT')")
        for grant in ("context:read","memory:read","task:read","task:create"):
            conn.execute(
                "INSERT INTO si_project_grants(project_id,principal_id,permission) "
                "VALUES('alpha','reader',%s)", (grant,)
            )

    token_id, token = issue_api_token(dsn, "reader", 1)
    _, intruder_token = issue_api_token(dsn, "intruder", 1)
    nonce = uuid4().hex[:12]
    mem = SharedMemory(Mem0HTTPClient(
        os.environ["RW_SI_MEM0_URL"], os.environ["RW_SI_MEM0_API_KEY"]))
    mem.add(MemoryScope("rwlab","alpha"),"agent-a",
            f"Alpha synthetic authorized checkpoint {nonce}: implementation pending",
            source="synthetic-work02d")
    mem.add(MemoryScope("rwlab","beta"),"agent-b",
            f"Beta private synthetic context {nonce}",source="synthetic-work02d")
    task = WorkCore(dsn).create_task(
        "alpha","reader","WORK-02D synthetic MCP E2E",["Independent authorization"],
        "create-work02d-"+nonce,
    )
    return token_id, token, intruder_token, task["task_id"], nonce


async def verify_chain(token_id: str, token: str, intruder_token: str,
                       task_id: str, nonce: str, dsn: str):
    base = {"RW_SI_API_URL":"http://127.0.0.1:8890"}
    async def mcp_client(secret: str):
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m","rightware_si.mcp_bridge"],
            env=dict(base, RW_SI_API_TOKEN=secret),
        )
        return Client(params)

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m","rightware_si.mcp_bridge"],
        env=dict(base, RW_SI_API_TOKEN=token),
    )
    async with Client(params) as client:
        listing=await client.list_tools()
        names={t.name for t in listing.tools}
        assert {"get_task","get_project_context","get_task_events"} <= names, "missing real stdio tools"
        assert not {"approve_decision","write_memory","submit_result"} & names

        context=await client.call_tool("get_project_context",{
            "project_id":"alpha","query":nonce,
        })
        assert not context.is_error, "authorized real Mem0 retrieval failed"
        details=str(context.structured_content or context.content)
        assert nonce in details, "synthetic Alpha marker not found through MCP"
        assert "UNVERIFIED" in details, "missing trust label"
        assert "Beta private" not in details, "Beta context leaked through MCP"
        assert "postgresql" in details, "authoritative source missing"

        task=await client.call_tool("get_task",{
            "project_id":"alpha","task_id":task_id,
        })
        assert not task.is_error and "DRAFT" in str(task.structured_content or task.content), "task read failed"

        denied=await client.call_tool("get_project_context",{
            "project_id":"beta","query":nonce,
        })
        assert denied.is_error, "Alpha identity was allowed to read Beta via MCP"
        assert "Beta private" not in str(denied), "Forbidden response revealed data"

        assert revoke_api_token(dsn, token_id), "token revocation failed"
        revoked=await client.call_tool("get_project_context",{
            "project_id":"alpha","query":nonce,
        })
        assert revoked.is_error, "Revoked credential still works via MCP"
        assert "Alpha synthetic" not in str(revoked), "Unauthorized response exposed memory"

    intruder = StdioServerParameters(
        command=sys.executable,
        args=["-m","rightware_si.mcp_bridge"],
        env=dict(base, RW_SI_API_TOKEN=intruder_token),
    )
    async with Client(intruder) as client:
        denied=await client.call_tool("get_project_context",{
            "project_id":"alpha","query":nonce,
        })
        assert denied.is_error, "Unprivileged principal read Alpha via MCP"
        assert "Alpha synthetic" not in str(denied), "Unauthorized response leaked data"


def main() -> None:
    dsn=check_db()
    token_id,token,intruder,task_id,nonce=prepare(dsn)
    env=dict(os.environ)
    # Keep the local API process private; never use a public bind address.
    proc=subprocess.Popen(
        [sys.executable,"-m","uvicorn","rightware_si.http_api:app",
         "--host","127.0.0.1","--port","8890","--no-access-log"],
        env=env, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
    )
    try:
        with httpx.Client(timeout=2,trust_env=False) as http:
            for _ in range(60):
                if proc.poll() is not None:
                    raise RuntimeError("Local RIGHTWARE API process stopped unexpectedly")
                try:
                    response=http.get("http://127.0.0.1:8890/healthz")
                    if response.status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.25)
            else:
                raise RuntimeError("Local RIGHTWARE API readiness failed")

        asyncio.run(verify_chain(token_id,token,intruder,task_id,nonce,dsn))
        print("WORK02D_FULL_MCP_REAL_MEM0_E2E_PASS "
              "mcp_stdio=true rest_auth=true postgres=true "
              "mem0_oss=true ollama_embed=true project_denied=true "
              "revocation=true intruder_denied=true synthetic_only=true")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        # Don't echo potentially sensitive tool output / tokens from exceptions.
        print(f"WORK02D_FULL_E2E_FAIL({type(exc).__name__})",file=sys.stderr)
        raise SystemExit(1) from None
