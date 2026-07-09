---
name: knowledge-setup
description: Use when a repository needs its three-file context layer created, refreshed, repaired, or reconciled from live evidence.
---

# Knowledge Setup

Create or refresh a small, evidence-backed Repository Context Layer in the current repository. Run it manually with `Use $knowledge-setup in this repo`.

The complete target surface is:

```text
AGENTS.md
.repo/context.md
.repo/graph.json
```

Source files and tests remain authoritative. The context layer only helps future agents route work.

## Contracts

```text
Existing AGENTS.md = verified instructions retained + context-layer router reconciled in place.
Small graph = verified commands + inspect_first routes + empty nodes/edges when deeper semantics add no value.
```

Use the starter files in [`templates/`](templates/) for reusable content and shape. Do not copy template text into this workflow.

## Workflow

1. Confirm the current directory is a Git repository. Report the branch and whether it appears to be the default branch; do not create or switch branches unless required.
2. Read an existing `AGENTS.md` before other edits. Inspect tracked files, README files, manifests, CI, tests, docs, generated or mirrored surfaces, and high-signal source roots.
3. Reconcile `AGENTS.md`:
   - If absent, start from [`templates/AGENTS.md`](templates/AGENTS.md).
   - If present, retain verified repository-specific instructions and reconcile the context-layer router in place. Remove an instruction only when live evidence proves it obsolete and the task authorizes removal.
4. Create or refresh `.repo/context.md` using [`templates/context.md`](templates/context.md). Keep the required headings. Record concise intent, verified hard constraints, and dated durable lessons rather than task history.
5. Create or refresh `.repo/graph.json` using [`templates/graph.json`](templates/graph.json):
   - Record only commands verified from repository evidence.
   - Make routes the primary navigation layer. Each route starts with existing repo-relative `inspect_first` paths.
   - Add `start_nodes`, nodes, or edges only when semantic boundaries materially improve repeated navigation. Otherwise keep `nodes` empty and `edges` empty.
   - Node IDs, when used, are stable lowercase dot-separated semantic IDs such as `area.core`, `boundary.public_api`, or `test.unit`; never use raw paths as IDs.
   - Edges, when used, connect node IDs with one allowed type: `depends_on`, `implements`, `calls`, `called_by`, `tested_by`, `documents`, `generates`, `mirrors`, `replaces`, or `do_not_edit`.
   - Omit unknown commands, inapplicable routes, and speculative relationships.
6. Validate the three files, then show their final diff. Commit only when the user or repository workflow expects it.

## Boundaries

- Modify only the three context-layer files unless the user expands scope.
- Do not add scripts, dependencies, generated indexes, databases, MCPs, vector stores, background services, or committed validation tooling.
- Treat source, tests, manifests, and CI as truth when documentation disagrees.
- Do not delete, move, ignore, or rewrite tracked hidden or tool files.
- Do not include local absolute paths in committed files or GitHub-facing text.
- Prefer a smaller accurate graph over a larger speculative graph.

## Validation

Use temporary commands; do not commit them as tooling.

```bash
test -s AGENTS.md
test -s .repo/context.md
test -s .repo/graph.json
for heading in '## Intent' '## Constraints' '## Evolved Context'; do
  grep -nFx "$heading" .repo/context.md || exit 1
done
python3 -m json.tool .repo/graph.json >/dev/null
```

Also verify:

- every command has `command`, `cwd`, and evidence grounded in the repository
- every route `inspect_first` path exists
- any `start_nodes`, node references, and edge endpoints resolve to real nodes
- edge types are allowed and evidence paths exist when supplied
- existing verified `AGENTS.md` instructions remain present
- none of the three files contains the local home path

## Closeout

Report routes created, unresolved uncertainties, files changed, validation run, and whether the diff was committed or left for review.
