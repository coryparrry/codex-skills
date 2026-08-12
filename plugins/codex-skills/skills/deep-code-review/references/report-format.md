# Report format

Lead with results. Keep validated defects, unresolved risks, process blockers, and coverage gaps separate.

## Report order

1. Validated change-related findings, ordered by priority
2. Pre-existing observations excluded from disposition
3. Material unresolved risks
4. Process, policy, duplication, or merge blockers
5. Validation performed
6. Coverage and uncertainty ledger
7. Review disposition
8. Merge readiness when a pull request is in scope

If a section is empty, state `None.` Do not bury a blocker below the coverage narrative.

## Finding contract

```text
[P1] Short behavioral title

Status: validated
Confidence: confirmed | high
Category: correctness | security | privacy | data | compatibility | concurrency | reliability | performance | dependency | operations | accessibility | internationalization | platform | maintainability | policy
Change relation: introduced | worsened | newly exposed | newly depended upon
Merge effect: <blocking | non-blocking> — <controlling contract or impact>

Changed path: <tight file and line>
Affected path: <consumer/config/data/runtime path and line when applicable>
Trigger: <smallest reachable scenario>
Execution or data path: <source through affected behavior>
Violated invariant: <property that must remain true>
Impact: <observable consequence>
Evidence: <repository, tool, runtime, test, or history evidence>
False-positive check: <alternative explanation or safeguard tested>
Why tests miss it: <reason or not applicable>
Smallest fix direction: <behavioral direction, not a speculative patch>
Validation: <check that distinguishes broken from corrected behavior>
Remaining uncertainty: <none or explicit limit>
```

Use tight line references for the causal code, not a broad file or the whole diff.

Put an unrelated pre-existing defect under `Pre-existing observations`, without a review priority or merge effect. Give enough evidence to distinguish it from the reviewed change, but do not let it affect disposition.

## Priority and confidence

- `P0`: immediate catastrophic impact requiring emergency action.
- `P1`: high-impact, reachable defect that should block merge.
- `P2`: material but limited-scope defect. State whether it blocks merge under a concrete compatibility, policy, product, release, or operational contract.
- `P3`: real but low-impact defect that need not block merge.

Priority describes impact and urgency. Confidence describes proof strength. Do not upgrade priority because confidence is low, or upgrade confidence because impact could be severe.

Keep high-severity candidates with uncertain reachability under unresolved risks, not validated findings.

## Unresolved risk contract

Record the claim, potential impact, evidence already checked, exact missing or conflicting evidence, and the next discriminating check. Do not give it a finding priority unless the defect is validated.

## Coverage ledger

```text
Review state
- Opening base/head: <sha or supplied boundary>
- Final base/head: <sha or working-tree snapshot>
- Comparison: <merge-base, direct, parent, combined, pasted-only>
- Dirty state: <summary>
- Final resnapshot: unchanged | changed and revalidated, with details
- Pull-request enforcement state: <draft, conflicts, current-head checks, required reviews, unresolved conversations, branch/rules, stale approvals, duplicate or superseding change; or unavailable/not applicable>

Coverage
- Changed paths inspected: <count/count>
- Changed symbols or artifacts classified: <count/count or method>
- Affected paths traced: <summary>
- Critical flows traced: <summary>
- Specialist lanes run: <list and triggers>
- Tests/checks run: <commands and results>
- History/policy/config/data/release surfaces: <summary>
- Omission pass: <independent, self-check only, or unavailable; plus leads validated>

Excluded or unavailable
- <surface and reason>

Unresolved
- <edge, assumption, environment, or runtime gap>

Completeness: complete | partial
```

## Review disposition

- `request changes`: at least one validated P0 or P1, explicitly merge-blocking P2, or validated policy, process, compatibility, or release blocker survives. A partial review may request changes for a proven blocker in the reviewed scope.
- `approve`: the inventory and required review lanes are complete, no validated finding or blocker survives, and no material unresolved risk or decision-blocking validation gap prevents approval.
- `comment`: only non-blocking P2 or P3 findings, non-blocking policy notes, or decision questions remain after a complete review.
- `not assessed`: scope, exact state, or required evidence is too incomplete to judge the whole change and no validated blocker establishes `request changes`. Use `not assessed — validation required` for a decision-blocking validation gap.

Never use `approve` for a partial review. If no finding survives, write `No validated findings.` and still report the validation and coverage limits.

Review disposition is not automatically a claim that GitHub will permit or should perform a merge.

## Merge readiness

For a pull request, report one separate state:

- `ready`: the final head is authoritative and unchanged; the pull request is not a draft; conflicts are absent; required checks passed on the current head; required reviews are satisfied and not stale; required conversations are resolved; applicable branch protection or rulesets are satisfied; and no known duplicate or superseding change blocks the merge.
- `blocked`: a verified repository or GitHub requirement prevents merge. Name each blocker.
- `not assessed`: any required pull-request or enforcement state is unavailable, stale, or ambiguous.
- `not applicable`: no pull request is in scope.

Do not infer `ready` from a clean code review, GitHub's coarse `mergeable` field, or checks from an earlier commit.
