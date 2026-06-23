# Codex Skills

![Codex Skill Bundle](https://img.shields.io/badge/Codex-Skill_Bundle-111827?style=for-the-badge)
![Review Gate](https://img.shields.io/badge/Review_Gate-Adversarial-b91c1c?style=for-the-badge)
![Automation Loops](https://img.shields.io/badge/Automation-Loops-2563eb?style=for-the-badge)
![Git Workflow](https://img.shields.io/badge/Git-Workflow-047857?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-16a34a?style=for-the-badge)
[![skills.sh](https://skills.sh/b/coryparrry/codex-skills)](https://skills.sh/coryparrry/codex-skills)

Small Codex skills for real workflow pressure: adversarial completion gates, bounded loops, beta multi-worktree orchestration, repository health audits, branch cleanup, and PR review triage.

These skills are meant to stay narrow. Each one handles one recurring failure mode, keeps the main `SKILL.md` readable, and moves heavier process detail into local references, templates, scripts, or user-facing docs.

## Quickstart (30-second setup)

Install the full bundle with `skills.sh`:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill '*'
```

If you use `codex-adversarial-gate`, also install its local reviewer agents:

```bash
bash "${CODEX_HOME:-$HOME/.codex}/skills/codex-adversarial-gate/scripts/install.sh"
```

Then invoke the skill you need:

```text
Use $codex-adversarial-gate to close this implementation slice with archived reviewer and critic evidence.
Use $writing-codex-loops to create a bounded heartbeat for this PR.
Use $auditing-repository-health to audit this repo before starting work.
Use $triage-review-comments to triage the review comments on this PR.
```

You can also install through the Codex app by adding this repository as a marketplace source and installing **Codex Skills**. See [Install Codex Skills](docs/installation.md).

## Why These Skills Exist

### #1: Codex Marks Work Complete Too Early

**The problem.** Implementation threads can confuse confidence, passing local checks, or a tidy summary with actual completion. That loses dissent, skips evidence, and makes review archives impossible to reconstruct later.

**The fix.** Use [`codex-adversarial-gate`](docs/codex-adversarial-gate.md). It keeps a phase or slice open until an independent reviewer returns `PASS`, a critic returns `AGREE_PASS`, and both exact outputs are archived under `docs/Adversarial Reviews/`.

### #2: Loops Drift Or Run Forever

**The problem.** "Keep checking" and "continue until done" prompts are under-specified. Without state, retry limits, stop conditions, and escalation, repeated work becomes unbounded or impossible to resume.

**The fix.** Use [`writing-codex-loops`](docs/writing-codex-loops.md). It turns recurring work into a loop contract with observable state, cadence, feedback, progress checks, retry rules, success stops, blocked stops, and a concrete escalation question.

### #3: Parallel Work Loses Control

**The problem.** Multi-thread or multi-worktree work can overlap edits, drop validation ownership, or merge child outputs based on summaries instead of live files.

**The fix.** Use [`multi-phase-orchestrator`](docs/multi-phase-orchestrator.md) when you explicitly want beta orchestration. It routes each work unit into a fresh worktree thread, monitors status, verifies output against live files and checks, and integrates deliberately.

### #4: PR Review Noise Hides Real Bugs

**The problem.** Bot comments, stale review threads, duplicate findings, and preference-only feedback can bury the issues that should actually block a PR.

**The fix.** Use [`triage-review-comments`](docs/triage-review-comments.md). It inventories review comments, verifies current-code reachability, rejects false positives, classifies real findings, and recommends prevention checks.

### #5: Repos Hide Readiness Problems

**The problem.** A clean branch or one passing test can hide missing setup scripts, undocumented validation gates, source/package drift, generated-file churn, stale docs, or repo-size problems.

**The fix.** Use [`auditing-repository-health`](docs/auditing-repository-health.md). It audits live Git state, normalized script responsibilities, validation surfaces, packaging/mirror health, generated-file hygiene, docs rendering, and size/history risks before work starts.

### #6: Merged Branch Cleanup Is Easy To Get Wrong

**The problem.** After a PR merge, local state can stay on a stale branch, default branch updates can be skipped, and unsafe deletion can remove work that was not actually merged.

**The fix.** Use [`git-clean-merged-branch`](docs/git-clean-merged-branch.md). It fetches, resolves the default branch, checks cleanliness, updates the default branch, and deletes only the branch it can safely clean up.

## Reference

These skills split by invocation discipline and risk, not by folder name.

### Everyday Model-Invoked Skills

- **[`codex-adversarial-gate`](skills/codex-adversarial-gate/SKILL.md)** - Use when reviewing Codex plans, closing implementation phases or slices, or auditing completion claims.
- **[`writing-codex-loops`](skills/writing-codex-loops/SKILL.md)** - Use when designing, writing, repairing, or scheduling Codex work loops and automations.
- **[`triage-review-comments`](skills/triage-review-comments/SKILL.md)** - Use when PR review comments, bot findings, stale threads, or prevention checks need triage.
- **[`auditing-repository-health`](skills/auditing-repository-health/SKILL.md)** - Use when auditing repo readiness, scripts, validation, hygiene, docs, packaging, or release health.
- **[`git-clean-merged-branch`](skills/git-clean-merged-branch/SKILL.md)** - Use when a merged GitHub branch should be cleaned up safely; short prompts like `sort git` or `clean merged branch` intentionally route here.

### Explicit Beta Skill

- **[`multi-phase-orchestrator`](skills/multi-phase-orchestrator/SKILL.md)** - Use only when the user explicitly names `$multi-phase-orchestrator` or directly asks for this beta orchestration flow.

### Packaging Surface

- **Source skills:** [`skills/`](skills/)
- **Installable plugin mirror:** [`plugins/codex-skills/skills/`](plugins/codex-skills/skills/)
- **Codex plugin manifest:** [`plugins/codex-skills/.codex-plugin/plugin.json`](plugins/codex-skills/.codex-plugin/plugin.json)
- **skills.sh grouping metadata:** [`skills.sh.json`](skills.sh.json)
- **Codex marketplace entry:** [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json)
- **Experimental work:** [`experimental/`](experimental/) stays outside the shipped bundle until explicitly promoted.

## Choose A Skill

| Situation | Skill |
|---|---|
| Review a plan before execution | `codex-adversarial-gate` |
| Close an implementation phase or slice | `codex-adversarial-gate` |
| Recover from a skipped completion gate | `codex-adversarial-gate` |
| Design or create a bounded Codex automation loop | `writing-codex-loops` |
| Coordinate related work units through fresh worktree threads | `multi-phase-orchestrator` beta |
| Audit repository readiness before work | `auditing-repository-health` |
| Clean up one merged local Git branch | `git-clean-merged-branch` |
| Classify PR review feedback | `triage-review-comments` |

## What Is Included

```text
.
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── docs/
│   ├── codex-adversarial-gate.md
│   ├── git-clean-merged-branch.md
│   ├── installation.md
│   ├── multi-phase-orchestrator.md
│   ├── reference.md
│   ├── triage-review-comments.md
│   ├── usage.md
│   └── writing-codex-loops.md
├── experimental/
│   └── codex-pr-packet-loop/
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
    ├── auditing-repository-health/
    ├── git-clean-merged-branch/
    ├── multi-phase-orchestrator/
    ├── triage-review-comments/
    └── writing-codex-loops/
```

## Install

### Codex Marketplace

1. Open **Plugins** in the Codex app.
2. Click **Add marketplace**.
3. Add this repository as the marketplace source: `https://github.com/coryparrry/codex-skills`.
4. Open **Codex Skills** and click the plus button or **Add to Codex**.

Marketplace install exposes the shipped skills, but it does not copy the adversarial gate custom reviewer TOMLs into `~/.codex/agents`. Run the adversarial gate installer when those agents are needed.

### skills.sh

Install every shipped skill:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill '*'
```

Install a single skill:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill codex-adversarial-gate
npx skills add coryparrry/codex-skills --global --agent codex --skill writing-codex-loops
npx skills add coryparrry/codex-skills --global --agent codex --skill multi-phase-orchestrator
npx skills add coryparrry/codex-skills --global --agent codex --skill auditing-repository-health
npx skills add coryparrry/codex-skills --global --agent codex --skill git-clean-merged-branch
npx skills add coryparrry/codex-skills --global --agent codex --skill triage-review-comments
```

The `skills` CLI stores global Codex skill copies under `~/.codex/skills/` when installed with `--agent codex`.

### Trusted Local Checkout

From a trusted checkout, install all repo skills into `${CODEX_HOME:-$HOME/.codex}` and install the adversarial gate custom agents:

```bash
bash scripts/install.sh
```

Do not pipe this installer from a remote URL. It intentionally expects a trusted local checkout.

## Maintaining This Bundle

Changes to shipped skill behavior must update the surfaces that future agents and users actually load.

| Surface | Rule |
|---|---|
| `skills/<skill>/` | Source of truth for the shipped skill. |
| `plugins/codex-skills/skills/<skill>/` | Keep this mirror synchronized for Codex marketplace installs. |
| `skills/<skill>/agents/openai.yaml` | Keep OpenAI skill metadata aligned with `SKILL.md`. |
| `docs/<skill>.md`, `docs/usage.md`, `docs/reference.md` | Update when workflow behavior, install steps, or user-facing invocation changes. |
| `README.md`, `skills.sh.json`, `.agents/plugins/marketplace.json`, `plugins/codex-skills/.codex-plugin/plugin.json` | Update when shipped skills, grouping, marketplace discovery, plugin prompts, or packaging metadata changes. |
| `scripts/` and skill-local `scripts/` | Update tests and installers when packaging behavior changes. |

Preserve the adversarial gate invariant: implementation closeout requires reviewer `PASS`, critic `AGREE_PASS`, and exact archived evidence. Preserve the loop-writing invariant: repeated Codex work needs observable state, retry limits, stop conditions, and escalation.

Do not mirror or list experimental skills as shipped until a promotion change explicitly moves them into `skills/`, `plugins/codex-skills/skills/`, package metadata, and the public docs together.

## Validation

Run the install smoke test:

```bash
bash scripts/test_install.sh
```

Run syntax and helper checks:

```bash
bash -n scripts/install.sh
bash -n skills/codex-adversarial-gate/scripts/install.sh
python3 -m json.tool skills.sh.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/codex-skills/.codex-plugin/plugin.json >/dev/null
python3 /path/to/skill-creator/scripts/quick_validate.py skills/writing-codex-loops
python3 /path/to/skill-creator/scripts/quick_validate.py skills/auditing-repository-health
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

## Documentation

- [Installation](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [Audit Repository Health](docs/auditing-repository-health.md)
- [Codex Adversarial Review Gate](docs/codex-adversarial-gate.md)
- [Writing Codex Loops](docs/writing-codex-loops.md)
- [Multi-Phase Orchestrator](docs/multi-phase-orchestrator.md)
- [Git Clean Merged Branch](docs/git-clean-merged-branch.md)
- [Triage Review Comments](docs/triage-review-comments.md)
- [Reference](docs/reference.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## Security

Do not commit secrets, tokens, private paths, or sensitive diagnostics. Do not archive review output that contains credentials. See [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
