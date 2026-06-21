#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REQUIRED_AGENT_KEYS = {"display_name", "short_description", "default_prompt"}


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


def run_core_tests() -> None:
    test_paths = [
        SKILLS / "codex-packet-loop-core" / "tests" / "test_packet_loop.py",
        SKILLS / "codex-packet-loop-core" / "tests" / "test_packet_loop_trial.py",
    ]
    for test_path in test_paths:
        if not test_path.exists():
            continue
        result = subprocess.run([sys.executable, str(test_path)], cwd=ROOT)
        if result.returncode != 0:
            raise SystemExit(result.returncode)


def main() -> int:
    if not (ROOT / "README.md").is_file():
        fail("experimental README.md is missing")
    for skill_dir in sorted(SKILLS.iterdir()):
        if skill_dir.is_dir():
            validate_skill(skill_dir)
    run_core_tests()
    print("Experimental packet-loop validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
