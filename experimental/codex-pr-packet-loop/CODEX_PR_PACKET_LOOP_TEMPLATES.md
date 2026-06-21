# Codex PR Packet Loop — Templates and Seed Prompts

These are starting templates. They are intentionally flexible so they can be refined with Codex instead of becoming a strict framework too early.

---

## 1. Suggested `AGENTS.md` section

Add this to the repo `AGENTS.md`, or adapt it into the existing file.

```md
## Codex PR Packet Loop

Do not implement large plans directly unless explicitly told to.

For medium or large work:
1. Create or update a PR packet queue first.
2. Slice large work into small PR packets.
3. Keep implementation threads focused on one packet only.
4. Track active work in `docs/codex/LOOP_STATE.md`.
5. Track planned work in `docs/codex/PR_QUEUE.md`.

### Worker thread rules

When assigned a packet:
- Work only on that packet.
- Do not implement adjacent packets.
- Do not perform broad opportunistic refactors.
- Prefer a small, reviewable diff.
- Stop if the work expands beyond the packet scope.
- Stop if you need to touch files reserved by another active packet.
- Run the validation command listed in the packet.
- Fix only failures caused by this packet.
- Open one PR for the packet.

### Orchestrator rules

When coordinating packets:
- Identify dependencies before dispatching work.
- Identify file, area, interface, test, and generated-file overlap.
- Prefer parallel work only where overlap risk is low.
- Merge serially until the workflow is proven.
- Update queue/state files after each merge.
- Reslice work that becomes too broad.

### PR description style

Use:

## Summary

## Mechanism
| Area | Change |
|---|---|

## Design decisions

## Verification

## Risks and review notes

## Follow-up work
```

---

## 2. `docs/codex/PR_QUEUE.md` template

```md
# PR Queue

## Purpose

This file is the source of truth for planned PR packets.

Statuses:

- candidate
- ready
- reserved
- in-progress
- pr-open
- reviewing
- needs-fix
- blocked
- needs-reslice
- merged
- rejected

---

## Current execution notes

- Current target branch:
- Current integration branch, if any:
- Current active packet limit:
- Current merge mode: serial / integration-branch / stacked

---

## Packet 001 — [short title]

Status: candidate  
Risk: low / medium / high  
Parallel-safe: yes / no / maybe  
Depends on: none  
Suggested branch: `agent/pr-001-short-title`  
PR:  

### Goal

### Why this matters

### Allowed files / areas

### Expected touched files / areas

### Areas to avoid

### Out of scope

### Validation command

```bash
# command here
```

### Notes for delegate

### Notes for orchestrator

### Merge notes
```

---

## 3. `docs/codex/LOOP_STATE.md` template

```md
# Codex Loop State

## Current objective

## Current mode

- Planning / slicing / dispatching / reviewing / merging / paused

## Active packet limit

## Active work

| Packet | Branch | Worktree/thread | Status | PR | Validation | Notes |
|---|---|---|---|---|---|---|

## Blocked work

| Packet | Reason | Needed decision |
|---|---|---|

## Recently merged

| Packet | PR | Merge notes | Follow-up needed |
|---|---|---|---|

## Open PRs needing review

| Packet | PR | Risk | Review focus |
|---|---|---|---|

## Packets affected by recent merges

| Packet | Why affected | Recommended action |
|---|---|---|

## Next recommended packets

| Packet | Why next | Parallel-safe | Notes |
|---|---|---|---|

## Repeated agent mistakes

## Decisions made

## Questions for human
```

---

## 4. `docs/codex/OWNERSHIP_MAP.md` template

```md
# Ownership Map

## Purpose

This file tracks temporary file/area reservations while PR packets are active.

Reservations are soft coordination signals. They are not permanent ownership rules.

---

## Active reservations

| Area / file | Packet | Branch | Type | Expires when | Notes |
|---|---|---|---|---|---|

---

## High-conflict areas

| Area / file | Why high-conflict | Default handling |
|---|---|---|
| `package.json` | Dependency changes can collide | Serialize |
| Lockfiles | Generated/dependency output | Serialize |
| Generated API clients | Regeneration churn | Serialize |
| Central app state files | Behavioural assumptions | Human review |

---

## Released reservations

| Area / file | Packet | Released because | Date |
|---|---|---|---|
```

