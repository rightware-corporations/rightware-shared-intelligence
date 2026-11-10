import unittest

from rightware_si.memory import (
    HandoffClaim, MemoryScope, MemoryScopeError, Mem0HTTPClient, SharedMemory,
)


class FakeMem0:
    """Deterministic fake: not an integration test of the real Mem0 server."""
    def __init__(self):
        self.rows = []
        self.calls = []

    def post(self, path, payload):
        self.calls.append((path, payload))
        if path == "/memories":
            row = {
                "id": str(len(self.rows) + 1),
                "memory": payload["messages"][0]["content"],
                "user_id": payload["user_id"],
                "agent_id": payload["agent_id"],
                "metadata": payload["metadata"],
            }
            self.rows.append(row)
            return {"results": [{"id": row["id"]}]}
        if path == "/search":
            expected = payload["filters"]["user_id"]
            return {"results": [
                r for r in self.rows if r["user_id"] == expected
            ][:payload["top_k"]]}
        raise AssertionError(f"unexpected path {path}")


class SharedMemoryTests(unittest.TestCase):
    def test_two_agents_share_one_project(self):
        fake = FakeMem0()
        memory = SharedMemory(fake)
        scope = MemoryScope("rightware", "jarvis")
        memory.handoff(scope, HandoffClaim("WORK04", "claude", "Unit tests prepared"))
        results = memory.search(scope, "What did Claude leave?")
        self.assertEqual(len(results), 1)
        self.assertIn("Unit tests prepared", results[0]["memory"])
        self.assertEqual(fake.calls[0][1]["infer"], False)
        self.assertEqual(results[0]["user_id"], "rw:rightware:jarvis")

    def test_project_isolation_on_filter(self):
        fake = FakeMem0()
        memory = SharedMemory(fake)
        memory.add(MemoryScope("rightware", "jarvis"), "claude", "Jarvis context")
        memory.add(MemoryScope("rightware", "pulse"), "gpt", "PULSE context")
        results = memory.search(MemoryScope("rightware", "jarvis"), "context")
        self.assertEqual(len(results), 1)
        self.assertIn("Jarvis", results[0]["memory"])

    def test_cross_project_upstream_response_fails_closed(self):
        class BadFake:
            def post(self, path, payload):
                return {"results": [{"user_id": "rw:rightware:pulse", "memory": "secret"}]}
        with self.assertRaises(MemoryScopeError):
            SharedMemory(BadFake()).search(MemoryScope("rightware", "jarvis"), "test")

    def test_invalid_identifiers_rejected(self):
        for project in ("", "../jarvis", "wrong:project", "x y"):
            with self.subTest(project=project), self.assertRaises(ValueError):
                MemoryScope("rightware", project)

    def test_unverified_handoff(self):
        fake = FakeMem0()
        SharedMemory(fake).handoff(
            MemoryScope("rightware", "jarvis"),
            HandoffClaim("WORK04", "claude", "I finished", "https://github.com/x/y/pull/1"),
        )
        metadata = fake.rows[0]["metadata"]
        self.assertEqual(metadata["rw_claim_state"], "unverified")
        self.assertEqual(metadata["rw_kind"], "handoff_claim")

    def test_client_rejects_plain_http_remote(self):
        with self.assertRaises(ValueError):
            Mem0HTTPClient("http://mem0.example.com", "x" * 32)

    def test_client_rejects_unsafe_base_url(self):
        with self.assertRaises(ValueError):
            Mem0HTTPClient("https://foo:secret@example.com", "x" * 32)

    def test_handoff_rejects_http_evidence_url(self):
        with self.assertRaises(ValueError):
            HandoffClaim("TASK1", "claude", "done", "http://example.com/ref")


if __name__ == "__main__":
    unittest.main()
