"""DB endpoint boundary tests; never open a database connection."""
from __future__ import annotations
import os
import socket
import unittest
from unittest.mock import patch
from rightware_si.lab_boundary import require_disposable_postgres as guard, is_disposable_postgres

GOOD="postgresql://rw:synthetic@127.0.0.1:5432/rw_test"

class LabBoundaryTests(unittest.TestCase):
    def denies(self, uri=GOOD, env=None, user=None):
        with self.assertRaises(RuntimeError):
            guard(uri, environ={} if env is None else env, expected_user=user)

    def test_01_allow_ip_loopback(self):
        guard(GOOD, environ={}, expected_user="rw")

    def test_02_allow_localhost_when_resolved_loopback(self):
        value=[(socket.AF_INET,socket.SOCK_STREAM,0,"",("127.0.0.1",5432))]
        with patch("rightware_si.lab_boundary.socket.getaddrinfo",return_value=value):
            guard(GOOD.replace("127.0.0.1","localhost"),environ={})

    def test_03_reject_localhost_redirected_to_remote(self):
        value=[(socket.AF_INET,socket.SOCK_STREAM,0,"",("203.0.113.9",5432))]
        with patch("rightware_si.lab_boundary.socket.getaddrinfo",return_value=value):
            self.denies(GOOD.replace("127.0.0.1","localhost"))

    def test_04_reject_remote_host(self):
        self.denies(GOOD.replace("127.0.0.1","db.example.test"))

    def test_05_reject_other_db(self):
        self.denies(GOOD.replace("/rw_test","/customer"))

    def test_06_reject_other_port(self):
        self.denies(GOOD.replace(":5432/",":5433/"))

    def test_07_reject_missing_user(self):
        self.denies("postgresql://127.0.0.1:5432/rw_test")

    def test_08_reject_hostaddr_query(self):
        self.denies(GOOD+"?hostaddr=203.0.113.9")

    def test_09_reject_service_query(self):
        self.denies(GOOD+"?service=remote")

    def test_10_reject_fragment(self):
        self.denies(GOOD+"#other")

    def test_11_reject_PGHOSTADDR_env(self):
        self.denies(env={"PGHOSTADDR":"203.0.113.9"})

    def test_12_reject_PGSERVICE_env(self):
        self.denies(env={"PGSERVICE":"remote"})

    def test_13_reject_PGSERVICEFILE_env(self):
        self.denies(env={"PGSERVICEFILE":"/tmp/conf"})

    def test_14_reject_unexpected_username(self):
        self.denies(user="not-rw")

    def test_15_lab_api_rejects_query_override(self):
        with patch.dict(os.environ,{"RW_SI_DATABASE_URL":GOOD,
                   "RW_SI_ENVIRONMENT":"lab","RW_SI_ENABLE_R2_R1C_LAB_API":"1",
                   "PGHOSTADDR":"","PGSERVICE":"","PGSERVICEFILE":""}):
            from rightware_si.http_api import create_app
            with self.assertRaises(RuntimeError):
                create_app(GOOD+"?hostaddr=203.0.113.9")

    def test_16_lab_api_rejects_PGHOSTADDR_override(self):
        with patch.dict(os.environ,{"RW_SI_DATABASE_URL":GOOD,
                   "RW_SI_ENVIRONMENT":"lab","RW_SI_ENABLE_R2_R1C_LAB_API":"1",
                   "PGHOSTADDR":"203.0.113.9","PGSERVICE":"","PGSERVICEFILE":""}):
            from rightware_si.http_api import create_app
            with self.assertRaises(RuntimeError):
                create_app(GOOD)


    def test_17_test_predicate_accepts_only_safe_uri(self):
        self.assertTrue(is_disposable_postgres(GOOD, expected_user="rw", environ={}))
        self.assertFalse(is_disposable_postgres(
            GOOD + "?hostaddr=203.0.113.9", expected_user="rw", environ={}))

    def test_18_test_predicate_blocks_runtime_libpq_env(self):
        self.assertFalse(is_disposable_postgres(
            GOOD, expected_user="rw", environ={"PGHOSTADDR": "203.0.113.9"}))
        self.assertFalse(is_disposable_postgres(
            GOOD, expected_user="rw", environ={"PGSERVICE": "remote"}))

    def test_19_disposable_fixture_guard_rejects_changed_env(self):
        # Collection-time safety is not enough: setUp must check before TRUNCATE.
        with patch.dict(os.environ, {"PGHOSTADDR": "203.0.113.9"}):
            with self.assertRaises(RuntimeError):
                guard(GOOD, expected_user="rw")

    def test_20_all_destructive_fixtures_enforce_use_time_guard(self):
        from pathlib import Path
        names = (
            "test_context_api.py", "test_http_api.py", "test_pg_core.py",
            "test_r2_r1b_ledger.py", "test_work03b_r1a.py",
            "test_work03b_r1b.py", "test_work03b_r1c.py",
        )
        for name in names:
            with self.subTest(name=name):
                source = (Path(__file__).resolve().parent / name).read_text(
                    encoding="utf-8")
                self.assertIn(
                    '_SAFE = is_disposable_postgres(_DSN, expected_user="rw")',
                    source)
                self.assertIn(
                    '        require_disposable_postgres(_DSN, expected_user="rw")',
                    source)

if __name__ == "__main__":
    unittest.main()
