# Use Codex Skills

This guide explains when and how to invoke the skills in this repository.

## Choose A Skill

| Goal | Skill |
|---|---|
| Audit an Apple app before upload or submission to App Store Connect | `appstore-readiness-audit` |
| Continue prior ChatGPT Deep Research or another existing research packet with live repository context | `continue-deep-research` |
| Decide which technologies a live repository should adopt, adapt, build, or reject | `research-repo-technology` |
| Route implementation to capability-matched Terra workers while the root remains a non-implementing advisor | `engineering-advisor` |
| Review a pull request, branch, commit, diff, or working tree across repository boundaries | `deep-code-review` as the umbrella review |
| Review focused Swift or Apple-platform changes, or provide the specialist lane for a deep review | `swift-code-review` |
| Clean up one merged local Git branch | `git-clean-merged-branch` |
| Classify PR review feedback | `triage-review-comments` |

Both research workflows begin from the available runtime. They use independent lanes when that materially improves coverage and the runtime supports them; otherwise they complete a bounded root-only audit and disclose the reduced coverage.

## Audit App Store readiness

Use `appstore-readiness-audit` before uploading or submitting an Apple app to App Store Connect:

```text
Use $appstore-readiness-audit to audit this release candidate for App Store submission readiness without changing it.
```

The skill refreshes current Apple sources, identifies the exact source and artifact under review, classifies product features, and runs separate project, release, privacy, policy, runtime, metadata, and reviewer-access gates. It distinguishes a candidate that is ready to upload from one with enough evidence to submit for review.

The audit is read-only. Missing runtime or App Store Connect evidence remains `NOT_TESTED` or `UNKNOWN` and can hold the verdict. A successful build or archive does not become a submission-ready result by itself.

## Run As An Engineering Advisor

Use `engineering-advisor` when the root agent must investigate, scope, delegate, review, and validate without modifying repository files itself:

```text
Use $engineering-advisor to route verified fixes to capability-matched Terra workers. Remain the non-implementing advisor and reject unnecessary code or behavior drift.
```

The root proves findings before assigning them, selects the lowest sufficient Terra reasoning tier, gives workers non-overlapping ownership, reviews every resulting diff, and runs the final validation. All tracked-file changes and follow-up corrections remain with Terra workers. If that lane is unavailable, the skill reports implementation blocked instead of falling back to root edits.

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

## Deep Code Review

Use `deep-code-review` for a language-agnostic, repository-wide review of a pull request, branch, commit, diff, or working tree:

```text
Use $deep-code-review as the repository-wide umbrella to review this change safely, validate only change-caused defects, and assess correctness, security, compatibility, and merge readiness.
```

The skill binds the review to an exact state, resolves repository policy, reconstructs intent, traces affected behavior beyond the diff, activates only relevant specialist lanes, challenges verification, and checks missing companion changes. It inspects execution hooks before running proposed code, tries to disprove every candidate finding, runs one bounded omission pass, and re-snapshots the state before reporting.

The review is read-only. A partial inventory cannot produce an approval. Tests, scanners, AI authorship, and suspicious-looking patterns remain evidence or search leads until the reviewer proves a reachable violated property.

## Swift Code Review

Use `swift-code-review` directly for a focused Swift or Apple-platform diff, branch, commit, or pull request. For a mixed-language or repository-wide review, use it as the specialist lane under `deep-code-review`:

```text
Use $swift-code-review to review these Swift and SwiftUI changes for concrete correctness and regression risks.
```

The skill first identifies the compiler, language mode, SDK, deployment target, and dependency versions.

Then it loads only the reference files that apply to the affected invariants.

The skill is read-only. It traces callers, cancellation, teardown, identity, representation, and side effects before it reports a finding.

The skill does not invent style comments. AI authorship does not increase the priority of a finding.

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
- [App Store Readiness Audit](appstore-readiness-audit.md)
- [Deep Code Review](deep-code-review.md)
- [Engineering Advisor](engineering-advisor.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
- [Triage Review Comments](triage-review-comments.md)
- [Continue Deep Research](continue-deep-research.md)
- [Repository Technology Research](research-repo-technology.md)
- [Swift Code Review](swift-code-review.md)
