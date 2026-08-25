#!/usr/bin/env python3
"""Tests for the release-contract validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_release_contract import (  # noqa: E402
    parse_semver,
    relative_files,
    skill_document_paths,
    changed_paths,
    shipped_plugin_change,
    validate_skills_sh,
    validate_agent_plugin_policy,
    validate_agent_plugin_manifest,
    validate_plugin_manifest,
    validate_marketplace_manifest,
    validate_shared_plugin_identity,
    validate_version_change,
)


class ReleaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.agent_plugin_schema = json.loads(
            (SCRIPTS_DIR / "schemas/agent-plugins/1.0.0/plugin.schema.json").read_text(
                encoding="utf-8"
            )
        )

    def test_parse_semver_orders_numeric_components(self) -> None:
        self.assertLess(parse_semver("0.14.9"), parse_semver("0.15.0"))
        self.assertLess(parse_semver("1.9.9"), parse_semver("2.0.0"))

    def test_parse_semver_rejects_non_semver(self) -> None:
        with self.assertRaises(ValueError):
            parse_semver("v1.2")

    def test_skills_sh_rejects_duplicate_and_stale_entries(self) -> None:
        data = {
            "groupings": [
                {
                    "title": "Review",
                    "description": "Review skills.",
                    "skills": ["alpha", "alpha", "stale"],
                }
            ]
        }
        errors = validate_skills_sh({"alpha", "beta"}, data)
        self.assertIn("skills.sh duplicate skill: alpha", errors)
        self.assertIn("skills.sh stale skill: stale", errors)
        self.assertIn("skills.sh missing skill: beta", errors)

    def test_shipped_plugin_change_detects_release_surfaces(self) -> None:
        self.assertTrue(shipped_plugin_change({"skills/example/SKILL.md"}))
        self.assertTrue(
            shipped_plugin_change(
                {"plugins/codex-skills/.codex-plugin/plugin.json"}
            )
        )
        self.assertTrue(
            shipped_plugin_change({"plugins/codex-skills/plugin.json"})
        )
        self.assertTrue(
            shipped_plugin_change({"plugins/codex-skills/assets/logo.png"})
        )
        self.assertTrue(shipped_plugin_change({"plugins/codex-skills/.app.json"}))
        self.assertTrue(shipped_plugin_change({"plugins/codex-skills/.mcp.json"}))
        self.assertTrue(shipped_plugin_change({"plugins/codex-skills/mcp.json"}))
        self.assertFalse(shipped_plugin_change({"docs/example.md"}))

    def test_shipped_change_requires_a_strict_version_increase(self) -> None:
        changed = {"skills/deep-code-review/SKILL.md"}
        self.assertEqual(
            validate_version_change("1.2.3", "1.2.3", changed),
            [
                "shipped plugin content changed but plugin version did not increase: "
                "1.2.3 -> 1.2.3"
            ],
        )
        self.assertEqual(validate_version_change("1.2.3", "1.2.4", changed), [])
        self.assertEqual(
            validate_version_change("1.2.3", "1.2.3", {"docs/reference.md"}), []
        )

    def test_relative_files_ignores_python_runtime_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "SKILL.md").write_text("skill", encoding="utf-8")
            cache = root / "scripts/__pycache__"
            cache.mkdir(parents=True)
            (cache / "helper.cpython-312.pyc").write_bytes(b"cache")

            self.assertEqual(relative_files(root), {Path("SKILL.md")})

    def test_skill_document_paths_supports_categories_and_finds_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = Path(temporary_directory)
            first = repo / "docs/code-review/deep-code-review.md"
            second = repo / "docs/archive/deep-code-review.md"
            routing = repo / "docs/orchestration/codex-routing.md"
            for path in (first, second, routing):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("docs\n", encoding="utf-8")

            paths = skill_document_paths(
                repo, {"deep-code-review", "codex-routing", "missing-skill"}
            )

            self.assertEqual(
                sorted(paths["deep-code-review"]),
                [
                    Path("docs/archive/deep-code-review.md"),
                    Path("docs/code-review/deep-code-review.md"),
                ],
            )
            self.assertEqual(
                paths["codex-routing"],
                [Path("docs/orchestration/codex-routing.md")],
            )
            self.assertEqual(paths["missing-skill"], [])

    def test_plugin_manifest_rejects_stale_or_incomplete_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manifest = {
                "name": "codex-skills",
                "version": "1.2.3",
                "description": "Skills.",
                "skills": "./skills/",
                "author": {"name": "Maintainer"},
                "interface": {
                    "displayName": "Codex Skills",
                    "shortDescription": "Skills.",
                    "longDescription": "Codex skills.",
                    "developerName": "Maintainer",
                    "category": "Coding",
                    "capabilities": ["Read"],
                    "logo": "./assets/logo.png",
                },
                "unsupported": True,
            }
            errors, version = validate_plugin_manifest(root, manifest)
            self.assertEqual(version, "1.2.3")
            self.assertIn("plugin manifest has unsupported field: unsupported", errors)
            self.assertIn("plugin manifest interface.defaultPrompt is required", errors)
            self.assertIn(
                "plugin manifest logo does not exist: ./assets/logo.png", errors
            )

    def test_agent_plugin_manifest_accepts_official_minimal_shape(self) -> None:
        manifest = {
            "$schema": (
                "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
            ),
            "name": "codex-skills",
        }

        self.assertEqual(
            validate_agent_plugin_manifest(manifest, self.agent_plugin_schema), []
        )

    def test_agent_plugin_manifest_uses_official_closed_schema(self) -> None:
        manifest = {
            "$schema": "https://example.com/plugin.schema.json",
            "name": "Codex--Skills",
            "version": "v1",
            "skills": "./skills/",
            "author": {"organization": "Example", "name": 42},
            "keywords": "agent-skills",
            "extensions": {"com.example.client": True},
        }

        errors = validate_agent_plugin_manifest(manifest, self.agent_plugin_schema)

        self.assertTrue(any("skills" in error for error in errors))
        self.assertTrue(any("Codex--Skills" in error for error in errors))
        self.assertFalse(any("SemVer" in error for error in errors))

    def test_agent_plugin_release_policy_requires_matching_semver(self) -> None:
        errors, version = validate_agent_plugin_policy(
            {"name": "codex-skills", "version": "v1"}
        )
        self.assertEqual(version, "v1")
        self.assertEqual(errors, ["invalid SemVer: v1"])

        errors, version = validate_agent_plugin_policy({"name": "codex-skills"})
        self.assertEqual(version, "")
        self.assertEqual(errors, ["Agent Plugins manifest version is required"])

    def test_shared_plugin_identity_detects_manifest_drift(self) -> None:
        shared = {
            "name": "codex-skills",
            "version": "1.2.3",
            "author": {"name": "Maintainer"},
            "homepage": "https://example.com",
            "repository": "https://example.com/repo",
            "license": "MIT",
        }
        agent = dict(shared)
        agent["repository"] = "https://example.com/other"

        self.assertEqual(
            validate_shared_plugin_identity(shared, agent),
            ["Codex and Agent Plugins manifest repository must match"],
        )

    def test_marketplace_manifest_requires_canonical_identity_and_source(self) -> None:
        marketplace = {
            "name": "codex-skills",
            "plugins": [
                {
                    "name": "codex-skills",
                    "source": {
                        "source": "local",
                        "path": "./plugins/codex-skills",
                    },
                    "policy": {
                        "installation": "AVAILABLE",
                        "authentication": "ON_INSTALL",
                    },
                    "category": "Coding",
                }
            ],
        }
        self.assertEqual(validate_marketplace_manifest(marketplace), [])

        marketplace["name"] = "wrong-marketplace"
        marketplace["plugins"][0]["name"] = "wrong-plugin"
        marketplace["plugins"][0]["source"]["source"] = "git"
        errors = validate_marketplace_manifest(marketplace)
        self.assertIn("marketplace name must be codex-skills", errors)
        self.assertIn("marketplace plugin name must be codex-skills", errors)
        self.assertIn("marketplace source.source must be local", errors)

    def test_changed_paths_includes_non_ignored_untracked_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = Path(temporary_directory)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(
                ["git", "config", "user.email", "tests@example.com"],
                cwd=repo,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Release Tests"],
                cwd=repo,
                check=True,
            )
            (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
            (repo / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "tracked.txt", ".gitignore"], cwd=repo, check=True
            )
            subprocess.run(
                ["git", "commit", "-qm", "initial"], cwd=repo, check=True
            )
            base_ref = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            skill = repo / "skills/new-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("new skill\n", encoding="utf-8")
            (repo / "ignored.txt").write_text("ignored\n", encoding="utf-8")

            changed, errors = changed_paths(repo, base_ref)

            self.assertEqual(errors, [])
            self.assertIn("skills/new-skill/SKILL.md", changed)
            self.assertNotIn("ignored.txt", changed)

    def test_changed_paths_preserves_non_ascii_and_control_characters(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = Path(temporary_directory)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(
                ["git", "config", "user.email", "tests@example.com"],
                cwd=repo,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Release Tests"],
                cwd=repo,
                check=True,
            )
            unusual_path = Path("skills/demo/references/café\nnotes.md")
            absolute_path = repo / unusual_path
            absolute_path.parent.mkdir(parents=True)
            absolute_path.write_text("before\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(
                ["git", "commit", "-qm", "initial"], cwd=repo, check=True
            )
            base_ref = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            absolute_path.write_text("after\n", encoding="utf-8")

            changed, errors = changed_paths(repo, base_ref)

            self.assertEqual(errors, [])
            self.assertIn(unusual_path.as_posix(), changed)
            self.assertTrue(shipped_plugin_change(changed))


if __name__ == "__main__":
    unittest.main()
