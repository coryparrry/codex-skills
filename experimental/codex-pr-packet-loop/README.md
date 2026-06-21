# Codex PR Packet Loop Pack

This pack contains a flexible plan for building a Codex workflow where:

```text
Plan → sliced PR packets → orchestrator → delegate worktrees → validation/fix loop → PRs → review → safe merge orchestration → state updates
```

## Files

- `CODEX_PR_PACKET_LOOP_PLAN.md` — Main operating plan and workflow design.
- `MERGE_OVERLAP_STRATEGY.md` — Dedicated strategy for the riskiest part: overlapping work and safe merges.
- `CODEX_PR_PACKET_LOOP_TEMPLATES.md` — Seed templates and paste-ready prompts for AGENTS.md, PR_QUEUE.md, LOOP_STATE.md, orchestrator, delegate workers, review, refresh, and queue maintenance.

## Recommended use

Start by giving Codex the main plan and asking it to brainstorm the smallest viable implementation for your repo.

Suggested prompt:

```text
Read CODEX_PR_PACKET_LOOP_PLAN.md, MERGE_OVERLAP_STRATEGY.md, and CODEX_PR_PACKET_LOOP_TEMPLATES.md.

I want to adapt this workflow to this repo without making it too rigid.

First, inspect the repo structure and current agent instructions.
Then propose the minimum set of files and rules needed to run a 3-packet trial.
Do not implement yet.
```

## Experimental Skill Suite

The first packet-loop harness lives entirely under this `experimental/codex-pr-packet-loop/` directory.

Do not mirror these skills into `skills/`, `plugins/codex-skills/skills/`, or package metadata until a separate promotion plan is approved.

### Skills

- `codex-packet-loop` is the controller/router. Start here for "continue", "advance", "inspect", or "run packet automation" requests.
- `codex-packet-loop-core` provides shared protocol references and deterministic CLI helpers.
- `codex-packet-init` initializes packet-loop state in a target repo.
- `codex-packet-slice` converts approved plans into scoped PR packet records.
- `codex-packet-dispatch` reserves ready packets and prepares worker prompts.
- `codex-packet-worker` executes one leased packet in one worktree.
- `codex-packet-review` reviews packet PRs against scope, validation, evidence, and overlap risk.
- `codex-packet-integrate` recommends merge order and stops before human-gated actions.
- `codex-packet-maintain` validates, repairs deterministic lease drift, and regenerates packet dashboards.

### Controller-First Flow

Use `$codex-packet-loop` for normal operation. The controller validates state, runs safe maintenance, inspects status, supervises active worker lanes, and routes to the next valid stage skill. Invoke a stage skill directly only when the stage is already known.

For Superpowers-driven work, give the controller an approved `docs/superpowers/plans/*.md` implementation plan. The slicer creates one Superpowers-compatible child plan per packet under `docs/superpowers/plans/packet-loop/`, verifies the child plan format, and dispatches workers to execute those plans with `superpowers:subagent-driven-development` or `superpowers:executing-plans`.

### Validation

Run the experimental validation command from the repo root:

```bash
python3 experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
```
