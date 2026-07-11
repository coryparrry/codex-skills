# AGENTS.md

This repo uses a tiny Repository Context Layer. Treat it as a routing aid, not source truth.

Before planning or editing:

1. Read only the context kernel: `Intent`, `Constraints`, and the evolved-context `Catalog`:

   ```sh
   awk '/^### Route:/ { exit } { print }' .repo/context.md
   ```

2. List only the graph route catalog:

   ```sh
   jq '.routes | to_entries | map({route: .key, summary: .value.summary, match: .value.match})' .repo/graph.json
   ```

3. Choose the closest route. Load only the `general` and selected evolved-context sections, replacing `<route>`:

   ```sh
   awk -v route='<route>' '/^### Route:/ { section = substr($0, length("### Route: ") + 1); selected = (section == "general" || section == route) } selected { print }' .repo/context.md
   ```

4. Load only the selected graph route and its starting nodes:

   ```sh
   jq -e --arg route '<route>' '.routes[$route] as $r | select($r != null) | {route: $r, nodes: [$r.start_nodes[]? as $id | {id: $id, definition: .nodes[$id]}]}' .repo/graph.json
   ```

5. Inspect the route's `inspect_first` paths and each node's `truth` paths before broad search. Load a relevant dependency node directly rather than reading the full graph.
6. Verify live source files before relying on graph or context.

Read the full context or graph only when no route fits, the task crosses several routes, or that context-layer file is being audited or updated. If `awk` or `jq` is unavailable, use another structured parser and preserve the same progressive-read sequence.

Rules:

- Treat `.repo/context.md` as progressively loaded repo intent, constraints, and durable learned context.
- Treat `.repo/graph.json` as progressively loaded, routes-first, evidence-backed navigation, not source truth.
- Source files and tests are authoritative when graph/context conflict with implementation.
- Update `.repo/context.md` when the work teaches a durable, non-obvious lesson.
- Update `.repo/graph.json` in the same change set when work changes commands, routes, tests, contracts, entrypoints, ownership, generated files, mirrored files, deprecated paths, do-not-edit areas, or important gotchas.
- Do not update the context layer for ordinary edits that do not change durable repo knowledge.
- Do not add scripts, dependencies, databases, MCPs, vector stores, background services, or generated indexes for this context layer unless explicitly requested.
