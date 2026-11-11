"""Standalone Jarvis-independent reader tests; no live Jarvis usage."""
import unittest
from unittest.mock import patch
import httpx

from rightware_si.client_readonly import read_task


class FakeResponse:
    status_code=200
    def json(self):
        return {"id":"00000000-0000-0000-0000-000000000001",
                "status":"READY","version":2}


class ClientTests(unittest.TestCase):
    @patch("rightware_si.client_readonly.httpx.Client")
    def test_reads_task_without_writes(self, client):
        client.return_value.__enter__.return_value.get.return_value=FakeResponse()
        r=read_task("alpha","00000000-0000-0000-0000-000000000001",
            api_url="http://127.0.0.1:8890",token="rwsi_"+"x"*60)
        self.assertEqual(r["status"],"READY")
        self.assertEqual(client.return_value.__enter__.return_value.get.call_count,1)
        self.assertEqual(client.return_value.__enter__.return_value.post.call_count,0)

    def test_remote_http_denied(self):
        with self.assertRaises(ValueError):
            read_task("alpha","00000000-0000-0000-0000-000000000001",
                      api_url="http://untrusted.example",token="rwsi_"+"x"*60)


if __name__=="__main__":
    unittest.main()
