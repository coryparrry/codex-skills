---
name: codex-packet-init
description: Initialize Codex PR packet loop state in a repository. Use when a repo opts into packet-loop orchestration or needs `.codex/packet-loop/` manifest, packet directory, event log, and generated dashboard setup.
---

# Codex Packet Init

Use this skill to opt a repo into the PR packet loop.

## Workflow

1. Read repo instructions and confirm the target repo root.
2. Load `$codex-packet-loop-core` and read its state contract.
3. Refuse to overwrite existing `.codex/packet-loop/manifest.json` unless the user explicitly approves reinitialization.
4. Run:

```bash
python3 <core-skill>/scripts/packet_loop.py --repo <repo> init --name <repo-name> --target-branch <branch>
```

5. Run:

```bash
python3 <core-skill>/scripts/packet_loop.py --repo <repo> validate
```

6. Report the created files and next valid skill: `$codex-packet-slice`.