---

## 5. `docs/codex/MERGE_LOG.md` template

```md
# Merge Log

## Purpose

This file records integration decisions and conflict handling.

---

## Merge entries

### [date/time] Packet 001 — [title]

PR:
Branch:
Merged into:
Validation:

#### Merge decision

#### Conflicts or overlap

#### Packets affected

#### Follow-up created

#### Notes
```

---

## 6. Planning prompt

Use this when starting from a broad feature or Compound Engineering-style plan.

```text
Repo:
[repo name]

Model:
Use the strongest Codex reasoning model available for planning.

Task:
Create a high-level engineering plan for the work below.

Important:
- Do not implement anything.
- Think broadly enough to identify architecture, dependencies, risks, and validation strategy.
- Do not convert this into implementation yet.
- End by identifying which parts should later be sliced into small PR packets.

Work:
[paste feature / bug / project goal]

Output:
- Goal
- Current repo assumptions to inspect
- Proposed approach
- Major components affected
- Risks
- Validation strategy
- Natural PR boundaries
- Questions / decisions needed
```

---

## 7. Slicer prompt

Use this after the plan exists.

```text
Repo:
[repo name]

Model:
Use the strongest Codex reasoning model available for planning/slicing.

Task:
Convert the plan into a PR packet queue.

Read:
- AGENTS.md
- docs/codex/PR_QUEUE.md if it exists
- docs/codex/LOOP_STATE.md if it exists

Instructions:
- Do not implement anything.
- Create small PR packets.
- Mark dependencies.
- Mark parallel-safe packets.
- Mark risky packets.
- Mark packets likely to overlap by file, area, interface, tests, generated files, or behaviour.
- Suggest expected touched files/areas for each packet.
- Suggest validation commands.
- Keep the queue useful and flexible; do not over-constrain implementation.

Output/update:
- docs/codex/PR_QUEUE.md
- docs/codex/LOOP_STATE.md summary section

Also output:
- Recommended execution order
- Suggested first parallel batch
- Human-review-first packets
- Packets that need reslicing before implementation
```

---

## 8. Orchestrator dispatch prompt

Use this when choosing what to run next.

```text
Repo:
[repo name]

Model:
Use the strongest Codex reasoning model available for orchestration.

Task:
Act as the main orchestrator for the Codex PR Packet Loop.

Read:
- AGENTS.md
- docs/codex/PR_QUEUE.md
- docs/codex/LOOP_STATE.md
- docs/codex/OWNERSHIP_MAP.md if present
- Recent branches/PRs if available

Instructions:
- Do not implement source code.
- Identify ready packets.
- Build a simple dependency and collision view.
- Identify which packets can run in parallel.
- Reserve expected files/areas for the next batch.
- Generate one delegate prompt per selected packet.
- Keep merge risk visible.

Output/update:
- docs/codex/LOOP_STATE.md
- docs/codex/OWNERSHIP_MAP.md if present

Final output:
- Selected packets
- Why they are safe to run now
- Packets deliberately not selected
- Collision/overlap notes
- Delegate prompts
```

---

## 9. Delegate worker prompt

Use this in a new Codex task/worktree for one packet.

```text
Start a new Codex task/thread.

Repo:
[repo name]

Branch/worktree:
Use or create branch: [branch name]

Model:
Use the appropriate Codex model for implementation. Use stronger reasoning if this packet is medium/high risk.

Task:
Work only on PR packet [ID] from docs/codex/PR_QUEUE.md.

Before changing code:
- Read AGENTS.md.
- Read docs/codex/PR_QUEUE.md.
- Read docs/codex/LOOP_STATE.md.
- Read docs/codex/OWNERSHIP_MAP.md if present.
- Confirm the packet goal, allowed files, expected touched areas, out-of-scope items, dependencies, and validation command.

Implementation loop:
1. Inspect only relevant files.
2. Make the smallest change that completes this packet.
3. Run the packet validation command.
4. If validation fails, fix only failures caused by this packet.
5. Repeat validation/fix only a small number of times.
6. If still failing, stop and document the blocker.

Stop and report instead of expanding scope if:
- You need to touch reserved files/areas.
- You need to modify more areas than expected.
- The packet depends on unmerged work.
- The task becomes a broad refactor.
- The validation failure is unrelated to this packet.

Deliverable:
- Open one PR for this packet only.
- Use the repo PR description style.
- Update docs/codex/LOOP_STATE.md with branch, status, validation result, PR, blockers, and risks.

Do not:
- Implement adjacent packets.
- Refactor unrelated code.
- Change public behaviour unless the packet explicitly requires it.
- Merge the PR.
```

