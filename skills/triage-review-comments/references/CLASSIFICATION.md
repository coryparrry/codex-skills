# Classification Rules

Use exactly one bucket per unique root cause.

## Fix Now

Use `Fix now` when the finding is verified true, reachable in current code, proven not to be a false positive, and meaningful enough to block merge.

Typical examples:
- security boundary issues
- auth or permission bugs
- data loss, data corruption, privacy leaks, or cross-workspace exposure
- crashes in important flows
- common-path correctness failures
- misleading UI that causes a real failed action

Security boundary, authorization, permission, privacy, data loss, and cross-workspace isolation bugs should default here when reachable.

## Fix If Cheap

Use `Fix if cheap` when the finding is verified valid, proven not to be a false positive, but impact is limited, the path is edge-case-heavy, or the patch is only worth taking if it stays small and low-risk.

Typical examples:
- smaller correctness bugs
- limited edge-case failures
- inconsistent but recoverable error handling
- missing tests around a real but narrow risky path
- misleading but recoverable UI state

## Defer

Use `Defer` when the concern is verified real, proven not to be a false positive, but should not block this PR.

Typical examples:
- resilience improvements
- broader refactors disguised as review comments
- valid concerns that need wider design discussion
- real follow-up work that is better in a separate PR

Deferred work should normally become a Linear issue when it is real, specific, likely to matter after merge, and not already tracked.

## Ignore

Use `Ignore` when the comment should not drive work.

Typical examples:
- duplicate of another finding
- stale or retracted comment
- already fixed in current code and safe to resolve
- speculative claim with weak evidence
- unverified claim that could not be proven against current code
- false positive caused by an incorrect premise or outdated snapshot
- false premise
- style-only or preference-only feedback
- technically true but practically irrelevant to the PR

## Confidence

Use `high`, `medium`, or `low`.

- `high`: concrete trigger, clear path, false-positive checks ruled out, little ambiguity.
- `medium`: issue reality and false-positive checks are proven, but impact, frequency, or best bucket still has some uncertainty.
- `low`: plausible concern but weak evidence.

Low-confidence comments should usually become `Ignore`. Do not put an unverified claim into `Fix now`, `Fix if cheap`, or `Defer`.
