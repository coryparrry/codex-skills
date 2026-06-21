---
name: codex-packet-loop-core
description: Shared state contract and deterministic CLI for Codex PR packet loop skills. Use when validating packet-loop JSON state, lifecycle transitions, leases, generated dashboards, or packet-loop helper behavior.
---

# Codex Packet Loop Core

Use this skill as the shared contract for the Codex PR packet loop suite.

## Required Context

Load only the references needed for the active stage:

- `references/workflow-protocol.md` for routing and authority order.
- `references/state-machine.md` before transitions.
- `references/autonomy-policy.md` before acting without user confirmation.
- `references/handoff-contracts.md` before creating worker, review, integration, or maintenance artifacts.
- `references/superpowers-plan-adapter.md` before slicing Superpowers plans or dispatching child plans.
- `references/evidence-contract.md` before recording or reviewing evidence.
- `references/overlap-policy.md` before dispatch, review, or integration.
- `references/recovery-playbook.md` when work is blocked, stale, failed, or mis-sliced.
- `references/behavioral-evals.md` when validating the skill suite.

## Deterministic CLI

Use `scripts/packet_loop.py` for state operations instead of editing JSON by hand when the operation is supported.

Common commands:

```bash
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> init --name <repo-name>
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> validate
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> status --format json
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> maintain --expire-stale-leases
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> record-evidence --packet <packet-id> --kind worker-report --path <path>
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> set-pr --packet <packet-id> --url <url> --number <number> --state open --head <branch> --base <branch>
```

## Rules

- Treat JSON under `.codex/packet-loop/` as authoritative.
- Treat `docs/codex/packet-loop.md` as generated output.
- Log deterministic repairs through the CLI so `events.jsonl` stays audit-ready.
- Refuse human-gated transitions unless the human explicitly approved them.
- Treat worker summaries as claims until review verifies files, diffs, checks, PR state, and evidence.
