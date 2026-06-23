---
name: auditing-repository-health
description: Use when auditing a repository before onboarding, planning, coding, debugging, cleanup, packaging, release, CI repair, adding a skill, checking missing scripts, or validating git state, generated files, install/test readiness, documentation health, and repeated-agent work readiness.
---

# Auditing Repository Health

## Overview

Audit whether a repository is ready for safe repeated work. A useful audit reports blockers, near-term fixes, and missing operating surfaces instead of only saying that commands passed.

Core principle: inspect the repo's own conventions first, then identify gaps that will slow future agents or contributors.

## Workflow

1. Establish live state.
   - Find the repo root and read active instructions such as `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, or nested equivalents.
   - Report branch, upstream, dirty tracked files, untracked files, ignored generated files when relevant, and whether the default branch is current.
   - Do not stash, discard, reset, clean, install dependencies, or add scripts unless the user explicitly asks for changes.
   - If the user asks for read-only audit, non-mutating checks are allowed, but list skipped checks when they would create temp installs, write caches, update refs, or call external services.

2. Inventory operating entry points.
   - Read `README`, contribution docs, package manifests, `scripts/`, `script/`, CI config, test config, install helpers, release docs, and skill/plugin metadata when present.
   - Prefer existing commands over guessed commands. If a command is documented but absent, report the mismatch.
   - For polyglot repos, separate language-level checks from repo-level checks.

3. Check standard repo scripts.
   Use the scripts-to-rule-them-all pattern as a reference shape, not a rule to impose.

| Script | Healthy when |
| --- | --- |
| `script/bootstrap` or equivalent | Installs required dependencies only. |
| `script/setup` or equivalent | Brings a fresh clone to a working initial state. |
| `script/update` or equivalent | Refreshes a stale checkout after pulling changes. |
| `script/server` or equivalent | Starts the app or local service stack. |
| `script/test` or equivalent | Runs tests and accepts a narrow path/filter when practical. |
| `script/cibuild` or equivalent | Runs the CI/closeout gate from a clean state. |
| `script/console` or equivalent | Opens a project console or REPL when the repo has one. |

4. Check validation and packaging health.
   - Identify the fastest useful check, focused behavior checks, full local gate, and release/package gate.
   - For skill repos, verify source skill folders, plugin mirrors, `agents/openai.yaml`, references, templates, install scripts, marketplace metadata, skills metadata, and docs all agree.
   - For generated artifacts, distinguish source of truth from derived output.

5. Check repo hygiene.
   - Inspect `.gitignore` for generated outputs, dependency folders, local caches, build products, logs, screenshots/videos, and tool-specific artifacts.
   - If `git-sizer` is already installed, run it for size/history risk. Do not install it without approval.
   - If `git-sizer` is unavailable, use built-in checks such as `git count-objects -vH`, largest tracked files, and suspicious tracked archives or generated outputs.

6. Check documentation and rendering health.
   - Look for broken or stale docs, duplicate docs, private/internal notes in public artifacts, missing install/use docs, and links to files that moved.
   - Run markdown lint/rendering checks only when the repo already provides them. Otherwise report the missing docs check as a gap, not as a failure.

7. Report with ranked actions.
   Lead with findings and readiness, then list evidence. Separate blockers from improvements.

## Output Contract

```md
## Verdict
- Ready to proceed: <yes/no/conditional>
- Blocking issues: <count>
- Recommended first fix: <one action or none>

## Findings
- P0/P1/P2/P3: <title>
  - Evidence: <file/command/state>
  - Impact: <why future work is blocked or slowed>
  - Fix shape: <smallest practical correction>

## Operating Surface
- Setup/update/server/test/CI scripts: <present/missing/mapped equivalents>
- Fast check: <command or missing>
- Full check: <command or missing>
- Release/package check: <command or missing>

## Hygiene
- Git/worktree: <branch, upstream, dirty/untracked/ignored concerns>
- Generated files and ignores: <notable risks>
- Size/history: <git-sizer or fallback result>
- Docs/rendering: <checks and gaps>

## Commands Run
- `<command>` - <result>

## Not Checked
- <area> - <reason>
```

## Quick Reference

| Situation | Audit focus |
| --- | --- |
| Fresh clone or onboarding | setup/update scripts, dependency docs, first useful test, server start. |
| Before coding | branch/upstream, dirty state, instructions, fast check, full gate. |
| Missing important scripts | map existing commands to bootstrap/setup/update/server/test/cibuild/console equivalents. |
| Skill or plugin repo | source/mirror parity, metadata, installer smoke tests, docs surfaces. |
| Docs-heavy repo | source vs generated docs, rendering/linting, private-note leakage, stale links. |
| Slow or bloated repo | ignored outputs, tracked archives, largest files, `git-sizer` or fallback Git metrics. |
| Release or packaging | install path, package metadata, generated artifacts, full validation gate. |

## Example

```md
## Verdict
- Ready to proceed: conditional
- Blocking issues: 0
- Recommended first fix: add a repo-level `scripts/validate.sh` or document the existing equivalent.

## Findings
- P2: no single closeout command
  - Evidence: `scripts/test_install.sh` exists, but no top-level validate/ci/preflight command wraps install, JSON, mirror, and whitespace checks.
  - Impact: future agents may claim the repo is healthy after one unrelated test.
  - Fix shape: add a small repo-owned validation script or document the command bundle in README.

## Operating Surface
- Setup/update/server/test/CI scripts: install and install-smoke exist; setup/update/server/ci equivalents are missing or undocumented.
- Fast check: `git diff --check`
- Full check: `bash scripts/test_install.sh` plus skill helper tests and JSON validation.
- Release/package check: plugin metadata and source/mirror parity check should be part of closeout.
```

## Common Mistakes

| Baseline failure | Better audit behavior |
| --- | --- |
| "Git is clean, so the repo is healthy." | Clean state is one lane; still check scripts, validation, docs, ignores, and packaging. |
| Listing ideal scripts without reading the repo | Map existing commands first, then name gaps. |
| Running one strong check and calling it complete | Tie each check to the surface it proves and list unverified areas. |
| Treating missing optional tools as failures | Use fallbacks and report missing tooling as an improvement unless the repo requires it. |
| Imposing `script/*` names on every repo | Use normalized scripts as a reference vocabulary, not a mandatory structure. |
| Ignoring ignored files | Ignored caches are usually fine, but ignored generated proof artifacts can still matter for audits. |
| Burying findings under commands | Findings and readiness come first; commands are evidence. |

## Red Flags

- No clear command to set up a fresh clone.
- No focused test command or documented filter path.
- No full local validation gate before closeout.
- Source and shipped/package mirror can drift without a check.
- Generated artifacts are tracked without a source-of-truth rule.
- Public docs can include private notes, stale links, or duplicated generated files.
- The audit says "healthy" but has no `Not Checked` section.
