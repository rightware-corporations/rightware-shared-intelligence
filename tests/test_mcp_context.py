"""MCP read-only project context tool contract (in-memory SDK client)."""
from __future__ import annotations
import unittest
from unittest.mock import patch
from mcp import Client

from rightware_si import mcp_bridge


class ContextToolTest(unittest.IsolatedAsyncioTestCase):
    async def test_context_tool_exists_and_uses_same_http_policy(self):
        with patch.object(mcp_bridge,"_read_api",
            return_value={"memory_status":"disabled","memories":[],
                          "source_of_truth":"postgresql"}) as api:
            async with Client(mcp_bridge.mcp) as client:
                listing=await client.list_tools()
                names={tool.name for tool in listing.tools}
                self.assertIn("get_project_context",names)
                self.assertNotIn("write_memory",names)
                self.assertNotIn("approve_decision",names)
                r=await client.call_tool("get_project_context",
                    {"project_id":"alpha","query":"continuation"})
                self.assertFalse(r.is_error)
                self.assertIn("disabled",str(r))
                self.assertEqual(api.call_count,1)
                self.assertIn("/v1/projects/alpha/context?query=continuation",
                              api.call_args.args[0])


if __name__=="__main__":
    unittest.main()
