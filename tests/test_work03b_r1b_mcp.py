"""MCP read-only resume tool invokes the REST authorization boundary."""
import unittest
from unittest.mock import patch

from mcp import Client
from rightware_si import mcp_bridge


class McpResumeContract(unittest.IsolatedAsyncioTestCase):
    async def test_resume_only_delegates_to_read_only_rest(self):
        data = {
            "snapshot_status": "CHECKPOINT_AVAILABLE",
            "source_of_truth": "postgresql",
            "verified_completion": False, "read_only": True,
            "checkpoint": {"checkpoint_seq": 1, "trust_state": "ASSERTED"},
        }
        with patch.object(mcp_bridge, "_read_api", return_value=data) as fn:
            async with Client(mcp_bridge.mcp) as client:
                listing = await client.list_tools()
                names = {item.name for item in listing.tools}
                self.assertIn("resume_task", names)
                self.assertNotIn("record_checkpoint", names)
                self.assertNotIn("accept_handoff", names)
                result = await client.call_tool("resume_task", {
                    "project_id":"alpha",
                    "task_id":"00000000-0000-0000-0000-000000000001",
                })
                self.assertFalse(result.is_error)
                self.assertIn("CHECKPOINT_AVAILABLE", str(result))
                fn.assert_called_once_with(
                    "/v1/projects/alpha/tasks/"
                    "00000000-0000-0000-0000-000000000001/resume"
                )

    async def test_rejected_malformed_identifier_does_not_call_rest(self):
        with patch.object(mcp_bridge, "_read_api") as fn:
            async with Client(mcp_bridge.mcp) as client:
                response = await client.call_tool("resume_task", {
                    "project_id":"", "task_id":"x",
                })
                self.assertTrue(response.is_error)
                fn.assert_not_called()


if __name__=="__main__":
    unittest.main()
