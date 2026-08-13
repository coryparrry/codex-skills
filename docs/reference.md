# Codex Skills Reference

## Repository Layout

```text
.agents/
  plugins/
plugins/
  codex-skills/
    .codex-plugin/
    skills/
scripts/
skills.sh.json
skills/
  appstore-readiness-audit/
  continue-deep-research/
  deep-code-review/
  engineering-advisor/
  git-clean-merged-branch/
  research-repo-technology/
  swift-code-review/
  triage-review-comments/
```

The source skill folders under `skills/` must match their copies under `plugins/codex-skills/skills/`.

## Published Skills

| Skill | Purpose | Main files |
|---|---|---|
| `appstore-readiness-audit` | Audit an Apple release candidate before App Store upload or submission | `SKILL.md`, `agents/openai.yaml`, `references/`, `scripts/`, `tests/` |
| `continue-deep-research` | Continue an existing evidence base and report only the verified research delta | `SKILL.md`, `agents/openai.yaml`, `references/` |
| `deep-code-review` | Audit a repository snapshot or review affected behavior across a change, with validated defects, blockers, and auditable coverage | `SKILL.md`, `agents/openai.yaml`, `references/` |
| `engineering-advisor` | Route edits to capability-matched Terra workers while root remains the non-implementing advisor | `SKILL.md`, `agents/openai.yaml` |
| `git-clean-merged-branch` | Clean up one merged local Git branch safely | `SKILL.md`, `agents/openai.yaml`, `scripts/`, `tests/` |
| `research-repo-technology` | Research which technologies a live repository should adopt, adapt, build, or reject | `SKILL.md`, `agents/openai.yaml`, `references/` |
| `swift-code-review` | Review focused Swift and Apple-platform changes or provide their specialist lane in a deep review | `SKILL.md`, `agents/openai.yaml`, `references/` |
| `triage-review-comments` | Classify PR review comments and recommend prevention checks | `SKILL.md`, `agents/openai.yaml`, `references/` |

## Package Metadata

| Surface | Path |
|---|---|
| Codex marketplace | `.agents/plugins/marketplace.json` |
| Plugin manifest | `plugins/codex-skills/.codex-plugin/plugin.json` |
| skills.sh grouping | `skills.sh.json` |

The plugin manifest exposes all skill folders under `plugins/codex-skills/skills/`. The skills.sh group names and entries must stay aligned with the source skill names.

## Repo-Level Scripts

| Script | Purpose |
|---|---|
| `scripts/install.sh` | Installs all top-level repo skills from a trusted checkout |
| `scripts/test_install.sh` | Smoke-tests bundle installation, preservation, and curl-style rejection |
| `scripts/check_skill_mirror.py` | Confirms a source skill matches its plugin mirror |
| `scripts/validate_release_contract.py` | Checks source, plugin, marketplace, docs, and skills.sh publication contracts |

## Git Cleanup Script

`skills/git-clean-merged-branch/scripts/clean_merged_branch.sh` supports:

| Option | Meaning |
|---|---|
| `--force-delete-unmerged` | Use `git branch -D` after safe deletion fails |
| `--keep-remote` | Preserve the old remote branch |
| `-h`, `--help` | Print script usage |

The script refuses to run outside a Git repository, without an `origin` remote, from detached `HEAD`, or with a dirty worktree.

## Triage Buckets

| Bucket | Meaning |
|---|---|
| `Fix now` | Reachable, meaningful, and should block merge |
| `Fix if cheap` | Probably valid, limited impact, and low-risk to take now |
| `Defer` | Real work, but better as follow-up |
| `Ignore` | Duplicate, stale, speculative, style-only, or already fixed |

## Validation Commands

```bash
python3 -m pip install -r requirements-release.txt
python3 scripts/tests/test_validate_release_contract.py
python3 scripts/validate_release_contract.py --base-ref origin/main
bash -n scripts/install.sh
bash scripts/test_install.sh
python3 skills/git-clean-merged-branch/tests/test_clean_merged_branch.py
python3 skills/appstore-readiness-audit/tests/test_check_review_notes.py
python3 scripts/check_skill_mirror.py appstore-readiness-audit
python3 scripts/check_skill_mirror.py deep-code-review
python3 scripts/check_skill_mirror.py engineering-advisor
python3 scripts/check_skill_mirror.py git-clean-merged-branch
python3 scripts/check_skill_mirror.py triage-review-comments
python3 scripts/check_skill_mirror.py continue-deep-research
python3 scripts/check_skill_mirror.py research-repo-technology
python3 scripts/check_skill_mirror.py swift-code-review
python3 -m json.tool skills.sh.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/codex-skills/.codex-plugin/plugin.json >/dev/null
npx skills add . --list
git diff --check
```

## Related Docs

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [App Store Readiness Audit](appstore-readiness-audit.md)
- [Deep Code Review](deep-code-review.md)
- [Engineering Advisor](engineering-advisor.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
- [Triage Review Comments](triage-review-comments.md)
- [Continue Deep Research](continue-deep-research.md)
- [Repository Technology Research](research-repo-technology.md)
- [Swift Code Review](swift-code-review.md)
