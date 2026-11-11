"""Explicit real Mem0 + local Ollama/pgvector smoke. NOT part of normal CI.

This script performs writes with SYNTHETIC data only. It requires a separate
lab Mem0 service and isolated project namespaces. Never use production keys.
"""
from __future__ import annotations

import os
import sys
from uuid import uuid4

from rightware_si.memory import Mem0HTTPClient, MemoryScope, SharedMemory


def main():
    base=os.environ["RW_SI_MEM0_URL"]
    key=os.environ["RW_SI_MEM0_API_KEY"]
    if base not in ("http://127.0.0.1:8891","http://localhost:8891"):
        raise RuntimeError("smoke requires a dedicated loopback Mem0 lab at :8891")
    memory=SharedMemory(Mem0HTTPClient(base,key))
    nonce=uuid4().hex[:12]
    scope_a=MemoryScope("rwlab",f"alpha-{nonce}")
    scope_b=MemoryScope("rwlab",f"beta-{nonce}")
    message=f"RIGHTWARE synthetic WORK-02C memory proof {nonce}: handoff pending."
    a=memory.add(scope_a,"agent-a",message,source="synthetic-work02c")
    b=memory.add(scope_b,"agent-b",f"Private Beta synthetic marker {nonce}")
    rows=memory.search(scope_a,nonce,limit=10)
    if not any(nonce in x.get("memory","") for x in rows):
        raise AssertionError("Mem0 did not retrieve the synthetic memory")
    if any(x.get("user_id")!=scope_a.mem0_user_id for x in rows):
        raise AssertionError("cross-project Mem0 memory leak")
    if any("Private Beta" in x.get("memory","") for x in rows):
        raise AssertionError("unexpected Beta content")
    print("REAL_MEM0_SMOKE_PASS",f"scope_a={scope_a.mem0_user_id}",
          f"retrieved={len(rows)}","synthetic_only=true")
    print("WARNING: This does not certify production isolation or retrieval accuracy.")


if __name__=="__main__":
    try:
        main()
    except Exception as e:
        print(f"REAL_MEM0_SMOKE_FAIL ({type(e).__name__})",file=sys.stderr)
        raise SystemExit(1) from None
