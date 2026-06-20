# Install Codex Skills

This how-to guide explains how to install one skill from this repository.

## Purpose

Use this guide when you want Codex to discover a skill from this repository.

## Before You Start

You need:

- Codex with local skills enabled.
- `skills` CLI support through `npx`.
- Python 3, if you install `codex-adversarial-gate`.

## Install Through Codex Marketplace

1. Open **Plugins** in the Codex app.
2. Click **Add marketplace**.
3. Add this repository as the marketplace source: `https://github.com/coryparrry/codex-skills`.
4. Open the **Codex Skills** entry and click the plus button or **Add to Codex**.

If you use `codex-adversarial-gate`, also install the skill with the `skills` CLI and run its local agent installer:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill codex-adversarial-gate
bash ~/.agents/skills/codex-adversarial-gate/scripts/install.sh
```

The marketplace install exposes `codex-adversarial-gate`, `git-clean-merged-branch`, and `triage-review-comments`.

The adversarial gate installer is still required when you need its custom reviewer TOMLs copied into `~/.codex/agents`.

## Install Through skills.sh

Install the repo skills for Codex with the `skills` CLI:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill '*'
```

The `skills` CLI stores global Codex skill copies under `~/.agents/skills/`.

If you use `codex-adversarial-gate`, also run its local agent installer:

```bash
bash ~/.agents/skills/codex-adversarial-gate/scripts/install.sh
```

The `skills` CLI installs the skill folders. The adversarial gate installer is still required for its custom reviewer TOMLs.

## Install Codex Adversarial Gate

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill codex-adversarial-gate
bash ~/.agents/skills/codex-adversarial-gate/scripts/install.sh
```

Use the install script for `codex-adversarial-gate` because it also copies the custom reviewer agents.

## Install Git Clean Merged Branch

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill git-clean-merged-branch
```

## Install Triage Review Comments

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill triage-review-comments
```

Restart Codex if the new skill does not appear.

## Common Problems

If Codex does not show an installed skill, restart Codex and check that `SKILL.md` is under the expected directory.

If `codex-adversarial-gate` loads but custom agents are missing, rerun `bash ~/.agents/skills/codex-adversarial-gate/scripts/install.sh`.

If the marketplace plugin does not appear, check that this repo contains `.agents/plugins/marketplace.json` and `plugins/codex-skills/.codex-plugin/plugin.json`, then remove and add the marketplace again in the Codex app.

If installation fails, check that `npx skills add coryparrry/codex-skills --global --agent codex --skill '*'` succeeds.

## Related Docs

- [Usage Guide](usage.md)
- [Reference](reference.md)
- [Codex Adversarial Review Gate](codex-adversarial-gate.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
- [Triage Review Comments](triage-review-comments.md)
