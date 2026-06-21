# Codex PR Packet Loop — Flexible Operating Plan

## Purpose

This document describes the workflow I want to build around Codex:

```text
Plan
  ↓
Plan sliced into PR packets
  ↓
Main orchestrator chooses safe packets
  ↓
Delegate Codex tasks/worktree threads implement packets
  ↓
Each delegate loops: implement → validate → fix → open PR
  ↓
Codex review + CI + human review
  ↓
Main orchestrator resolves merge order and overlap risk
  ↓
Merged work updates PR_QUEUE.md + LOOP_STATE.md
```

The goal is **not** to create a rigid process. The goal is to create a repeatable loop that lets agents ship smaller PRs safely, while keeping the main orchestrator responsible for coordination, dependencies, overlap risk, and final integration.

---

## What I want this workflow to achieve

- Turn large engineering plans into many small, mergeable PR packets.
- Run multiple Codex tasks/worktrees in parallel without creating chaos.
- Keep each worker thread focused on one packet only.
- Make validation and fix attempts repeatable.
- Avoid huge PRs that take too long to review.
- Make merge conflicts and overlapping work visible before they become painful.
- Keep a written state of what is active, blocked, merged, and safe to run next.
- Let the orchestrator decide when to merge, reslice, rebase, pause, or reject work.

---

## Core design principle

The system should treat Codex threads as **specialised workers**, not as one giant autonomous builder.

The main orchestrator owns:

- The plan.
- The PR queue.
- Packet dependencies.
- Worktree/thread dispatch.
- File/area ownership during a batch.
- Merge sequencing.
- Conflict handling.
- State updates.

Delegate worktree threads own:

- One packet.
- One branch/worktree.
- One validation loop.
- One PR.

---

## Roles

### 1. Planner

Creates the high-level engineering plan.

This can still be large and strategic. The planner is allowed to think broadly, compare options, and identify architecture direction.

The planner should not directly implement the whole plan.

---

### 2. Slicer

Converts the plan into small PR packets.

The slicer should identify:

- Small independent packets.
- Dependencies between packets.
- Which packets can run in parallel.
- Which packets are risky.
- Which packets should be human-reviewed before implementation.
- Which packets may overlap in files, interfaces, tests, or behaviour.

The slicer should aim for small PRs, but not become so restrictive that it blocks useful work.

---

### 3. Main Orchestrator

The orchestrator is the control plane.

It decides:

- Which packets are ready.
- Which packets should run now.
- Which packets should wait.
- Which packets can run in parallel.
- Which files/areas are temporarily reserved.
- Which PRs should merge first.
- Which branches need to rebase or refresh.
- Which packets need to be resliced.
- Which conflicts should be fixed by a delegate thread.

The orchestrator should not blindly merge every completed PR.

---

### 4. Delegate Worktree Thread

A delegate handles one PR packet.

The delegate should:

- Read the packet.
- Confirm the goal, allowed scope, validation command, and out-of-scope items.
- Implement the smallest change that completes the packet.
- Run validation.
- Fix only failures caused by the packet.
- Stop after a small number of failed fix attempts.
- Open one PR.
- Report any required reslicing or unexpected overlap.

The delegate should not implement adjacent packets.

---

### 5. Reviewer

The reviewer checks whether a PR is safe and useful.

Review can include:

- Codex PR review.
- CI output.
- Human review.
- Scope check against the packet.
- Diff-size check.
- Risk check.
- Follow-up packet suggestions.

---

### 6. Integrator

The integrator resolves the merge queue.

This may be the same Codex orchestrator thread, but conceptually it is a separate responsibility.

The integrator should:

- Merge one branch at a time.
- Re-check the branch against the latest target.
- Detect file and behavioural overlap.
- Push conflicted PRs back to a delegate fix thread.
- Update state files after each merge.
- Avoid merging multiple overlapping PRs at once.

---

## Suggested repo artifacts

These files are suggested starting points. Codex can brainstorm better names or merge some of them if the repo should stay simpler.

| File | Purpose |
|---|---|
| `docs/codex/PR_QUEUE.md` | Source of truth for planned packets and status. |
| `docs/codex/LOOP_STATE.md` | Current active work, branches, PRs, blockers, and next recommendations. |
| `docs/codex/OWNERSHIP_MAP.md` | Soft file/area reservations to reduce merge overlap. |
| `docs/codex/MERGE_LOG.md` | History of merge decisions, conflict resolutions, and rejected PRs. |
| `docs/codex/PACKET_TEMPLATE.md` | Template for each PR packet. |
| `.codex/skills/pr-packet-factory/SKILL.md` | Optional reusable slicer/orchestrator skill. |
| `AGENTS.md` | Repo-level rules for Codex and other coding agents. |

