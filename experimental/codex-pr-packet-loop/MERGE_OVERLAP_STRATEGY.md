# Merge Overlap Strategy for Codex PR Packet Loop

## Why this exists

Parallel Codex worktrees are useful only if merged safely.

The main risk is that multiple delegate threads may touch related files, shared interfaces, shared tests, generated files, or user flows. Some of these conflicts will be caught by Git. Others will not.

This document describes a flexible strategy for detecting and handling overlap before it becomes a painful merge problem.

---

## Types of overlap

### 1. File overlap

Two packets edit the same file.

Example:

```text
Packet 003 edits src/api/client.ts
Packet 007 edits src/api/client.ts
```

This is the easiest to detect.

---

### 2. Area overlap

Two packets edit different files in the same subsystem.

Example:

```text
Packet 003 edits auth service logic
Packet 007 edits auth error handling
```

Git may not conflict, but the behaviour may.

---

### 3. Interface overlap

One packet changes a function/type/API that another packet uses.

Example:

```text
Packet 002 changes createSession() return shape
Packet 006 adds tests using the old createSession() return shape
```

This can create broken assumptions without obvious merge conflicts.

---

### 4. Behaviour overlap

Two packets change the same user-visible behaviour through different code paths.

Example:

```text
Packet 004 changes empty-state rendering
Packet 009 changes loading-state rendering in the same component flow
```

This needs human or orchestrator judgement.

---

### 5. Test overlap

Two packets update the same tests or test assumptions.

Example:

```text
Packet 005 adds new validation tests
Packet 008 rewrites the same test fixture
```

This can cause noisy PR churn even when implementation is fine.

---

### 6. Generated/dependency overlap

Two packets touch generated files, lockfiles, package manifests, schemas, generated clients, or build artifacts.

Example:

```text
Packet 010 updates package.json
Packet 011 updates package-lock.json
Packet 012 regenerates API types
```

This should usually be serialized.

---

## Orchestrator responsibilities

The orchestrator should maintain a view of:

- Expected touched files/areas for each packet.
- Actual touched files after each PR opens.
- Active branches and worktrees.
- Packet dependencies.
- Potential collisions.
- Merge order.
- Packets that need rebasing or reslicing.

The orchestrator should be allowed to pause or reject a packet if it becomes broader than expected.

---

## Pre-dispatch checks

Before starting a batch of delegate worktrees, the orchestrator should answer:

1. Which packets are ready?
2. Which packets depend on unmerged work?
3. Which packets touch the same files?
4. Which packets touch the same subsystem?
5. Which packets might change the same interface?
6. Which packets touch generated files or lockfiles?
7. Which packets are high-risk?
8. Which packets are safe to run in parallel?
9. Which packet should merge first?
10. Which packet should wait?

---

## Soft reservations

Use soft reservations to coordinate parallel work.

A reservation is not a permanent ownership rule. It is a temporary signal that an active packet expects to edit an area.

Example:

