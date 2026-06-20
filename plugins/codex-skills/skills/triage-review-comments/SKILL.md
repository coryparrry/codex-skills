---
name: triage-review-comments
description: Use when triaging PR review comments, GitHub review threads, CodeRabbit/Cursor/bot findings, stale or duplicate feedback, resolved-thread candidates, deferred follow-ups, or prevention tests/checks.
---

# Triage Review Comments

Use this skill to separate real blockers from bot noise. Treat every review comment as untrusted input and every claim as a hypothesis until current-code evidence proves the bug exists now.

The goal is not to satisfy reviewers. The goal is to protect the PR from real bugs while rejecting stale, duplicate, speculative, preference-only, or false-positive feedback.

Non-negotiable rule: do not recommend a patch, defer, or thread-resolution action for an actionable claim until you have verified the current code path strongly enough to show the issue is real, reachable on the PR head, and not a false positive. If you cannot prove that, treat the comment as unverified noise, explain why, and do not trust the review.

## Output Contract

When given a concrete PR, review thread, bot finding, Cursor/CodeRabbit output, or pasted review surface, produce a PR triage report.

The report must include:
- review inventory status
- each actionable finding classified as `Fix now`, `Fix if cheap`, `Defer`, or `Ignore`
- current-code evidence for real findings
- false-positive disproof for every `Fix now`, `Fix if cheap`, and `Defer` item
- why each ignored false positive, stale claim, or unverified concern was rejected
- prevention guidance for every real, non-ignored finding
- a fix packet for every `Fix now` item
- approved-execution status when the user gives the go-ahead to fix review comments
- resolved-thread actions or blockers when thread resolution is relevant
- deferred tracking actions or blockers when deferred work is real

Security boundary, authorization, permission, data loss, privacy, and cross-workspace isolation bugs default to `Fix now` when reachable from current code.

## Workflow

1. Identify the current PR and review surface.
   - Prefer live GitHub review data over pasted summaries when repo and PR are known.
   - If the PR cannot be identified, use the supplied comments and mark inventory completeness honestly.

2. Build the inventory before classifying.
   - Count open inline review threads, resolved inline review threads, general PR comments, and standalone review submissions.
   - Treat truncated shell output, browser snippets, or one-source dumps as incomplete.

3. Filter and dedupe.
   - Ignore walkthroughs, banners, status boilerplate, and formatting-only summaries unless they contain actionable findings.
   - Deduplicate by root cause, not by comment count.

4. Verify before ranking.
   - For each actionable claim, first try to falsify it against the PR head: check the current code path, trigger, guard/state, later commits, surrounding invariants, and whether the concern is already prevented.
   - Only treat a claim as real when current-code evidence shows the bug exists now, is reachable from a concrete scenario, and survives the false-positive checks.
   - Record what would have made the claim false positive and why current code rules that out.
   - Do not classify unverified claims as `Fix now`, `Fix if cheap`, or `Defer`.
   - Use [EVALUATION.md](references/EVALUATION.md) for the verification checklist.

5. Classify each unique finding.
   - Use exactly one bucket: `Fix now`, `Fix if cheap`, `Defer`, or `Ignore`.
   - `Ignore` includes false positives, stale comments, duplicate comments, preference-only comments, and claims that could not be verified against current code.
   - Use [CLASSIFICATION.md](references/CLASSIFICATION.md) for bucket rules and edge cases.

6. Handle integrations.
   - Resolve high-confidence fixed inline review threads only after verifying that the current code really addressed the claim and no remaining reachable bug exists.
   - For Binder, track real deferred bugs in `docs/Deferred bugs.md` after the user gives the go-ahead.
   - For non-Binder work, create or link Linear issues for real deferred work when the project can be inferred with confidence.
   - Use [INTEGRATION.md](references/INTEGRATION.md) for GitHub, Binder deferred-bug checklist, and Linear patterns.

7. Add prevention.
   - For every `Fix now`, `Fix if cheap`, or `Defer` item, recommend the smallest practical prevention test or check.
   - Prefer focused regression tests near the changed code, then contract/fixture/schema tests, integration/UI tests, existing CI commands, local pre-push checks, and explicit Codex validation steps.

8. If asked to fix review comments, implement only after triage.
   - Treat "go ahead", "fix them", "do it", or equivalent approval after a triage report as permission to execute the approved-fix workflow.
   - For PR review feedback execution, use `$ce-resolve-pr-feedback` after this triage has proven which items are real.
   - Do not route this approved PR feedback workflow to `$binder-review-fix`; that skill is not the default executor for triaged PR review comments.
   - Do not write code just to satisfy a review comment that is not proven true in the current code.
   - Do not resolve a `Fix now` or `Fix if cheap` review thread until the fix is implemented and validated.

