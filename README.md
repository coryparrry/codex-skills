# Codex Skills

Small Codex skills for review gates, Git branch cleanup, and PR feedback triage.

## Skills

### [codex-adversarial-gate](skills/codex-adversarial-gate/SKILL.md)

Keeps implementation work open until an independent completion reviewer returns `PASS`, a critic returns `AGREE_PASS`, and both exact review outputs are archived under `docs/Adversarial Reviews/`.

Use it for plan checks, phase or slice closeout, and recovery when a completion gate was skipped. The installer also copies the bundled custom reviewer TOMLs into Codex's agents directory.

- [Installation](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [Reference](docs/reference.md)

### [git-clean-merged-branch](docs/git-clean-merged-branch.md)

Safely returns a repo to its default branch after the current branch has been merged. It fetches, fast-forward pulls, and deletes only the starting local branch after refusing dirty worktrees.

### [triage-review-comments](docs/triage-review-comments.md)

Inventories PR review comments, strips noise, deduplicates repeated findings, classifies the rest, resolves clearly fixed inline threads when tooling is available, and recommends prevention checks.

## Quick Start

Install the adversarial gate and its custom agents:

```bash
/bin/bash -c 'set -euo pipefail
tmp_dir="$(mktemp -d)"
trap "rm -rf \"$tmp_dir\"" EXIT
git clone --depth 1 https://github.com/coryparrry/codex-skills.git "$tmp_dir"
/bin/bash "$tmp_dir/scripts/install.sh"'
```

Install a single skill from a local clone:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"
cp -R skills/git-clean-merged-branch "$CODEX_HOME/skills/git-clean-merged-branch"
```

Restart Codex if the installed skills or agents do not appear immediately.

## Layout

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

## Codex Marketplace

The Codex plugin manifest lives at [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json) and exposes the skills under [`skills/`](skills/).

## License

MIT. See [LICENSE](LICENSE).
