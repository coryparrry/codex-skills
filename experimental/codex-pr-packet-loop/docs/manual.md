# Codex PR Packet Loop

The Codex PR packet loop turns a large approved plan into small PR packets that can be assigned to isolated Codex worktree workers.

## First Run

1. Initialize state:

```text
Use $codex-packet-init to initialize packet-loop state in this repo.
```

2. Slice the approved plan:

```text
Use $codex-packet-slice to convert this approved plan into packet records.
```

3. Dispatch one packet:

```text
Use $codex-packet-dispatch to lease the next safe ready packet.
```

4. Run the worker in the assigned worktree:

```text
Use $codex-packet-worker to execute packet P001 only.
```

5. Review the packet PR:

```text
Use $codex-packet-review to review the packet PR against its packet record.
```

6. Prepare merge sequencing:

```text
Use $codex-packet-integrate to recommend a safe merge order.
```

7. Maintain state:

```text
Use $codex-packet-maintain to validate packet-loop state and report next safe actions.
```

## Human Gates

The loop stops for human approval before merge, branch deletion, PR closing, force-push, default-branch writes, or security-sensitive changes.

## State Files

Structured state lives under `.codex/packet-loop/`. The generated dashboard lives at `docs/codex/packet-loop.md`.
