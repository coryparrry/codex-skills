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
- Git, to clone the repository
- Python 3 for the adversarial review archive helper

### Install A Skill

Install `codex-adversarial-gate`:

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills
bash skills/codex-adversarial-gate/scripts/install.sh
```

Use the install script for `codex-adversarial-gate` because it also copies the custom reviewer agents.

Install `git-clean-merged-branch`:

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills
mkdir -p ~/.codex/skills
cp -R skills/git-clean-merged-branch ~/.codex/skills/git-clean-merged-branch
```

Install `triage-review-comments`:

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills
mkdir -p ~/.codex/skills
cp -R skills/triage-review-comments ~/.codex/skills/triage-review-comments
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
