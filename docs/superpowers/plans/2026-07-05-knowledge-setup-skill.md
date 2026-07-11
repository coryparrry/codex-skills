# Knowledge Setup Skill Implementation Plan

> For agentic workers: Execute this plan sequentially. Do not add generated indexes, background services, repo-specific tooling, or new dependencies. If your environment provides a planning helper, it may be used only to follow this plan without expanding scope.

**Goal:** Create a reusable local Codex skill and starter stubs that initialize the three-file Repository Context Layer in any target repo.

**Architecture:** The local skill `Knowledge-setup` lives under the user's local Codex skills directory and contains the approved adoption workflow. Starter stubs provide the three files for new repo templates; the skill replaces or fills them from live repo evidence when invoked in a real repo.

**Tech Stack:** Committed/created artifacts are Markdown and JSON only. Temporary checks may use shell, Git, `find`, `grep`, and standard-library Python. If `rg` is available, agents may use it as a faster local convenience, but this plan must not depend on it.

## Global Constraints

- Build a local Codex skill, not a background automation.
- Use skill name `Knowledge-setup`.
- Do not add scripts, dependencies, generated indexes, databases, MCPs, vector stores, background services, or committed validation tooling.
- The skill must create or update exactly `AGENTS.md`, `.repo/context.md`, and `.repo/graph.json` in a target repo during adoption.
- The skill must inspect live repo evidence before writing.
- The skill must preserve only verified repo-specific hard constraints from an old `AGENTS.md`.
- The skill must treat source files, tests, manifests, and CI as live truth when docs disagree.
- The skill must not delete, move, ignore, or rewrite tracked hidden/tool files.
- The skill must not include local absolute paths in target repo files or GitHub-facing text.
- The skill must validate before commit.
- The skill must commit only when the user or target repo workflow expects commits; otherwise it leaves the three-file diff ready for review.

---

## File Structure

- Create: `~/.codex/skills/Knowledge-setup/SKILL.md`
  - Responsibility: local Codex skill entrypoint and full adoption workflow.
- Create: `~/.codex/skills/Knowledge-setup/templates/AGENTS.md`
  - Responsibility: starter tiny router stub for repo templates.
- Create: `~/.codex/skills/Knowledge-setup/templates/context.md`
  - Responsibility: starter `.repo/context.md` stub.
- Create: `~/.codex/skills/Knowledge-setup/templates/graph.json`
  - Responsibility: starter `.repo/graph.json` stub with the shared top-level schema.

No target repo is modified while creating the skill. The skill modifies a target repo only when later invoked from that repo.

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

Write `SKILL.md` to `"$HOME/.codex/skills/Knowledge-setup/SKILL.md"` after resolving `$HOME`. Do not pass a literal `~/.codex/...` path to `apply_patch`, because patch tools do not expand shell tildes.

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

### Task 2: Add Starter Stubs For New Repo Templates

**Files:**
- Create: `~/.codex/skills/Knowledge-setup/templates/AGENTS.md`
- Create: `~/.codex/skills/Knowledge-setup/templates/context.md`
- Create: `~/.codex/skills/Knowledge-setup/templates/graph.json`

**Interfaces:**
- Consumes: the skill contract from Task 1.
- Produces: copyable stubs for new repo templates.

- [ ] **Step 1: Write the `AGENTS.md` stub**

Write `AGENTS.md` to `"$HOME/.codex/skills/Knowledge-setup/templates/AGENTS.md"` after resolving `$HOME`, using the same tiny router content from the skill's `AGENTS.md Content` section.

Expected: The stub is usable as-is in a new repo and contains no repo-specific claims.

- [ ] **Step 2: Write the `context.md` stub**

Write `context.md` to `"$HOME/.codex/skills/Knowledge-setup/templates/context.md"` after resolving `$HOME`:

```md
# Repository Context

## Intent

This repo has not been set up yet. Run `$Knowledge-setup` from the repo root after the first real project files exist.

## Constraints

- Keep this context layer small and evidence-backed.

## Evolved Context

- Initial stub. Replace this entry when `$Knowledge-setup` adopts the repo from live evidence.
```

Expected: The stub is intentionally thin and makes clear that adoption still needs live evidence.

- [ ] **Step 3: Write the `graph.json` stub**

Write `graph.json` to `"$HOME/.codex/skills/Knowledge-setup/templates/graph.json"` after resolving `$HOME`:

