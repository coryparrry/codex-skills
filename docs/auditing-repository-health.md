# Audit Repository Health

This how-to guide explains how to use `auditing-repository-health` to check whether a repository is ready for safe repeated work.

## Purpose

Use this skill before onboarding, planning, coding, debugging, cleanup, packaging, release, CI repair, or adding another shipped skill.

The audit checks:

- live Git and worktree state;
- repository instructions and entry points;
- setup, update, server, test, CI, and release scripts;
- validation and packaging surfaces;
- generated-file and ignore hygiene;
- repository size or history risks;
- documentation rendering, stale docs, and public/private leakage risks.

## Install The Skill

Install the skill with the `skills` CLI:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill auditing-repository-health
```

Restart Codex if the skill does not appear.

## Run The Skill

From inside the repository you want audited, ask Codex:

```text
Use $auditing-repository-health to audit this repository before starting work.
```

For missing script checks, ask:

```text
Use $auditing-repository-health to check whether this repo has the standard scripts needed for onboarding, testing, validation, and shipping.
```

## Understand The Output

The skill should lead with a readiness verdict and ranked findings. It should not bury issues under a command transcript.

Expected sections:

- `Verdict`
- `Findings`
- `Operating Surface`
- `Hygiene`
- `Commands Run`
- `Not Checked`

`Ready to proceed: conditional` is acceptable when no blocker exists but the repo is missing a script, validation lane, docs check, or package-surface guard that should be fixed soon.

## Script Readiness

The skill uses the scripts-to-rule-them-all pattern as a reference vocabulary, not a mandatory structure. It maps the repo's actual commands to equivalent responsibilities:

| Responsibility | Common script name |
|---|---|
| Install dependencies | `script/bootstrap` |
| Prepare a fresh clone | `script/setup` |
| Refresh after pulling | `script/update` |
| Start the app or services | `script/server` |
| Run tests | `script/test` |
| Run the CI or closeout gate | `script/cibuild` |
| Open a project console | `script/console` |

If the repo uses `scripts/test_install.sh`, `npm test`, `make validate`, `just ci`, or another local convention, the skill should respect that convention and report missing equivalents rather than forcing new names.

## What The Skill Will Not Do

The skill will not:

- modify files unless the user asks for fixes;
- install third-party audit tools such as `git-sizer` without approval;
- treat one passing test as proof for unrelated repo surfaces;
- impose GitHub-specific workflows on repos that only use GitHub for storage;
- mark an audit complete without listing what was not checked.

## File Layout

```text
skills/auditing-repository-health/
  SKILL.md
  agents/
    openai.yaml
```

## Related Docs

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [Reference](reference.md)
- [Writing Codex Loops](writing-codex-loops.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
