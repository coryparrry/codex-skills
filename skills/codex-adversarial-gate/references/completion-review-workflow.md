# Completion Review Workflow

Read this for implementation closeout.

## Slice Boundary Contract

When `codex-adversarial-gate` is active, run this workflow at each reviewable implementation boundary, not only before the final response.

- Treat every named phase, slice, checkpoint, grouped unit, task-list item, or final-report row as reviewable if the implementing thread would mark it `complete`, `done`, `closed`, or equivalent.
- Keep the unit open as `implemented-awaiting-adversarial-review` or equivalent until reviewer `PASS`, critic `AGREE_PASS`, and both archive paths exist.
- If multiple slices are intentionally batched, freeze the artifact and gate the grouped checkpoint against all included acceptance criteria, changed files, validation, and risks. The final report must make the grouping explicit.
- If a slice was already called complete without this gate, freeze the current artifact, reopen or qualify the status, run the missed reviewer/critic cycle, archive both outputs, and only then restore the complete status.

## Required Flow

1. Freeze the artifact and evidence packet.
2. Run a fresh `task_completion_adversarial_reviewer`.
3. Archive the exact reviewer output under `<repo>/docs/Adversarial Reviews/`.
4. If the reviewer returns anything except `PASS`, keep the phase/slice open.
5. If the reviewer returns `PASS`, run a fresh `task_completion_review_critic` with the original packet and exact reviewer output.
6. Archive the exact critic output.
7. Accept closeout only when the critic returns `AGREE_PASS`.
8. Record verdicts, disagreement class, archive paths, evidence checked, and resolution in the final report.

## Compact Evidence Packet

Send pointers and raw artifacts, not long justification:

- phase/slice id and exact acceptance criteria;
- current branch/status and changed files, including staged, unstaged, and untracked files;
- diff inspection pointers;
- validation ledger: command, cwd, exit status, run order after latest fix, raw log path or raw output excerpt;
- rerun change log, skipped checks, and reasons;
- relevant plan entries, acceptance criteria, or repo-specific equivalents;
- changed contracts, user-facing behavior, security/privacy surfaces, and validation environment evidence when relevant;
- known risks, edge cases, and security-sensitive surfaces.

## PASS Standard

Reviewer `PASS` is preliminary. It requires raw evidence that acceptance criteria are met, current state/diffs were checked, scope did not drift, validation is current and behavior-matched, relevant contracts/docs/artifacts are updated, project-specific risk checks have no blocker, skipped checks are justified, and secrets/exposure/privacy risks were checked.

Final closeout requires critic `AGREE_PASS`.

## Evidence Integrity

- Implementer summaries and reviewer agreement are claims until backed by cited evidence.
- Raw evidence must identify command, cwd, exit status, and whether it ran after the latest fix.
- Stale logs, different branches, and pre-fix runs do not prove completion.
- Missing unsafe-to-rerun evidence means `BLOCKED_INSUFFICIENT_EVIDENCE`.
- Skipped integration or boundary tests do not prove changed persistence, migration, protocol/browser, production wiring, external side-effect, or runtime behavior.

## Prevention Checks

Always check for false confidence: stale branch, stale logs, uninspected diffs, validation that does not exercise the changed behavior, and summary-only proof.

Add source-of-truth, effective-state, side-effect, and security/redaction checks when touched surfaces call for them.

Use `references/task-completion-gate-rubric.md` for full PASS and non-PASS criteria.
