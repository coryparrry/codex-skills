#!/usr/bin/env python3
"""Tests for the release-contract validator."""

from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
