# Triage Review Comments Reference

This reference holds the fuller workflow for the `triage-review-comments` skill.

## What the skill is for

Use it to separate real review blockers from bot noise. Every review comment should be treated as a hypothesis that must be checked against the code.

Triage is read-only by default. Only implement fixes, reply to or resolve threads, or create follow-up records when the user explicitly requests that action. Once a class of action is authorized, complete it without asking again for each item.

## Workflow

1. Load the current PR review context first.
2. Build a complete inventory before triaging anything:
   - open inline review threads
   - resolved inline review threads
   - general PR comments
   - review submissions that contain standalone findings
3. Ignore formatting-only summaries, walkthrough notes, automation banners, and status boilerplate unless they contain actionable findings.
4. Deduplicate by underlying issue.
5. Identify fixed inline review threads that could be resolved; mutate GitHub only when resolution or an encompassing fix workflow was explicitly requested.
6. Recommend deferred tracking; create records only when the user asked to create or track them.
7. Evaluate each comment on reachability, impact, evidence, urgency, and prevention.
8. Classify each actionable comment into exactly one bucket:
   - `Fix now`
   - `Fix if cheap`
   - `Defer`
   - `Ignore`
9. For every real issue, recommend the smallest practical prevention test or check.

## Decision rules

- `Fix now`: reachable, meaningful, and should block merge.
- `Fix if cheap`: probably valid, limited in impact, and low-risk to take now.
- `Defer`: real work, but better as follow-up.
- `Ignore`: duplicate, stale, speculative, style-only, or already fixed.

## Thread resolution

When thread resolution is authorized, resolve an inline review thread only when all of these are true:

- the thread is still open
- the underlying concern is addressed by the current code
- the fix is visible in the current PR state, not merely planned
- the original concern no longer needs follow-up discussion
- confidence is high

Do not resolve general PR conversation comments because GitHub does not treat them as resolvable review threads.

## Linear follow-up

For every item classified as `Defer`, decide whether it should become a Linear issue. In read-only mode, report that recommendation without creating it.

When follow-up creation is authorized, create or update a Linear issue only when:

- the deferred item is a real engineering concern
- it is likely to matter after merge
- it is not already tracked in Linear
- it is specific enough to describe clearly

## Prevention

Prefer prevention in this order:

1. Focused regression tests near the changed code
2. Contract, fixture, schema, or decoder tests
3. Integration, smoke, or UI tests
4. Existing repo validation commands added to GitHub Actions
5. Local CLI or pre-push checks
6. Explicit Codex validation steps before push

## Output shape

The response should include:

- inventory counts
- each bucket with short reasons
- review fix briefs for every `Fix now` item
- threads that are already resolved or recommended for resolution
- execution and refetch evidence only when thread mutation was authorized
- prevention tests or checks
- a short summary with next steps

Do not include mutation claims in a read-only report.
