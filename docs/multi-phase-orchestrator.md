# Multi-Phase Orchestrator (Beta)

This guide explains how to use the beta `multi-phase-orchestrator` skill to coordinate several related Codex work units through fresh worktree threads.

Use it when one task is too broad for a single linear thread, but still needs one coordinator to preserve scope, validation, and integration discipline.

## What This Skill Is

`multi-phase-orchestrator` is a coordination skill. It helps a parent Codex thread split an approved work source into smaller units, send those units to fresh child worktree threads, monitor the work, verify each result, and integrate completed units safely.

The skill does not replace the skills used inside the units. If a unit needs `$codex-adversarial-gate`, `$triage-review-comments`, `$bug-hunt-swarm`, `$autoreview`, or another workflow, the orchestrator must pass that skill into the child thread packet.

The parent thread remains responsible for:

- binding the source of work;
- deciding which units can run in parallel;
- making each child thread's scope clear;
- checking child outputs against live repo state;
- integrating only reviewed and validated results;
- reporting what was completed, skipped, blocked, or left risky.

## When To Use It

Use `multi-phase-orchestrator` when the task has multiple related units that can be isolated, tracked, and integrated deliberately.

Good fits include:

- a plan with several phases or milestones;
- a set of review findings that can become separate implementation units;
- PR feedback split into independent clusters;
- several repo maintenance tasks that need different validation lanes;
- a large change that should land as smaller reviewed slices;
- a recovery run where prior work exists, but every accepted result must be rechecked.

Do not use it for:

- one narrow edit;
- review-only triage where no child implementation is needed;
- a vague request with no work source;
- urgent linear debugging where child coordination would add overhead;
- tasks where the user has not approved broad orchestration, branch work, or worktree threads.

## Mental Model

The orchestrator follows this lifecycle:

```text
work source
  -> work units
  -> child thread packets
  -> active monitoring
  -> unit validation and review
  -> integration
  -> combined validation
  -> cleanup and final report
```

A child thread summary is not proof. Treat it as a claim until the parent has checked the live files, diffs, commits, tests, logs, archives, and evidence records.

## Before You Start

You need:

- the `multi-phase-orchestrator` skill installed;
- a clear work source, such as a plan, review findings, PR feedback, or a list of phases;
- a target repo and target branch;
- an understanding of the target checkout state;
- the required skills or workflows for each kind of unit;
- expected validation commands or a clear way for child threads to discover them;
- a closeout expectation, such as local commits, a PR, archived review evidence, or a final report.

Install the beta skill with:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill multi-phase-orchestrator
```

## Prepare A Good Request

Invoke the skill explicitly:

```text
Use $multi-phase-orchestrator to coordinate these work units with fresh worktree threads.
```

Give the parent thread enough information to avoid inventing a source or routing. A good request names:

- **Work source:** the plan, PR, review findings, issue list, or explicit task list.
- **Target branch:** the branch the final integrated work should land on.
- **Required skills:** any workflows that must be used inside units.
- **Allowed scope:** files, directories, or behavior each unit may touch.
- **Validation:** worker-allowed lightweight checks, coordinator-only checks, forbidden commands, manual checks, UI checks, or evidence required before integration.
- **Review gates:** adversarial review, PR review triage, code review, or other closeout requirements.
- **Integration preference:** merge, cherry-pick, scoped checkout, manual consolidation, or local commit only.
- **Closeout:** what to report, commit, archive, push, or leave unpushed.

Example request:

```text
Use $multi-phase-orchestrator to implement the approved plan in docs/plans/import-cleanup.md.

