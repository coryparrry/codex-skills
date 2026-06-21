---
name: codex-packet-maintain
description: Maintain Codex packet-loop state by validating JSON records, expiring deterministic stale leases, regenerating dashboards, and reporting controller-safe next actions. Use for scheduled or manual packet-loop maintenance.
---

# Codex Packet Maintain

Use this skill for manual maintenance or as the repo-local workflow a local automation invokes.

## Workflow

1. Read repo instructions and packet-loop state.
2. Load `$codex-packet-loop-core` and read its state contract.
3. Run:

```bash
python3 <core-skill>/scripts/packet_loop.py --repo <repo> maintain --expire-stale-leases
```

4. Report:
   - expired leases
   - invalid records
   - ready packets
   - blocked packets
   - merge-eligible packets
   - next safe skill to run

## Repair Boundary

Deterministic repair may expire a stale lease for a packet without a PR. Destructive, external, or security-sensitive actions require human approval.
