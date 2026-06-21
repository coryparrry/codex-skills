# Reference

This reference describes the files, install paths, scripts, custom agents, and verdicts used by the `codex-skills` repository.

## Repository Layout

```text
.
  .agents/
    plugins/
      marketplace.json
  docs/
  plugins/
    codex-skills/
      .codex-plugin/
  scripts/
  skills.sh.json
  skills/
    codex-adversarial-gate/
    git-clean-merged-branch/
    multi-phase-orchestrator/
    triage-review-comments/
```

## Plugin Manifest

| Field | Value |
|---|---|
| Manifest path | `plugins/codex-skills/.codex-plugin/plugin.json` |
| Plugin name | `codex-skills` |
| Skills path | `./skills/` |
| Category | `Coding` |
| Capabilities | `Interactive`, `Read`, `Write` |

The manifest exposes the lightweight copied skill folders under `plugins/codex-skills/skills/`.

## skills.sh Config

| Field | Value |
|---|---|
| Config path | `skills.sh.json` |
| Repo page | `https://skills.sh/coryparrry/codex-skills` |
| Badge | `https://skills.sh/b/coryparrry/codex-skills` |
| Groups | `Review Gates`, `PR Review`, `Beta Orchestration`, `Git Workflow` |

The config controls how the repo page is grouped on skills.sh after the repo is seen by the `skills` CLI telemetry service.

## Marketplace Entry

Codex marketplace discovery uses a marketplace file that points at a plugin folder. This repo's marketplace file is:

```text
.agents/plugins/marketplace.json
```

It contains one plugin entry:

```json
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
```

Use the Codex app to add this repo as a marketplace source, then install **Codex Skills** from that marketplace.

Marketplace install exposes `codex-adversarial-gate`, `multi-phase-orchestrator` (beta), `git-clean-merged-branch`, and `triage-review-comments`. It does not copy custom reviewer TOMLs into `~/.codex/agents`; run `bash ~/.agents/skills/codex-adversarial-gate/scripts/install.sh` when those agents are needed.

## Skills

| Skill | Purpose | Main files |
|---|---|---|
| `codex-adversarial-gate` | Gate plan and implementation closeout with reviewer-plus-critic evidence | `SKILL.md`, `agents/`, `references/`, `scripts/`, `templates/` |
| `multi-phase-orchestrator` | Beta orchestration for related work units across fresh worktree threads | `SKILL.md`, `agents/openai.yaml` |
| `git-clean-merged-branch` | Clean up one merged local Git branch safely | `SKILL.md`, `agents/openai.yaml`, `scripts/clean_merged_branch.sh` |
| `triage-review-comments` | Classify PR review comments and recommend prevention checks | `SKILL.md`, `agents/openai.yaml`, `references/triage-review-comments.md` |

## Default Install Paths

| Component | Destination |
|---|---|
| `skills` CLI global skill copies | `~/.agents/skills/<skill-name>/` |
| Skills | `${CODEX_HOME:-$HOME/.codex}/skills/<skill-name>/` |
| Codex agents | `${CODEX_HOME:-$HOME/.codex}/agents/` |

`codex-adversarial-gate` needs a `skills` CLI copy first, then its local installer copies files into `CODEX_HOME`. The beta orchestrator and utility skills need only their skill folder.

## Repo-Level Scripts

| Script | Purpose |
|---|---|
| `scripts/install.sh` | Installs `codex-adversarial-gate` and its custom agents |
| `scripts/test_install.sh` | Smoke-tests local adversarial gate installs and curl-style installer rejection |

## Skill Scripts

| Script | Purpose |
|---|---|
| `skills/codex-adversarial-gate/scripts/install.sh` | Copies the adversarial gate skill and custom agents into Codex |
| `skills/codex-adversarial-gate/scripts/archive_adversarial_review.py` | Archives exact plan, completion, or critic review output |
| `skills/codex-adversarial-gate/scripts/test_archive_adversarial_review.py` | Tests the review archive helper |
| `skills/git-clean-merged-branch/scripts/clean_merged_branch.sh` | Fetches, switches to default branch, pulls, and deletes the starting branch |

## Codex Adversarial Gate Agents

| Agent | Purpose | Output |
|---|---|---|
| `plan_adversarial_reviewer` | Reviews plans before finalization or updates | `PASS_100`, `FAIL_NEEDS_REVISION`, `BLOCKED_OWNER_DECISION` |
| `task_completion_adversarial_reviewer` | Reviews implementation phase or slice closeout | `PASS`, `FAIL_NEEDS_FIX`, `BLOCKED_INSUFFICIENT_EVIDENCE`, `BLOCKED_OWNER_DECISION` |
| `task_completion_review_critic` | Audits reviewer `PASS` verdicts | `AGREE_PASS`, `DISAGREE_EVIDENCE`, `DISAGREE_CONCERN` |

All three agents are intended to be read-only.

## Review Archive Helper

Script:

```text
skills/codex-adversarial-gate/scripts/archive_adversarial_review.py
```

Arguments:

| Argument | Required | Description |
|---|---:|---|
| `--repo` | yes | Target repository root |
| `--kind` | yes | `plan`, `completion`, or `critic` |
| `--phase` | yes | Plan, phase, slice, or checkpoint name |
| `--reviewer` | yes | Reviewer role or custom agent name |
| `--verdict` | yes | Review disposition |
| `--resolution` | no | Implementer resolution when known |
| `--review-file` | one source required | File containing exact review output |
| `--stdin` | one source required | Read exact review output from standard input |

`--agent` is accepted as a hidden compatibility alias for `--reviewer`.

Archive files are written under:

```text
<repo>/docs/Adversarial Reviews/
```

## Git Cleanup Script

Script:

```text
skills/git-clean-merged-branch/scripts/clean_merged_branch.sh
```

Options:

| Option | Meaning |
|---|---|
| `--force-delete-unmerged` | Use `git branch -D` after safe deletion fails |
| `--keep-remote` | Preserve the old remote branch |
| `-h`, `--help` | Print script usage |

The script refuses to run outside a Git repo, without an `origin` remote, from detached `HEAD`, or with a dirty worktree.

## Triage Buckets

| Bucket | Meaning |
|---|---|
| `Fix now` | Reachable, meaningful, and should block merge |
| `Fix if cheap` | Probably valid, limited impact, and low-risk to take now |
| `Defer` | Real work, but better as follow-up |
| `Ignore` | Duplicate, stale, speculative, style-only, or already fixed |

## Validation Commands

```bash
bash -n scripts/install.sh
bash -n skills/codex-adversarial-gate/scripts/install.sh
bash scripts/test_install.sh
python3 skills/codex-adversarial-gate/scripts/test_archive_adversarial_review.py
python3 -m py_compile \
  skills/codex-adversarial-gate/scripts/archive_adversarial_review.py \
  skills/codex-adversarial-gate/scripts/test_archive_adversarial_review.py
python3 -m json.tool skills.sh.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/codex-skills/.codex-plugin/plugin.json >/dev/null
git diff --check
```

If `plugin-eval` is installed, run:

```bash
plugin-eval analyze plugins/codex-skills --format markdown
```

## Related Docs

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [Codex Adversarial Review Gate](codex-adversarial-gate.md)
- [Multi-Phase Orchestrator](multi-phase-orchestrator.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
- [Triage Review Comments](triage-review-comments.md)
