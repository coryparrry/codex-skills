<img width="2508" height="627" alt="Codexskillsheaders" src="https://github.com/user-attachments/assets/e4504b7c-2056-48ad-b5ac-70b3ae773aed" />

# Codex Skills

![Codex Skill Bundle](https://img.shields.io/badge/Codex-Skill_Bundle-111827?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-16a34a?style=for-the-badge)
[![skills.sh](https://skills.sh/b/coryparrry/codex-skills)](https://skills.sh/coryparrry/codex-skills)

> Eight Codex skills for research, App Store readiness, engineering advice, deep repository review, Swift review, PR feedback triage, and safe branch cleanup.

Each skill solves one repeated workflow problem. Its `SKILL.md` contains the main instructions.

Supporting details stay in references, scripts, or tests.

## 🚀 Install

### Codex marketplace

1. Open **Plugins** in Codex.
2. Select **Add marketplace**.
3. Add `https://github.com/coryparrry/codex-skills`.
4. Install **Codex Skills**.

Read the [installation guide](docs/installation.md) for more information.

### Cursor

The same eight skills are packaged as a portable Cursor Agent Plugin. Follow the [Cursor installation guide](docs/installation.md#install-in-cursor) to load it from Cursor's supported local-plugin directory.

### skills.sh

Install the full bundle:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill '*'
```

Install one skill:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill triage-review-comments
```

Replace the skill slug in the command.

## ✨ Skills

| Need | Skill | What it does |
|---|---|---|
| 🔬 Continue an existing research packet. | [`continue-deep-research`](docs/continue-deep-research.md) | Checks the existing evidence, resolves contradictions, and reports the verified delta. |
| 🔭 Assess technology options for a live repository. | [`research-repo-technology`](docs/research-repo-technology.md) | Uses repository evidence and primary sources to recommend whether to adopt, adapt, build, or reject an option. |
| 🍎 Audit an app before App Store submission. | [`appstore-readiness-audit`](docs/appstore-readiness-audit.md) | Reconciles the release candidate, Apple policy, runtime evidence, privacy, metadata, and reviewer access without changing the app. |
| 🧠 Keep the root agent in an advisor role. | [`engineering-advisor`](docs/engineering-advisor.md) | Sends edits to matched workers while the root owns scope, review, and validation. |
| 🔎 Audit a repository or review a change across it. | [`deep-code-review`](docs/deep-code-review.md) | Traces production flows, shared contracts, affected behavior, and explicit coverage gaps before reporting validated findings. |
| 🧩 Review Swift and Apple-platform changes. | [`swift-code-review`](docs/swift-code-review.md) | Looks for reachable ownership, isolation, identity, lifetime, representation, and side-effect problems. |
| 🧭 Triage pull-request feedback. | [`triage-review-comments`](docs/triage-review-comments.md) | Separates current, actionable findings from stale, duplicate, or unsupported comments. |
| 🧹 Remove a merged local branch. | [`git-clean-merged-branch`](docs/git-clean-merged-branch.md) | Checks the default branch, protects dirty worktrees and unmerged work, then removes the branch safely. |

The research skills work with the runtime that is available. They use independent lanes only when that improves coverage. Otherwise, they run a bounded root-only audit and say what was not covered.

## 🧰 What the Plugin Contains

| Surface | Purpose |
|---|---|
| [`skills/`](skills/) | Source skill folders for maintainers and skills.sh installations. |
| [`plugins/codex-skills/skills/`](plugins/codex-skills/skills/) | Plugin copies of the shipped skills. |
| [`plugins/codex-skills/.codex-plugin/plugin.json`](plugins/codex-skills/.codex-plugin/plugin.json) | Codex plugin metadata. |
| [`plugins/cursor-skills/plugin.json`](plugins/cursor-skills/plugin.json) | Cursor Agent Plugin manifest. |
| [`plugins/cursor-skills/`](plugins/cursor-skills/) | Portable Cursor Agent Plugin package. |
| [`skills.sh.json`](skills.sh.json) | Skill groups for the skills.sh repository page. |
| [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json) | Codex marketplace entry. |
| [`experimental/`](experimental/) | Unshipped experiments. The installer does not include them. |

## 🧪 Validation

Run these commands after a packaging change:

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
python3 scripts/check_skill_mirror.py appstore-readiness-audit cursor-skills
python3 scripts/check_skill_mirror.py deep-code-review cursor-skills
python3 scripts/check_skill_mirror.py engineering-advisor cursor-skills
python3 scripts/check_skill_mirror.py git-clean-merged-branch cursor-skills
python3 scripts/check_skill_mirror.py triage-review-comments cursor-skills
python3 scripts/check_skill_mirror.py continue-deep-research cursor-skills
python3 scripts/check_skill_mirror.py research-repo-technology cursor-skills
python3 scripts/check_skill_mirror.py swift-code-review cursor-skills
python3 -m json.tool skills.sh.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/codex-skills/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/cursor-skills/plugin.json >/dev/null
npx skills add . --list
git diff --check
```

## 📖 Documentation

- [Installation](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [App Store Readiness Audit](docs/appstore-readiness-audit.md)
- [Deep Code Review](docs/deep-code-review.md)
- [Engineering Advisor](docs/engineering-advisor.md)
- [Git Clean Merged Branch](docs/git-clean-merged-branch.md)
- [Triage Review Comments](docs/triage-review-comments.md)
- [Continue Deep Research](docs/continue-deep-research.md)
- [Repository Technology Research](docs/research-repo-technology.md)
- [Swift Code Review](docs/swift-code-review.md)
- [Reference](docs/reference.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## 🛡️ Security

Do not commit secrets, tokens, private paths, or sensitive diagnostics. See [SECURITY.md](SECURITY.md).

## 📄 License

MIT. See [LICENSE](LICENSE).
