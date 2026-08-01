# Use Codex Skills

This guide explains when and how to invoke the skills in this repository.

## Choose A Skill

| Goal | Skill |
|---|---|
| Continue prior ChatGPT Deep Research or another existing research packet with live repository context | `continue-deep-research` |
| Decide which technologies a live repository should adopt, adapt, build, or reject | `research-repo-technology` |
| Clean up one merged local Git branch | `git-clean-merged-branch` |
| Classify PR review feedback | `triage-review-comments` |

## Continue Existing Deep Research

Use `continue-deep-research` when ChatGPT Deep Research, notes, a report, source links, or a prior task already contain useful work and Codex should extend it with repository context:

```text
Use $continue-deep-research to continue this ChatGPT Deep Research report against the live repository. Verify the unresolved claims and return only the research delta.
```

The skill recovers the existing evidence base, checks the claims most likely to change the conclusion, and separates retained, confirmed, corrected, new, contradicted, and unresolved findings. It preserves the supplied materials and keeps research-only work read-only.

## Research Repository Technology

Use `research-repo-technology` when technology choices must be derived from verified gaps in the live repository:

```text
Use $research-repo-technology to determine which technologies this repository should adopt, adapt, build, or reject.
```

The skill audits the checkout before searching externally, inspects promising technologies at source level, ranks a short set of repo-specific opportunities, and proposes bounded proofs of concept without implementing them.

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
- [Continue Deep Research](continue-deep-research.md)
- [Repository Technology Research](research-repo-technology.md)