The minimum viable setup is probably:

```text
docs/codex/PR_QUEUE.md
docs/codex/LOOP_STATE.md
AGENTS.md
```

`OWNERSHIP_MAP.md` and `MERGE_LOG.md` can be added once parallel work starts creating real overlap.

---

## PR packet lifecycle

Suggested statuses:

```text
candidate
ready
reserved
in-progress
pr-open
reviewing
needs-fix
blocked
needs-reslice
merged
rejected
```

Suggested lifecycle:

```text
candidate
  ↓
ready
  ↓
reserved
  ↓
in-progress
  ↓
pr-open
  ↓
reviewing
  ↓
needs-fix OR merged OR blocked
```

---

## Packet shape

Each packet should include enough information for a delegate to work independently, but not so much that it becomes over-specified.

Suggested fields:

```md
## Packet ID

## Title

## Goal

## Why this matters

## Allowed files / areas

## Expected touched files / areas

## Areas to avoid

## Out of scope

## Dependencies

## Parallel-safe
Yes / No / Maybe

## Risk level
Low / Medium / High

## Validation command

## Suggested branch name

## Notes for delegate

## Notes for orchestrator
```

---

## Slicing guidance

A good packet is usually:

- One clear behaviour, fix, test, doc update, or refactor.
- Easy to review without understanding the whole plan.
- Small enough that CI and diff review are fast.
- Independent from other active packets, or clearly sequenced.
- Honest about dependencies and overlap risk.

A packet is probably too large if it requires:

- Multiple unrelated behaviours.
- Broad architecture changes.
- A schema change plus UI wiring plus tests plus docs in one PR.
- Touching many unrelated modules.
- Fixing unrelated issues discovered during implementation.

The goal is not to force every PR below an arbitrary line count. The goal is to keep PRs small enough that review and merge decisions stay safe.

---

## Work types that are good for this loop

Good candidates:

- Small bug fixes.
- Tests for existing behaviour.
- Docs updates.
- Type fixes.
- Small UI states.
- Minor refactors with no behaviour change.
- API client wrapper improvements.
- Error handling improvements.
- Logging improvements.
- One narrow vertical slice behind an existing boundary.

Use more caution with:

- Database migrations.
- Auth/security changes.
- Large dependency upgrades.
- Public API changes.
- Broad state-management changes.
- Cross-cutting UI architecture.
- Generated files or lockfile-heavy work.
- Anything likely to touch the same core files as other active packets.

---

## Main orchestrator loop

The orchestrator loop should be explicit and stateful.

```text
1. Read PR_QUEUE.md and LOOP_STATE.md.
2. Identify ready packets.
3. Build a dependency and overlap view.
4. Choose a safe parallel batch.
5. Reserve expected files/areas for that batch.
6. Dispatch one delegate thread/worktree per packet.
7. Track active branches and PRs.
8. Review completed PRs.
9. Merge in a safe order.
10. Update PR_QUEUE.md, LOOP_STATE.md, and ownership reservations.
11. Reslice or block packets that became unsafe.
```

---

## Delegate worktree loop

Each delegate thread should run a bounded loop.

```text
1. Read AGENTS.md.
2. Read the selected packet.
3. Read LOOP_STATE.md for active reservations and blockers.
4. Inspect only relevant files.
5. Implement the smallest useful change.
6. Run validation.
7. If validation fails, fix only packet-related failures.
8. Repeat fix/validation a small number of times.
9. If still failing, stop and report blocker.
10. Open one PR.
11. Update LOOP_STATE.md with status, branch, validation result, PR, and risks.
```

Suggested stop conditions:

- The delegate needs to touch a file reserved by another active packet.
- The delegate needs to change more areas than expected.
- Validation fails repeatedly.
- The packet appears to depend on another unmerged packet.
- The change is becoming a bigger refactor than expected.
- The packet goal is ambiguous after inspecting the code.

---

## Merge overlap is the main risk

The riskiest part is not implementation. The riskiest part is integrating multiple parallel branches that may have touched related files, interfaces, tests, or behaviour.

The workflow should solve this by making overlap visible early.

The orchestrator should track:

- Expected touched files.
- Actual touched files.
- Shared interfaces.
- Shared tests.
- Shared generated files.
- Shared dependencies.
- Shared user flows.
- Whether one PR changes assumptions used by another PR.

The orchestrator should not rely only on Git merge conflicts. Two PRs can merge cleanly but still conflict logically.

---

## Merge strategy options

The system can experiment with one of these approaches.

### Option A — Serial merge to main

Simplest and safest.

