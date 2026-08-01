# Codex Skills

![Codex Skill Bundle](https://img.shields.io/badge/Codex-Skill_Bundle-111827?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-16a34a?style=for-the-badge)
[![skills.sh](https://skills.sh/b/coryparrry/codex-skills)](https://skills.sh/coryparrry/codex-skills)

A focused Codex skill bundle for evidence-led research, PR review triage, and safe merged-branch cleanup.

Each skill handles one repeated workflow, keeps its top-level `SKILL.md` readable, and places supporting rules in local references, scripts, or tests.

## Install

Install the full bundle for Codex:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill '*'
```

Install one skill by replacing the slug:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill triage-review-comments
```

Prefer the Codex app marketplace? Add `https://github.com/coryparrry/codex-skills` as a marketplace source and install **Codex Skills**. Full install notes are in [docs/installation.md](docs/installation.md).

## Pick The Skill

| Use this when... | Skill | What it protects |
|---|---|---|
| Existing ChatGPT Deep Research, notes, or reports need continuing with repository context. | [`continue-deep-research`](docs/continue-deep-research.md) | Prior evidence and provenance, current verification, contradictions, and a clear research delta. |
| A live repository needs evidence-backed technology recommendations. | [`research-repo-technology`](docs/research-repo-technology.md) | Repository-specific fit, source-level evidence, privacy and licence constraints, and bounded proof costs. |
| PR comments need separating from bot noise. | [`triage-review-comments`](docs/triage-review-comments.md) | Stale review threads, duplicate findings, unverified claims, and missing prevention checks. |
| A merged branch needs local cleanup. | [`git-clean-merged-branch`](docs/git-clean-merged-branch.md) | Unsafe deletion, stale default branches, and mistaken cleanup of unmerged work. |

## What Is Shipped

| Surface | Purpose |
|---|---|
| [`skills/`](skills/) | Source skill folders loaded by local installs and maintainers. |
| [`plugins/codex-skills/skills/`](plugins/codex-skills/skills/) | Marketplace mirror for the shipped skills. |
| [`plugins/codex-skills/.codex-plugin/plugin.json`](plugins/codex-skills/.codex-plugin/plugin.json) | Codex plugin metadata. |
| [`skills.sh.json`](skills.sh.json) | skills.sh repo-page grouping metadata. |
| [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json) | Codex marketplace entry. |
| [`experimental/`](experimental/) | Reserved for unshipped experiments. |

## Validation

For packaging changes, run:

```bash
bash -n scripts/install.sh
bash scripts/test_install.sh
python3 skills/git-clean-merged-branch/tests/test_clean_merged_branch.py
python3 scripts/check_skill_mirror.py git-clean-merged-branch
python3 scripts/check_skill_mirror.py triage-review-comments
python3 scripts/check_skill_mirror.py continue-deep-research
python3 scripts/check_skill_mirror.py research-repo-technology
python3 -m json.tool skills.sh.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/codex-skills/.codex-plugin/plugin.json >/dev/null
git diff --check
```

## Documentation

- [Installation](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [Git Clean Merged Branch](docs/git-clean-merged-branch.md)
- [Triage Review Comments](docs/triage-review-comments.md)
- [Continue Deep Research](docs/continue-deep-research.md)
- [Repository Technology Research](docs/research-repo-technology.md)
- [Reference](docs/reference.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## Security

Do not commit secrets, tokens, private paths, or sensitive diagnostics. See [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
