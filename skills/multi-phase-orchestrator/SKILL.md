---
name: multi-phase-orchestrator
description: Beta, explicit-invocation-only orchestration for multiple work units through fresh Codex worktree threads, per-unit skill routing, monitored review or implementation loops, validation, safe integration, and branch or PR closeout. Use only when the user explicitly names $multi-phase-orchestrator or directly asks to use this skill.
---

# Multi-Phase Orchestrator (Beta)

Status: beta. Do not invoke this skill implicitly. Use it only when the user explicitly names `$multi-phase-orchestrator` or directly asks to use this skill.

Coordinate multiple work units by creating fresh Codex worktree threads, giving each thread a narrow packet, monitoring them, verifying their outputs, and integrating completed work safely. A work unit can be a plan phase, bug finding, PR comment, review finding, adversarial-gate slice, docs task, validation task, or integration fix.

This skill is an orchestration layer. It does not replace the skills or workflows used inside each unit; it routes them explicitly.

## Operating Model

Start from the work source the user gives. Do not invent a default source hierarchy. Valid sources include, but are not limited to:

- a user-provided plan
- a named review or bug-finding skill whose output should become work units
- a set of PR comments or review threads named by the user
- a list of phases, slices, milestones, or tasks
- a prior run the user explicitly names

If the user has not provided a source that can produce work units, ask for the source or ask whether to run a named discovery/review skill first.

Named skills and workflows are first-class routing requirements. If the user names `$bug-hunt-swarm`, `$codex-adversarial-gate`, `$review-workflows:triage-review-comments`, `$review-swarm`, `$autoreview`, or any other skill/tool, bind it to the relevant unit role and include it in the child thread packet with the skill name and path. Do not let a supporting skill replace the orchestrator's unit tracking, monitoring, and integration responsibilities.

## Skill Propagation Contract

Every delegated child prompt must carry the skills needed for that child to do its job. Do not assume the child inherits the parent thread's loaded skills.

Use one of these modes for each child:

- **Whole-skill delegation**: when the child must run a skill workflow itself, pass the exact skill invocation and path, such as `Use $skill-name at /path/to/skill-name/SKILL.md`. If the app/tool supports structured skill mentions, include the skill as a skill item as well as naming it in the prompt.
- **Role-slice delegation**: when the parent intentionally decomposes a workflow skill into separate child roles, pass the source skill name/path, the exact role name, and the role-specific instructions. Also say whether the child must not launch nested subagents because it is already one investigator/reviewer in the parent-run workflow.
- **No-skill delegation**: only use this when the unit truly needs no skill beyond repo instructions. State `Required skills: none` so the absence is deliberate.

For plan implementation units, always pass the plan-required skills through to the worktree thread. A child building a phase from a plan must see the same named implementation, testing, review, UI, or closeout skills that the user required for that phase or for the whole run.

## Core Rules

- Verify live repo state before creating worktree threads.
- Create fresh Codex worktree threads for new execution units. Do not resurrect old worktrees or old branches unless the user explicitly asks.
- Existing worktrees, branches, archives, and prior threads may be inspected as evidence only.
- Reuse only active child threads created by the current orchestration run, such as after context compaction or interruption.
- Keep the target checkout clean until completed units are ready to integrate.
- Give each child thread a narrow ownership scope and explicit required skills/workflows.
- Tell every child thread that other agents may be working in parallel and it must not revert or overwrite their work.
- Treat child-thread summaries, review verdicts, and evidence packets as claims until checked against live files, diffs, logs, tests, and records.
- Verify every finding before fixing it.
- Fix narrowly; reject speculative, duplicate, stale, or out-of-scope findings.
- Do not mark a unit complete until its configured review/gate is satisfied, validation is current, required records exist, required commits are made, and integration status is known.
- Integrate completed unit outputs deliberately, one unit at a time or by scoped file checkout when that is safer than merge commits.
- Confirm all accepted worktree-thread fixes are present on the target branch before pushing, opening a PR, or claiming closeout.

## Step 1: Bind Source, Skills, And Roles

Before dispatching work, state the run binding:

- **Work source**: where units come from, exactly as the user supplied or approved.
- **Discovery/review skill**: optional skill used to produce candidate units, such as a bug review or PR-comment triage workflow.
- **Implementation skill**: optional skill each worker must use to build or fix its assigned unit.
- **Review or gate skill**: per-unit review, critic, adversarial gate, or triage workflow.
- **Validation route**: repo tests, builds, scripts, UI checks, manual proof, or other checks.
- **Integration route**: merge, cherry-pick, scoped checkout, patch application, or manual consolidation.
- **Closeout route**: commits, docs, archives, learning notes, PR replies, or branch/PR actions.

Explicit user-named skills and workflows win. Additional repo-required skills are additive.

## Step 2: Derive Work Units

Turn the approved source into concrete work units.

