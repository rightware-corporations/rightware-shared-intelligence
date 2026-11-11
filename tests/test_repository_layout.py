"""WORK-03A architecture/layout regression checks (no network or model)."""
from pathlib import Path
import importlib
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RepositoryLayoutTests(unittest.TestCase):
    def test_backend_python_package_is_installed_from_backend(self):
        package = importlib.import_module("rightware_si")
        directory = Path(package.__file__).resolve().parent
        self.assertEqual(directory, ROOT / "backend" / "rightware_si")
        self.assertFalse((ROOT / "rightware_si").exists())

    def test_authoritative_sql_migrations_are_under_database(self):
        migrations = ROOT / "database" / "migrations"
        self.assertEqual(
            sorted(p.name for p in migrations.glob("*.sql")),
            ["0001_work02_core.sql", "0002_work02b_api_credentials.sql",
             "0003_work02d_scrub_lease_replays.sql"],
        )
        self.assertFalse((ROOT / "db" / "migrations").exists())

    def test_package_configuration_matches_module_location(self):
        with (ROOT / "pyproject.toml").open("rb") as stream:
            pyproject = tomllib.load(stream)
        self.assertEqual(pyproject["tool"]["setuptools"]["package-dir"][""], "backend")
        self.assertEqual(pyproject["tool"]["setuptools"]["packages"]["find"]["where"], ["backend"])

    def test_single_current_workflow_and_pinned_vendor(self):
        self.assertEqual(
            sorted(p.name for p in (ROOT / ".github" / "workflows").glob("*.yml")),
            ["ci.yml"],
        )
        self.assertTrue((ROOT / "vendor" / "mem0").is_dir())
        self.assertTrue((ROOT / "docs" / "HANDOFF_MASTER.md").is_file())
        self.assertTrue((ROOT / "docs" / "HANDOFF.md").is_file())


if __name__ == "__main__":
    unittest.main()
