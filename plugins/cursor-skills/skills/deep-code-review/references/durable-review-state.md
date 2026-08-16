# Durable review state

Use this protocol for every snapshot audit, multi-agent review, or review likely to exceed one context window. Its purpose is to preserve exact progress while preventing the root reviewer from accumulating every source file, tool result, and specialist thought in one context.

For Luna at `max`, [luna-max-whole-repository-audit.md](luna-max-whole-repository-audit.md) replaces the generic file layout below with a more explicit state machine. Preserve the ownership, bounded-context, and evidence-pointer rules from this file unless that Luna/max contract defines a stricter rule.

Markdown is the canonical state format because agents can update and resume it reliably. JSON may be generated as a derived index for tooling, but it must not be the only resumable record.

## Create isolated state files

Create one review directory in the user-requested location or writable scratch space outside the repository. Use this shape:

```text
<review-state>/
├── INDEX.md
├── root-integration.md
└── lanes/
    ├── <lane-id>.md
    └── <nested-lane-id>.md
```

The root reviewer alone owns `INDEX.md` and `root-integration.md`. Each agent or nested agent owns exactly one lane file. Never allow concurrent writers on one file. A parent integrates a child's compact handoff; it does not copy the child's entire checkpoint into its own.

Use parallel agents as a context boundary, not as a finding multiplier. After the root builds the denominator and shared-contract map, assign independent production areas or flows to separate agents within the selected model profile's concurrency limit. If the profile permits nested delegation and a lane still contains multiple independent areas or needs repeated evidence slices, its owner may create nested lane files and delegate those slices. If nesting is prohibited, the coordinator schedules those slices in later waves.

Do not delegate overlapping scopes, launch duplicate reviewers on the same area, or have the root repeat a lane's semantic review. Those patterns increase total context without isolating it. Keep integration, cross-lane validation, and final disposition with the root.

Do not stage or commit scratch review state. If the user explicitly asks for a tracked ledger, use the requested repository path and keep the same ownership rules.

## Initialize before broad reading

Put the exact review state, authority, dirty state, active model/reasoning profile, scope denominator, lane ownership, shared contracts, and exclusions in `INDEX.md`. Assign coherent production areas, flows, or contracts rather than arbitrary file ranges. Every in-scope area must have one primary owner.

Start each lane file with:

```markdown
# Lane: <id>

## Snapshot and scope
- Exact state:
- Owned areas:
- Entry points and contracts:
- Explicit exclusions:

## Coverage
| Area or flow | Status | Evidence pointers | Stopping boundary | Open edge |
|---|---|---|---|---|

## Candidates
| ID | State | Trigger and violated property | Evidence pointers | False-positive check | Next check |
|---|---|---|---|---|---|

## Cross-lane handoffs

## Validation

## Next bounded slice

## Handoff summary
```

Use evidence pointers such as repository-relative path and line, symbol, commit, test name, or saved command-artifact path. Do not paste source files, complete diffs, full logs, or repeated command output into checkpoints.

## Work in bounded evidence slices

Inventory with manifests, symbol search, and narrow ranges before opening implementation. Review one coherent area or flow at a time. As a default ceiling, checkpoint after at most eight newly opened files or about 2,000 newly loaded lines, whichever comes first; reduce the slice for large or highly coupled files. Never bulk-open a production root merely to establish coverage.

Update the owning checkpoint:

1. after each bounded slice;
2. when a candidate changes state;
3. before a long-running command, delegation, or wait;
4. after a tool failure or newly discovered cross-lane edge; and
5. immediately before returning or timing out.

Compaction itself is not a usable trigger because it can happen before the next model action. Event-based checkpoints make any completed slice recoverable.

Save verbose build, test, trace, and scanner output as external artifacts when possible. Bring only the exit status, discriminating failure lines, and evidence pointer into the active context and checkpoint.

## Keep the root context narrow

The root reviewer keeps only the exact-state index, coverage statuses, shared-contract map, compact lane handoffs, and candidates being independently validated. It must not read all lane checkpoints or replay their exploration by default.

Agents update their owned checkpoint rather than sending periodic raw progress to the root. Each agent returns only:

- its checkpoint path;
- completed and uncovered scope;
- validated or unresolved candidate IDs;
- cross-lane edges requiring integration; and
- its next recommended slice.

Keep this handoff to at most 300 words. The root reads specific checkpoint rows and narrow source slices only when integrating a contract or validating a candidate.

After compaction or interruption, read `INDEX.md`, the current lane's snapshot, `Next bounded slice`, and `Handoff summary` first. Re-resolve the exact repository state before continuing. If it changed, mark snapshot-dependent rows stale and re-read only affected slices.

## Finish and clean up

Before reporting, reconcile every lane status into `INDEX.md`, integrate cross-lane edges in `root-integration.md`, and apply the normal completeness gate. A missing checkpoint, absent final handoff, stale snapshot, or unexplained area remains uncovered.

Keep a tracked ledger when the user requested it. Otherwise remove disposable scratch state after the final report when safe and permitted; do not delete it while any reviewer may still need it.
