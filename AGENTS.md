# Repository Guidelines

## Project Structure & Module Organization

This repository packages Codex skills and a small set of custom subagent profiles. Source skills live under `skills/`, with one directory per skill. Each skill keeps its entrypoint in `SKILL.md`; supporting files belong in local `agents/`, `references/`, `scripts/`, or `tests/` subdirectories. Standalone subagent profiles live under the top-level `agents/` directory as TOML files.

The installable plugin copies live under `plugins/codex-skills/skills/` and `plugins/codex-skills/agents/`. Plugin metadata is in `plugins/codex-skills/.codex-plugin/plugin.json`. Keep every shipped skill and profile synchronized with its plugin copy. User-facing documentation belongs in `docs/`; repository install helpers live in `scripts/`.

## Skill catalogue and documentation

When adding, renaming, or removing a shipped skill, update the README in the same change. Keep its skill count, Skills table, documentation links, installation examples where relevant, and validation commands aligned with `skills/`. Also update the source skill, plugin mirror, plugin manifest, `skills.sh.json`, and any affected pages in `docs/`.

When adding, renaming, or removing a subagent profile, update the README Agent Profiles table, `docs/agent-profiles.md`, the standalone TOML file, the plugin Markdown copy, the installer tests, the release-contract tests, and the plugin manifest. Keep each profile's model and reasoning-effort pins consistent across its source, plugin copy, documentation, and validation contract. Change a pin only when the user explicitly requests it or representative evaluation evidence supports the change.

Use the `$humanizer:humanizer` skill only for README files and repository instruction documents such as `AGENTS.md`. Never use it for skill writing, including `SKILL.md`, skill references, prompts, or skill metadata. Keep frontmatter, code blocks, commands, data, and link targets unchanged unless the task requires a functional change.

## Marketplace Installation Workflow

Treat the Git-backed marketplace on GitHub `main` as the durable installed source for the plugin skills and profiles. During development, a local checkout may be installed only for bounded testing. After validation, remove that local installation, publish the completed change to `main`, refresh the marketplace against `main`, and verify that the enabled plugin resolves from the Git-backed marketplace cache. Do not leave a standalone local test copy, a local-path marketplace registration, or a marketplace pinned to a feature branch.

For every shipped plugin update, complete this release sequence:

1. Update the canonical skill under `skills/` and its copy under `plugins/codex-skills/skills/`. For a profile, update the source TOML under `agents/` and the matching plugin Markdown file under `plugins/codex-skills/agents/`. The release validator must confirm profile field and instruction parity.
2. Update `plugins/codex-skills/.codex-plugin/plugin.json` in the same change. Increment its `version` for every change to shipped skills, agent profiles, plugin metadata, or plugin assets because Codex uses that SemVer value as the installed-cache key. Use a minor version for a new capability and a patch version for a compatible fix or metadata refresh. Update descriptions, prompts, capabilities, and asset paths when the shipped surface changes, and verify every referenced file exists.
3. Keep `.agents/plugins/marketplace.json` valid and ensure the `codex-skills` entry retains `source.path: "./plugins/codex-skills"`, `policy.installation: "AVAILABLE"`, `policy.authentication: "ON_INSTALL"`, and a category. Do not put the release version in the marketplace entry; the authoritative version is in `plugin.json`.
4. Run the release-contract tests and validator. Validate each changed skill with `python3 scripts/check_skill_mirror.py <skill>`, validate the plugin with the system `plugin-creator` validator, parse `plugin.json`, `marketplace.json`, and `skills.sh.json` with `python3 -m json.tool`, run `bash scripts/test_install.sh`, and run `git diff --check`.
5. Commit and push the complete update, merge it to GitHub `main`, and verify the marketplace checkout revision equals `origin/main` before installing. Never release from an unmerged feature branch.
6. For a registered Git marketplace, run `codex plugin marketplace upgrade codex-skills`, then remove and reinstall `codex-skills@codex-skills` so the new version creates a fresh cache directory. If the marketplace is not registered, add `https://github.com/coryparrry/codex-skills.git` without a feature-branch `--ref`, then install the plugin.
7. Verify `codex plugin list --marketplace codex-skills --available --json` reports the expected version, enabled state, and Git marketplace source. Confirm that the installed manifest and agent profiles match the Git-backed `main` snapshot, the previous version cache is absent, and no standalone test copy remains under `${CODEX_HOME:-$HOME/.codex}/skills/` or `${CODEX_HOME:-$HOME/.codex}/agents/codex-skills/`.
8. Start a new Codex task after installation so it loads the refreshed skills and profiles. Remove any local testing installation when validation is complete.

## skills.sh Publication Workflow

