---
name: codex-packet-dispatch
description: Reserve a ready Codex PR packet, create or prepare a worktree worker assignment, and record the packet lease. Use when dispatching one ready packet to one Codex worker thread.
---

# Codex Packet Dispatch

Use this skill to assign one ready packet to one worker.

## Required Context

Load `$codex-packet-loop-core`, then read `references/workflow-protocol.md`, `references/state-machine.md`, `references/handoff-contracts.md`, `references/superpowers-plan-adapter.md`, `references/overlap-policy.md`, and `references/autonomy-policy.md`.

## Workflow

1. Run `packet_loop.py validate`.
2. Run `packet_loop.py status --format json`.
3. Select one `ready` packet whose dependencies are satisfied, child plan exists and is valid, controller monitoring capacity is available, required serialized resource lanes can be queued, and `reserved_areas` do not collide with live leases.
4. Create a branch name `codex/<packet-id-lower>-<short-title>`.
5. Create or request a fresh worktree/thread route.
6. Lease the packet with `packet_loop.py lease`.
7. Produce a worker handoff that invokes `$codex-packet-worker`.

## Handoff

The handoff must include packet id, child plan path, branch, worktree, owner thread, allowed scope, avoid scope, expected touched areas, reserved areas, resource lanes, validation commands, evidence directory, stop conditions, commit policy, PR policy, and next skill.

## Refusal Conditions

- Refuse dispatch when the packet is not `ready`.
- Refuse dispatch when dependencies are unsatisfied.
- Refuse dispatch when required child plan metadata is missing or invalid.
- Refuse dispatch when `reserved_areas` collide with a live lease.
- Refuse dispatch when no fresh worktree/thread route is available.
