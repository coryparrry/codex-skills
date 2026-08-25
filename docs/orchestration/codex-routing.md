# Codex Routing

`codex-routing` uses Sol to plan and coordinate coding work while Luna workers investigate and implement it. Sol reviews the integrated result and owns the final response.

Invoke it with:

```text
Use $codex-routing to coordinate this coding task with Sol advising and Luna workers executing.
```

Sol splits the task into bounded assignments and chooses each worker's effort from that assignment. Luna High handles clear work with strong checks, Luna xhigh handles harder investigation and implementation, and Luna Max is reserved for exceptionally broad or difficult bounded lanes.

Independent assignments can run in parallel. Dependent work stays sequential. A quiet or slow worker remains active until it finishes, reports a blocker, explicitly fails, or the user asks for a replacement.

Sol checks that the requested outcome was achieved, the constraints were preserved, and the validation is credible. Corrections go back to a Luna worker instead of turning Sol into the implementer.

## Related Docs

- [Installation](../installation.md)
- [Usage Guide](../usage.md)
- [Reference](../reference.md)
