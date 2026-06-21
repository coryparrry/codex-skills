---
name: codex-packet-init
description: Initialize Codex PR packet loop state in a repository. Use when a repo opts into packet-loop orchestration or needs `.codex/packet-loop/` manifest, packet directory, event log, and generated dashboard setup.
---

# Codex Packet Init

Use this skill to opt a repo into the PR packet loop.

## Required Context

Load `$codex-packet-loop-core`, then read `references/workflow-protocol.md`, `references/state-machine.md`, and `references/autonomy-policy.md`.

## Preflight

1. Resolve the repo root.
2. Read repo instructions.
3. Refuse to overwrite `.codex/packet-loop/manifest.json` unless the user explicitly approves reinitialization.

## Autonomous Actions

Run:

```bash
python3 <core-skill>/scripts/packet_loop.py --repo <repo> init --name <repo-name> --target-branch <branch>
python3 <core-skill>/scripts/packet_loop.py --repo <repo> validate
```

## Output

Report created state files and route to `$codex-packet-slice` when an approved plan exists, otherwise route to `$codex-packet-loop`.
