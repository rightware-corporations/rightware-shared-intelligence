"""RIGHTWARE Shared Intelligence experimental Python integration layer.

No externally hosted LLM, persistent database or real MCP server starts on import.
"""
from .memory import HandoffClaim, MemoryScope, Mem0HTTPClient, SharedMemory

__all__ = ["HandoffClaim", "MemoryScope", "Mem0HTTPClient", "SharedMemory"]
