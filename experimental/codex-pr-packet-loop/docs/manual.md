# Codex PR Packet Loop

The Codex PR packet loop turns a large approved plan into small PR packets that can be assigned to isolated Codex worktree workers.

## First Run

For normal operation, start with the controller:

```text
Use $codex-packet-loop to inspect packet-loop state and route to the next valid stage.
```

When bootstrapping a repo manually:

1. Use `$codex-packet-init` to initialize state.
2. Use `$codex-packet-slice` to convert an approved plan into packet records.
3. Use `$codex-packet-loop` to advance the loop from that point.

The controller may route to `$codex-packet-dispatch`, `$codex-packet-worker`, `$codex-packet-review`, `$codex-packet-integrate`, `$codex-packet-maintain`, or back to `$codex-packet-slice` depending on packet state.

When the source is a Superpowers implementation plan, each packet worker receives a generated child Superpowers plan. The worker executes that plan with `superpowers:subagent-driven-development` or `superpowers:executing-plans`, so normal TDD, review, verification, and finishing-branch behavior still apply inside the worktree.

## Human Gates

The loop stops for human approval before merge, branch deletion, PR closing, force-push, default-branch writes, or security-sensitive changes.

## State Files

Structured state lives under `.codex/packet-loop/`. The generated dashboard lives at `docs/codex/packet-loop.md`.

## Protocol Summary

- Packet JSON is authoritative.
- The generated dashboard is for humans and must not be hand-edited.
- Worker claims are verified by review before merge eligibility.
- Merge sequencing is serial in the MVP.
- Active worker supervision checks thread status, worktree dirt, and diff shape before integration.
