#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REQUIRED_AGENT_KEYS = {"display_name", "short_description", "default_prompt"}
REQUIRED_SKILLS = {
    "codex-packet-loop",
    "codex-packet-loop-core",
    "codex-packet-init",
    "codex-packet-slice",
    "codex-packet-dispatch",
    "codex-packet-worker",
    "codex-packet-review",
    "codex-packet-integrate",
    "codex-packet-maintain",
}
REQUIRED_REFERENCES = {
    "workflow-protocol.md",
    "state-machine.md",
    "autonomy-policy.md",
    "handoff-contracts.md",
    "superpowers-plan-adapter.md",
    "evidence-contract.md",
    "overlap-policy.md",
    "recovery-playbook.md",
    "behavioral-evals.md",
}
STAGE_NEXT_SKILLS = {
    "codex-packet-loop": [
        "codex-packet-init",
        "codex-packet-maintain",
        "codex-packet-review",
        "codex-packet-dispatch",
        "codex-packet-integrate",
        "codex-packet-slice",
    ],
    "codex-packet-init": ["codex-packet-slice", "codex-packet-loop"],
    "codex-packet-slice": ["codex-packet-dispatch", "codex-packet-loop"],
    "codex-packet-dispatch": ["codex-packet-worker"],
    "codex-packet-worker": ["codex-packet-review"],
    "codex-packet-review": ["codex-packet-worker", "codex-packet-integrate"],
    "codex-packet-integrate": ["codex-packet-loop", "codex-packet-maintain"],
    "codex-packet-maintain": [
        "codex-packet-loop",
        "codex-packet-dispatch",
        "codex-packet-review",
        "codex-packet-integrate",
        "codex-packet-slice",
    ],
}
STAGE_REQUIRED_REFERENCES = {
    "codex-packet-loop": ["superpowers-plan-adapter.md"],
    "codex-packet-slice": ["superpowers-plan-adapter.md"],
    "codex-packet-dispatch": ["superpowers-plan-adapter.md"],
    "codex-packet-worker": ["superpowers-plan-adapter.md"],
}
REQUIRED_FIXTURES = {
    "router-finds-next-stage.md",
    "dispatch-blocks-overlap.md",
    "worker-stops-on-scope-expansion.md",
    "review-distrusts-worker-summary.md",
    "maintenance-expires-stale-lease.md",
    "integration-stops-before-merge.md",
    "recovery-reslices-bad-packet.md",
    "controller-supervises-active-workers.md",
    "scheduler-has-no-fixed-worktree-cap.md",
    "validation-lanes-serialize-scarce-tools.md",
    "slicer-emits-valid-superpowers-child-plans.md",
    "worker-executes-child-plan.md",
}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text().splitlines()
    if not lines or lines[0] != "---":
        fail(f"{path} missing frontmatter")
    values: dict[str, str] = {}
    for line in lines[1:]:
        if line == "---":
            return values
        if ":" not in line:
            fail(f"{path} invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    fail(f"{path} unterminated frontmatter")


def parse_simple_openai_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    in_interface = False
    for raw in path.read_text().splitlines():
        line = raw.rstrip()
        if line == "interface:":
            in_interface = True
            continue
        if in_interface and line.startswith("  ") and ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"')
    return values


def validate_skill(skill_dir: Path) -> None:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        fail(f"{skill_dir} missing SKILL.md")
    frontmatter = parse_frontmatter(skill_file)
    expected_name = skill_dir.name
    if frontmatter.get("name") != expected_name:
        fail(f"{skill_file} name must be {expected_name}")
    if not frontmatter.get("description"):
        fail(f"{skill_file} missing description")
    metadata = skill_dir / "agents" / "openai.yaml"
    if not metadata.is_file():
        fail(f"{skill_dir} missing agents/openai.yaml")
    interface = parse_simple_openai_yaml(metadata)
    missing = REQUIRED_AGENT_KEYS - interface.keys()
    if missing:
        fail(f"{metadata} missing interface keys: {', '.join(sorted(missing))}")
    if f"${expected_name}" not in interface["default_prompt"]:
        fail(f"{metadata} default_prompt must mention ${expected_name}")


def validate_required_skills() -> None:
    actual = {path.name for path in SKILLS.iterdir() if path.is_dir()}
    missing = REQUIRED_SKILLS - actual
    if missing:
        fail(f"missing required skills: {', '.join(sorted(missing))}")


def validate_references() -> None:
    references = SKILLS / "codex-packet-loop-core" / "references"
    for name in sorted(REQUIRED_REFERENCES):
        path = references / name
        if not path.is_file():
            fail(f"missing required reference: {path}")
        text = path.read_text()
        if "# " not in text:
            fail(f"{path} must contain a Markdown heading")


def validate_stage_routing() -> None:
    for skill_name, next_skills in sorted(STAGE_NEXT_SKILLS.items()):
        path = SKILLS / skill_name / "SKILL.md"
        text = path.read_text()
        if "codex-packet-loop-core" not in text:
            fail(f"{path} must load codex-packet-loop-core")
        if "workflow-protocol.md" not in text:
            fail(f"{path} must reference workflow-protocol.md")
        for next_skill in next_skills:
            if f"${next_skill}" not in text:
                fail(f"{path} must name next skill ${next_skill}")
        for reference in STAGE_REQUIRED_REFERENCES.get(skill_name, []):
            if reference not in text:
                fail(f"{path} must reference {reference}")


def validate_behavioral_fixtures() -> None:
    fixtures_dir = ROOT / "evals" / "fixtures"
    for name in sorted(REQUIRED_FIXTURES):
        path = fixtures_dir / name
        if not path.is_file():
            fail(f"missing behavioral fixture: {path}")
        text = path.read_text()
        for required in (
            "## Starting State",
            "## Prompt",
            "## Expected Route",
            "## Forbidden Actions",
            "## Required Evidence",
        ):
            if required not in text:
                fail(f"{path} missing section {required}")


def run_core_tests() -> None:
    test_paths = [
        SKILLS / "codex-packet-loop-core" / "tests" / "test_packet_loop.py",
        SKILLS / "codex-packet-loop-core" / "tests" / "test_packet_loop_trial.py",
    ]
    for test_path in test_paths:
        if not test_path.is_file():
            fail(f"missing core test: {test_path}")
        result = subprocess.run([sys.executable, str(test_path)], cwd=ROOT)
        if result.returncode != 0:
            raise SystemExit(result.returncode)


def main() -> int:
    if not (ROOT / "README.md").is_file():
        fail("experimental README.md is missing")
    validate_required_skills()
    validate_references()
    for skill_dir in sorted(SKILLS.iterdir()):
        if skill_dir.is_dir():
            validate_skill(skill_dir)
    validate_stage_routing()
    validate_behavioral_fixtures()
    run_core_tests()
    print("Experimental packet-loop validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
