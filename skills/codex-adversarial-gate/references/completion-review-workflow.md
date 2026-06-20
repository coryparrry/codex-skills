# Completion Review Workflow

Read this for implementation closeout.

## Slice Boundary Contract

When `codex-adversarial-gate` is active for implementation work, run this workflow at each reviewable implementation boundary, not only before the final response.

- Treat every named phase, U-slice, checkpoint, grouped unit, goal-dashboard item, task-list item, Todo/checklist item, issue-tracker item, or final-report row as reviewable if the implementing thread would mark it `complete`, `done`, `closed`, or equivalent.
- Keep the unit open as `implemented-awaiting-adversarial-review` or equivalent until reviewer `PASS`, critic `AGREE_PASS`, and both archive paths exist.
- If multiple slices are intentionally batched, freeze the artifact and gate the grouped checkpoint against all included acceptance criteria, changed files, validation, and risks. The final report must make the grouping explicit.
- If a slice was already called complete without this gate, freeze the current artifact, reopen or qualify the status, run the missed reviewer/critic cycle, archive both outputs, and only then restore the complete status.

## Required Flow

1. Build the evidence packet.
2. Pre-freeze the final review surface:
   - write required raw evidence, manifests, checksums, and any already-known review archives;
   - stage the intended implementation, docs, generated artifacts, archives, and intentionally ignored evidence logs;
   - run current status, untracked-file, staged-diff, and whitespace checks after the latest stage;
   - record nonblocking caveats such as unsupported local tool versions or deliberately skipped broad checks.
3. Run a fresh `task_completion_adversarial_reviewer` with the frozen evidence packet.
4. Archive the exact reviewer output under `<repo>/docs/Adversarial Reviews/`.
5. If archiving changed the staged artifact, stage the archive and rerun the current staged status/whitespace checks before sending the critic.
6. If the reviewer returns anything except `PASS`, keep the phase/slice open.
7. If the reviewer returns `PASS`, run a fresh `task_completion_review_critic` with the original packet, exact reviewer output, reviewer archive path, and current frozen-state evidence.
8. Archive the exact critic output.
9. Accept closeout only when the critic returns `AGREE_PASS`.
10. Record verdicts, disagreement class, archive paths, evidence checked, and resolution in the final report.

## Compact Evidence Packet

Send pointers and raw artifacts, not long justification:

- phase/slice id and exact acceptance criteria;
- current branch/status and changed files, including staged, unstaged, and untracked files;
- diff inspection pointers;
- validation ledger: command, cwd, exit status, run order after latest fix, raw log path or raw output excerpt;
- frozen-state evidence: latest staged status, unstaged diff, untracked files, staged whitespace check, manifest/checksum status, and intentionally staged ignored evidence files;
- rerun change log, skipped checks, selected prevention lanes, and source-owner/proof-tier notes;
- relevant plan entries or repo-specific equivalents;
- concrete repo-specific prevention guard when present;
- production-composition, auth/exposure, acceptance traceability, and validation environment evidence when relevant;
- known risks, edge cases, and security-sensitive surfaces.

## PASS Standard

Reviewer `PASS` is preliminary. It requires raw evidence that acceptance criteria are met, current state/diffs were checked, scope did not drift, validation is current and behavior-matched, relevant contracts/docs/artifacts are updated, prevention lanes have no blocker, skipped checks are justified, and secrets/exposure/privacy risks were checked.

Final closeout requires critic `AGREE_PASS`.

## Evidence Integrity

- Implementer summaries and reviewer agreement are claims until backed by cited evidence.
- Raw evidence must identify command, cwd, exit status, and whether it ran after the latest fix.
- Stale logs, different branches, and pre-fix runs do not prove completion.
- Missing unsafe-to-rerun evidence means `BLOCKED_INSUFFICIENT_EVIDENCE`.
- Skipped integration or boundary tests do not prove changed persistence, migration, protocol/browser, production wiring, external side-effect, or repo-specific runtime behavior.

## Blocker Calibration

Keep the gate strict on issues that can make Codex drift from the plan or claim false completion:

- unmet acceptance criteria, product behavior defects, unsafe exposure, source-truth drift, stale generated artifacts, or scope creep;
- validation claims that are false against live staged state;
- missing, stale, wrong-branch, or non-inspectable raw evidence;
- staged or untracked files that make the commit differ from the reviewed artifact;
- missing reviewer/critic archives or unresolved critic dissent.

Treat archive formatting and evidence-file hygiene as artifact hygiene. It blocks closeout only when it fails a required check, contradicts the evidence packet, prevents later inspection of raw proof, or would commit an unreliable gate trail. If it does not affect those conditions, record it as a residual risk or cleanup note instead of rerunning the whole product review.

Before rerunning a full reviewer/critic cycle for hygiene-only changes, prefer a narrow frozen-state refresh: stage the hygiene fix, rerun status/whitespace/checksum verification, update the manifest, and send the critic the exact delta. Use a full fresh reviewer cycle when the implementation, validation result, scope, or acceptance evidence changed.

## Prevention Checks

Always apply `process-preflight-claim-prevention` and `false-confidence-test-prevention`.

Add source-owner, proof-tier, source-truth, effective-state, side-effect, and security/redaction checks when touched surfaces call for them.

Use `references/task-completion-gate-rubric.md` for full PASS and non-PASS criteria.
