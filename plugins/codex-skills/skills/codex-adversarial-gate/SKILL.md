---
name: codex-adversarial-gate
description: Use when closing implementation phases/slices, auditing completion claims, or reviewing/updating Codex plans. Blocks completion with adversarial reviewer-plus-critic gates until evidence, dissent handling, validation, and docs/Adversarial Reviews archival pass.
---

# Codex Adversarial Gate

Use this skill to prevent Codex from marking implementation work complete just because the implementing thread is confident.

Default to implementation closeout for implementation work. Plan review still exists for drafting or updating plans, but routine implementation should spend budget on completion review and archival, not on re-litigating an accepted plan.

When this skill is active for implementation work, it is a slice-boundary gate, not a final closeout add-on. Loading the skill, keeping a pending reminder, or saying the gate will happen later does not count as using it. Each reviewable phase, U-slice, checkpoint, or grouped implementation unit must stop at its completion boundary until the completion reviewer and critic outputs are archived.

## Routing

Use the bundled custom agents when installed:

- `plan_adversarial_reviewer`: plan drafting, plan updates, and plan finalization only.
- `task_completion_adversarial_reviewer`: implementation phase/slice closeout only.
- `task_completion_review_critic`: audit any completion-review `PASS` before the implementer accepts it.

If the environment supports separate reviewer contexts but not these custom agents, use the prompts in `references/reviewer-prompts.md` with equivalent read-only reviewer contexts. If no independent reviewer context is available, do not self-review; stop with `BLOCKED_REVIEW_CONTEXT_UNAVAILABLE` and ask the user for a separate review path.

Never use `plan_adversarial_reviewer` to close implementation work. A phase/slice is complete only after `task_completion_adversarial_reviewer` returns a preliminary `PASS`, `task_completion_review_critic` returns `AGREE_PASS`, and both review records are archived in the repo.

A reviewable phase/slice is any named implementation unit in the active plan, task list, Todo/checklist, goal dashboard, issue tracker, final report, or conversation checkpoint that the implementer might otherwise mark `complete`, `done`, `closed`, or equivalent. If several slices are intentionally batched into one checkpoint, gate that checkpoint against every included slice's acceptance criteria and changed files, then report archive rows for the grouped checkpoint. Do not mark the individual slices complete without archived gate evidence that covers them.

## Load Only What You Need

- For all uses, read `references/protocol-rules.md`.
- For plan drafting or plan updates, read `references/plan-review-workflow.md`, `references/plan-phase-score-rubric.md`, and `templates/plan-adversarial-review-section.md`.
- For implementation closeout, read `references/completion-review-workflow.md`, `references/task-completion-gate-rubric.md`, `references/review-archive.md`, and `templates/task-completion-gate-block.md`.
- If the custom agents are unavailable but an independent reviewer context exists, read `references/reviewer-prompts.md`.
- Use `scripts/archive_adversarial_review.py` to archive exact review outputs when Python 3 is available. If it is unavailable, follow `references/review-archive.md` manually.

## Non-Negotiable Rules

- Freeze the artifact during a reviewer/critic cycle. Do not edit files, change staging, regenerate artifacts, or rerun fix commands while the cycle is active.
- Freeze the final staged artifact before the decisive review cycle: write any required archives/evidence, stage intentionally ignored evidence files, refresh checksums or manifests, run the current status/whitespace checks, and only then dispatch the reviewer or critic.
- Treat implementer summaries, reviewer confidence, and reviewer/critic agreement as claims until backed by raw code, diff, status, validation, log, screenshot, or owner-decision evidence.
- Preserve dissent. If the critic returns `DISAGREE_EVIDENCE` or `DISAGREE_CONCERN`, keep the phase/slice open until a fresh review cycle resolves it with evidence, a fix, an owner decision, or an explicit blocker.
- Separate product blockers from artifact hygiene. Scope drift, stale or missing evidence, false validation claims, unsafe exposure, and unmet acceptance criteria block closeout. Archive formatting or evidence-file hygiene blocks only when it breaks required checks, contradicts the evidence packet, hides raw proof, or would make the committed gate trail unreliable.
- Use fresh reviewer and critic invocations for each reviewable phase/slice. Do not reuse a long-lived reviewer thread across closeout gates.
- Keep reviewers read-only. The implementing thread archives exact review output after receiving it; the reviewer does not mutate implementation files.
- Archive every plan review, completion review, and critic review under `<repo>/docs/Adversarial Reviews/` before calling the plan finalized or the phase/slice complete.
- Do not write `complete` for a phase/slice with a missing, failed, blocked, unarchived, or critic-disagreed gate.
- Do not advance from an implementation slice as `complete` while the gate is pending. Use an open status such as `implemented-awaiting-adversarial-review` until the archived critic verdict is `AGREE_PASS`.
- If you discover that a phase/slice was already marked complete without the archived reviewer-plus-critic gate, freeze the current artifact, reopen or qualify that status, run the missed gate per slice or grouped checkpoint, archive both outputs, and only then restore the complete status.

## Completion Closeout Checklist

For each reviewable implementation phase/slice:

0. Identify the exact review boundary before closeout: phase, U-slice, checkpoint, grouped unit, or any already-marked-complete slice that still lacks archived gate evidence.
1. Build a compact evidence packet with acceptance criteria, current branch/status, changed files including untracked files, diff pointers, validation ledger, skipped checks, prevention lanes, relevant plan-map entries or repo-specific equivalents, known risks, and rerun change log if applicable.
2. Pre-freeze the review surface: write required evidence artifacts, stage intended files including ignored logs, refresh manifests/checksums, run current staged status and whitespace checks, and record any nonblocking caveats.
3. Run `task_completion_adversarial_reviewer` with the packet.
4. Archive the exact reviewer output using `scripts/archive_adversarial_review.py` or the manual protocol.
5. If archiving changed the staged artifact, stage the archive, rerun the current staged status/whitespace checks, and update evidence before critic dispatch.
6. If the reviewer did not return `PASS`, keep the slice open, fix or gather evidence, then rerun with a new change log.
7. If the reviewer returned `PASS`, run `task_completion_review_critic` with the original packet, exact reviewer output, archive path, and current frozen-state evidence.
8. Archive the exact critic output.
9. Accept closeout only if the critic returns `AGREE_PASS`.
10. Include archive paths in the final implementation report.

## Plan Review Checklist

For plan work:

1. Ask owner-only questions before finalizing the plan. Do not hide unasked decisions as assumptions, TBDs, or future implementer choices.
2. Add the adversarial review contract from `templates/plan-adversarial-review-section.md`.
3. Run `plan_adversarial_reviewer` before finalizing the plan.
4. Run at most 3 completed plan-review iterations by default. Later iterations are delta reviews focused on prior findings and exact revisions.
5. Archive each plan review output.
6. Finalize only when every reviewable phase reaches 100 or the plan is explicitly blocked for owner decision.

## Final Report Requirement

Every final implementation report must include an `Adversarial Completion Review Results` table with:

- phase/slice;
- reviewer verdict and archive path;
- critic verdict and archive path;
- disagreement class;
- raw evidence checked;
- fixes or evidence required;
- final status.

Skipped or blocked gates must be reported as skipped or blocked, not complete.