Target branch: codex/import-cleanup.
Required skills: use $codex-adversarial-gate for each implementation slice closeout.
Scope: importer code, importer tests, and docs/imports.md only.
Worker-allowed validation: git diff --check and focused metadata checks.
Coordinator-only validation: npm test -- imports and npm run typecheck.
Integration: keep one commit per completed slice, then integrate locally.
Closeout: report child thread IDs, commits, validation, review archive paths, cleanup outcomes, and any skipped checks.
```

## Run The Orchestration

### 1. Bind The Run

Start by stating the run binding. This prevents the coordinator from silently changing the job.

Include:

- work source;
- discovery or review skill, if any;
- implementation skill, if any;
- review or gate skill;
- validation route, including worker-allowed checks and coordinator-only checks;
- integration route;
- closeout route.

If the source is unclear, stop and ask for it before creating child threads.

### 2. Derive Work Units

Turn the source into concrete units. Each unit needs a small enough scope that a child thread can execute it without owning the whole project.

Track units in a matrix:

| Unit | Source Ref | Status | Required Skills | Child Thread | Worktree | Branch | Scope | Review/Gate | Validation | Commit | Integrated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Import parser tests | Plan section 2 | planned | `$codex-adversarial-gate` | pending | pending | pending | importer tests | required | Worker: `git diff --check`; coordinator: `npm test -- imports` | pending | no |

Use statuses that show actual state, such as `planned`, `running`, `needs_steer`, `validated`, `ready_to_integrate`, `integrated`, `blocked`, or `done`.

### 3. Create Child Threads

Create fresh Codex worktree threads for runnable units when edits may conflict, units can run concurrently, or unit commits should stay separate.

Before dispatching, check:

- the target checkout state;
- whether the target branch is appropriate;
- whether any dirty files are user work;
- whether units overlap in files or behavior;
- whether a repo-specific worktree setup script exists.

Do not resurrect old worktrees unless the user explicitly asks. Old branches and threads can be evidence, but they should not become the default execution surface.

### 4. Send Complete Child Packets

Each child thread packet should start with a durable work-unit brief, then include enough operational context for the child to work independently and narrowly.

Include:

| Packet Field | Purpose |
|---|---|
| Work unit brief | States category, summary, source, current state, desired state, key interfaces, acceptance criteria, required skills, validation boundary, and out-of-scope work |
| Unit name and source ref | Ties the child to the approved source |
| Required skills | Preserves user-selected workflows inside the child thread |
| Skill propagation mode | Says whether the child runs a whole skill, one role, or no skill |
| Base branch or start state | Prevents branch confusion |
| Acceptance criteria | Defines when the unit is complete |
| Allowed write scope | Prevents drift into unrelated files |
| Dependencies | Shows what must wait or what can run in parallel |
| Worker-allowed checks | Tells the child what validation it may run itself |
| Coordinator-only checks | Tells the child what proof to report as needed, not run |
| Forbidden commands | Prevents child threads from starting expensive or scarce validation lanes |
| Review or gate requirements | Keeps closeout from being skipped |
| Commit requirements | Makes unit output durable |
| Reporting requirements | Gives the parent enough evidence to integrate |

Also tell every child thread that other agents may be working in parallel and that it must not revert, overwrite, or clean other agents' work.

For Apple-platform repositories, child packets must forbid `xcodebuild`, `xctest`, Xcode wrappers, simulator test runs, and repo scripts that invoke those tools. The child should report the needed command; the coordinator runs it after integration.

### 5. Monitor Actively

The parent thread must keep checking child status and live repo evidence. It should not wait until the end and trust summaries blindly.

Monitor:

- child thread status and blockers;
- dirty, staged, untracked, and committed files in each worktree;
- file overlap between units;
- edits outside assigned scope;
- missing required skill usage;
- skipped validation or attempts to run coordinator-only validation;
- stale or missing evidence packets;
- review or critic disagreement;
- claims of completion without commits, archives, or test output.

Steer a child thread when it drifts, blocks, skips a required workflow, edits outside scope, or claims completion without proof.

### 6. Integrate Completed Units

Integrate only units that are reviewed, validated, and frozen according to the run binding.

Choose the safest integration method for the actual output:

| Method | Use When |
|---|---|
| Merge | The unit branch history should be preserved and conflicts are low-risk |
| Cherry-pick | One or more unit commits should be copied without merging the full branch |
| Scoped checkout | The branch has useful files but also unrelated churn |
| Manual patch | The child produced a valid fix without a clean commit |
| Consolidated parent edit | Several units touched the same shared state, docs, or changelog |

After each integration, verify that the accepted fix is present on the target branch. Do not rely on the child branch alone.

Commit each accepted integration on the coordinator target branch before starting the next integration or combined validation phase. If an integration is a no-op because the target branch already contains the change, record the existing commit or evidence proving there is no new diff.

### 7. Validate Integrated Work

Run the combined validation route after integration. Unit-level validation does not prove the integrated state.

The coordinator owns resource-heavy validation. Child threads should run only explicitly allowed lightweight checks; broad builds, expensive test lanes, Xcode/XCTest, simulator tests, and scarce UI validation stay with the coordinator.

Use the checks named in the request and any repo-required checks. Also check:

- final diff scope;
- generated or shared files;
- docs and metadata consistency;
- private paths, secrets, and sensitive diagnostics;
- required review archives or evidence records;
- worktree cleanliness.

### 8. Close Out

The final report should say:

- work source and target branch;
- final unit matrix;
- child thread IDs and unit branches;
- commits or integration method;
- required skills used per unit;
- validation commands and results;
- review, gate, triage, and evidence paths;
- cleanup performed, retained, blocked, or unavailable;
- remaining risks, blockers, or unvalidated areas.

Do not delete worktrees or archive child threads until the target branch contains the accepted work and no required evidence exists only in the child worktree or thread summary.

## Monitoring And Trust Boundaries

The orchestrator is useful because it keeps one parent thread accountable for many child outputs. That accountability only works if the parent checks evidence.

Treat these as claims, not facts:

- "tests passed";
- "the fix is complete";
- "the branch is clean";
- "the review passed";
- "the archive exists";
- "the change is integrated";
- "there are no conflicts".

Verify with live commands, files, diffs, logs, commits, and archive paths. If a child cannot provide proof, mark the unit `blocked`, `needs_steer`, or `not integrated`.

## Integration Rules

Keep integration boring and reversible.

- Integrate one unit at a time unless the units were intentionally coupled.
- Prefer narrow file movement over broad merges when a branch contains extra churn.
- Re-run relevant checks after conflicts or parent-side consolidation.
- Keep unrelated target-branch changes out of the integration.
- Record when a child commit was superseded by a parent consolidation commit.
- Never claim that a unit is integrated until the target branch contains the accepted result.

For shared files such as status docs, changelogs, generated indexes, and build-state records, prefer one parent-side consolidated update instead of accepting every child copy.

## Beta Limitations

`multi-phase-orchestrator` is beta and explicit-invocation-only.

It is not:

- a fully automatic scheduler;
- a substitute for repo tests or review gates;
- a way to bypass user approval for broad branch or worktree operations;
- a reason to trust child summaries without evidence;
- a good fit for unclear sources or single-edit tasks.

The quality of the run depends heavily on the input packet. If the work source, scope, validation, or closeout route is vague, the parent should clarify before dispatching child threads.

## Related Docs

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [Reference](reference.md)
- [Writing Codex Loops](writing-codex-loops.md)
