# Report format

Lead with results. Keep validated defects, unresolved risks, process blockers, and coverage gaps separate.

## Report order

1. Validated in-scope findings, ordered by priority
2. Pre-existing observations excluded from disposition for change reviews
3. Material unresolved risks
4. Process, policy, duplication, or merge blockers
5. Validation performed
6. Coverage and uncertainty ledger
7. Review disposition
8. Merge readiness when a pull request is in scope

If a section is empty, state `None.` Do not bury a blocker below the coverage narrative.

## Finding contracts

Every finding includes status, confidence, category, trigger, execution or data path, violated invariant, impact, evidence, false-positive check, why tests miss it, smallest fix direction, validation, and remaining uncertainty.

For a change review, also include:

```text
Change relation: introduced | worsened | newly exposed | newly depended upon
Merge effect: <blocking | non-blocking> — <controlling contract or impact>
Changed path: <tight causal file and line>
Affected path: <consumer/config/data/runtime path and line when applicable>
```

For a snapshot audit, include instead:

```text
Snapshot scope: reachable at <exact state>
Audit effect: blocker | material | minor
Causal path: <tight source and consumer/runtime lines>
```

Do not demote a snapshot defect merely because it predates the reviewed state.

Use tight line references for the causal code, not a broad file or the whole diff.

For a change review, put an unrelated pre-existing defect under `Pre-existing observations`, without a review priority or merge effect. Give enough evidence to distinguish it from the reviewed change, but do not let it affect disposition. For a snapshot audit, a reachable pre-existing defect is in scope and belongs in the findings section.

## Priority and confidence

- `P0`: immediate catastrophic impact requiring emergency action.
- `P1`: high-impact, reachable defect that blocks the reviewed change or materially blocks safe operation of the snapshot.
- `P2`: material but limited-scope defect. For a change, state whether it blocks merge under a concrete contract. For a snapshot, state the affected operational scope.
- `P3`: real but low-impact defect.

Priority describes impact and urgency. Confidence describes proof strength. Do not upgrade priority because confidence is low, or upgrade confidence because impact could be severe.

Keep high-severity candidates with uncertain reachability under unresolved risks, not validated findings.

## Unresolved risk contract

Record the claim, potential impact, evidence already checked, exact missing or conflicting evidence, and the next discriminating check. Do not give it a finding priority unless the defect is validated.

## Coverage ledger

Both modes report exact opening/final state, dirty state, final resnapshot, specialist lanes, tests/checks, omission pass, exclusions, unresolved edges, and completeness.

Change reviews additionally report base/head, comparison, pull-request enforcement when applicable, changed paths and artifacts, affected paths, and critical flows.

Snapshot audits additionally report authority, production-area denominator and statuses, supported entry points, shared contracts, critical flows, and unexplained artifacts.

For a snapshot audit, `complete` also requires the gate in [whole-repository-audit.md](whole-repository-audit.md). File counts, import/export inventories, lexical searches, broad test totals, or launched-but-unreturned reviewer lanes do not satisfy production-area, critical-flow, or shared-contract coverage.

## Review disposition

Use review disposition for change reviews. For snapshot audits, report `audit completeness: complete | partial` and `snapshot risk: blockers found | material findings found | no validated findings in completed scope`. Do not call a repository snapshot approved or merge-ready.

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
