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
