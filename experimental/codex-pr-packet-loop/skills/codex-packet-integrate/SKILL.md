---
name: codex-packet-integrate
description: Sequence merge-eligible Codex packet PRs, detect overlap, recommend merge order, and update packet-loop state after approved merges. Use when one or more packet PRs are merge-eligible.
---

# Codex Packet Integrate

Use this skill to prepare safe merge sequencing. Do not merge unless the human explicitly approves the merge action.

## Workflow

1. Read repo instructions, manifest, packet records, open PRs, changed files, and validation evidence.
2. Load `$codex-packet-loop-core` and read its state contract.
3. Run packet-loop validation.
4. Build a merge matrix with file, area, interface, behavior, test, generated-file, dependency, and documentation overlap.
5. Recommend a serial merge order.
6. Identify packets that need refresh before merge.
7. Stop before merge, branch deletion, PR closing, force-push, default-branch write, or security-sensitive action.
8. After an approved merge has happened, transition only that packet to `merged` with `--human-approved`, regenerate dashboard, and re-check remaining packets.

## Default Merge Policy

Parallel implementation is allowed. Parallel merging is not allowed in this MVP.
