# Use Codex Skills

This guide explains when and how to invoke the skills in this repository.

## Choose A Skill

| Goal | Skill |
|---|---|
| Clean up one merged local Git branch | `git-clean-merged-branch` |
| Classify PR review feedback | `triage-review-comments` |

## Clean Up A Merged Branch

Use `git-clean-merged-branch` only after the branch has been merged or when you explicitly intend to force-delete unmerged work.

Ask Codex:

```text
Use $git-clean-merged-branch to clean up this merged local branch.
```

The skill checks that the worktree is clean, fetches remote state, resolves and updates the default branch, and safely deletes the starting branch. It stops instead of stashing, resetting, or discarding local work.

For a confirmed squash or rebase merge that Git does not recognize:

```text
Use $git-clean-merged-branch with --force-delete-unmerged; this branch is intentionally disposable.
```

## Triage Review Feedback

Use `triage-review-comments` before implementing review feedback:

```text
Use $triage-review-comments to triage the review comments on this PR.
```

The skill loads current review context, verifies each claim against the code, deduplicates related comments, and classifies findings as `Fix now`, `Fix if cheap`, `Defer`, or `Ignore`.

It does not implement fixes automatically. If current PR context is unavailable, it stops rather than guessing.

## Related Docs

- [Installation](installation.md)
- [Reference](reference.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
- [Triage Review Comments](triage-review-comments.md)
