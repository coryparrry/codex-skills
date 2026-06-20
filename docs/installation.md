# Install Codex Skills

This how-to guide explains how to install one skill from this repository.

## Purpose

Use this guide when you want Codex to discover a skill from this repository.

## Before You Start

You need:

- Codex with local skills enabled.
- Git, to clone the repository.
- Python 3, if you install `codex-adversarial-gate`.

## Install Through Codex Marketplace

1. Open **Plugins** in the Codex app.
2. Click **Add marketplace**.
3. Add this repository as the marketplace source: `https://github.com/coryparrry/codex-skills`.
4. Open the **Codex Skills** entry and click the plus button or **Add to Codex**.

If you use `codex-adversarial-gate`, also clone the repo and run its install script:

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills
bash skills/codex-adversarial-gate/scripts/install.sh
```

The marketplace install exposes the plugin skills. The adversarial gate script is still required because that skill needs custom reviewer TOMLs copied into `~/.codex/agents`.

## Install Through skills.sh

Install the repo skills for Codex with the `skills` CLI:

```bash
npx skills add https://github.com/coryparrry/codex-skills --agent codex --skill '*'
```

If you use `codex-adversarial-gate`, also clone the repo and run its install script:

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills
bash skills/codex-adversarial-gate/scripts/install.sh
```

The `skills` CLI installs the skill folders. The adversarial gate script is still required for the custom reviewer TOMLs.

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

If the marketplace plugin does not appear, check that this repo contains `.agents/plugins/marketplace.json` and `.codex-plugin/plugin.json`, then remove and add the marketplace again in the Codex app.

If cloning fails, check that `git` is available and that the repository URL is reachable.

## Related Docs

- [Usage Guide](usage.md)
- [Reference](reference.md)
- [Codex Adversarial Review Gate](codex-adversarial-gate.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
- [Triage Review Comments](triage-review-comments.md)
