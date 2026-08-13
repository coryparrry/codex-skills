#!/usr/bin/env python3
"""Tests for the deep-review report contract."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPORT_FORMAT = Path(__file__).resolve().parents[1] / "references/report-format.md"


class ReportContractTests(unittest.TestCase):
    def test_every_audit_effect_has_a_snapshot_risk_state(self) -> None:
        report = REPORT_FORMAT.read_text(encoding="utf-8")
        effects_match = re.search(r"Audit effect: ([^\n]+)", report)
        risks_match = re.search(r"snapshot risk: ([^`]+)", report)
        self.assertIsNotNone(effects_match)
        self.assertIsNotNone(risks_match)

        effects = {value.strip() for value in effects_match.group(1).split("|")}
        risks = {value.strip() for value in risks_match.group(1).split("|")}
        expected_states = {
            "blocker": "blockers found",
            "material": "material findings found",
            "minor": "minor findings found",
        }

        self.assertEqual(effects, set(expected_states))
        self.assertTrue(set(expected_states.values()).issubset(risks))
        self.assertIn("no validated findings in completed scope", risks)


if __name__ == "__main__":
    unittest.main()
