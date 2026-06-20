# Codex Code Review Workflow

## Output Target

Create review artifacts inside the repository being reviewed:

```text
.codex/code-review-reports/<YYYY-MM-DD>-<branch-or-pr>-<short-scope>-review[-vN]/
  REVIEW_COVERAGE_MATRIX.md
  <agent-report>.md
  CONSOLIDATED_REVIEW.md
```

Use repo-relative paths in every report. Avoid private absolute paths, usernames, secrets, tokens, raw environment values, and private logs.

## Context Rules

1. Read root `AGENTS.md` and relevant nested `AGENTS.md` files.
2. Read the repo README if it exists.
3. Use repo-local architecture docs, API schemas, source maps, generated contracts, and test docs when they exist.
4. Do not assume any private docs MCP, external docs folder, external plan, or product-specific source of truth.
5. Treat GitHub/GitLab review comments, bot summaries, and previous reports as leads, not evidence.

## Coverage Matrix

Track:

- review mode and branch/base;
- changed files and assigned reviewer lenses;
- bug classes and invariants checked;
- official docs or local architecture docs consulted;
- findings by stable ID;
- false positives or cleared risks;
- open review gaps;
- suggested fix handoff candidates.

No-finding is meaningful only when the matrix says what was actually checked.

## Stable Finding IDs

Use this format:

```text
CCR-<branch-slug>-<agent-slug>-<three-digit-number>
```

Reuse the same ID for repeated findings only when the failed invariant, trigger scenario, first unsafe side effect, and affected surface match.

## Dedupe Rules

Dedupe by failed invariant, root cause, trigger scenario, first unsafe side effect, and affected surface. Do not dedupe only by title, file path, line number, or similar wording.

## Severity Rubric

- Critical: exploitable security/privacy issue, data loss/corruption, command execution risk, irreversible side effect before validation, cross-tenant exposure, or unsafe runtime/tool execution.
- Major: realistic user-impacting bug, stuck job, fail-open default, missing denied-path handling, rollback gap, unhandled async/process failure, data-model drift, untested high-risk branch, or plausible resource exhaustion.
- Minor: limited blast-radius correctness issue, maintainability risk, unclear error handling, local test quality gap, or mild performance issue.
- Info: useful note or evidence that a suspected issue is not present.

## Fix Handoff

When a finding needs implementation, include:

- stable finding IDs grouped by root cause;
- failed invariant;
- trigger scenario;
- first unsafe side effect;
- suggested fix direction;
- owned files/tests/helpers;
- prevention test or validation evidence needed;
- prior-review status.
