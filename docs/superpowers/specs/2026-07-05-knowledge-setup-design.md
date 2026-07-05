# Repository Context Layer Design

## Purpose

Each repo should carry a small, dependency-free context layer that helps coding agents route work correctly without turning `AGENTS.md` into a stale operating manual.

The design optimizes for simple per-repo adoption:

- one tiny boot file agents auto-read
- one human-readable context file for durable repo memory
- one evidence-backed JSON architecture graph for navigation
- no scripts, generated indexes, background services, databases, MCPs, vector stores, or new dependencies

The system is agent-maintained after adoption, but only when a task changes durable repo knowledge.

## File Shape

Each repo gets exactly these files:

```text
AGENTS.md
.repo/context.md
.repo/graph.json
```

`AGENTS.md` is a tiny router. It tells agents to read `.repo/context.md` and `.repo/graph.json` before planning, choose the relevant route or node from the graph, and update the context layer when their work changes durable repo knowledge.

`.repo/context.md` is human-readable repo memory. It records intent, hard constraints, and dated durable lessons. Agents may append to it automatically, but only for non-obvious facts that should survive future sessions.

`.repo/graph.json` is the evidence-backed architecture graph. It describes real repo areas, boundaries, commands, tests, generated paths, mirrored paths, deprecated paths, and gotchas.

Source files remain the truth. The graph and context are routing aids that must stay grounded in live repo evidence.

## Delivery Mechanism

The repeatable setup should be a local Codex skill plus starter stubs, not a background automation.

Use a manual skill trigger from a target repo after the first real project files exist:

```text
Use $Knowledge-setup in this repo
```

The skill inspects live repo evidence, then creates or refreshes exactly `AGENTS.md`, `.repo/context.md`, and `.repo/graph.json`. New repo templates may include thin starter stubs for those three files, but the skill must replace or fill them from live evidence before they are treated as useful.

The skill should not run silently on arbitrary folders. Manual invocation prevents accidental mutation of scratch directories, vendor checkouts, generated repos, or incomplete experiments.

## Context Markdown Contract

`.repo/context.md` must use this structure:

```md
# Repository Context

## Intent

## Constraints

## Evolved Context
```

`Intent` describes what the repo is, what it optimizes for, and which design philosophy should guide changes.

`Constraints` contains only non-negotiable repo-specific rules, each with a reason when practical. Old `AGENTS.md` content should be preserved here only when it is truly repo-specific and still valid.

`Evolved Context` is append-only durable memory. Entries should be dated and concise.

Agents should append to `.repo/context.md` when they learn durable, non-obvious facts, such as:

- a test command only works with a specific flag
- a generated folder must not be edited directly
- a repo has a package/app boundary that agents keep confusing
- a provider, API, or runtime assumption was proven wrong
- a recurring failure mode has a known prevention rule

Agents must not append ordinary task summaries, generic coding advice, facts already obvious from source filenames, or speculative notes that were not verified.

## Graph JSON Schema

Every repo uses the same top-level schema:

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

`repo` stores basic metadata: name, kind, languages, package/build systems, and last reviewed date.

`agent_contract` states how agents use the graph: read context first, choose a route before broad search, inspect graph-listed files before wider exploration, and update the graph only when durable structural knowledge changes.

`commands` stores verified install, build, test, lint, typecheck, run, release, or smoke commands. Unknown commands are omitted or left empty. Agents must not invent commands.

Each command entry should use this shape:

```json
{
  "command": "exact command",
  "cwd": ".",
  "evidence": ["repo-relative/path"],
  "notes": "Optional short note."
}
```

`command` is the exact command. `cwd` is repo-relative. `evidence` points to a manifest, CI file, README, Makefile, package file, or observed successful local run.

`routes` maps task types to first inspection targets. Common route keys are:

- `understand_repo`
- `bug_fix`
- `feature_change`
- `ui_change`
- `api_or_contract_change`
- `persistence_change`
- `build_or_ci_change`
- `docs_change`
- `release_change`

Each route entry should use this shape:

```json
{
  "start_nodes": ["area.core"],
  "inspect_first": ["src/", "tests/"],
  "notes": ["Short practical routing note."]
}
```

`start_nodes` references node IDs in `nodes`. `inspect_first` contains repo-relative paths that exist. Task routes that do not apply to the repo are omitted.

`nodes` are stable semantic repo areas, not file paths. Example IDs:

