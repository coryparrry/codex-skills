# Use Codex Skills

This how-to guide explains when and how to invoke the skills in this repository.

## Purpose

Use this guide when the skills are already installed and you want to choose the right one for a task.

## Before You Start

Make sure the relevant skill is installed. See [Install Codex Skills](installation.md).

For `codex-adversarial-gate`, also make sure the custom reviewer agent TOMLs are installed. The skill depends on them for the normal reviewer and critic flow.

## Choose A Skill

| Goal | Skill |
|---|---|
| Review a plan before execution | `codex-adversarial-gate` |
| Close an implementation phase or slice | `codex-adversarial-gate` |
| Recover from a skipped completion gate | `codex-adversarial-gate` |
| Clean up one merged local Git branch | `git-clean-merged-branch` |
| Classify PR review feedback | `triage-review-comments` |

## Gate Plan Or Implementation Work

Use `codex-adversarial-gate` when Codex should not mark work complete without independent review evidence.

For a plan review, ask:

```text
Use $codex-adversarial-gate to adversarially review this plan before finalization.
```

For implementation closeout, ask:

```text
Use $codex-adversarial-gate to close this implementation slice with archived reviewer and critic evidence.
```

For implementation closeout, Codex should:

1. Build a compact evidence packet.
2. Pre-freeze the final review surface, including staged intended files, ignored evidence logs, manifest/checksum refreshes when used, and current status/whitespace checks.
3. Run `task_completion_adversarial_reviewer`.
4. Archive the exact reviewer output.
5. If archiving changes the staged artifact, stage the archive and rerun current staged status/whitespace checks.
6. Run `task_completion_review_critic` when the reviewer returns `PASS`, passing the reviewer archive path and frozen-state evidence.
7. Archive the exact critic output.
8. Accept completion only when the critic returns `AGREE_PASS`.

Do not use the plan reviewer to close implementation work.

## Archive Review Output

Archive a review from a file:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/codex-adversarial-gate/scripts/archive_adversarial_review.py" \
  --repo "$PWD" \
  --kind completion \
  --phase "parser cleanup" \
  --reviewer task_completion_adversarial_reviewer \
  --verdict PASS \
  --review-file ./review.md
```

Archive a review from standard input:

```bash
printf '%s\n' "$REVIEW_TEXT" | python3 "${CODEX_HOME:-$HOME/.codex}/skills/codex-adversarial-gate/scripts/archive_adversarial_review.py" \
  --repo "$PWD" \
  --kind critic \
  --phase "parser cleanup" \
  --reviewer task_completion_review_critic \
  --verdict AGREE_PASS \
  --stdin
```

The helper writes review records under:

```text
<repo>/docs/Adversarial Reviews/
```

## Clean Up A Merged Branch

Use `git-clean-merged-branch` after a PR has been merged and you want the local branch removed safely.

From inside the target Git repository, ask:

```text
git-clean-merged-branch
```

The skill should run its cleanup script from the installed skill folder:

```bash
bash "${CODEX_HOME:-$HOME/.codex}/skills/git-clean-merged-branch/scripts/clean_merged_branch.sh"
```

If GitHub used squash or rebase merge and the branch is definitely no longer needed, use the force-delete option:

```bash
bash "${CODEX_HOME:-$HOME/.codex}/skills/git-clean-merged-branch/scripts/clean_merged_branch.sh" --force-delete-unmerged
```

Do not use the force-delete option unless the branch is known to be merged or intentionally disposable.

## Triage PR Review Comments

Use `triage-review-comments` when a PR has review comments that need sorting before implementation.

Ask:

```text
Use $triage-review-comments to triage the review comments on this PR.
```

The skill should:

1. Load the current PR review context.
2. Inventory open and resolved inline threads, general comments, and standalone review findings.
3. Remove boilerplate and non-actionable comments.
4. Deduplicate repeated findings.
5. Classify actionable items into `Fix now`, `Fix if cheap`, `Defer`, or `Ignore`.
6. Resolve clearly fixed inline threads when GitHub tooling is available.
7. Recommend prevention checks for real issues.

The skill classifies review work. It does not implement fixes by itself.

## Common Cases

If a completion gate was skipped, use `codex-adversarial-gate` to freeze the current artifact, reopen the status, run reviewer and critic, archive both outputs, and only then restore completion.

If branch cleanup stops on local changes, commit, stash, or discard those changes before rerunning the skill.

If review triage has no PR context, load the PR or provide enough review context before invoking the skill.

## Related Docs

- [Installation](installation.md)
- [Reference](reference.md)
- [Codex Adversarial Review Gate](codex-adversarial-gate.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
- [Triage Review Comments](triage-review-comments.md)
