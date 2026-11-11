"""WORK-02B FastAPI gateway for the trusted PostgreSQL transactional core.

Experimental and single-organization/pilot only. No Mem0 indexing or Jarvis
integration. Server cannot start without RW_SI_DATABASE_URL. Every protected
request resolves its actor from a high-entropy bearer token, not JSON.
"""
from __future__ import annotations

import os
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from rightware_si.api_auth import make_principal_dependency
from rightware_si.core import AccessDenied, Conflict, InvalidTransition, Missing, WorkCore


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateTask(StrictModel):
    title: str = Field(min_length=1, max_length=200)
    acceptance_criteria: list[str] = Field(min_length=1, max_length=30)


class Versioned(StrictModel):
    expected_version: int = Field(gt=0, strict=True)


class OfferHandoff(Versioned):
    to_principal_id: str = Field(min_length=1, max_length=64)
    summary: str = Field(min_length=1, max_length=8000)
    lease_token: str = Field(min_length=20, max_length=256)


class SubmitResult(Versioned):
    lease_token: str = Field(min_length=20, max_length=256)
    evidence_url: str = Field(min_length=10, max_length=2048)


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


def create_app(dsn: str | None = None) -> FastAPI:
    dsn = dsn or os.environ.get("RW_SI_DATABASE_URL")
    if not dsn:
        raise RuntimeError("RW_SI_DATABASE_URL is required; refusing to start unconfigured")
    core = WorkCore(dsn)
    principal_dep = make_principal_dependency(dsn)
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
            body.summary, body.lease_token, body.expected_version, idem
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

    return app


# Used by: uvicorn rightware_si.http_api:app --host 127.0.0.1 --port 8890
# Refuses import/start without RW_SI_DATABASE_URL. This is intentional.
app = create_app()