- `area.ui`
- `area.core`
- `area.persistence`
- `boundary.public_api`
- `boundary.data_model`
- `workflow.ci`
- `workflow.release`
- `test.unit`
- `test.contract`
- `generated.public_sdk`
- `mirror.plugin_skills`
- `deprecated.legacy_runner`

Each node should use only fields that help future routing:

```json
{
  "kind": "area",
  "purpose": "Short practical purpose.",
  "owns": ["real/path/or/directory"],
  "entrypoints": ["real/path/to/entrypoint"],
  "depends_on": ["boundary.public_api"],
  "tested_by": ["test.contract"],
  "documented_by": ["doc.readme"],
  "gotchas": ["Durable warning grounded in source evidence."]
}
```

`edges` connect nodes with evidence-backed relationships. Allowed relationship types include:

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

Edges should include evidence paths when practical:

```json
{
  "from": "area.skills",
  "to": "mirror.plugin_skills",
  "type": "mirrors",
  "evidence": ["skills/", "plugins/codex-skills/skills/"]
}
```

`staleness_checks` are plain questions agents must consider. They are not runnable validation scripts.

## Graph Maintenance Rules

Agents update `.repo/graph.json` automatically and opportunistically when normal work changes or discovers durable structure:

- commands
- package managers
- build, test, lint, typecheck, release, or smoke lanes
- public contracts
- entrypoints
- ownership boundaries
- generated files
- mirrored files
- deprecated paths
- do-not-edit areas
- important gotchas
- routes agents should use in future

The graph update belongs in the same change set as the code change that made it necessary.

Agents should not update the graph for ordinary internal edits where architecture and routing did not change.

Every graph path must exist, except paths explicitly marked deprecated or missing. Every edge should include evidence paths when practical. If the agent is unsure, it should leave the graph unchanged rather than inventing structure.

Prefer a smaller accurate graph over a larger speculative graph. Agents should remove stale or unhelpful entries when discovered, rather than preserving doubtful structure because it already exists in the graph.

## Initial Adoption Flow

The first adoption pass for a repo is evidence-first:

1. Inspect existing `AGENTS.md`, README files, package/build files, test configuration, CI, docs, generated folders, and obvious source roots.
2. Preserve only true repo-specific hard constraints from old `AGENTS.md`; move them into `.repo/context.md`.
3. Replace `AGENTS.md` with the tiny router.
4. Create `.repo/context.md` with intent, constraints, and initial evolved context.
5. Create `.repo/graph.json` with real commands, routes, nodes, edges, and staleness questions.
6. Keep the graph useful, not exhaustive. Aim for roughly 8-30 nodes depending on repo size.
7. Validate JSON syntax, graph references, route targets, command evidence, path evidence, generated/mirrored markings, and local-path leakage before any commit.
8. Commit the adoption as a normal repo change when the user or repo workflow expects commits; otherwise leave the three-file diff ready for review.
9. From then on, agents update context and graph opportunistically with relevant code changes.

## Guardrails

- No repo-wide rewrite.
- No new dependencies.
- No generated tooling.
- No false precision.
- No local machine paths in GitHub-facing content.
- Existing tracked hidden/tool files must not be treated as junk.
- If existing docs contradict source, source wins and the conflict is called out.
- If a repo is unclear, create fewer nodes and record uncertainty in node `gotchas`.

## Verification

For adoption, the agent must verify:

- `AGENTS.md` is small and only acts as a router.
- `.repo/context.md` has `Intent`, `Constraints`, and `Evolved Context`.
- `.repo/graph.json` parses as valid JSON.
- graph paths are real, unless explicitly marked deprecated or missing.
- route `start_nodes`, node references, and edge endpoints point to real node IDs.
- edge types come from the allowed relationship list.
- commands in the graph came from live repo files or successful inspection.
- generated, mirrored, and do-not-edit surfaces are explicitly marked.
- old `AGENTS.md` constraints were not silently dropped.

Expected failure handling:

- If a repo is too unclear to map confidently, create fewer nodes and document the uncertainty.
- If a command cannot be verified, mark it unknown or omit it.
- If docs and source disagree, graph source truth and mention the doc mismatch.
- If an existing `AGENTS.md` is large or stale, preserve only verified constraints.
- If a graph update would be noisy or unrelated to the task, skip it.

## Definition Of Done

For each repo, a future agent can open the repo, read three files, identify the right area to inspect first, know the main commands and tests, and avoid known boundaries without reading a large instruction file.
