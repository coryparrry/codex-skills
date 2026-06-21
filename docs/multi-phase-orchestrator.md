# Multi-Phase Orchestrator

This how-to guide explains how to use the beta `multi-phase-orchestrator` skill to coordinate multiple related work units through fresh Codex worktree threads.

## Before You Start

You need:

- the `multi-phase-orchestrator` skill installed;
- a clear work source, such as a plan, review findings, PR feedback, or a list of phases;
- enough repo validation context to tell each child thread how completion will be checked.

Install the beta skill with:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill multi-phase-orchestrator
```

## Use The Skill

Ask for the skill explicitly:

```text
Use $multi-phase-orchestrator to coordinate these work units with fresh worktree threads.
```

The skill should:

1. Bind the work source, required skills, validation route, integration route, and closeout route.
2. Derive concrete work units with scope, dependencies, required skills, review gates, and validation.
3. Create fresh Codex worktree threads for runnable units.
4. Monitor child thread status, changed files, validation, review or gate evidence, and commits.
5. Integrate only reviewed, validated, and frozen unit outputs.
6. Run combined validation, check for private paths or secrets, and report remaining risks.

## Beta Boundaries

The skill is explicit-invocation-only. Do not use it for a single narrow edit, review-only work, or tasks where the user has not provided or approved a source of work units.

Treat child thread summaries as claims until checked against live files, diffs, tests, and evidence records.

## Related Docs

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [Reference](reference.md)
