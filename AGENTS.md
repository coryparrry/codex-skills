# Repository Guidelines

## Project Structure & Module Organization

This repository packages a small Codex skill bundle. Source skills live under `skills/`, with one directory per skill, including research, review-triage, and branch-cleanup workflows. Each skill keeps its entrypoint in `SKILL.md`; supporting files belong in local `agents/`, `references/`, `scripts/`, or `tests/` subdirectories.

The installable plugin mirror lives under `plugins/codex-skills/skills/`, and plugin metadata is in `plugins/codex-skills/.codex-plugin/plugin.json`. Keep mirrored skill files synchronized when changing shipped skill behavior. User-facing documentation belongs in `docs/`; repository install helpers live in `scripts/`.

## Marketplace Installation Workflow

Treat the Git-backed marketplace on GitHub `main` as the only durable installed source for these skills. During development, a skill may be installed from the local checkout only for bounded testing. After validation, remove that local installation, publish the completed change to `main`, repoint or refresh the marketplace against `main`, and verify the enabled plugin resolves from the Git-backed marketplace cache. Do not leave a standalone local skill, a local-path marketplace registration, or a marketplace pinned to a feature branch after testing is complete.

## Build, Test, and Development Commands

- `bash scripts/test_install.sh`: runs the install smoke test against temporary Codex homes.
- `bash -n scripts/install.sh`: syntax-checks the repo installer.
- `python3 skills/git-clean-merged-branch/tests/test_clean_merged_branch.py`: runs branch cleanup behavior tests.
- `python3 scripts/check_skill_mirror.py git-clean-merged-branch`: verifies source/plugin mirror parity.
- `python3 scripts/check_skill_mirror.py triage-review-comments`: verifies source/plugin mirror parity.
- `python3 scripts/check_skill_mirror.py continue-deep-research`: verifies source/plugin mirror parity.
- `python3 scripts/check_skill_mirror.py research-repo-technology`: verifies source/plugin mirror parity.
- `python3 scripts/check_skill_mirror.py swift-code-review`: verifies source/plugin mirror parity.
- `python3 -m json.tool skills.sh.json >/dev/null`: validates package metadata JSON.
- `git diff --check`: catches trailing whitespace and patch formatting issues.

## Coding Style & Naming Conventions

Use Markdown for skill instructions and references, Bash for installers, and Python 3 for helpers/tests. Keep `SKILL.md` concise; move detailed rules into `references/` and reusable snippets into `templates/`. Python uses standard library modules, 4-space indentation, type-friendly `pathlib` patterns, and `unittest` tests. Shell scripts should start with `#!/usr/bin/env bash` and `set -euo pipefail`.

## Testing Guidelines

Add or update focused tests for behavior changes. Name Python test files `test_*.py` and keep temporary filesystem or Git fixtures self-contained. For workflow or documentation changes, run the commands that cover the changed surface; do not treat one passing smoke test as coverage for unrelated skills.

## Commit & Pull Request Guidelines

Recent commits use concise imperative messages, often Conventional Commit style such as `fix(cleanup): protect dirty worktrees` or `docs(triage): clarify review buckets`. PRs should summarize the problem, the solution, and validation performed. Link related issues when applicable and call out any skill/plugin mirror changes.

## Security & Agent-Specific Instructions

Do not commit secrets, private paths, tokens, or organization-specific workflow assumptions. Preserve the branch-cleanup safeguards around dirty worktrees, default-branch resolution, and unmerged deletion. Preserve review-triage verification: comments are hypotheses until checked against current code.
