# Codex Skills

**Spend your strongest Codex model on judgment, not file searching.**

A collection of reusable skills that make your Codex usage last longer by routing suitable work to cheaper, bounded workers — without giving up quality where it matters.

---

## Why this exists

I kept hitting my Codex limits halfway through real work. The root model was burning through expensive credits on repo scans, log triage, routine test fixes, and repeated validation loops — work that cheaper models could handle just fine. I also had Spark limits sitting completely unused because there was no safe, structured way to route work to them.

`codex-budget-router` changes that. It's a routing policy that keeps the root model focused on architecture, judgment, and integration, while moving broad search, routine implementation, tests, and bounded review to cheaper workers. It's saved me up to 20% of my limits by displacing expensive-model work, not by reducing total tokens.

---

## Skills

### [`codex-budget-router`](codex-budget-router/SKILL.md)

Route suitable work to cheaper bounded workers while keeping final judgment in the root session.

**What it does:**

- Keeps root focused on orchestration, architecture, acceptance criteria, integration, and final risk review
- Uses `cheap_mapper` / `cheap_researcher` (gpt-5.4-mini) for broad code search, docs lookup, and log condensation
- Uses `spark_worker` (gpt-5.3-codex-spark) first for low-risk routine work — tests, scripts, fixtures, docs cleanup, mechanical refactors
- Uses `codex_worker` (gpt-5.3-codex) for bounded non-trivial implementation after the root has decided the approach
- Uses `mid_reviewer` / `mid_debugger` (gpt-5.4) for bounded diff review and tricky debugging
- Prevents root from duplicating work already assigned to workers
- Forces multi-wave delegation after workers return, validation failures happen, or context compacts

**What it doesn't do:**

- Bypass usage limits
- Change OpenAI pricing
- Promise exact savings
- Delegate feature design or architecture to cheaper models
- Help with tiny one-file edits or highly sequential tasks

**Before / after:**

| Before | After |
|--------|-------|
| Root model reads many files to map the codebase | `cheap_mapper` finds relevant files; root only reads what it needs to decide |
| Root model fixes routine tests and lints | `spark_worker` handles mechanical fixes from a tight brief |
| Root model reviews its own diff | `mid_reviewer` checks the bounded diff; root integrates findings |
| Spark limits sit unused | Routine work routes to Spark by default when safe |

---

## How it works

The routing policy is simple:

1. **Root owns judgment.** Feature design, architecture, product behavior, and final go/no-go stay with the root model — always.
2. **Workers own bounded execution.** Each worker gets a tight scope, known files, acceptance criteria, and a validation command.
3. **Spark-first for routine work.** If a task is low-risk and mechanical, Spark gets first refusal.
4. **Multi-wave delegation.** A routed task isn't one-and-done. Workers returning, validation failures, and reviewer findings all trigger new routing checkpoints.
5. **No duplicate root/worker work.** Once a worker owns a search, review, or patch, root doesn't redo it.

The key metric is **model-tier displacement**, not total tokens. A run that uses more total tokens can still be cheaper and better if heavy work moved off the root model.

---

## Installation

Each skill is self-contained. Install only what you want.

### Quick install

```bash
git clone https://github.com/<your-org>/codex-skills.git
cd codex-skills

# Install the skill + agent profiles
cp -r codex-budget-router ~/.agents/skills/codex-budget-router
codex-budget-router/scripts/install-agent-profiles.sh
```

Or, from inside Codex:

```text
Use the skill installer to install codex-budget-router from this repo.
Then check whether all six codex-budget-router agent profiles are installed.
If any are missing, run codex-budget-router/scripts/install-agent-profiles.sh.
```

Then restart Codex.

### Agent profiles

The skill expects these worker profiles in `~/.codex/agents/`:

| Agent | Model | Purpose |
|-------|-------|---------|
| `cheap_mapper` | gpt-5.4-mini | Read-only file/symbol search |
| `cheap_researcher` | gpt-5.4-mini | Docs and log summarization |
| `spark_worker` | gpt-5.3-codex-spark | Low-risk routine implementation |
| `codex_worker` | gpt-5.3-codex | Bounded non-trivial implementation |
| `mid_reviewer` | gpt-5.4 | Bounded diff review |
| `mid_debugger` | gpt-5.4 | Tricky debugging and reproduction |

The install script copies them from `codex-budget-router/agents/` without overwriting local changes.

---

## Usage

Invoke the skill by name:

```text
Use codex-budget-router for this task.
```

**Good fits:**

- Security finding batches with many files to audit
- PR review + fix passes with separable concerns
- Large refactors where mapping, implementation, and review can run independently
- Test failure / log triage across multiple sources
- Docs and script cleanup at scale

**Poor fits:**

- One-file typo fixes
- Highly sequential tasks where every step needs root judgment
- Tasks small enough that worker overhead exceeds the savings

During a routed task, you'll see compact routing lines:

```text
Budget route: root=orchestration/integration; workers=mapper/spark/codex/reviewer; target=30%+; risk=low.
Budget gate: root_reads=1/2; workers=4/4; spark=spawned; root=integration; gate=pass.
Budget scorecard: workers=4/mapper+spark+codex+reviewer; spark=yes; waves=2; failures_routed=yes; root_patches=none; result=pass.
```

---

## Audit

Check whether the router actually displaced expensive-model work:

```bash
python3 codex-budget-router/scripts/budget_router_audit.py --limit 12
```

This reads your local Codex Desktop state and prints a per-thread verdict with model-tier displacement. Requires Python 3 and access to `~/.codex/state_5.sqlite`.

---

## Layout

```text
codex-budget-router/
  SKILL.md              — routing rules, activation, model policy
  agents/               — worker TOML profiles
  references/           — workflows, prompts, fallback detail
  scripts/              — install script, audit tool
  tests/                — audit script tests
```

Each skill lives in its own top-level folder. Supporting files stay inside that skill folder.

---

## Contributing

- Keep the public version generic — no private paths, secrets, or machine-specific config.
- Keep `SKILL.md` compact; move long-form detail into `references/`.
- New skills should follow the same folder layout.
- Agent profiles should use the models in the routing table so the skill works out of the box.

---

## License

MIT — see [LICENSE](LICENSE).
