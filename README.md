# Codex Skills

![Codex Skill Bundle](https://img.shields.io/badge/Codex-Skill_Bundle-111827?style=for-the-badge)
![Review Gate](https://img.shields.io/badge/Review_Gate-Adversarial-b91c1c?style=for-the-badge)
![Git Workflow](https://img.shields.io/badge/Git-Workflow-2563eb?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-16a34a?style=for-the-badge)
[![skills.sh](https://skills.sh/b/coryparrry/codex-skills)](https://skills.sh/coryparrry/codex-skills)

> A small Codex skill bundle for adversarial review gates, code review, safe Git branch cleanup, and practical PR feedback triage.

## 📌 Overview

`codex-skills` packages focused Codex skills that solve repeatable engineering workflow problems without bringing along a heavy process framework.

The main skill in this repo is `codex-adversarial-gate`. It keeps implementation work open until:

1. An independent completion reviewer returns `PASS`.
2. A critic reviews that `PASS` and returns `AGREE_PASS`.
3. Both exact review outputs are archived under `docs/Adversarial Reviews/`.

The repo also includes utility skills for generic code review, safe merged-branch cleanup, and PR review feedback triage.

## ✨ Skills

- 🧠 **codex-adversarial-gate** gates plan and implementation closeout with reviewer-plus-critic evidence.
- 🔍 **codex-code-review** runs repository-local multi-lens code review and writes review artifacts into the reviewed repo.
- 🌿 **git-clean-merged-branch** returns a repo to its default branch and deletes merged local and remote branches after safety checks.
- 🔎 **triage-review-comments** inventories PR comments, removes noise, deduplicates findings, and classifies real review work.
- 🧾 **Codex marketplace plugin** exposes the bundle through `plugins/codex-skills`.
- ✅ **Install smoke tests** verify the adversarial gate installer and custom-agent copy flow.

## 🧰 What Is Included

```text
.
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── docs/
│   ├── codex-adversarial-gate.md
│   ├── codex-code-review.md
│   ├── git-clean-merged-branch.md
│   ├── installation.md
│   ├── reference.md
│   ├── triage-review-comments.md
│   └── usage.md
├── plugins/
│   └── codex-skills/
│       ├── .codex-plugin/
│       └── skills/
├── scripts/
│   ├── install.sh
│   └── test_install.sh
├── skills.sh.json
└── skills/
    ├── codex-adversarial-gate/
    ├── codex-code-review/
    ├── git-clean-merged-branch/
    └── triage-review-comments/
```

## 🧩 Codex Marketplace

The repo marketplace lives at [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json). The Codex plugin manifest lives at [`plugins/codex-skills/.codex-plugin/plugin.json`](plugins/codex-skills/.codex-plugin/plugin.json), and it exposes the lightweight installable skills under [`plugins/codex-skills/skills/`](plugins/codex-skills/skills/).

Install through the Codex app:

1. Open **Plugins** in the Codex app.
2. Click **Add marketplace**.
3. Add this repository as the marketplace source: `https://github.com/coryparrry/codex-skills`.
4. Open the **Codex Skills** entry and click the plus button or **Add to Codex**.

If you use `codex-adversarial-gate`, also clone the repo and run its agent installer:

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills
bash skills/codex-adversarial-gate/scripts/install.sh
```

Marketplace install exposes `codex-adversarial-gate`, `git-clean-merged-branch`, and `triage-review-comments`. Use the skills.sh or manual install path for `codex-code-review`, which carries a larger reviewer-profile set.

The adversarial gate installer is still required when you need its custom reviewer TOMLs copied into `~/.codex/agents`.

## ⚡ Quick Usage

Run the adversarial completion gate:

```text
Use $codex-adversarial-gate to close this implementation slice with archived reviewer and critic evidence.
```

Run a generic code review:

```text
Use $codex-code-review to review this PR.
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
- [Codex Adversarial Review Gate](docs/codex-adversarial-gate.md)
- [Codex Code Review](docs/codex-code-review.md)
- [Reference](docs/reference.md)
- [Git Clean Merged Branch](docs/git-clean-merged-branch.md)
- [Triage Review Comments](docs/triage-review-comments.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## 🚀 Install

### Prerequisites

- Codex with local skills enabled
- Git, to clone the repository
- Python 3 for the adversarial review archive helper

### Install With skills.sh

Install the repo skills for Codex with the `skills` CLI:

```bash
npx skills add https://github.com/coryparrry/codex-skills --agent codex --skill '*'
```

If you use `codex-adversarial-gate` or `codex-code-review`, also run the agent installers:

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills
bash skills/codex-adversarial-gate/scripts/install.sh
bash skills/codex-code-review/scripts/install-agent-profiles.sh
```

### Install A Skill

Install `codex-adversarial-gate`:

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills
bash skills/codex-adversarial-gate/scripts/install.sh
```

Install `codex-code-review`:

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills
mkdir -p ~/.codex/skills
cp -R skills/codex-code-review ~/.codex/skills/codex-code-review
bash ~/.codex/skills/codex-code-review/scripts/install-agent-profiles.sh
```

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

## 🧪 Validation

Run the install smoke test:

```bash
bash scripts/test_install.sh
```

Run syntax and helper checks:

```bash
bash -n scripts/install.sh
bash -n skills/codex-adversarial-gate/scripts/install.sh
bash -n skills/codex-code-review/scripts/install-agent-profiles.sh
python3 -m json.tool skills.sh.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/codex-skills/.codex-plugin/plugin.json >/dev/null
python3 skills/codex-adversarial-gate/scripts/test_archive_adversarial_review.py
python3 -m py_compile \
  skills/codex-adversarial-gate/scripts/archive_adversarial_review.py \
  skills/codex-adversarial-gate/scripts/test_archive_adversarial_review.py
python3 skills/git-clean-merged-branch/tests/test_clean_merged_branch.py
git diff --check
```

Run a plugin packaging check when `plugin-eval` is available:

```bash
plugin-eval analyze plugins/codex-skills --format markdown
```

## 🤝 Contributing

Contributions should keep each skill small, installable, and generic. Changes to `codex-adversarial-gate` should preserve the central invariant: implementation work is not complete until reviewer `PASS`, critic `AGREE_PASS`, and both exact review outputs are archived.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow.

## 🛡️ Security

Do not archive review output that contains credentials, tokens, private paths, or sensitive diagnostics. See [SECURITY.md](SECURITY.md).

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE).
