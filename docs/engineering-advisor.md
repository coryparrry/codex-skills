# Engineering Advisor

`engineering-advisor` runs implementation through Terra Xhigh workers while the root agent remains a non-implementing advisor.

## Use It For

- asking Sol or the current root to advise workers without editing files;
- sending verified audit or review findings to Terra for implementation;
- keeping bug fixes narrow, regression-safe, and free of unnecessary code;
- making root-owned review and validation independent from worker implementation.

Ask Codex:

```text
Use $engineering-advisor to verify these findings and send legitimate fixes to Terra Xhigh. You are the advisor only: do not implement, and reject unnecessary code or behavior drift.
```

## Role Boundary

The root may inspect, reproduce, scope, delegate, review, test, validate a fresh runtime, and perform authorized Git handoff. It must not modify repository files, finish a worker patch, or make a small follow-up edit. Every implementation correction returns to the owning Terra Xhigh worker.

The root still owns the result. It verifies findings before delegation, gives workers explicit non-overlapping ownership, reviews the combined diff, and runs the final tests and runtime checks. Worker claims are evidence to inspect, not proof by themselves.

If Terra Xhigh is unavailable, the skill can continue read-only diagnosis but reports implementation blocked. It does not silently substitute another model or let the root implement.

## Scope And Minimality

Each worker receives a bounded packet containing the proven trigger, desired behavior, preservation constraints, prevention check, validation, owned files, and explicit out-of-scope work. The skill rejects speculative abstractions, compatibility layers, configuration, services, or UI changes that the verified problem does not require.

For user-visible work, completion requires a fresh build from the final source when that validation is available. Direct user feedback about live behavior overrides stale artifacts or green tests.

## Related Docs

- [Usage Guide](usage.md)
- [Installation](installation.md)
- [Reference](reference.md)
