---
name: codex-packet-dispatch
description: Reserve a ready Codex PR packet, create or prepare a worktree worker assignment, and record the packet lease. Use when dispatching one ready packet to one Codex worker thread.
---

# Codex Packet Dispatch

Use this skill to assign one ready packet to one worker.

## Workflow

1. Read repo instructions, manifest, ready packets, and active leases.
2. Load `$codex-packet-loop-core` and read its state contract.
3. Run packet-loop validation.
4. Choose one ready packet whose dependencies are satisfied and whose expected areas do not collide with live leases.
5. Create a branch name in this form:

```text
codex/<packet-id-lower>-<short-title>
```

6. Create or request a fresh worktree thread for the worker.
7. Record the lease:

```bash
python3 <core-skill>/scripts/packet_loop.py --repo <repo> lease --packet <packet-id> --owner-thread <thread-id> --branch <branch> --worktree <path> --ttl-hours 24
```

8. Produce a worker prompt that explicitly invokes `$codex-packet-worker` and includes the packet id, branch, worktree, allowed scope, validation command, and stop conditions.
9. Report next valid skill: `$codex-packet-worker` in the worker thread.

## Refusal Conditions

- Refuse dispatch when the packet is not `ready`.
- Refuse dispatch when dependencies are unmerged.
- Refuse dispatch when expected areas collide with a live lease.
- Refuse dispatch when no fresh worktree/thread route is available.
