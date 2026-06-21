---
name: codex-packet-slice
description: Convert an approved plan into small Codex PR packet records. Use when slicing broad implementation plans into packet JSON with dependencies, allowed scope, validation commands, risk, and overlap notes.
---

# Codex Packet Slice

Use this skill after packet-loop state is initialized and a plan has been approved for implementation.

## Workflow

1. Read the plan and repo instructions.
2. Load `$codex-packet-loop-core` and read its state contract.
3. Run packet-loop validation before editing state.
4. Propose packet boundaries before writing records when the source plan is broad or ambiguous.
5. Create one packet per reviewable PR unit with:
   - one goal
   - allowed scope
   - expected touched areas
   - avoid scope
   - dependencies
   - risk
   - parallel safety
   - validation commands
6. Add packets with `packet_loop.py add-packet`.
7. Transition packets from `candidate` to `ready` only when dependencies and validation are clear.
8. Regenerate dashboard through the CLI and report next valid skill: `$codex-packet-dispatch`.

## Packet Quality Rules

- Prefer packets that can be reviewed without reading the whole plan.
- Mark generated files, lockfiles, central state, public API, security, and broad UI flows as higher risk.
- Keep dependent packets serial unless the dependency is already merged.
- Do not hide ambiguous owner decisions inside packet text.
