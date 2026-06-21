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
