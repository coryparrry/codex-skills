# My Codex Skills

A personal collection of Codex skills I've built to solve real problems in my daily workflow. Each skill is self-contained, generic, and ready to install — grab the ones you want.

---

## Skills

### [codex-budget-router](codex-budget-router/README.md)

> *"Spend your strongest Codex model on judgment, not file searching."*

I built this because I kept hitting my Codex limits halfway through real work. The root model was burning through expensive credits on repo scans, log triage, and routine test fixes — work cheaper models could handle just fine. Worse, my Spark limits sat completely unused because there was no safe way to route work to them.

This skill saves me up to **20% of my limits** by routing broad search, routine implementation, tests, and bounded review to cheaper workers while keeping architecture and final judgment with the root model.

**Six worker profiles** cover the full spectrum: cheap mapping and research (gpt-5.4-mini), Spark-first routine implementation (gpt-5.3-codex-spark), bounded non-trivial work (gpt-5.3-codex), and mid-tier review and debugging (gpt-5.4).

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

```bash
git clone https://github.com/<your-org>/codex-skills.git
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
  SKILL.md        — the skill Codex loads
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
```

---

## License

MIT
