---
name: codex-packet-loop-core
description: Shared state contract and deterministic CLI for Codex PR packet loop skills. Use when validating packet-loop JSON state, lifecycle transitions, leases, generated dashboards, or packet-loop helper behavior.
---

# Codex Packet Loop Core

Use this skill as the shared contract for the Codex PR packet loop suite.

## Required Context

Read `references/state-contract.md` before changing packet-loop state.

## Deterministic CLI

Use `scripts/packet_loop.py` for state operations instead of editing JSON by hand when the operation is supported.

Common commands:

```bash
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> init --name <repo-name>
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> validate
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> maintain --expire-stale-leases
```

## Rules

- Treat JSON under `.codex/packet-loop/` as authoritative.
- Treat `docs/codex/packet-loop.md` as generated output.
- Log deterministic repairs through the CLI so `events.jsonl` stays audit-ready.
- Refuse human-gated transitions unless the human explicitly approved them.
