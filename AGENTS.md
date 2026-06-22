# Repository Guidelines

## Project Structure & Module Organization

This repository packages a small Codex skill bundle. Source skills live under `skills/`, with one directory per skill such as `skills/codex-adversarial-gate/`, `skills/writing-codex-loops/`, and `skills/git-clean-merged-branch/`. Each skill keeps its entrypoint in `SKILL.md`; supporting files belong in local `agents/`, `references/`, `templates/`, `scripts/`, or `tests/` subdirectories.

The installable plugin mirror lives under `plugins/codex-skills/skills/`, and plugin metadata is in `plugins/codex-skills/.codex-plugin/plugin.json`. Keep mirrored skill files synchronized when changing shipped skill behavior. User-facing documentation belongs in `docs/`; repository install helpers live in `scripts/`.

## Build, Test, and Development Commands

- `bash scripts/test_install.sh`: runs the install smoke test against temporary Codex homes.
- `bash -n scripts/install.sh`: syntax-checks the repo installer.
- `bash -n skills/codex-adversarial-gate/scripts/install.sh`: syntax-checks the skill installer.
- `python3 skills/codex-adversarial-gate/scripts/test_archive_adversarial_review.py`: tests the review archive helper.
- `python3 skills/git-clean-merged-branch/tests/test_clean_merged_branch.py`: runs branch cleanup behavior tests.
- `python3 -m json.tool skills.sh.json >/dev/null`: validates package metadata JSON.
- `git diff --check`: catches trailing whitespace and patch formatting issues.

## Coding Style & Naming Conventions

Use Markdown for skill instructions and references, Bash for installers, and Python 3 for helpers/tests. Keep `SKILL.md` concise; move detailed rules into `references/` and reusable snippets into `templates/`. Python uses standard library modules, 4-space indentation, type-friendly `pathlib` patterns, and `unittest` tests. Shell scripts should start with `#!/usr/bin/env bash` and `set -euo pipefail`.

## Testing Guidelines

Add or update focused tests for behavior changes. Name Python test files `test_*.py` and keep temporary filesystem or Git fixtures self-contained. For workflow or documentation changes, run the commands that cover the changed surface; do not treat one passing smoke test as coverage for unrelated skills.

## Commit & Pull Request Guidelines

Recent commits use concise imperative messages, often Conventional Commit style such as `fix(adversarial-gate): tighten closeout contract` or `chore(skills): link experimental multi-phase orchestrator`. PRs should summarize the problem, the solution, and validation performed. Link related issues when applicable and call out any skill/plugin mirror changes.

## Security & Agent-Specific Instructions

Do not commit secrets, private paths, tokens, or organization-specific workflow assumptions. Preserve the adversarial gate invariant: implementation closeout requires reviewer `PASS`, critic `AGREE_PASS`, and exact archived evidence. Preserve the loop-writing invariant: recurring or repeated Codex work needs observable state, retry limits, stop conditions, and escalation.
