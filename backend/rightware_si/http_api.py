"""WORK-02B FastAPI gateway for the trusted PostgreSQL transactional core.

Experimental and single-organization/pilot only. No Mem0 indexing or Jarvis
integration. Server cannot start without RW_SI_DATABASE_URL. Every protected
request resolves its actor from a high-entropy bearer token, not JSON.
"""
from __future__ import annotations

import os
from urllib.parse import urlsplit
from typing import Annotated

import psycopg
from uuid import UUID
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from rightware_si.api_auth import make_principal_dependency
from rightware_si.core import AccessDenied, Conflict, InvalidTransition, Missing, WorkCore
from rightware_si.context_service import ScopedContextReader, SemanticUnavailable
from rightware_si.continuity import ContinuityCore
from rightware_si.memory import Mem0HTTPClient, SharedMemory
from rightware_si.verification_ledger import EvidenceLedger


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateTask(StrictModel):
    title: str = Field(min_length=1, max_length=200)
    acceptance_criteria: list[str] = Field(min_length=1, max_length=30)


class Versioned(StrictModel):
    expected_version: int = Field(gt=0, strict=True)


class VerifyEvidence(StrictModel):
    policy_id: UUID
    expected_task_version: int = Field(gt=0, strict=True)


class OfferHandoff(Versioned):
    to_principal_id: str = Field(min_length=1, max_length=64)
    summary: str = Field(min_length=1, max_length=8000)
    lease_token: str = Field(min_length=20, max_length=256)
    # Optional only for legacy tasks with NO checkpoint. Required when one exists.
    checkpoint_id: UUID | None = None
    expected_checkpoint_seq: int | None = Field(default=None, gt=0, strict=True)


class RecoverLease(Versioned):
    expected_generation: int = Field(gt=0, strict=True)


class MemorySearch(StrictModel):
    query: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=10)


class SubmitResult(Versioned):
    lease_token: str = Field(min_length=20, max_length=256)
    evidence_url: str = Field(min_length=10, max_length=2048)


class StartAgentRun(Versioned):
    lease_token: str = Field(min_length=20, max_length=256)
    runtime_label: str = Field(min_length=1, max_length=120)


class RegisterSource(Versioned):
    task_id: UUID
    agent_run_id: UUID
    lease_token: str = Field(min_length=20, max_length=256)
    source_kind: Literal["GIT_REF", "TOOL_RECEIPT"]
    source_uri: str = Field(min_length=1, max_length=2048)
    source_revision: str = Field(min_length=1, max_length=128)
    digest_sha256: str | None = None


class RecordObservation(Versioned):
    task_id: UUID
    agent_run_id: UUID
    lease_token: str = Field(min_length=20, max_length=256)
    claim: str = Field(min_length=1, max_length=2000)
    source_ids: list[UUID] = Field(min_length=1, max_length=10)


class RecordCheckpoint(Versioned):
    agent_run_id: UUID
    lease_token: str = Field(min_length=20, max_length=256)
    expected_checkpoint_seq: int = Field(ge=0, strict=True)
    summary: str = Field(min_length=1, max_length=2000)
    next_actions: list[str] = Field(min_length=1, max_length=12)
    blockers: list[str] = Field(default_factory=list, max_length=12)
    observation_ids: list[UUID] = Field(default_factory=list, max_length=20)


def _invoke(operation):
    try:
        return operation()
    except AccessDenied:
        raise HTTPException(status_code=403, detail="Forbidden") from None
    except Missing:
        raise HTTPException(status_code=404, detail="Resource not found") from None
    except (Conflict, InvalidTransition):
        raise HTTPException(status_code=409, detail="State conflict") from None
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid operation") from None


