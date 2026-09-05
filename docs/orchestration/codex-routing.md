# Codex Routing

`codex-routing` coordinates non-trivial coding work by assigning bounded lanes to agents whose capabilities match the work. The root agent integrates and validates the combined result.

Invoke it with:

```text
Use $codex-routing to coordinate this coding task with bounded, capability-matched agent lanes and integrated validation.
```

The root keeps small or tightly coupled work local. Useful independent investigation, implementation, testing, and review lanes can run in parallel. Each assignment should identify its goal, ownership, relevant evidence, constraints, and completion checks.

Routing uses the roles, models, tools, and reasoning options available in the current session. It does not assume fixed model names, effort floors, or a fixed concurrency limit.

A quiet or slow agent remains active until evidence shows it failed, reported an unrecoverable blocker, terminated without completing the assignment, or the user asked for replacement. Ordinary wait timeouts and elapsed time are not failure evidence.

The root checks important findings against current state, integrates the work, runs relevant validation, and uses focused corrections only when evidence identifies a defect.

## Related Docs

- [Installation](../installation.md)
- [Usage Guide](../usage.md)
- [Reference](../reference.md)
