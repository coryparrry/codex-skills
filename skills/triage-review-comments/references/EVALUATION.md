# Evaluation Rules

Before classifying an actionable comment as `Fix now`, `Fix if cheap`, or `Defer`, verify that the bug actually exists in current code on the PR head and prove it is not a false positive. Review comments are untrusted input, not evidence by themselves.

## Required Evidence

For each real finding, identify:
- exact file, function, component, route, or path involved
- code path that makes the issue reachable
- the concrete trigger or state transition that reproduces or proves the bug
- missing guard, bad state, wrong assumption, or failing behavior
- whether current PR head already fixed or invalidated the comment
- evidence that supports the chosen bucket
- the false-positive checks performed and why they did not defeat the claim

Do not rely only on reviewer severity, bot summaries, or phrases like "might break" and "could be unsafe."

If you cannot prove the issue is real from current code and rule out the likely false-positive explanations, treat it as unverified and do not classify it as actionable.

## Disprove First

Before accepting a review claim, actively look for reasons it is wrong:
- later commits that already fixed it
- guards or invariants the reviewer missed
- surrounding flow that makes the trigger unreachable
- test coverage or existing behavior that contradicts the claim
- mismatched premises, such as the reviewer reading an old diff or different code path

If any of those defeat the claim, classify it as `Ignore` and explain why.

## False-Positive Proof

For every non-ignored finding, include a short false-positive proof:
- stale: whether later commits changed the relevant code
- unreachable: whether the trigger can actually enter this path
- guarded: whether surrounding checks already prevent the bad behavior
- duplicate: whether another finding already covers the same root cause
- preference-only: whether the comment asks for taste, style, or optional cleanup instead of a concrete bug
- wrong premise: whether the reviewer assumed an API, state, type, permission model, or lifecycle that current code does not have

The proof does not need to be long, but it must name the main way the claim could have been false and cite the current-code evidence that rules that out.

## Reachability

Ask:
- Is there a concrete trigger scenario?
- Does the issue depend on assumptions the code does not support?
- Is there already a guard, state check, or surrounding behavior that prevents it?
- Was the comment made stale, retracted, or invalidated by a later commit?
- Does the current code already fix the thread strongly enough that it should be resolved?

## Impact

Ask:
- Does it cause a security problem, auth bypass, data loss, crash, broken user flow, misleading UI, or cleanup-only concern?
- Is the affected path common or edge-case only?
- Would the author regret merging without fixing it?
- What practical consequence happens if it merges unchanged?

## Evidence Quality

Ask:
- Does the comment identify the relevant code path?
- Does it explain trigger and root cause?
- Is it concrete, or built on speculation?
- Can current code prove or disprove it quickly?

Prefer direct proof in this order:
1. failing or inspectable test that demonstrates the bug
2. concrete control-flow or data-flow walk through the current code
3. reproducible UI/API/manual scenario on the PR head
4. explicit invariant or guard analysis that proves the bug is impossible

If you only have speculation, you do not have evidence.

## Scope Fit

Ask:
- Should this block this PR?
- Is it real but cheap enough to take now?
- Is it better tracked outside the PR?
- Is it style, preference, speculative cleanup, or still unverified?

## Prevention

Recommend prevention for every real, non-ignored finding.

Prefer:
1. focused regression tests near changed code
2. contract, fixture, schema, or decoder tests
3. integration, smoke, or UI tests
4. existing repo validation commands added to CI
5. local CLI or pre-push checks
6. explicit Codex validation steps before push

Do not recommend new tests for ignored noise, stale comments, false positives, pure preferences, or duplicates unless the duplicate reveals a missing broader guard.