If the source is a plan, split by plan phase or milestone. If the source is a bug-review skill, run that skill first, verify or triage its output as required, and turn accepted findings into units. If the source is PR feedback, use the named PR-review workflow and make each verified actionable thread or related cluster a unit.

Create and maintain this matrix:

| Unit | Source Ref | Status | Required Skills | Child Thread | Worktree | Branch | Scope | Review/Gate | Findings/Fixes | Validation | Evidence/Records | Commit | Integrated |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Use statuses that show actual state, such as `planned`, `discovery`, `queued`, `running`, `needs_steer`, `review_failed`, `fixing`, `validated`, `committed`, `ready_to_integrate`, `integrated`, `blocked`, or `done`.

For each unit, record:

- source reference and acceptance criteria
- required skills/workflows for that unit
- allowed write scope
- dependencies and ordering constraints
- whether it can run in parallel
- likely validation commands
- review, critic, adversarial gate, or triage requirements
- required docs, archives, state files, commits, PR replies, or closeout records

Do not dispatch child threads until each initial unit has enough scope, routing, and validation detail to work independently.

## Step 3: Create Fresh Worktree Threads

Create one fresh Codex worktree thread per runnable unit when edits may conflict, units can run concurrently, or unit commits should stay separate.

Do not reuse old worktrees. If a same-purpose old worktree exists, inspect it only for evidence, then create a fresh worktree thread from the intended base/current branch unless the user explicitly asks to continue that old worktree.

Prefer branch names like:

```text
codex/<topic>-<unit>-<shortid>
```

Before creating child threads:

- verify the target branch is not the default branch unless explicitly allowed
- verify target checkout dirty state and preserve unrelated work
- decide whether each unit starts from the target branch, a named base branch, or a specific approved commit
- use repo-provided worktree setup scripts when present
- copy only approved ignored local state
- avoid destructive git commands unless explicitly requested

If the target checkout is dirty in a way that blocks safe orchestration, create a dedicated integration worktree or report the blocker.

## Step 4: Send Child Thread Packets

Each child thread prompt must include:

- unit name and source reference
- required skills/workflows to load and use, including skill names and paths when available
- skill propagation mode: whole-skill, role-slice, or no-skill
- worktree/thread purpose
- base branch or starting state
- acceptance criteria
- allowed write scope
- dependencies and ordering constraints
- files and docs to inspect
- validation commands or how to discover them
- required review, adversarial gate, critic, triage, evidence, or archive records
- commit requirements
- closeout/reporting requirements
- instruction not to revert, overwrite, or clean other agents' work

When a child thread must use a skill, say that explicitly in the child prompt, for example:

```text
Use $bug-hunt-swarm at ${CODEX_HOME:-$HOME/.codex}/skills/bug-hunt-swarm/SKILL.md for read-only diagnosis before proposing fixes.
Use $codex-adversarial-gate at ${CODEX_HOME:-$HOME/.codex}/skills/codex-adversarial-gate/SKILL.md for this unit's completion reviewer and critic.
Use $review-workflows:triage-review-comments at <resolved-skill-path> to verify PR feedback before implementing.
```

When a child is only one role inside a parent-run skill, say that explicitly instead of pretending it is running the whole skill:

```text
Role source: $bug-hunt-swarm at ${CODEX_HOME:-$HOME/.codex}/skills/bug-hunt-swarm/SKILL.md.
Role: Reproduction and Scope Investigation.
Do not launch nested subagents; you are one of the swarm investigators.
Follow the role instructions below.
```

Each child thread should:

1. inspect live repo state inside its fresh worktree;
2. load required skills/workflows;
3. implement, review, diagnose, or validate only its unit;
4. build a compact evidence packet;
5. run configured unit review/gate;
6. fix verified findings narrowly;
7. rerun required review/gate when needed;
8. run validation;
9. update required records;
10. commit if required;
11. report changed files, commit hash, validation, records, and unresolved risks.

## Step 5: Monitor Child Threads

Track child threads actively enough to prevent drift:

- child thread status and latest summary
- worktree dirty files, staged files, untracked files, branch, and commit
- overlapping changed files between units
- edits outside assigned scope
- missing required skills or skipped workflow steps
- failed validation
- reviewer/critic disagreement or unresolved triage
- stale evidence packets
- dirty worktrees after claimed commits
- units marked complete without required record paths
- source-dependent docs or shared files being edited in multiple worktrees

Active monitoring is required. The coordinator should keep reading child status, checking worktree dirt, comparing changed-file sets, updating the matrix, and sending scoped follow-up prompts when direction is useful.

Allowed non-blocking parent actions include:

- ask a child for a concise status or exact blocker
- remind a child to use a required skill or branch/commit discipline
- narrow scope when a child is drifting
- clarify acceptance criteria, evidence requirements, or validation commands
- route around file overlap before conflicts grow
- pause integration of one unit while other units keep running
- continue independent parent-side checks that do not compete with child validation or mutate child worktrees

