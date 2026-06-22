# Write Codex Loops

This how-to guide explains how to use `writing-codex-loops` to design or create bounded Codex work loops.

Use it for heartbeat automations, recurring project automations, PR or CI loops, retry loops, multi-agent follow-up loops, and any workflow that must repeat with explicit state, cadence, validation, stop conditions, and escalation.

## Purpose

The skill turns vague loop requests into a concrete loop contract. A good loop names:

- the state it observes;
- the action it repeats;
- the evidence it trusts;
- the rule for continuing;
- the exact condition that stops or escalates.

If the user asks for a loop that should actually run, the skill should create or update a Codex Automation. If the user asks only for a draft, it should return a loop contract without creating an automation.

## Before You Start

You need:

- the `writing-codex-loops` skill installed;
- a clear goal or workflow to loop over;
- a source of truth for live state, such as a thread, repo path, PR, issue, dashboard, logs, or external API;
- enough permission context to know whether the loop may create an automation, edit files, post comments, run checks, or ask before acting.

The skill should stop and ask when the loop would require destructive actions, broad scope expansion, paid operations, credentials, unclear product judgment, or security tradeoffs.

## Install The Skill

Install the skill with the `skills` CLI:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill writing-codex-loops
```

Restart Codex if the skill does not appear.

## Run The Skill

For an actual heartbeat or recurring automation, ask for the loop to be created:

```text
Use $writing-codex-loops to create a heartbeat that checks this PR every 10 minutes until required checks pass, a required check fails three times, or review feedback needs owner input.
```

For draft-only design, say not to create the automation:

```text
Use $writing-codex-loops to draft a loop contract for daily dependency review, but do not create the automation.
```

For immediate in-thread work, describe the bounded loop and the stop rule:

```text
Use $writing-codex-loops to run an in-thread loop over these failing tests until each failure has a live cause, a fix, or a blocker with evidence.
```

## Understand The Contract

The skill should produce or use a contract with these fields:

| Field | Meaning |
|---|---|
| Goal | Observable final state |
| Trigger | Manual request, schedule, CI failure, review comment, stale state, or event |
| State | Phase, source of truth, artifacts, attempt count, last observation, and owner |
| Cycle | Observe, decide, act, verify, update state, and report |
| Feedback | Tests, logs, review threads, screenshots, command output, user decisions, or API results |
| Progress | What must change or decrease each pass |
| Invariants | Scope, branch, permissions, approval gates, and no unrelated edits |
| Cadence | Event-driven, per edit, per validation run, every N minutes, daily, weekly, or timeboxed |
| Retry | Retryable errors, max attempts, backoff, idempotency, and non-retryable failures |
| Stop | Exact success, max attempts, no-progress threshold, blocked state, or user redirect |
| Escalation | Concrete user question with evidence and choices |
| Audit | What each pass reports so the loop can be inspected or resumed |

## Loop Kinds

Use a thread heartbeat when the loop should wake up the same conversation with preserved context.

Use a standalone or project automation when the loop should run independently across a project or workspace. These prompts need a durable state source because they cannot rely only on chat context.

Use an in-thread loop when all repetition happens in the current turn and no scheduled wake-up is needed.

Use a multi-agent loop when work is split across agents. The coordinator must assign ownership, prevent overlapping edits, validate results against live state, and integrate deliberately.

## Validation Rules

Before handing off a loop, check that it is:

- bounded by success, blocked, max-attempt, and no-progress stops;
- observable from live evidence;
- idempotent across repeated passes;
- scoped to named repos, files, branches, actions, and approval gates;
- progress-aware through a decreasing or advancing variant;
- recoverable through retry and escalation rules;
- auditable through compact pass reports.

Do not accept prompts like "keep going until done" without replacing them with concrete continue, stop, and escalation predicates.

## File Layout

```text
skills/writing-codex-loops/
  SKILL.md
  agents/
    openai.yaml
  references/
    loop-principles.md
```

## Related Docs

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [Reference](reference.md)
- [Multi-Phase Orchestrator](multi-phase-orchestrator.md)
