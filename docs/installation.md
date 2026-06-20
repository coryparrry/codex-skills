# Installation

This is a Codex-focused install guide for `codex-adversarial-gate`.

## Goal

Install both required parts of the package:

- the skill folder under Codex skills;
- the custom reviewer TOMLs under Codex agents.

Installing only the skill folder is incomplete because the workflow routes to three named custom agents.

## Prerequisites

- Codex installed and configured
- Git, for the one-command install
- Python 3 for the archive helper

## One-Command Install

Copy and paste this command:

```bash
/bin/bash -c 'set -euo pipefail
tmp_dir="$(mktemp -d)"
trap "rm -rf \"$tmp_dir\"" EXIT
git clone --depth 1 https://github.com/coryparrry/codex-skills.git "$tmp_dir"
/bin/bash "$tmp_dir/scripts/install.sh"'
```

The installer copies the skill and the custom agents into separate Codex locations:

```text
${CODEX_HOME:-$HOME/.codex}/skills/codex-adversarial-gate/
${CODEX_HOME:-$HOME/.codex}/agents/plan-adversarial-reviewer.toml
${CODEX_HOME:-$HOME/.codex}/agents/task-completion-adversarial-reviewer.toml
${CODEX_HOME:-$HOME/.codex}/agents/task-completion-review-critic.toml
```

Use a custom Codex home when needed:

```bash
CODEX_HOME="$HOME/.codex" /bin/bash -c 'set -euo pipefail
tmp_dir="$(mktemp -d)"
trap "rm -rf \"$tmp_dir\"" EXIT
git clone --depth 1 https://github.com/coryparrry/codex-skills.git "$tmp_dir"
/bin/bash "$tmp_dir/scripts/install.sh"'
```

## Install From A Local Clone

Use this when you already have a checkout:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}" bash scripts/install.sh
```

## Verify Installation

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

test -f "$CODEX_HOME/skills/codex-adversarial-gate/SKILL.md"
test -f "$CODEX_HOME/agents/plan-adversarial-reviewer.toml"
test -f "$CODEX_HOME/agents/task-completion-adversarial-reviewer.toml"
test -f "$CODEX_HOME/agents/task-completion-review-critic.toml"
```

## Update An Existing Install

Rerun the installer:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}" /bin/bash -c 'set -euo pipefail
tmp_dir="$(mktemp -d)"
trap "rm -rf \"$tmp_dir\"" EXIT
git clone --depth 1 https://github.com/coryparrry/codex-skills.git "$tmp_dir"
/bin/bash "$tmp_dir/scripts/install.sh"'
```

Restart Codex if it does not immediately pick up updated skill or agent definitions.

## Uninstall

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

rm -rf "$CODEX_HOME/skills/codex-adversarial-gate"
rm -f "$CODEX_HOME/agents/plan-adversarial-reviewer.toml"
rm -f "$CODEX_HOME/agents/task-completion-adversarial-reviewer.toml"
rm -f "$CODEX_HOME/agents/task-completion-review-critic.toml"
```

## Installed Files

| File | Purpose |
|---|---|
| `SKILL.md` | Main skill entrypoint and routing instructions |
| `agents/plan-adversarial-reviewer.toml` | Read-only plan reviewer |
| `agents/task-completion-adversarial-reviewer.toml` | Read-only completion reviewer |
| `agents/task-completion-review-critic.toml` | Read-only critic for reviewer `PASS` verdicts |
| `scripts/install.sh` | Installs the skill folder and custom agent TOMLs into Codex |
| `scripts/archive_adversarial_review.py` | Archive exact review output under `docs/Adversarial Reviews/` |
| `references/` | Workflow details and rubrics loaded on demand |
| `templates/` | Plan and completion gate snippets |
