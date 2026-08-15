# Contributing

Thanks for improving `codex-skills`.

## Development Principles

- Keep shipped skill source under `skills/` synchronized with the plugin mirror under `plugins/codex-skills/skills/`.
- Keep standalone Codex profiles under `agents/` synchronized with the plugin profiles under `plugins/codex-skills/agents/`.
- Preserve research-only non-mutation boundaries, primary-source verification, contradiction handling, and explicit uncertainty.
- Treat PR review comments as hypotheses and verify them against current code before recommending action.
- Keep Swift reviews focused on risk. Use the active toolchain and the changed execution paths as evidence.
- Keep merged-branch cleanup conservative: verify remote state, protect dirty worktrees, and require explicit force for unmerged deletion.
- Do not add private workflow assumptions, personal paths, secrets, or organization-specific jargon.
- Prefer references and scripts over bloating `SKILL.md`.

## Project Layout

| Path | Purpose |
|---|---|
| `skills/continue-deep-research/` | Existing-research continuation skill and evidence-delta references |
| `skills/git-clean-merged-branch/` | Safe local merged-branch cleanup skill and tests |
| `skills/research-repo-technology/` | Repository technology research skill and report contracts |
| `skills/swift-code-review/` | Swift and Apple-platform review workflow and reference files |
| `skills/triage-review-comments/` | PR review feedback triage skill and references |
| `agents/` | Standalone Codex subagent profile source |
| `plugins/codex-skills/agents/` | Installable Codex plugin profiles |
| `plugins/codex-skills/skills/` | Installable plugin mirror of shipped skills |
| `scripts/` | Repo-level installer, mirror checker, and install tests |
| `docs/` | User-facing documentation |

## Before You Commit

Run:

```bash
bash -n scripts/install.sh
bash scripts/test_install.sh
python3 skills/git-clean-merged-branch/tests/test_clean_merged_branch.py
python3 scripts/check_skill_mirror.py git-clean-merged-branch
python3 scripts/check_skill_mirror.py triage-review-comments
python3 scripts/check_skill_mirror.py continue-deep-research
python3 scripts/check_skill_mirror.py research-repo-technology
python3 scripts/check_skill_mirror.py swift-code-review
python3 -m json.tool skills.sh.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/codex-skills/.codex-plugin/plugin.json >/dev/null
git diff --check
```

Run the Codex skill validator for each changed skill if it is available:

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py skills/git-clean-merged-branch
python3 /path/to/skill-creator/scripts/quick_validate.py skills/triage-review-comments
python3 /path/to/skill-creator/scripts/quick_validate.py skills/continue-deep-research
python3 /path/to/skill-creator/scripts/quick_validate.py skills/research-repo-technology
python3 /path/to/skill-creator/scripts/quick_validate.py skills/swift-code-review
```

## Documentation Changes

When changing shipped behavior, update the relevant source skill or agent profile, plugin mirror, user guide, reference documentation, and validation coverage.

## Pull Request Checklist

- [ ] Source and plugin mirror copies match for changed shipped skills.
- [ ] Standalone and plugin copies match for changed agent profiles, including their model and reasoning-effort pins.
- [ ] Review findings are verified against current code.
- [ ] Branch cleanup retains dirty-worktree and unmerged-branch safeguards.
- [ ] No private paths, credentials, or local workflow assumptions were introduced.
- [ ] Validation commands pass.
