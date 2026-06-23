---
name: writing-codex-loops
description: Use when designing, writing, repairing, or scheduling Codex work loops, heartbeat automations, recurring project automations, PR or CI loops, multi-agent loops, retry loops, or skill-driven follow-up workflows that need explicit state, cadence, validation, stop conditions, or escalation.
---

# Writing Codex Loops

## Overview

Write loops as bounded Codex Automations when the user wants the loop to actually run. A usable loop names the state it observes, the action it repeats, the evidence it trusts, the rule for continuing, and the condition that stops or escalates.

If the request depends on unfamiliar loop theory, read [references/loop-principles.md](references/loop-principles.md).

## Workflow

1. Classify the user's intent.
   - Actual loop request: "create", "set up", "watch", "monitor", "keep checking", "wake up", "check back", "continue later", "make sure it loops", or any recurring/scheduled wording means create or update a Codex Automation with `automation_update`.
   - Draft-only request: "write a prompt", "draft", "design", "what would it do", or "do not create" means return a loop contract and do not call `automation_update`.
   - Same thread context or sub-hour follow-up: thread automation / heartbeat.
   - Independent recurring run, multi-project scan, or Triage findings: standalone/project automation.
   - Immediate work inside this turn only: in-thread work loop, not an automation.
   - Parallel implementation or review: multi-agent loop with explicit ownership and integration; pair it with a heartbeat/cron only when the user wants continuation across turns.

2. Collect the contract fields before writing the prompt.

| Field | Required content |
| --- | --- |
| Problem | Why this loop exists and what repeated failure it prevents. |
| Goal | Final state the loop is trying to reach. |
| Trigger | Manual request, schedule, CI failure, review comment, stale state, or event. |
| State | Current phase, source of truth, artifacts, attempt count, last observation, and owner. |
| Key interfaces | Stable repos, PRs, dashboards, files, APIs, commands, skills, or automations the loop will touch. |
| Cycle | Plan/act/observe/decide steps, including named skills/tools. |
| Feedback | Tests, logs, review threads, screenshots, command output, user decision, or external API result. |
| Progress | What must change or decrease each pass: failing tests, unresolved comments, unknowns, blockers. |
| Invariants | Rules that must stay true: scope, branch, permissions, no destructive ops, no unrelated edits. |
| Cadence | Event-driven, per edit, per validation run, every N minutes, daily, weekly, or timeboxed. |
| Retry | Retryable errors, max attempts, backoff/jitter, idempotency, and non-retryable failures. |
| Stop | Exact success, max attempts, no-progress threshold, blocked state, or user redirect. |
| Escalation | Concrete user question with evidence and 2-3 choices, not vague "what now?" |
| Out of scope | Adjacent work the loop must not absorb. |
| Audit | What each pass reports: actions, changed files, checks, decisions, next step. |

3. Write the loop as a contract, not prose.
   Use this skeleton:

```markdown
# Loop Contract: <name>

Problem: <current workflow gap or repeated failure this loop prevents>
Goal: <observable done state>
Loop kind: <heartbeat | project automation | standalone automation | in-thread | multi-agent>
Cadence: <interval or event>
State source: <thread context, file path, PR, issue, dashboard, logs, etc.>
Key interfaces:
- <stable repo, PR, dashboard, file, API, command, skill, or automation touched by the loop>

Acceptance criteria:
- [ ] <specific condition that proves the loop can stop successfully>
- [ ] <specific condition that proves the loop preserved required invariants>

Each pass:
1. Observe: <live state to read>
2. Decide: <comparison rule against goal/progress>
3. Act: <smallest safe action; named skills/tools>
4. Verify: <checks or evidence>
5. Update state: <attempt count, last observation, next action>
6. Report: <compact status format>

Continue while:
- <condition>

Stop successfully when:
- <condition>

Stop blocked and ask when:
- <condition + exact evidence to provide>

Do not:
- <task-specific invariant>

Out of scope:
- <adjacent work the loop must not absorb>
```

4. For actual loop requests, create or update the automation.
   - Use `automation_update`; do not stop after drafting a prompt.
   - For same-thread follow-up, call `automation_update` with `kind=heartbeat` and `destination=thread`.
   - For independent recurring project/workspace jobs, call `automation_update` with `kind=cron`, `cwds`, and the correct execution environment.
   - Prefer `suggested_create` or `suggested_update` when proposing worktree automations with local environment setup config.
   - Inspect existing automations first when the user asks to change an existing loop, and update rather than duplicating.
   - Make prompts durable: describe each wake-up action, reporting threshold, stop condition, and when to ask.
   - For fresh standalone/project runs, include a durable state source because the run does not preserve thread context.
   - Prefer worktrees for Git automation that may edit files.
   - Do not show raw RRULE strings to the user; put cadence in the tool field and describe it normally in the response.
   - After the tool call, report the automation name, type, cadence in plain language, and what evidence will stop/escalate the loop.

