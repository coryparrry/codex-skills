---
name: codex-packet-maintain
description: Maintain Codex packet-loop state by validating JSON records, expiring deterministic stale leases, regenerating dashboards, and reporting controller-safe next actions. Use for scheduled or manual packet-loop maintenance.
---

# Codex Packet Maintain

Use this skill for manual maintenance or as the repo-local workflow a local automation invokes.

## Required Context

Load `$codex-packet-loop-core`, then read `references/workflow-protocol.md`, `references/state-machine.md`, `references/autonomy-policy.md`, `references/evidence-contract.md`, and `references/recovery-playbook.md`.

## Workflow

1. Run `packet_loop.py validate`.
2. If validation succeeds, run `packet_loop.py maintain --expire-stale-leases`.
3. Run `packet_loop.py status --format json`.
4. Write `maintenance-report.md` when state changes.
5. Record maintenance evidence with `packet_loop.py record-evidence` when a packet state changes.
6. Report invalid records, expired leases, ready packets, blocked packets, merge-eligible packets, and next safe skill.

## Repair Boundary

Deterministic repair may expire a stale lease for a packet without a PR. Destructive, external, or security-sensitive actions require human approval.
