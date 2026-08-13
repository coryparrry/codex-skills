#!/usr/bin/env python3
"""Tests for the release-contract validator."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_release_contract import (  # noqa: E402
    parse_semver,
    parse_skill_frontmatter,
    relative_files,
    changed_paths,
    shipped_plugin_change,
    validate_skills_sh,
    validate_plugin_manifest,
    validate_version_change,
)


class ReleaseContractTests(unittest.TestCase):
    def test_parse_semver_orders_numeric_components(self) -> None:
        self.assertLess(parse_semver("0.14.9"), parse_semver("0.15.0"))
        self.assertLess(parse_semver("1.9.9"), parse_semver("2.0.0"))

    def test_parse_semver_rejects_non_semver(self) -> None:
        with self.assertRaises(ValueError):
            parse_semver("v1.2")

    def test_parse_skill_frontmatter_requires_matching_name(self) -> None:
        text = "---\nname: example-skill\ndescription: Example.\n---\n"
        self.assertEqual(
            parse_skill_frontmatter(text, expected_name="example-skill"),
            [],
        )
        self.assertIn(
            "frontmatter name must be other-skill, got example-skill",
            parse_skill_frontmatter(text, expected_name="other-skill"),
        )

    def test_parse_skill_frontmatter_enforces_catalogue_limits(self) -> None:
        text = (
            "---\n"
            f"name: {'a' * 65}\n"
            "description: Do not use <placeholder> text.\n"
            "unknown: value\n"
            "---\n"
        )
        errors = parse_skill_frontmatter(text, expected_name="a" * 65)
        self.assertIn("frontmatter name must be at most 64 characters", errors)
        self.assertIn("frontmatter description cannot contain angle brackets", errors)
        self.assertIn("unexpected frontmatter field: unknown", errors)

    def test_parse_skill_frontmatter_resolves_folded_yaml_description(self) -> None:
        text = (
            "---\n"
            "name: example-skill\n"
            "description: >-\n"
            "  A valid folded\n"
            "  description.\n"
            "---\n"
        )
        self.assertEqual(parse_skill_frontmatter(text, "example-skill"), [])

    def test_parse_skill_frontmatter_checks_literal_yaml_description(self) -> None:
        text = (
            "---\n"
            "name: example-skill\n"
            "description: |\n"
            "  Hidden <invalid> content.\n"
            "---\n"
        )
        self.assertIn(
            "frontmatter description cannot contain angle brackets",
            parse_skill_frontmatter(text, "example-skill"),
        )

    def test_parse_skill_frontmatter_checks_resolved_description_length(self) -> None:
        text = (
            "---\n"
            "name: example-skill\n"
            "description: |\n"
            f"  {'a' * 1025}\n"
            "---\n"
        )
        self.assertIn(
            "frontmatter description must be at most 1024 characters",
            parse_skill_frontmatter(text, "example-skill"),
        )

    def test_parse_skill_frontmatter_rejects_non_string_values(self) -> None:
        text = "---\nname: 123\ndescription: [not, text]\n---\n"
        errors = parse_skill_frontmatter(text, "example-skill")
        self.assertIn("frontmatter name must be a string", errors)
        self.assertIn("frontmatter description must be a string", errors)

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
            shipped_plugin_change({"plugins/codex-skills/assets/logo.png"})
        )
        self.assertTrue(shipped_plugin_change({"plugins/codex-skills/.app.json"}))
        self.assertTrue(shipped_plugin_change({"plugins/codex-skills/.mcp.json"}))
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
