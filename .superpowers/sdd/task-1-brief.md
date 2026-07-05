### Task 1: Create The Local Skill

**Files:**
- Create: `~/.codex/skills/Knowledge-setup/SKILL.md`

**Interfaces:**
- Consumes: the approved Repository Context Layer design.
- Produces: an invocable local skill named `Knowledge-setup`.

- [ ] **Step 1: Confirm the skill target does not already exist**

```bash
test ! -e "$HOME/.codex/skills/Knowledge-setup" || {
  printf 'Skill already exists: ~/.codex/skills/Knowledge-setup\n' >&2
  exit 1
}
```

Expected: The path does not exist. If it exists, inspect it and ask before overwriting or merging.

- [ ] **Step 2: Create the skill directory**

```bash
mkdir -p "$HOME/.codex/skills/Knowledge-setup/templates"
```

Expected: The local skill directory and template directory exist.

- [ ] **Step 3: Write `SKILL.md`**

Use `apply_patch` to create `~/.codex/skills/Knowledge-setup/SKILL.md`:

```md
---
name: Knowledge-setup
description: Use in a repo to create or refresh the tiny three-file Repository Context Layer: AGENTS.md, .repo/context.md, and .repo/graph.json.
---

# Knowledge Setup

Create or refresh a small, evidence-backed Repository Context Layer in the current repo.

Use this skill when the user asks to initialize, adopt, set up, refresh, or repair the repo context layer for a repo. This is a manual trigger, not a background automation.

## Outcome

The target repo has exactly these context-layer files:

```text
AGENTS.md
.repo/context.md
.repo/graph.json
```

`AGENTS.md` is a tiny router. `.repo/context.md` contains durable repo intent, constraints, and learned context. `.repo/graph.json` contains an evidence-backed semantic architecture graph.

## Hard Rules

- Inspect live repo evidence before writing.
- Do not create scripts, dependencies, generated indexes, databases, MCPs, vector stores, background services, or committed validation tooling.
- Modify only `AGENTS.md`, `.repo/context.md`, and `.repo/graph.json` unless the user explicitly expands scope.
- Preserve only verified repo-specific hard constraints from an old `AGENTS.md`.
- Treat source files, tests, manifests, and CI as truth when docs disagree.
- Do not delete, move, ignore, or rewrite tracked hidden/tool files.
- Do not include local absolute paths in committed files or GitHub-facing text.
- Validate before commit.
- Commit only when the user or target repo workflow expects commits; otherwise leave the three-file diff ready for review.
- Prefer a smaller accurate graph over a larger speculative graph.

## Workflow

1. Confirm the current directory is a Git repo.
2. Report the current branch and whether it appears to be the default branch. Do not create or switch branches unless explicitly required.
3. Inventory repo evidence using `git ls-files`, `find`, `grep`, and direct file reads. `rg` is allowed only as an optional speedup.
4. Read existing instruction files, README files, manifests, CI, docs, generated surfaces, mirrored surfaces, and high-signal source roots.
5. Create `.repo/` if needed. Do not touch unrelated files inside `.repo/`.
6. Replace or create `AGENTS.md` as the tiny router.
7. Create or update `.repo/context.md` from evidence.
8. Create or update `.repo/graph.json` from evidence.
9. Validate Markdown headings, JSON syntax, semantic graph references, evidence paths, generated/mirrored markings, and local-path leakage.
10. Show the final three-file diff.
11. Commit only when expected by the user or repo workflow.

## AGENTS.md Content

Use this content for `AGENTS.md`:

```md
# AGENTS.md

This repo uses a tiny Repository Context Layer. Treat it as a routing aid, not source truth.

Before planning or editing:

1. Read `.repo/context.md`.
2. Read `.repo/graph.json`.
3. Choose the relevant route or node from `.repo/graph.json`.
4. Inspect graph-listed files before broad search.
5. Verify live source files before relying on graph or context.

Rules:

- Treat `.repo/context.md` as repo intent, constraints, and durable learned context.
- Treat `.repo/graph.json` as an evidence-backed navigation graph, not source truth.
- Source files and tests are authoritative when graph/context conflict with implementation.
- Update `.repo/context.md` when the work teaches a durable, non-obvious lesson.
- Update `.repo/graph.json` in the same change set when work changes commands, routes, tests, contracts, entrypoints, ownership, generated files, mirrored files, deprecated paths, do-not-edit areas, or important gotchas.
- Do not update the context layer for ordinary edits that do not change durable repo knowledge.
- Do not add scripts, dependencies, databases, MCPs, vector stores, background services, or generated indexes for this context layer unless explicitly requested.
```

## Context Contract

`.repo/context.md` must use this exact structure:

```md
# Repository Context

## Intent

## Constraints

## Evolved Context
```

`Intent` is one short paragraph from live evidence. `Constraints` contains only verified repo-specific hard rules. `Evolved Context` is dated durable memory, not a task log.

## Graph Contract

`.repo/graph.json` must use this top-level shape:

```json
{
  "schema_version": "0.1",
  "repo": {},
  "agent_contract": {},
  "commands": {},
  "routes": {},
  "nodes": {},
  "edges": [],
  "staleness_checks": []
}
```

Command entries use:

```json
{
  "command": "exact command",
  "cwd": ".",
  "evidence": ["repo-relative/path"],
  "notes": "Optional short note."
}
```

Route entries use:

```json
{
  "start_nodes": ["area.core"],
  "inspect_first": ["src/", "tests/"],
  "notes": ["Short practical routing note."]
}
```

Node IDs are stable, lowercase, dot-separated semantic IDs such as `area.core`, `boundary.public_api`, `workflow.ci`, `test.unit`, `generated.sdk`, `mirror.plugin`, or `deprecated.legacy_runner`. Do not use raw file paths as node IDs.

Allowed edge types:

- `depends_on`
- `implements`
- `calls`
- `called_by`
- `tested_by`
- `documents`
- `generates`
- `mirrors`
- `replaces`
- `do_not_edit`

## Validation Commands

Use temporary validation commands only. Do not commit them as scripts.

```bash
test -s AGENTS.md
test -s .repo/context.md
test -s .repo/graph.json
grep -nE '^## (Intent|Constraints|Evolved Context)$' .repo/context.md
python3 -m json.tool .repo/graph.json >/dev/null
python3 - <<'PY'
from pathlib import Path

home = str(Path.home())
leaks = []

for name in ("AGENTS.md", ".repo/context.md", ".repo/graph.json"):
    text = Path(name).read_text(errors="ignore")
    if home in text:
        leaks.append(name)

if leaks:
    for name in leaks:
        print(f"Home path leaked into context layer: {name}")
    raise SystemExit(1)
PY
```

Also validate graph semantics with temporary Python:

- top-level keys exist
- route `start_nodes` reference real node IDs
- route `inspect_first` paths exist
- node `depends_on`, `tested_by`, and `documented_by` references exist
- command entries have `command`, `cwd`, and `evidence`
- command `cwd` and `evidence` paths exist
- edge `from` and `to` nodes exist
- edge `type` is allowed
- edge evidence paths exist

## Closeout

Report:

- routes created
- unresolved uncertainties
- files changed
- validation run
- whether the three-file diff was committed or left ready for review
```

Expected: The skill file exists, has valid frontmatter, and contains the full repo adoption workflow without requiring extra tooling.
