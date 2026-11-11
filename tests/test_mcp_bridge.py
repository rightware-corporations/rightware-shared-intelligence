"""MCP 2.x in-memory protocol tests, not a deployed remote MCP acceptance test."""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from mcp import Client
from rightware_si import mcp_bridge


class McpBridgeTests(unittest.IsolatedAsyncioTestCase):
    async def test_sdk_lists_tools_and_dispatches_read_only_get(self):
        with patch.object(mcp_bridge, "_read_api", return_value={
            "id":"00000000-0000-0000-0000-000000000001",
            "status":"READY","version":2
        }) as fn:
            async with Client(mcp_bridge.mcp) as client:
                tools = await client.list_tools()
                names = {t.name for t in tools}
                self.assertIn("get_task",names)
                self.assertIn("get_task_events",names)
                self.assertNotIn("approve_task",names)
                result = await client.call_tool("get_task",{
                    "project_id":"alpha",
                    "task_id":"00000000-0000-0000-0000-000000000001",
                })
                self.assertFalse(result.is_error)
                self.assertIn("READY",str(result))
                fn.assert_called_once()

    def test_read_api_rejects_missing_token(self):
        with patch.dict(os.environ,{"RW_SI_API_TOKEN":"",
                                   "RW_SI_API_URL":"http://127.0.0.1:8890"}):
            with self.assertRaises(RuntimeError):
                mcp_bridge._read_api("/v1/projects/alpha/tasks/example")

    def test_non_https_remote_backend_rejected(self):
        with patch.dict(os.environ,{"RW_SI_API_URL":"http://example.org:8890"}):
            with self.assertRaises(RuntimeError):
                mcp_bridge._base_url()

    def test_credential_in_origin_rejected(self):
        with patch.dict(os.environ,{"RW_SI_API_URL":"https://x:secret@example.org"}):
            with self.assertRaises(RuntimeError):
                mcp_bridge._base_url()


if __name__=="__main__":
    unittest.main()
