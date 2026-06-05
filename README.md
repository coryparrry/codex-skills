# My Codex Skills

A personal collection of Codex skills I've built to solve real problems in my daily workflow. Each skill is self-contained, generic, and ready to install — grab the ones you want.

---

## Skills

### [generic-code-review](generic-code-review/README.md)

> *"Run a serious review without dragging private project assumptions into the next repo."*

This skill is a genericized version of a product-specific code-review workflow. It keeps the useful parts: specialist review lanes, coverage matrices, AI-generated-code failure-pattern calibration, and report consolidation. It removes private product names, private paths, product-specific docs tooling, and phase assumptions.

Reports are written inside the reviewed repository under `.codex/code-review-reports/`, and the skill includes Codex TOML profiles for reviewer, consolidator, and bounded fixer agents.

[Full docs →](generic-code-review/README.md)

### [codex-budget-router](codex-budget-router/README.md)

> *"Spend your strongest Codex model on judgment, not file searching."*

**Deprecated / needs update:** this skill still depends on removed GPT-5.3 Codex model routes and should not be used as-is until its routing table and agent profiles are refreshed.

I built this because I kept hitting my Codex limits halfway through real work. The root model was burning through expensive credits on repo scans, log triage, and routine test fixes — work cheaper models could handle just fine. Worse, my Spark limits sat completely unused because there was no safe way to route work to them.

This skill used to save me up to **20% of my limits** by routing broad search, routine implementation, tests, and bounded review to cheaper workers while keeping architecture and final judgment with the root model. It needs a current model refresh before it is useful again.

**Six worker profiles** cover the historical routing spectrum, but the GPT-5.3 Codex profiles are now stale.

[Full docs →](codex-budget-router/README.md)

### [git-clean-merged-branch](git-clean-merged-branch/README.md)

> *"Stop babysitting git. One command, done."*

I built this because I was fed up with the repetitive chore of cleaning up local branches after they'd been merged on GitHub. Fetch, switch, pull, delete — the same four commands every time, and I'd still occasionally delete the wrong branch. I found it boring, so I automated it.

This skill wraps the entire cleanup into a single safe command. It inspects before acting, refuses to run on a dirty worktree, resolves the actual default branch, and handles edge cases like squash-merge detection — all without `git reset --hard` or any other broad destructive command.

[Full docs →](git-clean-merged-branch/README.md)

### [triage-review-comments](triage-review-comments/README.md)

> *"Stop manually sorting PR feedback. Let the skill classify it for you."*

I built this because every time I submitted a PR and the reviews came back, I'd spend time manually reading through each comment, figuring out what was a real blocker versus noise, and deciding what to do about it. CodeRabbit, Cursor, and human reviewers all produce different formats and different signal-to-noise ratios — and I was doing the same triage dance every time. I realized I didn't actually have to.

This skill loads the full PR review context, builds a complete inventory, deduplicates by underlying issue, classifies everything into four buckets, resolves fixed inline threads on GitHub, tracks real deferred work in Linear, and recommends prevention tests so the same issues don't come back.

[Full docs →](triage-review-comments/README.md)

---

## Quick start

### Plugin marketplace install

The recommended install path is the Codex plugin marketplace flow. In the Codex app, open Settings -> Plugins, choose the option to add another marketplace source, and paste this repository URL:

```text
https://github.com/coryparrry/codex-skills.git
```

Codex can then install the `personal-codex-skills` plugin from that marketplace source and keep it updated from the Git repo.

CLI equivalent:

```bash
codex plugin marketplace add \
  'https://github.com/coryparrry/codex-skills.git' \
  --ref 'main' \
  --sparse '.agents/plugins' \
  --sparse 'plugins'

codex plugin list --marketplace codex-skills
codex plugin add personal-codex-skills --marketplace codex-skills
```

### Manual skill install

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills

# Install a skill
cp -r codex-budget-router ~/.agents/skills/codex-budget-router
codex-budget-router/scripts/install-agent-profiles.sh
```

Then restart Codex. Each skill's README has detailed install and usage instructions.

---

## Layout

Each skill lives in its own folder with a `SKILL.md`, agent profiles, scripts, and optional references and tests.

```text
codex-budget-router/
  SKILL.md        — deprecated routing skill
  README.md       — full documentation
  agents/         — worker TOML profiles
  references/     — workflows, prompts, fallback
  scripts/        — installer, audit tool
  tests/          — tests for the audit script

git-clean-merged-branch/
  SKILL.md        — the skill Codex loads
  README.md       — full documentation
  agents/         — agent metadata
  scripts/        — the cleanup script

triage-review-comments/
  SKILL.md        — the skill Codex loads
  README.md       — full documentation
  agents/         — agent metadata
  references/     — fuller triage guidance

generic-code-review/
  SKILL.md        — generic review router
  README.md       — full documentation
  agents/         — reviewer, consolidator, and fixer TOML profiles
  references/     — workflow and calibration references
  assets/         — report and coverage matrix templates
  scripts/        — agent profile installer

plugins/personal-codex-skills/
  .codex-plugin/  — plugin manifest
  skills/         — bundled installable copies of the skills

.agents/plugins/
  marketplace.json — repository marketplace manifest
```

---

## License

MIT
