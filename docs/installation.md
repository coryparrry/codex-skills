# Install Codex Skills

This how-to guide explains how to install the skills in this repository into a local Codex setup.

## Purpose

Use this guide when you want Codex to discover one or more skills from this repository.

The repository contains two kinds of installable content:

- `codex-adversarial-gate`, which needs both a skill folder and custom reviewer agent TOMLs.
- Utility skills, which only need their skill folder copied into Codex.

## Before You Start

You need:

- Codex with local skills enabled.
- Git, if you use the clone-based install command.
- Python 3, if you use `codex-adversarial-gate` review archival.

The examples use this default Codex home:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
```

Set `CODEX_HOME` before running commands if your Codex install uses a different location.

## Choose What To Install

Install `codex-adversarial-gate` when you need plan or completion gates with independent reviewer and critic agents.

Install `git-clean-merged-branch` when you want a small Git cleanup skill.

Install `triage-review-comments` when you want a PR review triage skill.

## Install Codex Adversarial Gate

Use the repo-level installer for `codex-adversarial-gate`. It copies both the skill folder and the required custom agents.

```bash
/bin/bash -c 'set -euo pipefail
tmp_dir="$(mktemp -d)"
trap "rm -rf \"$tmp_dir\"" EXIT
git clone --depth 1 https://github.com/coryparrry/codex-skills.git "$tmp_dir"
/bin/bash "$tmp_dir/scripts/install.sh"'
```

The installer writes:

```text
${CODEX_HOME:-$HOME/.codex}/skills/codex-adversarial-gate/
${CODEX_HOME:-$HOME/.codex}/agents/plan-adversarial-reviewer.toml
${CODEX_HOME:-$HOME/.codex}/agents/task-completion-adversarial-reviewer.toml
${CODEX_HOME:-$HOME/.codex}/agents/task-completion-review-critic.toml
```

From an existing clone, run:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}" bash scripts/install.sh
```

## Install A Utility Skill

Utility skills do not need custom agent TOMLs. Copy the skill folder into Codex.

Install `git-clean-merged-branch`:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"
cp -R skills/git-clean-merged-branch "$CODEX_HOME/skills/git-clean-merged-branch"
```

Install `triage-review-comments`:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"
cp -R skills/triage-review-comments "$CODEX_HOME/skills/triage-review-comments"
```

Restart Codex if the new skills do not appear immediately.

## Verify Installation

Check the adversarial gate install:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

test -f "$CODEX_HOME/skills/codex-adversarial-gate/SKILL.md"
test -f "$CODEX_HOME/agents/plan-adversarial-reviewer.toml"
test -f "$CODEX_HOME/agents/task-completion-adversarial-reviewer.toml"
test -f "$CODEX_HOME/agents/task-completion-review-critic.toml"
```

Check a utility skill install:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

test -f "$CODEX_HOME/skills/git-clean-merged-branch/SKILL.md"
test -f "$CODEX_HOME/skills/triage-review-comments/SKILL.md"
```

## Update An Install

For `codex-adversarial-gate`, rerun the repo-level installer:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}" bash scripts/install.sh
```

For utility skills, copy the skill folder again:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
cp -R skills/git-clean-merged-branch "$CODEX_HOME/skills/git-clean-merged-branch"
cp -R skills/triage-review-comments "$CODEX_HOME/skills/triage-review-comments"
```

Restart Codex if updated skills or agents are not picked up.

## Uninstall

Remove the adversarial gate skill and custom agents:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

rm -rf "$CODEX_HOME/skills/codex-adversarial-gate"
rm -f "$CODEX_HOME/agents/plan-adversarial-reviewer.toml"
rm -f "$CODEX_HOME/agents/task-completion-adversarial-reviewer.toml"
rm -f "$CODEX_HOME/agents/task-completion-review-critic.toml"
```

Remove utility skills:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

rm -rf "$CODEX_HOME/skills/git-clean-merged-branch"
rm -rf "$CODEX_HOME/skills/triage-review-comments"
```

## Common Problems

If Codex does not show an installed skill, restart Codex and check that `SKILL.md` is under the expected directory.

If `codex-adversarial-gate` loads but custom agents are missing, rerun `scripts/install.sh`. Installing only `skills/codex-adversarial-gate/` is incomplete for that skill.

If a clone-based install fails, check that `git` is available and that the repository URL is reachable.

## Related Docs

- [Usage Guide](usage.md)
- [Reference](reference.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
- [Triage Review Comments](triage-review-comments.md)