Wait for child threads to finish their current validation, review, gate, build, test, or commit step unless there is a legitimate coordination issue. Long-running tests, quiet review calls, Xcode/build output gaps, and slow subagents are normal waiting states, not reasons to interrupt or take over.

Legitimate intervention reasons include:

- explicit blocker or request for owner decision
- edits outside assigned scope
- overlapping files that would create integration conflict
- missing required skill usage or skipped workflow step
- wrong branch, old worktree reuse, detached-HEAD commit risk, or dirty worktree after claimed commit
- failed validation that needs parent routing
- reviewer/critic disagreement that the child cannot resolve
- claimed completion without visible commit, archive, evidence, or validation record
- repeated identical failure or retry loop
- no observable progress beyond the agreed wait window and no running validation/review process to wait on

Send steering prompts when they help the child proceed correctly or prevent drift. Keep prompts narrow and compatible with the child continuing its work. Prefer one precise status nudge before taking over work.

If a child stalls at a gate boundary, the coordinator may finish that exact review or critic step only when the source artifact is frozen, prior dissent is preserved, and the required output can be archived or recorded without changing the unit source.

## Step 6: Integrate Completed Units

Integrate only units that are reviewed/gated, validated, and committed or otherwise frozen according to the run binding.

Use the safest integration method for the run:

- merge or cherry-pick unit commits when commit history should be preserved
- scoped file checkout when worker branches contain useful files but shared churn must be consolidated
- manual patch application when a worker produced a verified fix without a clean commit
- primary-branch consolidation for shared docs or state files

For shared closeout files such as build-state docs, status trackers, aggregate reports, or changelogs, prefer one consolidated update on the target branch instead of accepting conflicting copies from every worker.

After each unit integration:

- verify the expected files and fixes are present
- keep unrelated target-branch changes out
- resolve conflicts minimally
- update the matrix

Answer explicitly whether accepted worktree-thread fixes are now present on the local target branch.

## Step 7: Validate And Review Integrated Work

After integration, run the configured combined validation and review:

- focused tests for changed behavior
- broader build/test lanes required by the repo
- diff hygiene checks
- private-path, generated-artifact, and secret scans
- integrated diff review when requested or required
- behavior-change review when executable behavior changed

For every integrated-review finding:

- verify legitimacy against live code and the user-approved source;
- reject speculative, duplicate, stale, or out-of-scope findings;
- fix legitimate findings narrowly;
- validate the fix;
- rerun relevant review or validation if behavior changed;
- commit follow-up fixes normally unless the user explicitly asks to amend.

## Step 8: Push Or PR

Before pushing or opening/updating a PR:

- verify the worktree is clean;
- verify the target branch contains every accepted unit result;
- verify validation results are current;
- verify required reviews, gates, triage, and integrated-review findings are handled;
- prepare PR or update text from actual changes, tests, risks, and skipped checks.

Use the repo's required PR tooling. Reply inline to review comments when applicable. Do not resolve review threads unless asked.

## Step 9: Cleanup Completed Threads And Worktrees

After integration, validation, required review, and push/PR closeout are complete, clean up orchestration resources. Do not clean up before proving that the target branch contains the accepted work.

Before archiving a child thread:

- record its thread ID, unit name, branch, final status, commit hash, and evidence/validation paths in the matrix or final report;
- verify it is complete, blocked, or intentionally closed;
- verify no needed result exists only in the thread summary without being recorded elsewhere.

Archive completed or intentionally closed child threads using the Codex thread archive tool when available. Leave active, blocked, or user-requested follow-up threads unarchived and report why.

Before removing a worktree:

- verify the target branch contains that unit's accepted files, fixes, docs, archives, and records;
- verify the unit branch commit is integrated, cherry-picked, superseded by a consolidated commit, or otherwise no longer the only copy of the work;
- verify the worktree has no uncommitted or untracked required files;
- verify shared closeout files were consolidated on the target branch;
- verify any PR replies, archives, or evidence paths needed for audit are present outside the worktree;
- run a final `git status --short --branch` for the worktree and target branch.

Remove only worktrees that pass those checks. Do not delete phase branches unless the user explicitly asks for branch deletion. If a worktree is dirty, contains unintegrated commits, contains unique evidence, or cannot be verified, keep it and report the blocker.

## Final Report

Report:

- work source and target branch
- PR URL, if any
- orchestration matrix with final statuses
- child thread IDs and unit branches
- unit commits or integration method
- required skill/workflow usage per unit
- review, gate, triage, and evidence record paths
- validation commands and results
- integrated-review findings accepted or rejected
- cleanup performed: archived threads, removed worktrees, retained worktrees, and reasons
- skipped checks and reasons
- remaining risks or blockers
