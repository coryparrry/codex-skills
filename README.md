# Codex Skills

![Codex Skill Bundle](https://img.shields.io/badge/Codex-Skill_Bundle-111827?style=for-the-badge)
![Repository Audits](https://img.shields.io/badge/Repository-Audits-0f766e?style=for-the-badge)
![Review Gate](https://img.shields.io/badge/Review_Gate-Adversarial-b91c1c?style=for-the-badge)
![Automation Loops](https://img.shields.io/badge/Automation-Loops-2563eb?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-16a34a?style=for-the-badge)
[![skills.sh](https://skills.sh/b/coryparrry/codex-skills)](https://skills.sh/coryparrry/codex-skills)

Reusable Codex skills for workflow pressure points: repository context, repo readiness, completion evidence, bounded loops, PR review triage, safe branch cleanup, and beta multi-thread orchestration.

These are intentionally narrow. Each skill handles one repeated failure mode, keeps the top-level `SKILL.md` readable, and pushes deeper rules into local references, scripts, templates, or docs.

## Install

Install the full bundle for Codex:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill '*'
```

Install one skill by swapping the slug:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill auditing-repository-health
```

`codex-adversarial-gate` also ships local reviewer agents. After installing that skill, run `bash "${CODEX_HOME:-$HOME/.codex}/skills/codex-adversarial-gate/scripts/install.sh"`.

Prefer the Codex app marketplace? Add `https://github.com/coryparrry/codex-skills` as a marketplace source and install **Codex Skills**. Full install notes are in [docs/installation.md](docs/installation.md).

## Pick The Skill

| Use this when... | Skill | What it protects |
|---|---|---|
| 🗺️ A repo needs a compact context layer for repeated agent work. | [`knowledge-setup`](docs/knowledge-setup.md) | Stale instructions, whole-graph context loading, speculative architecture maps, and broad search before source verification. |
| 🏥 A repo is unfamiliar, drifting, or about to receive repeated agent work. | [`auditing-repository-health`](docs/auditing-repository-health.md) | Setup, scripts, validation gates, docs, packaging, generated-file hygiene, and source/mirror drift. |
| 🛡️ Codex wants to call a phase done. | [`codex-adversarial-gate`](docs/codex-adversarial-gate.md) | Completion claims, missing evidence, skipped dissent, and unarchived reviewer output. |
| 🔁 A task needs to run again later or keep checking state. | [`writing-codex-loops`](docs/writing-codex-loops.md) | Unbounded loops, vague retry behavior, missing stop conditions, and unclear escalation. |
| 🧭 PR comments need separating from bot noise. | [`triage-review-comments`](docs/triage-review-comments.md) | Stale review threads, duplicate findings, unverified claims, and missing prevention checks. |
| 🧹 A merged branch needs local cleanup. | [`git-clean-merged-branch`](docs/git-clean-merged-branch.md) | Unsafe deletion, stale default branches, and mistaken cleanup of unmerged work. |
| 🧪 Related work needs explicit beta orchestration. | [`multi-phase-orchestrator`](docs/multi-phase-orchestrator.md) | Overlapping worktrees, summary-only integration, and unowned validation lanes. |

## What Is Shipped

| Surface | Purpose |
|---|---|
| [`skills/`](skills/) | Source skill folders loaded by local installs and maintainers. |
| [`plugins/codex-skills/skills/`](plugins/codex-skills/skills/) | Marketplace mirror for the shipped skills. |
| [`plugins/codex-skills/.codex-plugin/plugin.json`](plugins/codex-skills/.codex-plugin/plugin.json) | Codex plugin metadata. |
| [`skills.sh.json`](skills.sh.json) | skills.sh repo-page grouping metadata. |
| [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json) | Codex marketplace entry. |
| [`experimental/`](experimental/) | Unshipped experiments; not installed until explicitly promoted. |

## Why This Bundle Exists

| Failure mode | Guardrail |
|---|---|
| Agents repeatedly rediscover repository structure or load an entire architecture graph. | Maintain a three-file context layer and progressively load only the selected route and nodes. |
| One passing check gets treated as proof the repo is ready. | Run the repository health audit before changing unfamiliar or high-churn repos. |
| Implementation closeout becomes a confident summary instead of evidence. | Gate the phase through reviewer `PASS`, critic `AGREE_PASS`, and archived outputs. |
| "Keep going" prompts turn into endless or unresumable work. | Write loops with observable state, cadence, retry limits, stops, and escalation. |
| Review feedback hides real bugs under stale or speculative comments. | Triage every claim against current code before fixing or resolving it. |
| Branch cleanup runs on hope. | Fetch, resolve the default branch, prove the branch is merged, then delete safely. |
| Parallel work merges summaries instead of verified files. | Use the beta orchestrator only when explicit worktree/thread coordination is wanted. |

## Validation

For packaging changes, run the checks that match the touched surface:

| Surface | Minimum checks |
|---|---|
| Installer or package metadata | `bash scripts/test_install.sh`, `python3 -m json.tool skills.sh.json >/dev/null`, `git diff --check` |
| Knowledge setup | `python3 skills/knowledge-setup/tests/test_progressive_graph_contract.py`, `python3 scripts/check_skill_mirror.py knowledge-setup` |
| Audit skill | `python3 skills/auditing-repository-health/tests/test_audit_repository_health.py`, `python3 scripts/check_skill_mirror.py auditing-repository-health` |
| Adversarial gate | `python3 skills/codex-adversarial-gate/scripts/test_archive_adversarial_review.py` |
| Git cleanup | `python3 skills/git-clean-merged-branch/tests/test_clean_merged_branch.py` |

The full validation matrix lives in [docs/reference.md](docs/reference.md#validation-commands).

## Documentation

- [Installation](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [Knowledge Setup](docs/knowledge-setup.md)
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
