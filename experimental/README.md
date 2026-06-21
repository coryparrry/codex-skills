# Experimental Skills

This folder is for local skill experiments that are committed to the repo but
are not part of the shipped `skills/` bundle or plugin mirror.

`multi-phase-orchestrator` lives in this repository so its source can be
reviewed and versioned. Local Codex discovery can use a symlink from the
personal skills directory back to this repo copy.

Create or refresh the personal skills link with:

```bash
bash scripts/link_experimental_skill.sh
```

If an older personal directory already exists and the repo copy is now the
source of truth, replace it with:

```bash
bash scripts/link_experimental_skill.sh --replace-existing
```

Pass an explicit target path when needed:

```bash
bash scripts/link_experimental_skill.sh /path/to/personal/skills/multi-phase-orchestrator
```
