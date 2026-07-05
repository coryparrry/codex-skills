### Task 2: Add Starter Stubs For New Repo Templates

**Files:**
- Create: `~/.codex/skills/Knowledge-setup/templates/AGENTS.md`
- Create: `~/.codex/skills/Knowledge-setup/templates/context.md`
- Create: `~/.codex/skills/Knowledge-setup/templates/graph.json`

**Interfaces:**
- Consumes: the skill contract from Task 1.
- Produces: copyable stubs for new repo templates.

- [ ] **Step 1: Write the `AGENTS.md` stub**

Use `apply_patch` to create `~/.codex/skills/Knowledge-setup/templates/AGENTS.md` with the same tiny router content from the skill's `AGENTS.md Content` section.

Expected: The stub is usable as-is in a new repo and contains no repo-specific claims.

- [ ] **Step 2: Write the `context.md` stub**

Use `apply_patch` to create `~/.codex/skills/Knowledge-setup/templates/context.md`:

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

Use `apply_patch` to create `~/.codex/skills/Knowledge-setup/templates/graph.json`:

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
