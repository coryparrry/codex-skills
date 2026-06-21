---
name: codex-packet-slice
description: Convert an approved plan into small Codex PR packet records. Use when slicing broad implementation plans into packet JSON with dependencies, allowed scope, validation commands, risk, and overlap notes.
---

# Codex Packet Slice

Use this skill after packet-loop state is initialized and a plan has been approved for implementation.

## Required Context

Load `$codex-packet-loop-core`, then read `references/workflow-protocol.md`, `references/state-machine.md`, `references/handoff-contracts.md`, `references/superpowers-plan-adapter.md`, `references/overlap-policy.md`, and `references/autonomy-policy.md`.

## Workflow

1. Validate existing packet-loop state.
2. Read the approved plan and repo instructions.
3. If the input is not an approved Superpowers implementation plan, route to `superpowers:writing-plans` before slicing.
4. Propose packet boundaries before writing records when the plan is broad or ambiguous.
5. Use `superpowers:writing-plans` output shape to create one Superpowers-compatible child plan per packet under `docs/superpowers/plans/packet-loop/`.
6. Verify each child plan has the required Superpowers header, checkbox tasks, source plan references, packet id, exact file paths, exact validation commands, dependencies, resource lanes, and no placeholders.
7. For each packet, define goal, allowed scope, avoid scope, expected touched areas, reserved areas, resource lanes, dependencies, risk, parallel safety, validation commands, overlap notes, human review requirement, parent plan path, child plan path, source plan refs, and plan format status.
8. Add each packet with `packet_loop.py add-packet`.
9. Produce or update a human-readable packet queue/build-order artifact that includes dependency gates, dispatch waves, serialized resource lanes, human-review-first packets, and packets not suitable for blind agents.
10. Transition a packet to `ready` only when dependencies and validation routes are clear and `plan_format_status` is `valid`.
11. Report next valid skill `$codex-packet-dispatch` or `$codex-packet-loop`.

## Refusal

Refuse to hide product decisions, security tradeoffs, or broad ambiguous ownership inside packet text.
