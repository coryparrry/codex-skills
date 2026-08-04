#!/usr/bin/env python3
"""Regression checks for availability-aware research instructions."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]


class RuntimeAvailabilityTests(unittest.TestCase):
    def test_research_skills_allow_bounded_root_only_audits(self) -> None:
        for relative_path in (
            "skills/research-repo-technology/SKILL.md",
            "skills/continue-deep-research/SKILL.md",
        ):
            contents = (REPO / relative_path).read_text()
            self.assertIn("Do not refuse research solely", contents)
            self.assertIn("bounded root-only audit", contents)
            self.assertNotIn("Requires the root parent agent", contents)
            self.assertNotIn("If Luna Max or subagent tools are unavailable, stop", contents)


if __name__ == "__main__":
    unittest.main()