Treat `skills.sh` as a separate GitHub-backed distribution surface from the Codex plugin marketplace. There is no `skills publish` command and `plugin.json` SemVer does not version skills.sh packages. The public `skills/` directories on GitHub `main` are the published source; skills.sh discovers them through the `skills` CLI and adds repositories to its directory automatically from install telemetry.

For every skills.sh release:

1. Keep each public skill under `skills/<skill-name>/SKILL.md` with valid YAML frontmatter whose `name` matches the directory. Do not publish experimental or internal skills through the public `skills/` tree.
2. Add every new or renamed public skill to the appropriate grouping in `skills.sh.json`, remove stale names, and keep group labels and descriptions aligned with the current bundle. `skills.sh.json` controls repository-page grouping; it does not replace skill discovery from `SKILL.md`.
3. Before publishing, run the system `skill-creator` validator for every changed source skill, parse `skills.sh.json` with `python3 -m json.tool`, run the relevant mirror checks and install smoke test, and run `npx skills add . --list`. The local discovery result must contain exactly the intended public skill names.
4. Merge the complete change to GitHub `main` before treating it as published. After merge, run `npx skills add coryparrry/codex-skills --list` to verify discovery from the remote GitHub source rather than the working tree.
5. Verify `https://skills.sh/coryparrry/codex-skills` and any new skill page after the service indexes the repository. Directory appearance and install counts are telemetry-driven and may lag; do not invent a manual registry upload or claim publication from a local-only result.
6. Do not globally install a skills.sh copy merely to force indexing. If a disposable install test is necessary, isolate it from the user's real Codex home and remove it after verification so the Git-backed Codex plugin remains the only durable local installation.

## Build, Test, and Development Commands

- `python3 -m pip install -r requirements-release.txt`: installs the pinned dependency used by release validation.
- `python3 scripts/tests/test_validate_release_contract.py`: tests the release-contract checker.
- `python3 scripts/validate_release_contract.py --base-ref origin/main`: validates the public catalogue and requires a plugin version increase when shipped plugin content changed.
- `bash scripts/test_install.sh`: runs the install smoke test against temporary Codex homes.
- `bash -n scripts/install.sh`: syntax-checks the repo installer.
- `python3 skills/appstore-readiness-audit/tests/test_check_review_notes.py`: runs the App Review Notes byte-limit tests.
- `python3 skills/git-clean-merged-branch/tests/test_clean_merged_branch.py`: runs branch cleanup behavior tests.
- `python3 scripts/check_skill_mirror.py appstore-readiness-audit`: verifies source/plugin mirror parity.
- `python3 scripts/check_skill_mirror.py git-clean-merged-branch`: verifies source/plugin mirror parity.
- `python3 scripts/check_skill_mirror.py triage-review-comments`: verifies source/plugin mirror parity.
- `python3 scripts/check_skill_mirror.py continue-deep-research`: verifies source/plugin mirror parity.
- `python3 scripts/check_skill_mirror.py research-repo-technology`: verifies source/plugin mirror parity.
- `python3 scripts/check_skill_mirror.py swift-code-review`: verifies source/plugin mirror parity.
- `python3 -m json.tool skills.sh.json >/dev/null`: validates package metadata JSON.
- `git diff --check`: catches trailing whitespace and patch formatting issues.

## Coding Style & Naming Conventions

Use Markdown for skill instructions, references, and plugin agent profiles. Use TOML for standalone Codex profiles, Bash for installers, and Python 3 for helpers and tests. Keep `SKILL.md` concise; move detailed rules into `references/` and reusable snippets into `templates/`. Python uses standard library modules unless a dependency is pinned in a repository requirements file. Use 4-space indentation, type-friendly `pathlib` patterns, and `unittest` tests. Shell scripts should start with `#!/usr/bin/env bash` and `set -euo pipefail`.

## Testing Guidelines

Add or update focused tests for behavior changes. Name Python test files `test_*.py` and keep temporary filesystem or Git fixtures self-contained. For workflow or documentation changes, run the commands that cover the changed surface; do not treat one passing smoke test as coverage for unrelated skills.

## Commit & Pull Request Guidelines

Recent commits use concise imperative messages, often Conventional Commit style such as `fix(cleanup): protect dirty worktrees` or `docs(triage): clarify review buckets`. PRs should summarize the problem, the solution, and validation performed. Link related issues when applicable and call out any skill/plugin mirror changes.

## Security & Agent-Specific Instructions

Do not commit secrets, private paths, tokens, or organization-specific workflow assumptions. Preserve the branch-cleanup safeguards around dirty worktrees, default-branch resolution, and unmerged deletion. Preserve review-triage verification: comments are hypotheses until checked against current code.
