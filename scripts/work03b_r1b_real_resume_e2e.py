"""WORK-03B R1B synthetic subprocess acceptance: A exits, B resumes via real REST.

Refuses all databases except disposable localhost:5432/rw_test. No secrets,
real Jarvis, personal conversations, model calls or paid services are used.
Run after migrations 0001-0005, before Ollama/Mem0 services start.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from uuid import uuid4

import httpx
import psycopg

from rightware_si.core import WorkCore
from rightware_si.token_admin import issue_api_token
from rightware_si.lab_boundary import require_disposable_postgres

URL = "http://127.0.0.1:8892"
CLAIM = "Agent A recorded a synthetic receipt; not independently verified"
SUMMARY = "Prepared synthetic integration; verification still pending"


def require(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def request(client, method, path, token, body=None, idem=None, expected=200):
    headers = {"Authorization":f"Bearer {token}"}
    if idem:
        headers["Idempotency-Key"] = idem
    response = client.request(method, URL + path, headers=headers, json=body)
    require(response.status_code == expected, f"unexpected HTTP status for {path}")
    return response.json() if response.status_code in (200,201) else {}


def agent_a():
    task = os.environ["RW_R1B_TASK"]
    lease = os.environ["RW_R1B_LEASE"]
    token = os.environ["RW_R1B_ACTOR_TOKEN"]
    with httpx.Client(timeout=8,trust_env=False,follow_redirects=False) as client:
        run = request(client,"POST",f"/v1/projects/alpha/tasks/{task}/runs",token,{
            "expected_version":3,"lease_token":lease,"runtime_label":"process-a-r1b"
        }, "r1b-e2e-run-a",201)
        source = request(client,"POST","/v1/projects/alpha/sources",token,{
            "task_id":task,"agent_run_id":run["run_id"],
            "expected_version":3,"lease_token":lease,
            "source_kind":"TOOL_RECEIPT",
            "source_uri":"urn:rw:synthetic-checkpoint-lab",
            "source_revision":"r1b-a"
        },"r1b-e2e-source-a",201)
        observation = request(client,"POST","/v1/projects/alpha/observations",token,{
            "task_id":task,"agent_run_id":run["run_id"],
            "expected_version":3,"lease_token":lease,
            "claim":CLAIM,"source_ids":[source["source_id"]],
        },"r1b-e2e-obs-a",201)
        checkpoint = request(client,"POST",
            f"/v1/projects/alpha/tasks/{task}/checkpoints",token,{
            "agent_run_id":run["run_id"],"expected_version":3,
            "expected_checkpoint_seq":0,"lease_token":lease,
            "summary":SUMMARY,
            "next_actions":["Continue with independent verification"],
            "blockers":["Verification pending"],
            "observation_ids":[observation["observation_id"]],
        },"r1b-e2e-cp-a",201)
        offer = request(client,"POST",f"/v1/projects/alpha/tasks/{task}/handoffs",token,{
            "expected_version":3,"to_principal_id":"agent-b",
            "summary":"Handoff after immutable checkpoint",
            "lease_token":lease,
            "checkpoint_id":checkpoint["checkpoint_id"],
            "expected_checkpoint_seq":checkpoint["checkpoint_seq"],
        },"r1b-e2e-handoff-a",201)
        require(offer["status"]=="BLOCKED", "handoff did not block A")
        require(offer["checkpoint_binding"]=="BOUND_R1C"
                and offer["checkpoint_id"]==checkpoint["checkpoint_id"],
                "checkpoint was not bound atomically")
        denied = client.post(
            URL+f"/v1/projects/alpha/tasks/{task}/checkpoints",
            headers={"Authorization":f"Bearer {token}",
                     "Idempotency-Key":"r1b-e2e-denied-stale"},
            json={"agent_run_id":run["run_id"],"expected_version":4,
                  "expected_checkpoint_seq":1,"lease_token":lease,
                  "summary":SUMMARY,"next_actions":["unsafe retry"],
                  "blockers":[],"observation_ids":[]},
        )
        require(denied.status_code==409, "old agent lease still accepted")
        print(json.dumps({
            "checkpoint_id":checkpoint["checkpoint_id"],
            "handoff_id":offer["handoff_id"],
            "checkpoint_seq":checkpoint["checkpoint_seq"],
            "status":"A_CHECKPOINTED_AND_EXITED",
        }))


def agent_b():
    task=os.environ["RW_R1B_TASK"]
    handoff=os.environ["RW_R1B_HANDOFF"]
    token=os.environ["RW_R1B_ACTOR_TOKEN"]
    with httpx.Client(timeout=8,trust_env=False,follow_redirects=False) as client:
        accepted = request(client,"POST",
            f"/v1/projects/alpha/handoffs/{handoff}/accept",token,{
                "expected_version":4,
            },"r1b-e2e-accept-b",200)
        require(accepted["version"]==5, "handoff acceptance version wrong")
        require(accepted["checkpoint_binding"]=="BOUND_R1C",
                "B accepted unbound handoff")
        # Simulate the holder losing the one-time lease response: do not use
        # accepted['lease_token'] to continue. Generation is nonsecret and can
        # be retrieved by the same authenticated holder.
        original_lease=accepted.pop("lease_token")
        status=request(client,"GET",
            f"/v1/projects/alpha/tasks/{task}/lease-status",token,expected=200)
        require(status["lease_generation"]==accepted["lease_generation"],
                "holder lease generation not recoverable")
        recovered=request(client,"POST",
            f"/v1/projects/alpha/tasks/{task}/lease-recovery",token,{
                "expected_version":5,
                "expected_generation":status["lease_generation"],
            },"r1c-e2e-rekey-b",200)
        require(recovered["lease_generation"]>accepted["lease_generation"],
                "fencing generation failed to advance")
        require(recovered["lease_token"]!=original_lease,
                "lost-response rekey reused the same secret")
        replay=client.post(
            URL+f"/v1/projects/alpha/tasks/{task}/lease-recovery",
            headers={"Authorization":f"Bearer {token}",
                     "Idempotency-Key":"r1c-e2e-rekey-b"},
            json={"expected_version":5,
                  "expected_generation":status["lease_generation"]},
        )
        require(replay.status_code==409,"one-time lease secret was replayed")
        # The recovered token is not logged, and resume remains read-only.
        snap = request(client,"GET",
            f"/v1/projects/alpha/tasks/{task}/resume",token,expected=200)
        require(snap["snapshot_status"]=="CHECKPOINT_AVAILABLE",
                "checkpoint unavailable in new process")
        require(snap["checkpoint"]["summary"]==SUMMARY,
                "canonical checkpoint not reconstructed")
        require(snap["checkpoint"]["observations"][0]["claim"]==CLAIM,
                "source-linked observation missing from resume")
        require(snap["checkpoint"]["trust_state"]=="ASSERTED",
                "claim incorrectly promoted to verified")
        require(snap["task"]["status"]=="IN_PROGRESS" and snap["task"]["version"]==5,
                "canonical work state incorrect after handoff")
        require(snap["memory_status"]=="NOT_QUERIED",
                "resume unexpectedly requires Mem0/Ollama")
        require(snap["read_only"] and not snap["lease_issued"]
                and not snap["verified_completion"],
                "resume mistakenly minted authority or approval")
        require(snap["last_handoff"]["checkpoint_id"]==
                accepted["checkpoint_id"],
                "handoff bound checkpoint changed during rekey")
        require(snap["last_handoff"]["checkpoint_binding"]=="BOUND_R1C",
                "handoff checkpoint binding missing")
        require(snap["handoff_checkpoint"]["checkpoint_id"]==
                snap["checkpoint"]["checkpoint_id"],
                "resumed checkpoint is not the bound one")
        require("lease_token" not in json.dumps(snap), "lease secret leaked by resume")
        print(json.dumps({
            "checkpoint_id":snap["checkpoint"]["checkpoint_id"],
            "checkpoint_seq":snap["checkpoint"]["checkpoint_seq"],
            "task_version":snap["task"]["version"],
            "status":"B_RESUMED_FROM_NEW_PROCESS_WITHOUT_CHAT",
        }))


def prepare(dsn):
    with psycopg.connect(dsn) as conn:
        conn.execute("TRUNCATE si_organizations,si_principals RESTART IDENTITY CASCADE")
        conn.execute("INSERT INTO si_organizations(id) VALUES('r1b-lab')")
        conn.execute("INSERT INTO si_projects(id,organization_id) VALUES('alpha','r1b-lab')")
        conn.execute("INSERT INTO si_principals(id,principal_kind) VALUES"
                     "('agent-a','AGENT'),('agent-b','AGENT'),('intruder','AGENT')")
        permissions={
            "agent-a":["task:create","task:manage","task:execute","task:read",
                       "context:read","source:write","observation:write",
                       "checkpoint:write","handoff:offer"],
            "agent-b":["task:execute","task:read","context:read",
                       "handoff:accept","checkpoint:write","task:recover"],
        }
        for actor,grants in permissions.items():
            for grant in grants:
                conn.execute("INSERT INTO si_project_grants "
                             "(project_id,principal_id,permission) VALUES('alpha',%s,%s)",
                             (actor,grant))
    token_a = issue_api_token(dsn,"agent-a",1)[1]
    token_b = issue_api_token(dsn,"agent-b",1)[1]
    token_c = issue_api_token(dsn,"intruder",1)[1]
    work=WorkCore(dsn)
    task=work.create_task("alpha","agent-a","Process-resumable synthetic test",
                          ["B reads canonical checkpoint without A chat"],
                          "r1b-create-"+uuid4().hex[:12])
    work.publish_task("alpha","agent-a",task["task_id"],1,
                      "r1b-publish-"+uuid4().hex[:12])
    lease=work.claim_task("alpha","agent-a",task["task_id"],2,
                          "r1b-claim-"+uuid4().hex[:12])["lease_token"]
    return task["task_id"],lease,token_a,token_b,token_c


def run_child(role, task, token, lease=None, handoff=None):
    # Children must not inherit infrastructure credentials or DB passwords.
    # Only the agent-specific bearer (and A's temporary lease) cross this boundary.
    allow = {"PATH","PYTHONPATH","PYTHONHOME","VIRTUAL_ENV","HOME","LANG",
             "TMPDIR","SYSTEMROOT","LD_LIBRARY_PATH"}
    env={k:v for k,v in os.environ.items() if k in allow}
    env["RW_R1B_TASK"]=task
    env["RW_R1B_ACTOR_TOKEN"]=token
    if lease:
        env["RW_R1B_LEASE"]=lease
    if handoff:
        env["RW_R1B_HANDOFF"]=handoff
    child=subprocess.run([sys.executable,__file__,role],env=env,
                         text=True,capture_output=True,timeout=35)
    # The child output MUST never include token/lease or arbitrary HTTP response.
    require(child.returncode==0, f"{role} process failed")
    output=json.loads(child.stdout)
    require("lease_token" not in child.stdout and token not in child.stdout,
            "subprocess exposed secrets")
    return output


def main():
    dsn=os.environ.get("RW_TEST_DATABASE_URL","")
    require_disposable_postgres(dsn, expected_user="rw")
    require(os.environ.get("RW_SI_DATABASE_URL")==dsn,
            "API and disposable test databases must match")
    require(os.environ.get("RW_R1B_URL",URL)==URL,
            "only loopback API is allowed")
    task,lease,token_a,token_b,token_c=prepare(dsn)
    env=dict(os.environ)
    # Even if the CI has a URL configured, no Mem0 service runs in this phase.
    # This REST route NEVER queries memory; deliberately do not start Ollama.
    proc=subprocess.Popen(
        [sys.executable,"-m","uvicorn","rightware_si.http_api:app",
         "--host","127.0.0.1","--port","8892","--no-access-log"],
        env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
    )
    try:
        with httpx.Client(timeout=2,trust_env=False) as client:
            for _ in range(80):
                require(proc.poll() is None, "API subprocess died")
                try:
                    if client.get(URL+"/healthz").status_code==200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.2)
            else:
                raise AssertionError("loopback API not ready")

        a=run_child("agent-a",task,token_a,lease=lease)
        require(a["status"]=="A_CHECKPOINTED_AND_EXITED","A did not finish")
        # A's subprocess is already terminated; B receives ONLY its own bearer
        # and a handoff identifier, no A lease, chat or checkpoint payload.
        b=run_child("agent-b",task,token_b,handoff=a["handoff_id"])
        require(b["status"]=="B_RESUMED_FROM_NEW_PROCESS_WITHOUT_CHAT",
                "B did not reconstruct canonical state")
        require(b["checkpoint_id"]==a["checkpoint_id"],
                "B read different checkpoint")
        with httpx.Client(timeout=5,trust_env=False) as client:
            denied=request(client,"GET",
                f"/v1/projects/alpha/tasks/{task}/resume",token_c,
                expected=403)
            require(denied=={}, "intruder got data")
        with psycopg.connect(dsn) as conn:
            conn.execute("DELETE FROM si_project_grants WHERE "
                         "project_id='alpha' AND principal_id='agent-b' "
                         "AND permission='context:read'")
        with httpx.Client(timeout=5,trust_env=False) as client:
            denied=request(client,"GET",
                f"/v1/projects/alpha/tasks/{task}/resume",token_b,
                expected=403)
            require(denied=={}, "revoked read remained available")
        print("WORK03B_R1B_RESUME_E2E_PASS "
              "a_process_exited=true b_new_process=true rest_auth=true "
              "postgres_checkpoint=true independent_context=true "
              "memory_offline=true bound_checkpoint=true a_lease_denied=true "
              "intruder_denied=true revocation_denied=true synthetic_only=true")
        print("WORK03B_R1C_BOUND_LEASE_RECOVERY_E2E_PASS "
              "bound_checkpoint=true independent_agents=true "
              "fencing_rekey=true secret_replay_denied=true "
              "memory_offline=true synthetic_only=true")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


if __name__=="__main__":
    try:
        role = sys.argv[1] if len(sys.argv)==2 else "orchestrator"
        if role=="agent-a":
            agent_a()
        elif role=="agent-b":
            agent_b()
        elif role=="orchestrator":
            main()
        else:
            raise ValueError("unknown mode")
    except Exception as exc:
        # Sanitized error only: never print HTTP bodies, secret-bearing env or tokens.
        print(f"WORK03B_R1B_E2E_FAIL({type(exc).__name__})",file=sys.stderr)
        raise SystemExit(1) from None
