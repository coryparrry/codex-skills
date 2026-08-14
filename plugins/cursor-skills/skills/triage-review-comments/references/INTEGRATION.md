# Integration Rules

Use this reference for GitHub review-thread handling, Linear follow-up tracking, and Binder deferred-bug checklist updates.

## GitHub Inventory

Prefer structured GitHub connector tools when available. CLI fallback patterns:

```bash
gh pr view <number> --json number,title,headRefName,reviewThreads,comments,reviews,statusCheckRollup
gh api repos/<owner>/<repo>/pulls/<number>/comments
gh api repos/<owner>/<repo>/issues/<number>/comments
gh api graphql -f query='<GraphQL query for pullRequest.reviewThreads including id,isResolved,path,line,comments>'
```

Inventory should account for:
- open inline review threads
- resolved inline review threads
- general PR comments
- review submissions with standalone findings
- actionable findings after boilerplate filtering and dedupe

If counts come from truncated shell output, browser snippets, or one source only, mark inventory incomplete.

## Resolving Review Threads

Resolve an inline review thread only when:
- the thread is still open
- current code addresses the underlying concern
- the fix is visible in current PR state, not merely planned
- there is no unresolved design question
- confidence is high

Do not resolve:
- general PR comments
- partially addressed comments
- ambiguous concerns
- sidestepped issues
- threads with unresolved design discussion

Structured GitHub tool example:

```text
Resolve review thread <thread-id>, then re-fetch the thread state.
```

GraphQL fallback shape:

```bash
gh api graphql -f query='
mutation($threadId: ID!) {
  resolveReviewThread(input: {threadId: $threadId}) {
    thread { id isResolved }
  }
}' -f threadId='<thread-id>'
```

Never count a thread as resolved unless it was already resolved before the run or the remote resolve operation succeeded.

## Linear Follow-ups

For non-Binder work, create or link a Linear issue for `Defer` items only when:
- the item is a real engineering concern
- it is likely to matter after merge
- it is not already tracked
- it is specific enough to describe clearly
- the correct project can be inferred with confidence

Before creating:
- search for an existing issue covering the same concern
- infer project from repo, PR title, linked work, existing project conventions, or nearby issues
- ask the user only when the project is genuinely ambiguous

Issue body should include:
- concise title
- why it was deferred
- concrete risk or improvement area
- PR/review link when useful
- suggested prevention test/check when applicable

## Binder Deferred Bugs

When the user gives the go-ahead after triaging Binder review comments, record real `Defer` items in the Binder repo at:

```text
docs/Deferred bugs.md
```

Create `docs/` and `docs/Deferred bugs.md` if they do not exist.

Only record verified real issues:
- current-code evidence proves the issue exists
- false-positive checks did not defeat the claim
- the item is not stale, duplicate, preference-only, or already tracked in the same file
- the item should survive after the current PR if not fixed now

Use a checklist format so later Codex runs can check items off:

```md
# Deferred Bugs

Open deferred review bugs that were verified against current code but intentionally not fixed in the originating PR.

- [ ] <short title>
  - Source: <PR/review/thread/comment link or local review surface>
  - Verified: <current-code evidence and reachability>
  - False-positive check: <why stale/unreachable/guarded/duplicate/preference-only explanations do not apply>
  - Impact: <practical consequence if left unresolved>
  - Suggested prevention: <test/check that should fail before the fix or guard against recurrence>
```

When resolving a deferred bug, change `[ ]` to `[x]` only after the fix and prevention have been implemented and validated. Keep the original evidence, and add a short `Resolved:` line with the validation command or PR link.
