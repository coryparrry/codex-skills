#!/usr/bin/env python3
"""Tests for the portable Agent Plugins package builder."""

from __future__ import annotations

import filecmp
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

from build_agent_plugin import REPO_ROOT, SOURCE_ROOT, build_agent_plugin  # noqa: E402


class BuildAgentPluginTests(unittest.TestCase):
    def test_builds_clean_portable_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "codex-skills"

            build_agent_plugin(output)

            self.assertEqual(
                sorted(path.name for path in output.iterdir()),
                ["LICENSE", "plugin.json", "skills"],
            )
            self.assertEqual(list(output.glob("skills/*/agents")), [])
            self.assertTrue(
                filecmp.cmp(
                    SOURCE_ROOT / "plugin.json",
                    output / "plugin.json",
                    shallow=False,
                )
            )
            self.assertTrue(
                filecmp.cmp(
                    REPO_ROOT / "LICENSE", output / "LICENSE", shallow=False
                )
            )
            self.assertEqual(
                sorted(path.name for path in (SOURCE_ROOT / "skills").iterdir()),
                sorted(path.name for path in (output / "skills").iterdir()),
            )

    def test_refuses_to_replace_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "codex-skills"
            output.mkdir()

            with self.assertRaises(FileExistsError):
                build_agent_plugin(output)

    def test_includes_portable_mcp_configuration_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            (source / "skills/example").mkdir(parents=True)
            (source / "plugin.json").write_text("{}\n", encoding="utf-8")
            (source / "mcp.json").write_text(
                '{"$schema":"schema","mcpServers":{}}\n', encoding="utf-8"
            )
            (source / "skills/example/SKILL.md").write_text(
                "---\nname: example\ndescription: Example.\n---\n",
                encoding="utf-8",
            )
            license_path = root / "LICENSE"
            license_path.write_text("Example license\n", encoding="utf-8")
            output = root / "output"

            build_agent_plugin(output, source, license_path)

            self.assertTrue(
                filecmp.cmp(source / "mcp.json", output / "mcp.json", shallow=False)
            )


if __name__ == "__main__":
    unittest.main()
