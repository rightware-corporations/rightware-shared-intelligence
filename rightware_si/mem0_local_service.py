"""Experimental self-hosted Mem0 library REST shim with LOCAL Ollama/pgvector.

Only for isolated labs. Not a replacement for an independently audited Mem0
server or authorization boundary. Must bind to 127.0.0.1, not 0.0.0.0.
Uses pinned vendor/mem0 library; no paid LLM API is configured.
"""
from __future__ import annotations

import hashlib
import os
import re
import secrets
from urllib.parse import urlsplit

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field


_SCOPE = re.compile(r"^rw:[A-Za-z0-9._-]{1,64}:[A-Za-z0-9._-]{1,64}$")


class MemoryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    messages: list[dict[str, str]] = Field(min_length=1, max_length=4)
    user_id: str
    agent_id: str | None = None
    metadata: dict | None = None
    infer: bool = False


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1, max_length=2000)
    filters: dict[str, str]
    top_k: int = Field(default=5, ge=1, le=10)


def _local_origin(url: str) -> bool:
    parsed = urlsplit(url)
    return (
        parsed.scheme == "http"
        and parsed.hostname in ("localhost", "127.0.0.1", "::1")
        and not parsed.username
        and not parsed.password
        and not parsed.query
        and not parsed.fragment
        and parsed.path in ("", "/")
    )


def _local_mem0_from_env():
    """Construct the real Mem0 2.2.1 library with explicit Ollama/pgvector.

    Fail rather than silently auto-pull embedding models or reach hosted APIs.
    Operator must pre-install the chosen embedding model in local Ollama.
    """
    os.environ["MEM0_TELEMETRY"] = "false"
    pg_dsn = os.environ.get("RW_SI_MEM0_PG_DSN", "")
    ollama_url = os.environ.get("RW_SI_OLLAMA_URL", "http://127.0.0.1:11434")
    embed_model = os.environ.get("RW_SI_OLLAMA_EMBED_MODEL", "all-minilm:latest")
    llm_model = os.environ.get("RW_SI_OLLAMA_LLM_MODEL", "qwen3.5:2b")
    dims = int(os.environ.get("RW_SI_OLLAMA_EMBED_DIMS", "384"))
    history = os.environ.get("RW_SI_MEM0_HISTORY", "")
    if not pg_dsn or not history or not _local_origin(ollama_url):
        raise RuntimeError("MEM0 local configuration incomplete or non-loopback Ollama")
    if dims <= 0 or dims > 2048:
        raise RuntimeError("Embedding dimensions outside approved lab bounds")
    from ollama import Client
    models = Client(host=ollama_url).list()["models"]
    available = {
        str(m.get("model") or m.get("name") or "") for m in models
    }
    if embed_model not in available:
        raise RuntimeError("Embedding model is not installed locally; refusing automatic pull")
    # Query dimension at startup to catch model/index mismatch BEFORE any write.
    vector = Client(host=ollama_url).embed(model=embed_model,input="dimension probe")["embeddings"][0]
    if len(vector) != dims:
        raise RuntimeError("Configured embedding dimension mismatch")
    from mem0 import Memory
    config = {
        "version": "v1.1",
        "history_db_path": history,
        "vector_store": {"provider": "pgvector", "config": {
            "connection_string": pg_dsn,
            "collection_name": "rw_si_work02c",
            "embedding_model_dims": dims,
        }},
        "embedder": {"provider": "ollama", "config": {
            "model": embed_model, "embedding_dims": dims,
            "ollama_base_url": ollama_url,
        }},
        "llm": {"provider": "ollama", "config": {
            "model": llm_model,"ollama_base_url": ollama_url,
            "temperature": 0.0,
        }},
    }
    return Memory.from_config(config)


def create_mem0_lab_app(memory=None, api_key: str | None = None) -> FastAPI:
    # Production should have a proper service-to-service identity system.
    key = api_key or os.environ.get("RW_SI_MEM0_API_KEY", "")
    if len(key) < 32:
        raise RuntimeError("RW_SI_MEM0_API_KEY must be an unguessable 32+ character secret")
    app = FastAPI(title="RIGHTWARE Mem0 local lab", docs_url=None, redoc_url=None)
    # Only lazy-load actual model after an authorized request; keeps test CI GPU-free.
    cached = [memory]

    def authorized(x_api_key: str | None = Header(default=None)):
        if not x_api_key or not secrets.compare_digest(
            hashlib.sha256(x_api_key.encode()).digest(),
            hashlib.sha256(key.encode()).digest(),
        ):
            raise HTTPException(status_code=401, detail="Unauthorized")

    def backend():
        if cached[0] is None:
            cached[0] = _local_mem0_from_env()
        return cached[0]

    @app.post("/memories", dependencies=[Depends(authorized)])
    def add(body: MemoryRequest):
        if not _SCOPE.fullmatch(body.user_id) or body.infer is not False:
            raise HTTPException(status_code=422, detail="Scoped infer=false only")
        if not all(
            item.get("role") in ("user","assistant")
            and isinstance(item.get("content"),str)
            and 0 < len(item["content"]) <= 10000
            for item in body.messages
        ):
            raise HTTPException(status_code=422, detail="Invalid messages")
        return backend().add(
            messages=body.messages, user_id=body.user_id,
            agent_id=body.agent_id, metadata=body.metadata or {},
            infer=False,
        )

    @app.post("/search", dependencies=[Depends(authorized)])
    def search(body: SearchRequest):
        scope = body.filters.get("user_id")
        if len(body.filters) != 1 or not isinstance(scope,str) or not _SCOPE.fullmatch(scope):
            raise HTTPException(status_code=422, detail="Scoped filter required")
        return backend().search(query=body.query,filters={"user_id":scope},
                                top_k=body.top_k)
    return app


def main():
    import uvicorn
    # Force loopback only regardless of arbitrary environment host.
    uvicorn.run(create_mem0_lab_app(),host="127.0.0.1",port=8891,log_level="warning")


if __name__ == "__main__":
    main()
