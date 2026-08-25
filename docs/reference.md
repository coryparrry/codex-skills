# Codex Skills Reference

## Repository Layout

```text
.agents/
  plugins/
plugins/
  codex-skills/
    .codex-plugin/
    plugin.json
    skills/
scripts/
skills.sh.json
skills/
  appstore-readiness-audit/
  codex-routing/
  continue-deep-research/
  deep-code-review/
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
| `codex-routing` | Coordinate Sol advice and Luna investigation and implementation | `SKILL.md`, `agents/openai.yaml` |
| `continue-deep-research` | Continue an existing evidence base and report only the verified research delta | `SKILL.md`, `agents/openai.yaml`, `references/` |
| `deep-code-review` | Audit a repository snapshot or review affected behavior across a change, with validated defects, blockers, and auditable coverage | `SKILL.md`, `agents/openai.yaml`, `references/` |
| `git-clean-merged-branch` | Clean up one merged local Git branch safely | `SKILL.md`, `agents/openai.yaml`, `scripts/`, `tests/` |
| `research-repo-technology` | Research which technologies a live repository should adopt, adapt, build, or reject | `SKILL.md`, `agents/openai.yaml`, `references/` |
| `swift-code-review` | Review focused Swift and Apple-platform changes or provide their specialist lane in a deep review | `SKILL.md`, `agents/openai.yaml`, `references/` |
| `triage-review-comments` | Classify PR review comments and recommend prevention checks | `SKILL.md`, `agents/openai.yaml`, `references/` |

## Package Metadata

| Surface | Path |
|---|---|
| Codex marketplace | `.agents/plugins/marketplace.json` |
| Agent Plugins v1 manifest | `plugins/codex-skills/plugin.json` |
| Codex manifest | `plugins/codex-skills/.codex-plugin/plugin.json` |
| skills.sh grouping | `skills.sh.json` |

Agent Plugins v1 clients discover immediate skill directories from `plugins/codex-skills/skills/`. Codex uses the same skill folders through its own manifest. Both manifests share one version, and the skills.sh group names and entries must stay aligned with the source skill names.

## Repo-Level Scripts

| Script | Purpose |
|---|---|
| `scripts/install.sh` | Installs all top-level repo skills from a trusted checkout |
| `scripts/test_install.sh` | Smoke-tests bundle installation, preservation, and curl-style rejection |
| `scripts/build_agent_plugin.py` | Builds a clean Agent Plugins v1 package without Codex-only files |
| `scripts/check_skill_mirror.py` | Confirms a source skill matches its plugin mirror |
| `scripts/marketplace_release_evidence.py` | Emits repository-only marketplace candidate evidence; it never claims local Codex refresh |
| `scripts/validate_release_contract.py` | Checks source, manifests, the pinned Agent Plugins schema, marketplace, docs, and skills.sh publication contracts |

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
python3 scripts/tests/test_marketplace_release_evidence.py
python3 scripts/tests/test_validate_release_contract.py
python3 scripts/tests/test_build_agent_plugin.py
python3 scripts/validate_release_contract.py --base-ref origin/main
python3 scripts/marketplace_release_evidence.py --event pull_request --base-ref origin/main
bash -n scripts/install.sh
bash scripts/test_install.sh
python3 skills/git-clean-merged-branch/tests/test_clean_merged_branch.py
python3 skills/appstore-readiness-audit/tests/test_check_review_notes.py
python3 scripts/check_skill_mirror.py appstore-readiness-audit
python3 scripts/check_skill_mirror.py codex-routing
python3 scripts/check_skill_mirror.py deep-code-review
python3 scripts/check_skill_mirror.py git-clean-merged-branch
python3 scripts/check_skill_mirror.py triage-review-comments
python3 scripts/check_skill_mirror.py continue-deep-research
python3 scripts/check_skill_mirror.py research-repo-technology
python3 scripts/check_skill_mirror.py swift-code-review
python3 -m json.tool skills.sh.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/codex-skills/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/codex-skills/plugin.json >/dev/null
npx skills add . --list
for skill in skills/*; do skills-ref validate "$skill"; done
git diff --check
```

## Related Docs

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [App Store Readiness Audit](app-review/appstore-readiness-audit.md)
- [Codex Routing](orchestration/codex-routing.md)
- [Deep Code Review](code-review/deep-code-review.md)
- [Git Clean Merged Branch](git-workflow/git-clean-merged-branch.md)
- [Triage Review Comments](code-review/triage-review-comments.md)
- [Continue Deep Research](research/continue-deep-research.md)
- [Repository Technology Research](research/research-repo-technology.md)
- [Swift Code Review](code-review/swift-code-review.md)
