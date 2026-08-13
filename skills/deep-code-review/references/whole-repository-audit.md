# Whole-repository audit

Use this reference only for snapshot audits. Its purpose is to leave enough evidence that another reviewer can see what was traced, where expansion stopped, and what remains uncovered.

## Build the ledger before reviewing details

Create a persistent ledger when the user requests one. Otherwise maintain the same structure in working notes. Record evidence as each row completes and before context compaction.

### Scope and authority

Record the reviewed commit, branch or tag, default branch, upstream comparison, dirty state, included first-party roots, excluded generated/vendor/build roots, and why the state is authoritative. A detached or stale state with no explicit user selection cannot represent an unqualified whole-repository audit.

Build the coverage denominator from repository evidence before grouping areas: reconcile all first-party tracked roots with build and package manifests, executable entry-point registries, workflow and deployment configuration, generators and mirrors, and release inventories. Assign every discovered executable or shipped artifact to exactly one production-area row or a reasoned exclusion. Group files only when they share one owner, contract, entry/exit boundary, and failure model; do not use a repo-wide catch-all row. Any unexplained artifact forces `partial`.

### Production-area ledger

Use one row per production module or coherent artifact when a file is not the right unit.

| Area or artifact | Role and supported behavior | Inbound reachability | Outbound dependencies, state, and side effects | Config, consumers, and tests | Evidence and stopping boundary | Status |
|---|---|---|---|---|---|---|

Allowed statuses are `traced`, `unresolved`, `excluded with reason`, and `not reviewed`. A list of paths, imports, exports, search hits, line counts, or test names does not fill these columns.

### Critical-flow ledger

Use one row per supported entry point or externally meaningful workflow.

| Entry and trigger | Ordered production path | Authority and data transformations | Failure, retry, cancellation, and recovery | Observable sink | Evidence | Unresolved edge |
|---|---|---|---|---|---|---|

Trace CLI commands, HTTP or RPC routes, jobs, events, user interactions, package/install flows, migrations, and release/deployment paths that the repository supports. Read the implementation on both sides of each important edge. Stop only at a stable external contract, exhaustive consumer set, verified adapter, or runtime observation, and record that proof.

### Shared-contract ledger

Use one row for each contract that crosses production areas.

| Contract | Canonical producer | Derived or mirrored artifacts | Runtime consumers | Drift or compatibility check | Evidence and result |
|---|---|---|---|---|---|

Typical contracts include schemas, config keys, permissions, feature flags, package assets, generated clients, workflow copies, lockfiles, manifests, cache keys, event formats, policy files, and release pins.

### Candidate ledger

Keep validated, unresolved, disproved, stale, and observation-only candidates. For each, record the trigger, path, violated property, evidence, false-positive check, and disposition. This prevents promising leads from disappearing across batches or compaction. Do not promote findings to meet a quota.

## Review in connected passes

1. Inventory first-party production areas, supported entry points, and shared contracts.
2. Walk every entry point vertically to its observable sinks and failure paths.
3. Walk shared contracts horizontally across producers, mirrors, configuration, runtime consumers, tests, and release artifacts.
4. Inspect negative space, trust boundaries, concurrency, compatibility, resource lifetime, and operations where triggered.
5. Run deterministic and behavioral checks that discriminate correct behavior from plausible failures.
6. Integrate specialist lanes, validate candidates, and run the omission pass against the ledger.

Tests can validate a traced claim. They cannot prove that untraced paths were reviewed. Broad green suites are not substitutes for reading callers, consumers, and runtime wiring.

Do not stop the audit because several findings have already survived. Continue through every in-scope production area and flow until the completeness gate passes or a concrete limit forces a `partial` result. Finding count is neither a stopping rule nor a coverage metric.

## Completeness gate

A snapshot audit is `complete` only when:

- the reviewed state is authoritative for the user's request;
- every in-scope production area is `traced` or `excluded with reason`;
- every supported entry point has a critical-flow row;
- every material shared contract has a cross-area row;
- every expansion stops at a recorded safe boundary;
- every triggered material specialist lane and the omission pass completed and was integrated; unavailable, timed-out, or interrupted results force `partial`;
- no material unresolved or not-reviewed edge remains.

If time, context, dependencies, credentials, runtime access, or a missing lane prevents these conditions, report `partial`. State the completed slices and the next bounded slices instead of converting inventory breadth into a completeness claim.
