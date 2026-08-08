# Engineering Advisor

`engineering-advisor` routes repository edits to capability-matched Terra workers while the root agent remains a non-implementing advisor.

Use it only when the user explicitly requires Sol or the current root to advise without editing files:

```text
Use $engineering-advisor to verify these findings and route legitimate fixes to capability-matched Terra workers. You are the advisor only: do not implement.
```

## Role Boundary

The root investigates, scopes, delegates, reviews, validates a fresh runtime, and performs authorized Git publication after reviewing the final diff. It does not modify tracked working-tree contents as implementation or finish a worker patch. Every implementation correction returns to the owning Terra worker.

This is a behavioural restriction on the root, not a requirement to make the parent runtime read-only. When implementation is authorized, the permission mode must still let the worker edit.

## Routed Workers

Editing agents always use the `worker` type, `gpt-5.6-terra`, an explicitly selected reasoning effort, `fork_turns: "none"`, and a self-contained assignment. Medium is the default; Low is reserved for fully specified mechanical edits, High handles non-trivial interactions or state, and Xhigh is reserved for real trust, authorization, data-integrity, migration, race, cryptographic, or sandbox boundaries.

Reconnaissance and independent review use read-only Terra explorers. A bounded Sol Low second opinion may challenge one decision but never implements or accepts the final diff. Delegated agents cannot spawn their own agents.

## Evidence And Minimality

The root verifies findings before delegation, keeps ownership non-overlapping, and reviews the actual diff rather than accepting worker claims. Assignments describe the behavioural contract, preservation constraints, prevention, validation, and out-of-scope work without dictating a line-by-line patch.

For user-visible work, completion requires a fresh build from the final source when available. Direct user feedback about live behaviour overrides stale artifacts or green tests.

## Related Docs

- [Usage Guide](usage.md)
- [Installation](installation.md)
- [Reference](reference.md)