5. Validate the loop contract before handing it off.

| Check | Pass condition |
| --- | --- |
| Not unbounded | Has success, blocked, max-attempt, and no-progress stops. |
| Observable | Every continue/stop decision uses live evidence. |
| Idempotent | Repeated passes do not duplicate work or corrupt state. |
| Scoped | Names allowed files/repos/branches/actions and approval gates. |
| Progress-aware | Tracks a variant such as open comments or failing checks. |
| Recoverable | Has retry/backoff for transient failures and escalation for hard failures. |
| Auditable | Each pass leaves enough status to resume or inspect. |

## Example

```markdown
# Loop Contract: PR Review And CI Heartbeat

Problem: PR closeout can stall or drift when CI, review threads, and local branch hygiene are checked manually.
Goal: The current PR has no failing or pending required checks, no unresolved actionable review threads, and the local branch contains only scoped intentional changes.
Loop kind: heartbeat
Cadence: every 5 minutes while CI/review is active
State source: current thread context, local repo, current branch, GitHub PR
Key interfaces:
- GitHub PR checks and review threads
- Local Git branch and changed files
- Required repo validation commands

Acceptance criteria:
- [ ] Required checks are passing.
- [ ] Actionable review threads are resolved or addressed with evidence.
- [ ] Local changes are scoped and relevant validation passes.

Each pass:
1. Observe: run `git status --short`, confirm current branch, resolve the open PR with `gh pr view`, fetch check status and unresolved review threads.
2. Decide: if checks are pending, report and wait; if checks failed, inspect logs; if actionable review threads exist, classify them.
3. Act: use `$github:gh-fix-ci` for failing checks and `$github:gh-address-comments` for actionable review threads when available. Make the smallest scoped fix.
4. Verify: run the narrow local check for the changed path, then the strongest practical PR validation before closeout.
5. Update state: record attempt count, latest failing check or review thread count, files changed, commits made, and next expected action.
6. Report: PR URL, branch, CI state, review-thread count, changes made, validation, next action.

Continue while:
- Required checks are pending or failing.
- Actionable unresolved review threads remain.
- A validation failure has a fixable cause and the same failure has not repeated 3 times.

Stop successfully when:
- Required checks pass, actionable review threads are resolved/addressed, relevant validation passes, and local changes are scoped.

Stop blocked and ask when:
- Auth, permission, missing logs, external service state, destructive action, dependency installation, or product/security judgment is required.
- The same failure class repeats 3 times after focused fixes.

Do not:
- Merge the PR.
- Push to the default branch.
- Post review replies or resolve threads unless the user allowed it.
- Touch unrelated files.

Out of scope:
- Product changes unrelated to the PR's failing checks or actionable review findings.
```

If the user asked to make this loop run, create a heartbeat automation with this prompt. Do not merely paste the contract back to the user.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| "Keep going until done" | Replace with explicit continue, success, blocked, and no-progress predicates. |
| Heartbeat with no state | Include phase, attempt count, last observation, next action, and stop condition in every wake-up report. |
| Standalone automation relying on chat context | Add a file, issue, PR, dashboard, or external source as durable state. |
| Retry everything | Separate transient/idempotent retries from non-retryable errors and approval-gated actions. |
| Reflection-only loop | Use executable checks or external evidence before self-critique. |
| Multi-agent loop with overlapping edits | Assign ownership and integrate results in the coordinator. |
| One passing check as proof | Tie validation to the changed behavior and state remaining unvalidated areas. |

## Red Flags

- No stop condition.
- No attempt cap or stall threshold.
- No live-state observation step.
- No durable state for fresh recurring runs.
- No idempotency rule for repeated actions.
- No approval gate for destructive, broad, paid, or external side effects.
- No validation evidence before claiming success.

## Failure Counters

| Temptation | Counter |
| --- | --- |
| "Thread context is enough for a heartbeat." | Require each wake-up report to include phase, attempt count, last observation, next action, and stop status. |
| "A standalone automation can use this chat's context." | Put durable state in the prompt or a named external source. |
| "A bespoke prompt is faster than a contract." | Use the contract fields so different loop types converge on the same safety shape. |
| "Writing the prompt means the loop exists." | If the user asked for an actual recurring loop, call `automation_update`; a prompt alone does not loop. |
| "Retry until it works." | Add retryable/non-retryable errors, idempotency, backoff, max attempts, and escalation. |
| "Aggressive means unbounded." | Parallelize safe work, but cap cycles and stop on repeated no-progress. |
