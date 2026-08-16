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
MODEL_PROFILES = (
    Path(__file__).resolve().parents[1]
    / "references/model-and-reasoning-profiles.md"
)
LUNA_MAX_PROTOCOL = (
    Path(__file__).resolve().parents[1]
    / "references/luna-max-whole-repository-audit.md"
)


class ReportContractTests(unittest.TestCase):
    def test_review_starts_with_model_and_reasoning_calibration(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")

        calibration = skill.index("## 0. Calibrate the active reviewer")
        state_binding = skill.index("## 1. Bind the review to an exact state")
        self.assertLess(calibration, state_binding)
        self.assertIn("Before inspecting the repository", skill)
        self.assertIn("ask one concise blocking question", skill)
        self.assertIn("coordinator model and reasoning level", skill)
        self.assertIn("[model-and-reasoning-profiles.md]", skill)

    def test_model_profiles_preserve_review_standards(self) -> None:
        contract = MODEL_PROFILES.read_text(encoding="utf-8")

        self.assertIn("Reasoning level changes scheduling and context control only", contract)
        self.assertIn("Strict Luna/max protocol", contract)
        self.assertIn("[luna-max-whole-repository-audit.md]", contract)
        self.assertIn("controlling orchestration contract", contract)

    def test_model_profiles_resolve_every_advertised_selection(self) -> None:
        contract = MODEL_PROFILES.read_text(encoding="utf-8")

        family_rows = {
            match.group("family"): {
                "fanout": match.group("fanout").strip(),
                "nesting": match.group("nesting").strip(),
                "subagents": match.group("subagents").strip(),
            }
            for match in re.finditer(
                r"^\| (?P<family>Luna|Terra|Sol) \| (?P<fanout>[^|]+) \| "
                r"(?P<nesting>[^|]+) \| (?P<subagents>[^|]+) \|",
                contract,
                re.MULTILINE,
            )
        }
        self.assertEqual(set(family_rows), {"Luna", "Terra", "Sol"})

        reasoning_rows = {}
        for match in re.finditer(
            r"^\| `(?P<reasoning>low|medium|high|xhigh|max|ultra)` \| "
            r"(?P<files>\d+) files or (?P<lines>[\d,]+) lines \| "
            r"(?P<validation>[^|]+) \|$",
            contract,
            re.MULTILINE,
        ):
            reasoning_rows[match.group("reasoning")] = {
                "files": int(match.group("files")),
                "lines": int(match.group("lines").replace(",", "")),
                "validation": match.group("validation").strip(),
            }

        advertised = {
            "Luna": {"low", "medium", "high", "xhigh", "max"},
            "Terra": {"low", "medium", "high", "xhigh", "max", "ultra"},
            "Sol": {"low", "medium", "high", "xhigh", "max", "ultra"},
        }
        self.assertEqual(set(reasoning_rows), set().union(*advertised.values()))

        for family, reasoning_levels in advertised.items():
            for reasoning in reasoning_levels:
                with self.subTest(family=family, reasoning=reasoning):
                    profile = reasoning_rows[reasoning]
                    self.assertTrue(family_rows[family]["fanout"])
                    self.assertTrue(family_rows[family]["nesting"])
                    self.assertTrue(family_rows[family]["subagents"])
                    self.assertGreater(profile["files"], 0)
                    self.assertGreater(profile["lines"], 0)
                    self.assertTrue(profile["validation"])

        for family in ("Luna", "Terra", "Sol"):
            with self.subTest(family=family):
                self.assertIn("No skill-imposed cap", family_rows[family]["fanout"])
                self.assertIn("Permitted", family_rows[family]["nesting"])
        self.assertEqual(
            family_rows["Luna"]["subagents"],
            "Luna at `max` for every descendant; no model or effort fallback.",
        )
        for family in ("Terra", "Sol"):
            with self.subTest(family=family):
                self.assertIn(
                    "Risk-routed across Luna, Terra, and Sol",
                    family_rows[family]["subagents"],
                )
        self.assertEqual(reasoning_rows["max"]["files"], 8)
        self.assertEqual(reasoning_rows["max"]["lines"], 2000)
        self.assertIn("every available worker slot after reserving the coordinator", contract)

    def test_luna_descendants_are_luna_max_only(self) -> None:
        contract = MODEL_PROFILES.read_text(encoding="utf-8")

        routes = {
            match.group("model"): {
                "risk": match.group("risk").strip(),
                "effort": match.group("effort"),
            }
            for match in re.finditer(
                r"^\| (?P<risk>[^|]+) \| `(?P<model>gpt-5\.6-(?:luna|terra|sol))` "
                r"\| `(?P<effort>[^`]+)` \|",
                contract,
                re.MULTILINE,
            )
        }

        self.assertEqual(set(routes), {
            "gpt-5.6-luna",
            "gpt-5.6-terra",
            "gpt-5.6-sol",
        })
        self.assertEqual(routes["gpt-5.6-luna"]["effort"], "max")
        self.assertEqual(routes["gpt-5.6-terra"]["effort"], "high")
        self.assertEqual(routes["gpt-5.6-sol"]["effort"], "high")
        policy_rule = next(
            line for line in contract.splitlines() if line.startswith("For any Luna coordinator")
        )
        self.assertIn("Mixed-model policy: prohibited; Luna/max descendants only", policy_rule)
        self.assertIn("hard invariant, not a user-configurable default", policy_rule)
        luna_rule = next(
            line for line in contract.splitlines() if line.startswith("2. For every Luna coordinator")
        )
        self.assertIn("model: gpt-5.6-luna", luna_rule)
        self.assertIn("reasoning_effort: max", luna_rule)
        self.assertIn("Never inherit, infer, or substitute another model or effort", luna_rule)
        self.assertNotIn("gpt-5.6-terra", luna_rule)
        self.assertNotIn("gpt-5.6-sol", luna_rule)
        self.assertIn("Do not apply this mixed-model rule to a Luna coordinator", contract)
        self.assertIn("This matrix never applies to a Luna coordinator", contract)
        self.assertIn("preserve the family selected by the risk matrix", contract)
        self.assertIn("elevate a routed Terra or Sol specialist to `ultra`", contract)
        critical_rule = next(
            line for line in contract.splitlines() if line.startswith("For a critical-risk lane")
        )
        fallback_rule = critical_rule.split("then fall back in order to ", maxsplit=1)[1]
        fallback = [
            fallback_rule.index(label) for label in ("`max`", "`xhigh`", "`high`")
        ]
        self.assertEqual(fallback, sorted(fallback))
        skill_routing = next(
            line for line in SKILL.read_text(encoding="utf-8").splitlines()
            if line.startswith("When independent subagents are available")
        )
        self.assertIn("For a Luna coordinator", skill_routing)
        self.assertIn("`gpt-5.6-luna` at `max`", skill_routing)
        self.assertIn("never substitute another model or effort", skill_routing)

        luna_protocol = LUNA_MAX_PROTOCOL.read_text(encoding="utf-8")
        descendant_rule = next(
            line for line in luna_protocol.splitlines()
            if line.startswith("Nested delegation is permitted")
        )
        self.assertIn("Every descendant must be explicitly created as Luna at `max`", descendant_rule)
        self.assertIn("model: gpt-5.6-luna", descendant_rule)
        self.assertIn("reasoning_effort: max", descendant_rule)
        self.assertNotIn("gpt-5.6-terra", descendant_rule)
        self.assertNotIn("gpt-5.6-sol", descendant_rule)
        self.assertIn("mixed-model policy fixed to `prohibited; Luna/max descendants only`", luna_protocol)
        self.assertNotIn("a Luna coordinator may create Luna, Terra, or Sol descendants", luna_protocol)

    def test_luna_max_protocol_defines_exact_durable_state(self) -> None:
        contract = LUNA_MAX_PROTOCOL.read_text(encoding="utf-8")

        for state_file in (
            "STATE.json",
            "STATUS.md",
            "COVERAGE.tsv",
            "FINDINGS.md",
            "CANDIDATES.md",
            "REJECTED.md",
            "FINAL_REPORT.md",
        ):
            self.assertIn(state_file, contract)
        self.assertIn("path\tclassification\tprimary_lane\tstatus\tnotes", contract)
        self.assertIn("Only the coordinator may edit the seven shared files", contract)
        self.assertIn("Continue only from the recorded exact next action", contract)

    def test_luna_max_protocol_is_a_phase_gated_state_machine(self) -> None:
        contract = LUNA_MAX_PROTOCOL.read_text(encoding="utf-8")

        phases = [
            "## Phase 1: repository inventory",
            "## Phase 2: discovery lanes",
            "## Phase 3: cross-boundary investigation",
            "## Phase 4: independent candidate validation",
            "## Phase 5: final synthesis",
        ]
        positions = [contract.index(phase) for phase in phases]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("Do not impose a skill-level limit", contract)
        self.assertIn("Permit nested Luna/max delegation", contract)
        self.assertIn("Continue creating disjoint Luna/max lanes", contract)
        self.assertNotIn("Run no more than four subagents concurrently", contract)
        self.assertNotIn("Do not allow nested delegation", contract)
        self.assertIn("Coordinator duties after every result", contract)
        self.assertIn("Only then process another result", contract)
        self.assertIn("Required validation return", contract)
        self.assertIn("Checkpoint after at most eight newly opened files", contract)
        self.assertIn("handoff of at most 300 words", contract)
        self.assertIn("The audit is complete only when all conditions are true", contract)

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
        self.assertIn("may create nested lane files", contract)

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
