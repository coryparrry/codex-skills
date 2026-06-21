---
name: codex-packet-loop
description: Controller and router for the experimental Codex PR packet loop. Use when asked to continue, advance, inspect, maintain, or run packet-loop automation without a specific stage skill.
---

# Codex Packet Loop

Use this skill as the controller for the packet-loop suite.

## Required Context

1. Read repo and nested `AGENTS.md` instructions for the target repo.
2. Load `$codex-packet-loop-core`.
3. Read `references/workflow-protocol.md`, `references/state-machine.md`, `references/autonomy-policy.md`, and `references/recovery-playbook.md`.
4. Read `references/superpowers-plan-adapter.md` before slicing a Superpowers plan or dispatching a packet with a child plan.
5. Read `references/overlap-policy.md` before dispatch or integration decisions.
6. Read `references/handoff-contracts.md` and `references/evidence-contract.md` before creating or judging worker artifacts.
7. For child-plan execution, preserve the Superpowers route to `superpowers:subagent-driven-development` or `superpowers:executing-plans`.

## Controller Loop

1. Resolve the repo root.
2. If `.codex/packet-loop/manifest.json` is missing, route to `$codex-packet-init`.
3. Run `packet_loop.py --repo <repo> validate`.
4. Run `packet_loop.py --repo <repo> maintain --expire-stale-leases` when validation succeeds.
5. Run `packet_loop.py --repo <repo> status --format json`.
6. Inspect active leases, ready packets, PR-open packets, reviewing packets, blocked packets, needs-reslice packets, and merge-eligible packets.
7. Choose exactly one next stage:
   - invalid deterministic state -> `$codex-packet-maintain`
   - approved Superpowers plan needs child plans -> `$codex-packet-slice`
   - PR-open or reviewing packets -> `$codex-packet-review`
   - dependency-ready packets fit monitoring and resource-lane capacity -> `$codex-packet-dispatch`
   - merge-eligible packets -> `$codex-packet-integrate`
   - blocked or needs-reslice packets -> `$codex-packet-slice` or user decision
   - no safe action -> report state and stop

## Active Worker Supervision

When active leases exist, supervise before dispatching more work:

1. Poll each active worker thread summary when thread tooling is available.
2. Inspect each leased worktree with `git status --short --branch`.
3. Inspect file names and diffstat before reading full diffs.
4. Send steering only to workers with scope drift, detached-HEAD commit risk, unstable validation loops, missing evidence, privacy leaks, or ambiguous blockers.
5. Leave non-drifting workers alone.
6. Keep the primary checkout clean until packet outputs pass review and are intentionally integrated.

## Autonomous Actions

- Validate packet state.
- Expire deterministic stale leases.
- Regenerate dashboards through the core CLI.
- Reserve ready packets when dependency, monitoring capacity, resource-lane constraints, and overlap checks pass.
- Create worker handoff prompts.
- Record status reports and evidence paths through the core CLI.
- Recommend merge order.

## Human Stops

Stop before merge, force-push, branch deletion, PR closing, default-branch writes, destructive Git operations, discarding useful work, security-sensitive tradeoffs, or external submissions not already authorized.

## Output

End with a compact state report:

- validation status
- maintenance action taken
- active packet count
- selected next skill
- reason for the route
- human gate or blocker when no autonomous action remains