```text
PR ready
  ↓
Update branch against main
  ↓
Run validation
  ↓
Merge
  ↓
Update queue
  ↓
Move to next PR
```

Best when starting out.

---

### Option B — Integration branch per batch

Useful when several PRs are intended to land together.

```text
main
  ↓
integration/batch-001
  ↓
merge candidate branches one by one
  ↓
run broader validation
  ↓
merge integration branch to main
```

Best when packets are related but need a combined validation pass.

---

### Option C — Stacked PRs

Useful when packets naturally depend on each other.

```text
packet 001
  ↓
packet 002 built on 001
  ↓
packet 003 built on 002
```

Best for foundation → dependent work.

This is more powerful but also more complicated.

---

## Preferred starting approach

Start with:

```text
Serial merge to main
+ soft ownership map
+ max 3 active worker threads
+ no automatic merging
```

Then evolve toward:

```text
parallel worktrees
+ batch-aware ownership map
+ integration branch for related packet groups
+ stacked PRs only where dependencies are clear
```

---

## Soft ownership map

A soft ownership map is not meant to block useful work forever. It is a coordination tool.

Example:

```md
# Ownership Map

## Active reservations

| Area / file | Packet | Branch | Type | Expires when | Notes |
|---|---|---|---|---|---|
| `src/auth/*` | 004 | `agent/pr-004-auth-errors` | expected | PR merged or abandoned | Avoid parallel auth changes. |
| `package-lock.json` | 006 | `agent/pr-006-dep-upgrade` | high-conflict | PR merged | Do not run other dependency updates. |
```

If a delegate discovers it needs a reserved area, it should stop and report the conflict rather than quietly expanding scope.

---

## Collision matrix

Before dispatching a batch, the orchestrator can build a simple matrix.

```md
| Packet | Expected areas | Potential collision | Decision |
|---|---|---|---|
| 001 | docs only | none | parallel-safe |
| 002 | auth service | overlaps 004 | sequence before 004 |
| 003 | UI loading state | none | parallel-safe |
| 004 | auth errors | overlaps 002 | wait for 002 |
```

This does not need to be perfect. It just needs to catch obvious overlap before parallel work begins.

---

## What should be automated first

Automate the low-risk parts first:

1. Plan slicing.
2. PR queue formatting.
3. Packet risk tagging.
4. Collision matrix generation.
5. Next-packet recommendations.
6. Delegate prompt generation.
7. PR review summaries.
8. Queue/state updates.

Avoid automating merge decisions until the workflow is proven.

---

## What should stay human-controlled at first

- Final merge to main.
- High-risk packet approval.
- Broad architecture choices.
- Conflict resolution strategy.
- Database migration sequencing.
- Public API changes.
- Security/auth changes.
- Large dependency upgrades.

---

## Practical starting limits

These are suggested defaults, not permanent rules.

```text
Active delegate threads: 3
High-risk packets in flight: 0 or 1
Merge mode: serial to main
Auto-merge: off
Required validation: packet-specific command
Fix loop: small bounded number of attempts
Human merge: yes
```

Scale up only when merges become boring.

---

## Success metrics

Track whether the loop improves real shipping, not just PR count.

Useful metrics:

- PRs opened per day.
- PRs merged per day.
- Average files changed per PR.
- Average review time.
- CI pass rate.
- Number of PRs needing reslice.
- Number of merge conflicts.
- Number of logical conflicts missed by Git.
- Number of rejected/noisy PRs.
- Number of times Codex touched out-of-scope files.

Good result:

```text
More small useful PRs
+ fewer giant diffs
+ lower review pain
+ fewer merge conflicts
+ clearer queue state
```

Bad result:

```text
More PRs
+ more noise
+ more conflicts
+ more manual cleanup
```

---

## Open questions for Codex brainstorming

Use these questions to refine the workflow with Codex.

1. Should the orchestrator live as a Codex thread, a skill, a repo script, or a combination?
2. Should `OWNERSHIP_MAP.md` be manually maintained at first or generated from PR diffs?
3. Should the orchestrator create worktrees directly, or should it only generate delegate prompts?
4. Should related packets merge through an integration branch?
5. When should stacked PRs be used instead of independent PRs?
6. How should the orchestrator detect logical conflicts, not just file conflicts?
7. What validation command should be mandatory for each packet type?
8. Should Codex update Linear/issues as part of the state loop?
9. Which packets are safe for cheaper/faster models, and which need the strongest model?
10. What should happen when a delegate opens a PR that is technically correct but too broad?

---

## One-sentence summary

I want a Codex workflow where a main orchestrator turns large plans into small PR packets, delegates packets to separate worktree threads, each thread loops through implementation and validation, and the orchestrator safely coordinates review, overlap detection, merge order, and state updates.
