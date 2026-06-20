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

Clone the repository and link it into your local plugin folder:

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills
mkdir -p ~/plugins ~/.agents/plugins
ln -sfn "$PWD" ~/plugins/codex-skills
```

Create `~/.agents/plugins/marketplace.json`:

```json
{
  "name": "local",
  "interface": {
    "displayName": "Local Plugins"
  },
  "plugins": [
    {
      "name": "codex-skills",
      "source": {
        "source": "local",
        "path": "./plugins/codex-skills"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Coding"
    }
  ]
}
```

If `marketplace.json` already exists, add the `codex-skills` object to its `plugins` array instead of replacing the file.

Restart Codex so it reloads the marketplace, then install **Codex Skills** from the **Local Plugins** marketplace.

If you use `codex-adversarial-gate`, run its install script after the marketplace install:

```bash
bash skills/codex-adversarial-gate/scripts/install.sh
```

The marketplace install exposes the plugin skills. The adversarial gate script is still required because that skill needs custom reviewer TOMLs copied into `~/.codex/agents`.

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

If the marketplace plugin does not appear, check that `~/plugins/codex-skills/.codex-plugin/plugin.json` exists and that the marketplace entry path is `./plugins/codex-skills`.

If cloning fails, check that `git` is available and that the repository URL is reachable.

## Related Docs

- [Usage Guide](usage.md)
- [Reference](reference.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
- [Triage Review Comments](triage-review-comments.md)
