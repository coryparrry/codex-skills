---
name: triage-review-comments
description: Triage pull request review comments and classify them into fix now, fix if cheap, defer, or ignore, with a practical prevention check. Use when reviewing current PR comments, CodeRabbit or Cursor output, or human review threads.
---

# Triage Review Comments

Use this skill to separate real blockers from bot noise. Treat every review comment as a hypothesis that must be checked against the code.

## Core Workflow

1. Load the current PR review context first.
2. Build a complete inventory: open inline threads, resolved inline threads, general comments, and standalone review findings.
3. Ignore boilerplate, walkthrough notes, and automation banners unless they contain an actionable finding.
4. Deduplicate comments that describe the same issue.
5. Resolve fixed inline review threads when the current code clearly addresses them and GitHub tooling is available.
6. Track real deferred work in Linear when the project is clear.
7. Classify every actionable comment into exactly one bucket.
8. For every real issue, recommend the smallest practical prevention test or check.

## Buckets

- `Fix now`: reachable, meaningful, and should block merge.
- `Fix if cheap`: probably valid, limited impact, and low-risk to take now.
- `Defer`: real work, but better as follow-up.
- `Ignore`: duplicate, stale, speculative, style-only, or already fixed.

## Output

Return:

- Inventory counts
- Each bucket with short reasons
- Threads resolved on GitHub
- Threads that look fixed but were not resolved remotely
- Prevention tests or checks for real issues
- A short summary with next steps

Use `references/triage-review-comments.md` for the fuller triage rubric and expected response shape.