```md
| Area / file | Packet | Branch | Reservation type | Notes |
|---|---|---|---|---|
| `src/auth/*` | 004 | `agent/pr-004-auth-errors` | area | Avoid parallel auth work. |
| `package-lock.json` | 006 | `agent/pr-006-upgrade-router` | generated/lockfile | Serialize package changes. |
```

If a delegate needs a reserved file or area, it should stop and report:

```text
This packet appears to overlap with active packet 004 because it needs to edit src/auth/session.ts. Recommend reslicing or sequencing after packet 004 merges.
```

---

## Collision matrix

The orchestrator can create a collision matrix before dispatching work.

Example:

```md
| Packet | Expected areas | Collides with | Collision type | Decision |
|---|---|---|---|---|
| 001 | docs/codex/* | none | none | parallel-safe |
| 002 | src/auth/session.ts | 004 | file/area | run before 004 |
| 003 | tests/ui/loading.test.ts | none | none | parallel-safe |
| 004 | src/auth/errors.ts, src/auth/session.ts | 002 | area/interface | wait |
| 005 | package.json, lockfile | any dependency work | generated/lockfile | serialize |
```

The matrix does not need to be perfect. It exists to avoid obvious bad parallel batches.

---

## Merge sequencing rules

Use these as guidelines, not hard laws.

### Merge first

- Documentation-only packets.
- Tests that do not depend on unmerged implementation.
- Foundation changes needed by later packets.
- Small bug fixes with low overlap.
- Pure type/helper extractions with clear boundaries.

### Merge later

- Packets depending on foundation changes.
- UI wiring that depends on backend or state changes.
- Packets touching shared interfaces.
- Packets touching generated clients or lockfiles.
- Packets with higher risk.

### Avoid merging in parallel

- Multiple dependency updates.
- Multiple schema/API generated-file changes.
- Multiple broad state-management changes.
- Multiple packets touching the same central component/service.

---

## Recommended starting merge mode

Start with serial merges to main.

```text
1. Pick one completed PR.
2. Update/rebase it against latest main.
3. Run validation.
4. Merge.
5. Update queue/state.
6. Re-check remaining PRs against latest main.
7. Repeat.
```

This is slower than full automation, but safer while learning the workflow.

---

## Integration branch mode

Use an integration branch when a set of PRs are related and should be validated together.

```text
main
  ↓
integration/batch-001
  ↓
merge packet 001
  ↓
merge packet 002
  ↓
merge packet 003
  ↓
run broader validation
  ↓
merge integration/batch-001 to main
```

Good for:

- Related vertical slices.
- Small dependent groups.
- Refactor plus tests.
- Backend contract plus UI usage.

Avoid using it for unrelated random PRs, because it can hide which packet caused breakage.

---

## Stacked PR mode

Use stacked PRs when packets have clear dependencies.

Example:

```text
001-foundation-types
  ↓
002-service-uses-types
  ↓
003-ui-uses-service
  ↓
004-tests-and-docs
```

Good for:

- Foundation → usage flows.
- API contract → implementation → UI.
- Refactor preparation → behaviour change.

Risk:

- More branch maintenance.
- Harder review if the stack changes often.
- One broken base PR blocks the stack.

Use stacked PRs deliberately, not by default.

---

## What the orchestrator should do when overlap appears

### Case 1 — harmless overlap

Example: two docs packets touch different sections of the same docs folder.

Action:

```text
Allow, but merge serially.
```

---

### Case 2 — same file overlap

Action:

```text
Pause the later packet or rebase it after the first merges.
```

---

### Case 3 — interface overlap

Action:

```text
Merge the interface/foundation packet first, then refresh dependent packets.
```

---

### Case 4 — generated/lockfile overlap

Action:

```text
Serialize. Only one generated/dependency packet active at a time.
```

---

### Case 5 — logical/behaviour overlap

Action:

```text
Human review before merge. Consider reslicing into foundation + behaviour + tests.
```

---

### Case 6 — delegate expands scope

Action:

```text
Reject or send back for reslice. Do not merge broad unexpected changes just because they work.
```

---

## Merge decision checklist

Before merging a PR, the orchestrator should check:

```md
- [ ] Does this PR match the selected packet?
- [ ] Did it touch only expected files/areas?
- [ ] Did validation pass?
- [ ] Did Codex review find serious issues?
- [ ] Did CI pass?
- [ ] Does it overlap with another open PR?
- [ ] Should another PR merge first?
- [ ] Does this change invalidate assumptions in active packets?
- [ ] Does LOOP_STATE.md need updating?
- [ ] Does PR_QUEUE.md need status/dependency changes?
```

---

## Merge conflict handling loop

If a PR conflicts or becomes stale:

```text
1. Mark packet as needs-refresh or needs-fix.
2. Assign the same delegate thread or a new fix thread.
3. Scope the fix to rebase/conflict resolution only.
4. Run validation again.
5. Return to review.
```

Prompt shape:

```text
This PR is stale or conflicted after another packet merged.
Refresh this branch against the latest target branch.
Resolve only conflicts caused by packet [ID].
Do not add new behaviour.
Run the original validation command.
Update LOOP_STATE.md with the result.
```

---

## State updates after merge

After every merge:

Update `PR_QUEUE.md`:

```text
Packet status: merged
Merged PR: link/reference
Merged at: date/time
Follow-up packets created: yes/no
```

Update `LOOP_STATE.md`:

```text
Remove branch from active work.
Record validation result.
Record merge notes.
Flag open packets affected by the merge.
Recommend next safe packets.
```

Update `OWNERSHIP_MAP.md`:

```text
Release reservations for merged/abandoned branches.
Add new temporary reservations if follow-up packets are created.
```

Update `MERGE_LOG.md`:

```text
Record merge order, conflict notes, and any manual decisions.
```

---

## The safest early rule

Until the workflow is proven:

```text
Parallel implementation is allowed.
Parallel merging is not.
```

That means multiple Codex worktrees can build PRs at the same time, but the orchestrator merges them one at a time with state updates between merges.