```json
{
  "schema_version": "0.1",
  "repo": {
    "name": "",
    "kind": "",
    "description": "",
    "primary_languages": [],
    "package_managers": [],
    "last_reviewed": ""
  },
  "agent_contract": {
    "purpose": "Fast deterministic navigation for coding agents.",
    "load_order": [".repo/context.md", ".repo/graph.json"],
    "planning_rule": "Choose a route or node before broad repository search.",
    "read_rule": "Read graph-listed files first, then inspect adjacent implementation files as needed.",
    "update_rule": "Update this graph in the same change set when structure, commands, tests, contracts, ownership, entrypoints, generated files, mirrored files, deprecated paths, do-not-edit areas, or important gotchas change.",
    "no_go": [
      "Do not add dependencies for this context layer.",
      "Do not add MCP, database, vector search, background indexers, generated graph tooling, or background services unless explicitly requested.",
      "Do not treat this graph as a substitute for verifying source files."
    ]
  },
  "commands": {},
  "routes": {},
  "nodes": {},
  "edges": [],
  "staleness_checks": [
    "Do command entries match current package, build, or CI files?",
    "Do node owns paths exist or explicitly state why they are deprecated or missing?",
    "Do public API and data model nodes match current exported contracts?",
    "Do tests listed under tested_by exist?",
    "Are generated, mirrored, deprecated, and do-not-edit paths clearly marked?"
  ]
}
```

Expected: The stub parses as JSON and contains no invented repo facts.

### Task 3: Verify Skill Installation And Template Validity

**Files:**
- Check: `~/.codex/skills/Knowledge-setup/SKILL.md`
- Check: `~/.codex/skills/Knowledge-setup/templates/AGENTS.md`
- Check: `~/.codex/skills/Knowledge-setup/templates/context.md`
- Check: `~/.codex/skills/Knowledge-setup/templates/graph.json`

**Interfaces:**
- Consumes: skill and templates from Tasks 1 and 2.
- Produces: a locally installed skill ready to invoke.

- [ ] **Step 1: Check files exist**

```bash
test -s "$HOME/.codex/skills/Knowledge-setup/SKILL.md"
test -s "$HOME/.codex/skills/Knowledge-setup/templates/AGENTS.md"
test -s "$HOME/.codex/skills/Knowledge-setup/templates/context.md"
test -s "$HOME/.codex/skills/Knowledge-setup/templates/graph.json"
```

Expected: All four files exist and are non-empty.

- [ ] **Step 2: Check skill frontmatter**

```bash
sed -n '1,12p' "$HOME/.codex/skills/Knowledge-setup/SKILL.md"
```

Expected: The first lines include `name: Knowledge-setup` and a concise `description`.

- [ ] **Step 3: Check template JSON**

```bash
python3 -m json.tool "$HOME/.codex/skills/Knowledge-setup/templates/graph.json" >/dev/null
```

Expected: The graph template parses as JSON.

- [ ] **Step 4: Check no actual home path leaked into skill content**

```bash
python3 - <<'PY'
from pathlib import Path

skill_dir = Path.home() / ".codex" / "skills" / "Knowledge-setup"
home = str(Path.home())
leaks = []

for path in skill_dir.rglob("*"):
    if path.is_file():
        text = path.read_text(errors="ignore")
        if home in text:
            leaks.append(path)

if leaks:
    for path in leaks:
        print(f"Home path leaked into skill content: {path}")
    raise SystemExit(1)
PY
```

Expected: The user's actual home path does not appear in the skill or templates.

### Task 4: Dry-Run The Invocation Contract Without Changing A Repo

**Files:**
- Check: `~/.codex/skills/Knowledge-setup/SKILL.md`

**Interfaces:**
- Consumes: installed skill instructions.
- Produces: confidence that a future invocation will modify only the three context-layer files.

- [ ] **Step 1: Read the skill as Codex would**

```bash
sed -n '1,260p' "$HOME/.codex/skills/Knowledge-setup/SKILL.md"
```

Expected: The skill gives a complete adoption workflow without referencing missing files, scripts, generated tooling, or background automation.

- [ ] **Step 2: Confirm the future invocation wording**

Use this manual trigger from any target repo:

```text
Use $Knowledge-setup in this repo
```

Expected: The skill activates as a manual one-command repo initialization workflow. It does not run automatically on arbitrary folders.