def create_app(dsn: str | None = None, memory_provider=None) -> FastAPI:
    dsn = dsn or os.environ.get("RW_SI_DATABASE_URL")
    if not dsn:
        raise RuntimeError("RW_SI_DATABASE_URL is required; refusing to start unconfigured")
    # R2 R1C is deliberately disabled by default and only registered for the
    # disposable loopback PostgreSQL synthetic lab. No production endpoint.
    r2_lab_enabled = os.environ.get("RW_SI_ENABLE_R2_R1C_LAB_API") == "1"
    if r2_lab_enabled:
        parsed_dsn = urlsplit(dsn)
        if (os.environ.get("RW_SI_ENVIRONMENT") != "lab" or
                parsed_dsn.scheme not in ("postgresql", "postgres") or
                parsed_dsn.hostname not in ("127.0.0.1", "localhost") or
                parsed_dsn.port != 5432 or parsed_dsn.path != "/rw_test"):
            raise RuntimeError("R2 R1C lab API requires disposable local /rw_test and lab environment")
    core = WorkCore(dsn)
    continuity = ContinuityCore(dsn)
    principal_dep = make_principal_dependency(dsn)
    if memory_provider is None:
        mem0_url = os.environ.get("RW_SI_MEM0_URL", "")
        mem0_key = os.environ.get("RW_SI_MEM0_API_KEY", "")
        if bool(mem0_url) != bool(mem0_key):
            raise RuntimeError("Mem0 URL and key must be configured together")
        if mem0_url:
            memory_provider = SharedMemory(Mem0HTTPClient(mem0_url, mem0_key))
    context_reader = ScopedContextReader(dsn, memory_provider)
    app = FastAPI(
        title="RIGHTWARE Shared Intelligence — WORK-02B experimental API",
        description="Authenticated pilot task/handoff API. No production or external use.",
        version="0.2.0",
        debug=False,
    )

    @app.middleware("http")
    async def no_store(request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/healthz")
    def healthz():
        return {"status": "running", "phase": "WORK-02B", "production_ready": False}

    @app.get("/v1/projects/{project_id}/tasks/{task_id}")
    def get_task(
        project_id: str, task_id: UUID,
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: core.get_task(project_id, actor, str(task_id)))

    @app.get("/v1/projects/{project_id}/tasks/{task_id}/events")
    def task_events(
        project_id: str, task_id: UUID,
        actor: str = Depends(principal_dep),
    ):
        return {"events": _invoke(lambda: core.task_events(project_id, actor, str(task_id)))}

    @app.post("/v1/projects/{project_id}/tasks", status_code=201)
    def create_task(
        project_id: str, body: CreateTask,
        idem: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: core.create_task(
            project_id, actor, body.title, body.acceptance_criteria, idem
        ))

    @app.post("/v1/projects/{project_id}/tasks/{task_id}/publish")
    def publish_task(
        project_id: str, task_id: UUID, body: Versioned,
        idem: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: core.publish_task(
            project_id, actor, str(task_id), body.expected_version, idem
        ))

    @app.post("/v1/projects/{project_id}/tasks/{task_id}/claim")
    def claim_task(
        project_id: str, task_id: UUID, body: Versioned,
        idem: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: core.claim_task(
            project_id, actor, str(task_id), body.expected_version, idem
        ))

    @app.post("/v1/projects/{project_id}/tasks/{task_id}/handoffs", status_code=201)
    def offer_handoff(
        project_id: str, task_id: UUID, body: OfferHandoff,
        idem: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: core.offer_handoff(
            project_id, actor, str(task_id), body.to_principal_id,
            body.summary, body.lease_token, body.expected_version, idem,
            checkpoint_id=(str(body.checkpoint_id) if body.checkpoint_id else None),
            expected_checkpoint_seq=body.expected_checkpoint_seq,
        ))

    @app.post("/v1/projects/{project_id}/handoffs/{handoff_id}/accept")
    def accept_handoff(
        project_id: str, handoff_id: UUID, body: Versioned,
        idem: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: core.accept_handoff(
            project_id, actor, str(handoff_id), body.expected_version, idem
        ))

    @app.get("/v1/projects/{project_id}/tasks/{task_id}/lease-status")
    def get_lease_status(
        project_id: str, task_id: UUID,
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: core.get_lease_state(
            project_id, actor, str(task_id),
        ))

    @app.post("/v1/projects/{project_id}/tasks/{task_id}/lease-recovery")
    def recover_lease(
        project_id: str, task_id: UUID, body: RecoverLease,
        idem: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: core.recover_lease(
            project_id, actor, str(task_id),
            body.expected_version, body.expected_generation, idem,
        ))

    @app.post("/v1/projects/{project_id}/tasks/{task_id}/submit")
    def submit_result(
        project_id: str, task_id: UUID, body: SubmitResult,
        idem: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: core.submit_result(
            project_id, actor, str(task_id), body.expected_version,
            body.lease_token, body.evidence_url, idem
        ))

    @app.get("/v1/projects/{project_id}/context")
    def get_project_context(
        project_id: str, query: str = "project context",
        task_id: UUID | None = None, limit: int = 5,
        actor: str = Depends(principal_dep),
    ):
        if not query.strip() or len(query) > 2000 or not 1 <= limit <= 10:
            raise HTTPException(status_code=422, detail="Invalid context request")
        return _invoke(lambda: context_reader.context(
            project_id, actor, query, str(task_id) if task_id else None, limit
        ))

    @app.post("/v1/projects/{project_id}/memories/search")
    def search_project_memory(
        project_id: str, body: MemorySearch,
        actor: str = Depends(principal_dep),
    ):
        try:
            return _invoke(lambda: context_reader.search(
                project_id, actor, body.query, body.limit
            ))
        except SemanticUnavailable:
            raise HTTPException(status_code=503, detail="Semantic memory unavailable") from None

    @app.post("/v1/projects/{project_id}/tasks/{task_id}/runs", status_code=201)
    def start_agent_run(
        project_id: str, task_id: UUID, body: StartAgentRun,
        idem: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: continuity.start_run(
            project_id, actor, str(task_id), body.expected_version,
            body.lease_token, body.runtime_label, idem
        ))

    @app.post("/v1/projects/{project_id}/sources", status_code=201)
    def register_source(
        project_id: str, body: RegisterSource,
        idem: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: continuity.register_source(
            project_id, actor, str(body.task_id), str(body.agent_run_id),
            body.expected_version, body.lease_token, body.source_kind,
            body.source_uri, body.source_revision, body.digest_sha256, idem
        ))

    @app.post("/v1/projects/{project_id}/observations", status_code=201)
    def record_observation(
        project_id: str, body: RecordObservation,
        idem: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: continuity.record_observation(
            project_id, actor, str(body.task_id), str(body.agent_run_id),
            body.expected_version, body.lease_token, body.claim,
            [str(s) for s in body.source_ids], idem
        ))

    @app.get("/v1/projects/{project_id}/tasks/{task_id}/observations")
    def list_task_observations(
        project_id: str, task_id: UUID,
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: continuity.list_observations(
            project_id, actor, str(task_id)
        ))

    @app.post("/v1/projects/{project_id}/tasks/{task_id}/checkpoints", status_code=201)
    def record_checkpoint(
        project_id: str, task_id: UUID, body: RecordCheckpoint,
        idem: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: continuity.record_checkpoint(
            project_id, actor, str(task_id), str(body.agent_run_id),
            body.expected_version, body.lease_token,
            body.expected_checkpoint_seq, body.summary,
            body.next_actions, body.blockers,
            [str(x) for x in body.observation_ids], idem,
        ))

    @app.get("/v1/projects/{project_id}/tasks/{task_id}/resume")
    def resume_task(
        project_id: str, task_id: UUID,
        actor: str = Depends(principal_dep),
    ):
        return _invoke(lambda: continuity.resume_task(
            project_id, actor, str(task_id)
        ))

    if r2_lab_enabled:
        # Experimental adapter: the request cannot choose actor, provider,
        # transport, token, source URL or trust-state. All authority stays in
        # the authenticated ledger and its transaction-time rechecks.
        verification = EvidenceLedger(dsn)

        @app.post("/v1/projects/{project_id}/evidence/{evidence_id}/verify")
        def verify_evidence(
            project_id: str, evidence_id: UUID, body: VerifyEvidence,
            idem: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
            actor: str = Depends(principal_dep),
        ):
            try:
                return _invoke(lambda: verification.verify_and_record(
                    project_id, actor, str(body.policy_id),
                    body.expected_task_version, idem,
                    expected_evidence_id=str(evidence_id),
                ))
            except psycopg.OperationalError:
                raise HTTPException(status_code=503, detail="Verification service unavailable") from None

    return app


# Used by: uvicorn rightware_si.http_api:app --host 127.0.0.1 --port 8890
# Refuses import/start without RW_SI_DATABASE_URL. This is intentional.
app = create_app()
