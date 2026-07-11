# Knowledge Setup

`knowledge-setup` creates or refreshes a compact Repository Context Layer so future agents can navigate a repository without repeatedly rediscovering its structure or loading a full architecture graph.

## Use It

From the target repository root, ask:

```text
Use $knowledge-setup in this repo.
```

The skill inspects live source, tests, manifests, CI, documentation, and existing instructions before reconciling exactly three files:

```text
AGENTS.md
.repo/context.md
.repo/graph.json
```

It preserves verified repository-specific instructions and durable context. It removes or rewrites entries only when live evidence proves them stale, invalid, inapplicable, or speculative.

## How Agents Read It

Future agents:

1. Read only the context kernel: repository intent, constraints, and the evolved-context catalog.
2. Query only the graph route catalog.
3. Select the route matching the task.
4. Load only `general` plus the selected route's evolved context.
5. Load only the selected graph route and its starting nodes.
6. Inspect the listed source-truth and test paths.
7. Verify live implementation before relying on summaries.

Agents read the full context or graph only when no route fits, work crosses several routes, or that context-layer file is under review.

## Keep It Current

Update `.repo/context.md` when work changes repository intent, a hard constraint, or a durable non-obvious lesson. Keep the always-loaded kernel concise, list populated context sections in `Catalog`, place route-specific lessons under matching `### Route: <route>` headings, and reserve `general` for cross-cutting lessons. Update `.repo/graph.json` in the same change set when work changes commands, routes, source-truth locations, ownership, tests, contracts, generated or mirrored surfaces, deprecated paths, or important boundaries.

Run `$knowledge-setup` again for an explicit refresh or repair. The skill reconciles existing entries instead of replacing verified knowledge wholesale.

## Boundaries

The context layer is a routing aid, not implementation truth. Source files, tests, manifests, and CI remain authoritative. The skill does not add dependencies, databases, vector stores, MCPs, background services, or generated indexes.

## Related Docs

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [Reference](reference.md)