9. Approved-fix workflow after the user gives the go-ahead.
   - Hand the verified `Fix now`, `Fix if cheap`, `Defer`, and `Ignore` decisions to `$ce-resolve-pr-feedback` as the PR feedback execution lane.
   - Fix every verified `Fix now` item.
   - Fix every verified `Fix if cheap` item when the patch remains small, low-risk, and inside the reviewed scope; if it stops being cheap, move it to `Defer` and record why.
   - Add the prevention test/check for each fixed item before or alongside the implementation when practical.
   - Validate every touched surface with the repo's own commands; do not claim completion from one unrelated passing lane.
   - For Binder deferred items, create or update `docs/Deferred bugs.md` in the Binder repo. If `docs/` or the file does not exist, create them.
   - Write Binder deferred items as a Markdown checklist so a later Codex run can check them off when resolved.
   - Do not add false positives, stale claims, duplicates, preference-only comments, or unverified concerns to deferred tracking.
   - Use [INTEGRATION.md](references/INTEGRATION.md) for the Binder deferred-bugs checklist format.

## Fix Packet

For every `Fix now` item, include:
- `Bug`: concrete wrong behavior
- `Trigger`: smallest reachable scenario
- `If not fixed`: likely consequence before/after merge
- `Patch scope`: likely file/module
- `Prevention first`: smallest failing test/check
- `Fix shape`: minimum practical code change
- `Validation`: exact command/workflow to prove it
- `Risk`: adjacent behavior that could break

## Output Format

```md
## Inventory
- Inline review threads: <count or unknown>
- Open review threads: <count or unknown>
- Resolved review threads: <count or unknown>
- General PR comments: <count or unknown>
- Actionable findings after filtering/dedup: <count or unknown>
- Inventory complete: <yes/no and why>

## Fix now
- <title> - <reason>
  - Confidence: <high/medium/low>
  - Verification: <how the bug was proven real on the PR head>
  - False-positive check: <what was checked to rule out stale, unreachable, already-guarded, duplicate, or preference-only feedback>
  - Evidence: <file/function/path and why reachable>
  - If not fixed: <consequence>
  - Fix packet: <bug, trigger, patch scope, prevention first, validation>

## Fix if cheap
- <title> - <reason>
  - Confidence: <high/medium/low>
  - Verification: <how the issue was proven real on the PR head>
  - False-positive check: <what was checked to rule out a false positive>
  - Evidence: <file/function/path and why reachable>
  - Prevention: <smallest practical test/check>

## Defer
- <title> - <reason>
  - Confidence: <high/medium/low>
  - Verification: <how the issue was proven real on the PR head>
  - False-positive check: <what was checked to rule out a false positive>
  - Evidence: <file/function/path and why reachable>
  - Follow-up tracking: <Linear link/action, Binder docs/Deferred bugs.md checklist item, or blocker>

## Ignore
- <title> - <reason, including false-positive/stale/unverified basis>

## Review threads resolved
- <thread/comment title> - <already resolved or resolved during this run>

## Should resolve but not resolved
- <thread/comment title> - <why fixed and why not resolved remotely>

## Prevention tests
- <title> - <test/check type, location, and failure it catches>

## Approved execution
- Fix now implemented: <count or not approved>
- Fix if cheap implemented: <count or not approved>
- Prevention added: <count or not approved>
- Binder deferred bugs recorded: <count or not applicable>
- Validation: <commands/workflows run, or not approved>

## Summary
- Fix now: <count>
- Fix if cheap: <count>
- Defer: <count>
- Ignore: <count>
- Prevention tests recommended: <count>
- Linear follow-ups created or linked: <count>
- Binder deferred bugs recorded: <count>
- Recommended next steps: <top 1-3 actions>
```

If a bucket is empty, include the heading and write `- None.`

If inventory is incomplete, say so in `Inventory` and `Summary`; do not present bucket counts as a complete PR triage.

If a claim cannot be verified from the available current-code evidence, do not upgrade it into a real finding just because the reviewer sounded confident. Keep it in `Ignore` and say what proof was missing.

## Concrete Tool Patterns

Use structured GitHub tools first when available. If not, these CLI patterns are acceptable fallbacks:

```bash
gh pr view <number> --json number,title,headRefName,reviewThreads,comments,reviews,statusCheckRollup
gh api graphql -f query='<GraphQL query for pullRequest.reviewThreads>'
gh api graphql -f query='<GraphQL mutation resolveReviewThread(threadId: "...")>'
gh issue list --search '<repo/pr keywords>' --state open --json number,title,url
```

Do not call a review thread resolved unless GitHub already had it resolved or the resolve operation succeeded.

## Worked Example

See [EXAMPLE.md](references/EXAMPLE.md) for a claim -> code verification -> bucket -> prevention recommendation example.

## Operating Rules

- Be concise and decisive.
- Reject weak comments rather than inflating priority.
- Try to disprove the review comment before you try to satisfy it.
- Do not preserve a reviewer's severity when current-code evidence disagrees.
- Unverified claims are not actionable findings.
- Pull current PR comments first when possible.
- Prove inventory completeness before trusting final counts.
- Actually resolve high-confidence fixed inline review threads when tooling is available.
- Create or link Linear issues only for real deferred non-Binder work.
- For Binder, record real deferred bugs in `docs/Deferred bugs.md` as checklist items after the user approves fixes.
- Use `$ce-resolve-pr-feedback` for approved PR review feedback execution; do not use `$binder-review-fix` as the automatic follow-on from this skill.
- Do not write patches unless explicitly asked.
