#!/usr/bin/env python3
"""Tests for the deep-review report contract."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPORT_FORMAT = Path(__file__).resolve().parents[1] / "references/report-format.md"
SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
DURABLE_STATE = (
    Path(__file__).resolve().parents[1] / "references/durable-review-state.md"
)


class ReportContractTests(unittest.TestCase):
    def test_large_reviews_load_the_durable_state_protocol(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")

        self.assertIn("For every snapshot audit, multi-agent review", skill)
        self.assertIn("[durable-review-state.md]", skill)
        self.assertIn("Checkpoint after every bounded evidence slice", skill)
        self.assertIn("actively fan out genuinely non-overlapping", skill)
        self.assertIn("delegate independent lanes in parallel waves", skill)

    def test_durable_state_is_lane_owned_and_summary_only(self) -> None:
        contract = DURABLE_STATE.read_text(encoding="utf-8")

        self.assertIn("owns exactly one lane file", contract)
        self.assertIn("Never allow concurrent writers on one file", contract)
        self.assertIn("at most eight newly opened files", contract)
        self.assertIn("must not read all lane checkpoints", contract)
        self.assertIn("at most 300 words", contract)
        self.assertIn("Use parallel agents as a context boundary", contract)
        self.assertIn("should create nested lane files", contract)

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
