# Codex Skills

![Codex Skill Bundle](https://img.shields.io/badge/Codex-Skill_Bundle-111827?style=for-the-badge)
![Review Gate](https://img.shields.io/badge/Review_Gate-Adversarial-b91c1c?style=for-the-badge)
![Git Workflow](https://img.shields.io/badge/Git-Workflow-2563eb?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-16a34a?style=for-the-badge)

> A small Codex skill bundle for adversarial review gates, safe Git branch cleanup, and practical PR feedback triage.

## 📌 Overview

`codex-skills` packages focused Codex skills that solve repeatable engineering workflow problems without bringing along a heavy process framework.

The main skill in this repo is `codex-adversarial-gate`. It keeps implementation work open until:

1. An independent completion reviewer returns `PASS`.
2. A critic reviews that `PASS` and returns `AGREE_PASS`.
3. Both exact review outputs are archived under `docs/Adversarial Reviews/`.

The repo also includes smaller utility skills for safely cleaning up merged Git branches and triaging PR review feedback.

## ✨ Skills

- 🧠 **codex-adversarial-gate** gates plan and implementation closeout with reviewer-plus-critic evidence.
- 🌿 **git-clean-merged-branch** returns a repo to its default branch and deletes the old local branch only after safety checks.
- 🔎 **triage-review-comments** inventories PR comments, removes noise, deduplicates findings, and classifies real review work.
- 🧾 **Codex plugin metadata** exposes the bundle through `.codex-plugin/plugin.json`.
- ✅ **Install smoke tests** verify the adversarial gate installer and custom-agent copy flow.

## 🧰 What Is Included

```text
.
├── .codex-plugin/
│   └── plugin.json
├── docs/
│   ├── git-clean-merged-branch.md
│   ├── installation.md
│   ├── reference.md
│   ├── triage-review-comments.md
│   └── usage.md
├── scripts/
│   ├── install.sh
│   └── test_install.sh
└── skills/
    ├── codex-adversarial-gate/
    │   ├── SKILL.md
    │   ├── agents/
    │   ├── references/
    │   ├── scripts/
    │   └── templates/
    ├── git-clean-merged-branch/
    │   ├── SKILL.md
    │   ├── agents/
    │   └── scripts/
    └── triage-review-comments/
        ├── SKILL.md
        ├── agents/
        └── references/
```

## 🚀 Install

### Prerequisites

- Codex with local skills enabled
- Git, for the one-command install
- Python 3 for the adversarial review archive helper

### One-Command Install

Copy and paste this command to install `codex-adversarial-gate` and its bundled custom agents:

```bash
/bin/bash -c 'set -euo pipefail
tmp_dir="$(mktemp -d)"
trap "rm -rf \"$tmp_dir\"" EXIT
git clone --depth 1 https://github.com/coryparrry/codex-skills.git "$tmp_dir"
/bin/bash "$tmp_dir/scripts/install.sh"'
```

The installer copies:

```text
~/.codex/skills/codex-adversarial-gate/
~/.codex/agents/plan-adversarial-reviewer.toml
~/.codex/agents/task-completion-adversarial-reviewer.toml
~/.codex/agents/task-completion-review-critic.toml
```

If you use a custom Codex home, set `CODEX_HOME`:

```bash
CODEX_HOME="$HOME/.codex" /bin/bash -c 'set -euo pipefail
tmp_dir="$(mktemp -d)"
trap "rm -rf \"$tmp_dir\"" EXIT
git clone --depth 1 https://github.com/coryparrry/codex-skills.git "$tmp_dir"
/bin/bash "$tmp_dir/scripts/install.sh"'
```

### Install From A Local Clone

Use this when you have already cloned the repository:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}" bash scripts/install.sh
```

Install an individual utility skill from a local clone:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"
cp -R skills/git-clean-merged-branch "$CODEX_HOME/skills/git-clean-merged-branch"
```

Restart Codex if the new skills or agents do not appear immediately.

## ⚡ Quick Usage

Run the adversarial completion gate:

```text
Use $codex-adversarial-gate to close this implementation slice with archived reviewer and critic evidence.
```

Clean up a branch after GitHub merge:

```text
git-clean-merged-branch
```

Triage PR review comments:

```text
Use $triage-review-comments to triage the review comments on this PR.
```

## 📖 Documentation

- [Installation](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [Reference](docs/reference.md)
- [Git Clean Merged Branch](docs/git-clean-merged-branch.md)
- [Triage Review Comments](docs/triage-review-comments.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## 🧩 Codex Marketplace

The Codex plugin manifest lives at [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json). It exposes the installable skills under [`skills/`](skills/).

Use the installer above for the adversarial gate because it copies both the skill and the bundled custom agent TOMLs.

## 🧪 Validation

Run the install smoke test:

```bash
bash scripts/test_install.sh
```

Run syntax and helper checks:

```bash
bash -n scripts/install.sh
bash -n skills/codex-adversarial-gate/scripts/install.sh
python3 skills/codex-adversarial-gate/scripts/test_archive_adversarial_review.py
python3 -m py_compile \
  skills/codex-adversarial-gate/scripts/archive_adversarial_review.py \
  skills/codex-adversarial-gate/scripts/test_archive_adversarial_review.py
git diff --check
```

Run a plugin packaging check when `plugin-eval` is available:

```bash
plugin-eval analyze . --format markdown
```

## 🤝 Contributing

Contributions should keep each skill small, installable, and generic. Changes to `codex-adversarial-gate` should preserve the central invariant: implementation work is not complete until reviewer `PASS`, critic `AGREE_PASS`, and both exact review outputs are archived.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow.

## 🛡️ Security

Do not archive review output that contains credentials, tokens, private paths, or sensitive diagnostics. See [SECURITY.md](SECURITY.md).

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE).
