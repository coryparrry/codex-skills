---
name: codex-packet-worker
description: Execute exactly one leased Codex PR packet in one worktree. Use when a worker thread receives a packet assignment with allowed scope, validation route, branch, and lease.
---

# Codex Packet Worker

Use this skill inside the assigned packet worktree.

## Workflow

1. Read repo instructions.
2. Load `$codex-packet-loop-core` and read its state contract.
3. Validate the packet exists, is leased to this worker, and is `reserved`.
4. Transition the packet to `in-progress`.
5. Inspect only files needed for the packet.
6. Implement the smallest change that satisfies the packet goal.
7. Run the packet validation commands.
8. Fix only failures caused by the packet.
9. Stop after two failed fix attempts with the same root cause.
10. Record evidence under `.codex/packet-loop/evidence/<packet-id>/`.
11. Prepare or open one PR for the packet.
12. Transition to `pr-open` only after evidence and validation are recorded.
13. Report next valid skill: `$codex-packet-review`.

## Stop Conditions

Stop and mark the packet `blocked` or `needs-reslice` when:

- required changes leave `allowed_scope`
- validation requires unrelated fixes
- a reserved area is needed
- dependencies are missing
- the packet goal is ambiguous after code inspection
- security-sensitive decisions are required

Do not implement adjacent packets.
