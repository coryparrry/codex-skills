# Experimental Skills

This folder is for local skill experiments that are not part of the shipped
`skills/` bundle or plugin mirror.

`multi-phase-orchestrator` is intentionally generated as a local symlink instead
of being committed. The source skill lives in the local Codex skills directory,
and the symlink target is machine-specific.

Create or refresh the local link with:

```bash
bash scripts/link_experimental_skill.sh
```

Pass an explicit source directory when needed:

```bash
bash scripts/link_experimental_skill.sh /path/to/multi-phase-orchestrator
```
