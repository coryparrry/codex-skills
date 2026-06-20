# Install Codex Skills

This how-to guide explains how to install one skill from this repository.

## Purpose

Use this guide when you want Codex to discover a skill from this repository.

## Before You Start

You need:

- Codex with local skills enabled.
- Git, to clone the repository.
- Python 3, if you install `codex-adversarial-gate`.

## Install Codex Adversarial Gate

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills
bash skills/codex-adversarial-gate/scripts/install.sh
```

Use the install script for `codex-adversarial-gate` because it also copies the custom reviewer agents.

## Install Git Clean Merged Branch

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills
mkdir -p ~/.codex/skills
cp -R skills/git-clean-merged-branch ~/.codex/skills/git-clean-merged-branch
```

## Install Triage Review Comments

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills
mkdir -p ~/.codex/skills
cp -R skills/triage-review-comments ~/.codex/skills/triage-review-comments
```

Restart Codex if the new skill does not appear.

## Common Problems

If Codex does not show an installed skill, restart Codex and check that `SKILL.md` is under the expected directory.

If `codex-adversarial-gate` loads but custom agents are missing, rerun `bash skills/codex-adversarial-gate/scripts/install.sh`.

If cloning fails, check that `git` is available and that the repository URL is reachable.

## Related Docs

- [Usage Guide](usage.md)
- [Reference](reference.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
- [Triage Review Comments](triage-review-comments.md)