---

## 10. PR review prompt/comment

Use on the PR.

```text
@codex review

Review this PR against its packet in docs/codex/PR_QUEUE.md.
Focus on:
- correctness
- scope creep
- CI/test risk
- merge overlap with other active packets
- serious issues only
```

If fixes are needed:

```text
@codex fix only the P1/CI issues identified in review.
Do not refactor unrelated code.
Do not implement adjacent packet work.
Keep the fix minimal and update the PR notes if risk changed.
```

---

## 11. Merge orchestrator prompt

Use this when PRs are ready and need sequencing.

```text
Repo:
[repo name]

Model:
Use the strongest Codex reasoning model available for merge orchestration.

Task:
Act as the merge orchestrator for the Codex PR Packet Loop.

Read:
- AGENTS.md
- docs/codex/PR_QUEUE.md
- docs/codex/LOOP_STATE.md
- docs/codex/OWNERSHIP_MAP.md if present
- Open PRs and their changed files if available
- CI/review status if available

Instructions:
- Do not merge automatically unless explicitly asked.
- Recommend a safe merge order.
- Identify file overlap, interface overlap, behaviour overlap, test overlap, and generated-file overlap.
- Identify PRs that need refresh/rebase before merge.
- Identify PRs that should be blocked or resliced.
- Prefer serial merges until the loop is proven.

Output:
- Recommended merge order
- Why this order is safe
- PRs not safe to merge yet
- Required refresh/fix actions
- State updates needed after merge
```

---

## 12. Branch refresh/fix prompt

Use when a PR goes stale after another packet merges.

```text
Repo:
[repo name]

Branch:
[branch name]

Task:
Refresh this PR branch against the latest target branch.

Scope:
- Resolve only conflicts caused by packet [ID].
- Do not add new behaviour.
- Do not refactor unrelated code.
- Keep the PR aligned with the original packet.

Validation:
Run the original packet validation command.

Output:
- What changed during refresh
- Whether validation passed
- Any remaining conflict/overlap risk
- Update docs/codex/LOOP_STATE.md
```

---

## 13. Queue maintenance prompt

Use this manually or as a future automation.

```text
Repo:
[repo name]

Task:
Maintain the Codex PR Packet Loop state.

Read:
- docs/codex/PR_QUEUE.md
- docs/codex/LOOP_STATE.md
- docs/codex/OWNERSHIP_MAP.md if present
- docs/codex/MERGE_LOG.md if present
- Recent merged PRs if available

Instructions:
- Do not change source code.
- Mark merged packets as merged.
- Release stale reservations.
- Mark blocked packets.
- Identify packets affected by recent merges.
- Reslice packets that are now too broad or stale.
- Recommend the next safe batch.

Output/update:
- docs/codex/PR_QUEUE.md
- docs/codex/LOOP_STATE.md
- docs/codex/OWNERSHIP_MAP.md if present
- docs/codex/MERGE_LOG.md if needed
```

---

## 14. Minimal first experiment

Use this to test the loop without overbuilding it.

```text
Goal:
Run a small trial of the Codex PR Packet Loop.

Limits:
- 3 packets only.
- 3 separate worktrees/threads.
- Low-risk work only.
- Serial merge only.
- Human merge required.
- State tracked in PR_QUEUE.md and LOOP_STATE.md.

Success criteria:
- Each packet opens a small PR.
- No worker implements adjacent packet work.
- Merge order is clear.
- State files remain useful.
- Any conflict is captured and fed back into the workflow.
```
