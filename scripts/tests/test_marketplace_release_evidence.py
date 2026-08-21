#!/usr/bin/env python3
"""Tests for the Codex marketplace release-evidence receipt."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts/marketplace_release_evidence.py"


class MarketplaceReleaseEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary_directory.name) / "repo"
        self._write_fixture()
        self._git("add", ".")
        self._git("commit", "-qm", "initial")
        self.base = self._git("rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _git(self, *arguments: str) -> str:
        result = subprocess.run(
            ["git", *arguments],
            cwd=self.repo,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def _write_json(self, path: str, value: object) -> None:
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def _write_fixture(self) -> None:
        shutil.copytree(
            REPO_ROOT,
            self.repo,
            ignore=shutil.ignore_patterns(".git", "__pycache__"),
        )
        self._git("init", "-q")
        self._git("config", "user.email", "marketplace-tests@example.com")
        self._git("config", "user.name", "Marketplace Tests")

    def _run(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(self.repo), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def _receipt(self, *arguments: str) -> dict[str, object]:
        result = self._run(*arguments)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_pr_shipped_change_requires_local_refresh(self) -> None:
        skill = self.repo / "skills/deep-code-review/SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nChanged.\n", encoding="utf-8")
        mirror = self.repo / "plugins/codex-skills/skills/deep-code-review/SKILL.md"
        mirror.write_text(skill.read_text(encoding="utf-8"), encoding="utf-8")
        for path in (
            "plugins/codex-skills/.codex-plugin/plugin.json",
            "plugins/codex-skills/plugin.json",
        ):
            data = json.loads((self.repo / path).read_text(encoding="utf-8"))
            data["version"] = "0.19.0"
            self._write_json(path, data)
        self._git("add", ".")
        self._git("commit", "-qm", "ship alpha")
        receipt = self._receipt("--event", "pull_request", "--base-ref", self.base)
        self.assertEqual(
            receipt["local_codex_refresh_status"], "required_after_merge"
        )
        self.assertTrue(receipt["shipped_plugin_content_changed"])
        self.assertFalse(receipt["local_codex_refresh_verified"])
        self.assertEqual(receipt["plugin"]["version"], "0.19.0")
        self.assertEqual(receipt["marketplace"]["source"]["source"], "local")

    def test_pr_non_shipped_change_needs_no_plugin_refresh(self) -> None:
        (self.repo / "docs.md").write_text("Documentation.\n", encoding="utf-8")
        self._git("add", "docs.md")
        self._git("commit", "-qm", "docs")
        receipt = self._receipt("--event", "pull_request", "--base-ref", self.base)
        self.assertEqual(receipt["local_codex_refresh_status"], "not_required_for_change")
        self.assertFalse(receipt["shipped_plugin_content_changed"])

    def test_push_binds_exact_commit_but_not_local_refresh(self) -> None:
        head = self._git("rev-parse", "HEAD")
        receipt = self._receipt(
            "--event",
            "push",
            "--head-commit",
            head,
            "--ref",
            "refs/heads/main",
        )
        self.assertEqual(receipt["tested_commit"], head)
        self.assertEqual(receipt["repository_candidate_status"], "valid")
        self.assertFalse(receipt["local_codex_refresh_verified"])
        self.assertEqual(receipt["local_codex_refresh_status"], "unknown")

    def test_manifest_version_mismatch_fails(self) -> None:
        path = self.repo / "plugins/codex-skills/plugin.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["version"] = "0.2.0"
        self._write_json(str(path.relative_to(self.repo)), data)
        result = self._run(
            "--event", "pull_request", "--base-ref", self.base
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Codex and Agent Plugins manifest version must match", result.stderr
        )

    def test_marketplace_identity_and_source_fields_fail(self) -> None:
        path = self.repo / ".agents/plugins/marketplace.json"
        original = json.loads(path.read_text(encoding="utf-8"))
        cases = {
            "name": lambda value: value.update(name="wrong"),
            "plugin name": lambda value: value["plugins"][0].update(name="wrong"),
            "source source": lambda value: value["plugins"][0]["source"].update(source="git"),
            "source path": lambda value: value["plugins"][0]["source"].update(path="./wrong"),
            "policy": lambda value: value["plugins"][0]["policy"].update(installation="DENIED"),
        }
        for label, mutate in cases.items():
            with self.subTest(label=label):
                value = json.loads(json.dumps(original))
                mutate(value)
                self._write_json(str(path.relative_to(self.repo)), value)
                result = self._run(
                    "--event", "pull_request", "--base-ref", self.base
                )
                self.assertNotEqual(result.returncode, 0)
                path.write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8")

    def test_mirror_or_catalogue_failure_fails(self) -> None:
        (self.repo / "plugins/codex-skills/skills/deep-code-review/SKILL.md").unlink()
        result = self._run(
            "--event", "pull_request", "--base-ref", self.base
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("plugin mirror missing skill", result.stderr)

        self._write_fixture_skill_mirror()
        data = json.loads((self.repo / "skills.sh.json").read_text(encoding="utf-8"))
        data["groupings"][0]["skills"] = []
        self._write_json("skills.sh.json", data)
        result = self._run(
            "--event", "pull_request", "--base-ref", self.base
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("skills.sh grouping 0 has no skills", result.stderr)

    def _write_fixture_skill_mirror(self) -> None:
        mirror = self.repo / "plugins/codex-skills/skills/deep-code-review"
        mirror.mkdir(parents=True, exist_ok=True)
        source = self.repo / "skills/deep-code-review/SKILL.md"
        (mirror / "SKILL.md").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    def test_invalid_base_or_commit_evidence_fails(self) -> None:
        result = self._run("--event", "pull_request")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires --base-ref", result.stderr)
        result = self._run("--event", "pull_request", "--base-ref", "missing-ref")
        self.assertNotEqual(result.returncode, 0)
        result = self._run(
            "--event",
            "push",
            "--head-commit",
            "0" * 40,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_workflow_dispatch_without_base_is_unknown_manual_snapshot(self) -> None:
        receipt = self._receipt("--event", "workflow_dispatch")
        self.assertIsNone(receipt["base_ref"])
        self.assertEqual(receipt["local_codex_refresh_status"], "unknown")

    def test_output_write_failure_is_nonzero(self) -> None:
        result = self._run(
            "--event",
            "workflow_dispatch",
            "--output",
            str(self.repo / "missing" / "receipt.json"),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No such file", result.stderr)


if __name__ == "__main__":
    unittest.main()
