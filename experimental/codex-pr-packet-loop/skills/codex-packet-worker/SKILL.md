---
name: codex-packet-worker
description: Execute exactly one leased Codex PR packet in one worktree. Use when a worker thread receives a packet assignment with allowed scope, validation route, branch, and lease.
---

# Codex Packet Worker

Use this skill inside the assigned packet worktree.

## Required Context

Load `$codex-packet-loop-core`, then read `references/workflow-protocol.md`, `references/state-machine.md`, `references/handoff-contracts.md`, `references/superpowers-plan-adapter.md`, `references/evidence-contract.md`, `references/overlap-policy.md`, `references/recovery-playbook.md`, and `references/autonomy-policy.md`.

## Workflow

1. Confirm the current worktree and branch match the packet lease.
2. Read the packet child plan path from packet JSON.
3. Invoke the Superpowers execution skill required by the child plan: `superpowers:subagent-driven-development` or `superpowers:executing-plans`.
4. Validate state and transition `reserved` to `in-progress` with actor, reason, and evidence path when available.
5. Follow the child plan exactly while respecting packet allowed scope.
6. Run each packet validation command.
7. Fix only packet-caused failures.
8. Stop after two failed fix attempts with the same root cause.
9. Write worker evidence under `.codex/packet-loop/evidence/<packet-id>/`.
10. Record evidence with `packet_loop.py record-evidence`.
11. Prepare one PR, or open/update one PR only when authorized.
12. Record PR metadata with `packet_loop.py set-pr` when PR metadata exists.
13. Transition to `pr-open` only after evidence and validation are recorded.

## Stop Conditions

Stop and mark the packet `blocked` or `needs-reslice` when:

- required changes leave `allowed_scope`
- validation requires unrelated fixes
- a reserved area is needed
- dependencies are missing
- the packet goal is ambiguous after code inspection
- security-sensitive decisions are required

Do not implement adjacent packets.

## Output

Write `worker-report.md`, record validation and diff evidence, and report next valid skill `$codex-packet-review`.
