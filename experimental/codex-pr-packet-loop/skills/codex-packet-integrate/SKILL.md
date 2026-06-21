---
name: codex-packet-integrate
description: Sequence merge-eligible Codex packet PRs, detect overlap, recommend merge order, and update packet-loop state after approved merges. Use when one or more packet PRs are merge-eligible.
---

# Codex Packet Integrate

Use this skill to prepare safe merge sequencing. Do not merge unless the human explicitly approves the merge action.

## Required Context

Load `$codex-packet-loop-core`, then read `references/workflow-protocol.md`, `references/state-machine.md`, `references/handoff-contracts.md`, `references/evidence-contract.md`, `references/overlap-policy.md`, and `references/autonomy-policy.md`.

## Workflow

1. Run `packet_loop.py validate`.
2. Read merge-eligible packet records, PR metadata, changed files, and review evidence.
3. Build `merge-matrix.md` with stale status, conflict status, overlap categories, and serial order.
4. Recommend one merge order.
5. Stop before merge or destructive/external action.
6. After the user confirms a merge happened, transition only that packet to `merged` with `--human-approved`.
7. Re-run validation and status summary after each approved state update.

## Default Merge Policy

Parallel implementation is allowed. Parallel merging is not allowed in this MVP.

## Output

Write `merge-matrix.md` and `integration-report.md`, then route back to `$codex-packet-loop`. After any human-approved merge state update, route to `$codex-packet-maintain` for stale lease, dependency, and readiness cleanup.
