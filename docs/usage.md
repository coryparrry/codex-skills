# Usage Guide

Use this guide when you want Codex to apply the adversarial review gate to a plan or implementation closeout.

## When To Use The Skill

Use `codex-adversarial-gate` when:

- finalizing or updating an implementation plan;
- closing a phase, slice, checkpoint, or grouped implementation unit;
- recovering from a skipped review gate;
- auditing a completion claim before marking work complete.

Do not use the plan reviewer to close implementation work. Completion closeout requires the completion reviewer and then the critic.

## Plan Review

Use plan review before finalizing a plan.

```text
Use $codex-adversarial-gate to adversarially review this plan before finalization.
```

Expected flow:

1. Add the contract from `templates/plan-adversarial-review-section.md`.
2. Run `plan_adversarial_reviewer`.
3. Revise the plan if the reviewer returns `FAIL_NEEDS_REVISION`.
4. Archive the exact review output.
5. Finalize only when every reviewable phase reaches `PASS_100`, or stop for owner input if blocked.

## Completion Closeout

Use completion review before marking a phase or slice complete.

```text
Use $codex-adversarial-gate to close this implementation slice with archived reviewer and critic evidence.
```

Build a compact packet with:

- phase or slice name;
- exact acceptance criteria;
- current branch and status;
- changed files, including untracked files;
- relevant diff pointers;
- validation commands, cwd, exit status, and raw output or log path;
- skipped checks and reasons;
- known risks or security-sensitive surfaces;
- rerun change log when applicable.

Then run:

1. `task_completion_adversarial_reviewer`
2. archive the exact reviewer output
3. `task_completion_review_critic` if the reviewer returns `PASS`
4. archive the exact critic output

The phase or slice is complete only when the critic returns `AGREE_PASS`.

## Archive Review Output

Archive from a file:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/codex-adversarial-gate/scripts/archive_adversarial_review.py" \
  --repo "$PWD" \
  --kind completion \
  --phase "parser cleanup" \
  --reviewer task_completion_adversarial_reviewer \
  --verdict PASS \
  --review-file ./review.md
```

Archive from standard input:

```bash
printf '%s\n' "$REVIEW_TEXT" | python3 "${CODEX_HOME:-$HOME/.codex}/skills/codex-adversarial-gate/scripts/archive_adversarial_review.py" \
  --repo "$PWD" \
  --kind critic \
  --phase "parser cleanup" \
  --reviewer task_completion_review_critic \
  --verdict AGREE_PASS \
  --stdin
```

The helper creates `docs/Adversarial Reviews/` in the target repository and prints the archive path.

## Recover A Skipped Gate

If a phase was already marked complete without archived reviewer and critic outputs:

1. Freeze the current artifact.
2. Reopen or qualify the completion status.
3. Build a fresh evidence packet.
4. Run `task_completion_adversarial_reviewer`.
5. Archive the reviewer output.
6. Run `task_completion_review_critic` for reviewer `PASS`.
7. Archive the critic output.
8. Restore complete status only after `AGREE_PASS`.

## Fallback Prompts

If the custom agents are unavailable but an independent reviewer context exists, use `references/reviewer-prompts.md`.

Do not run fallback prompts in the same implementing thread. If no independent reviewer context is available, stop with `BLOCKED_REVIEW_CONTEXT_UNAVAILABLE`.
