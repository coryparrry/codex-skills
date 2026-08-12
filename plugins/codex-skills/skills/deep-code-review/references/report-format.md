# Report format

Lead with results. Keep validated defects, unresolved risks, process blockers, and coverage gaps separate.

## Report order

1. Validated findings, ordered by priority
2. Material unresolved risks
3. Process, policy, duplication, or merge blockers
4. Validation performed
5. Coverage and uncertainty ledger
6. Disposition

If a section is empty, state `None.` Do not bury a blocker below the coverage narrative.

## Finding contract

```text
[P1] Short behavioral title

Status: validated
Confidence: confirmed | high
Category: correctness | security | data | compatibility | concurrency | reliability | performance | dependency | operations | maintainability | policy

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

## Priority and confidence

- `P0`: immediate catastrophic impact requiring emergency action.
- `P1`: high-impact, reachable defect that should block merge.
- `P2`: material correctness, security, reliability, compatibility, or operational defect that should normally be fixed before merge.
- `P3`: real but low-impact defect that need not block merge.

Priority describes impact and urgency. Confidence describes proof strength. Do not upgrade priority because confidence is low, or upgrade confidence because impact could be severe.

Keep high-severity candidates with uncertain reachability under unresolved risks, not validated findings.

## Unresolved risk contract

Record the claim, potential impact, evidence already checked, exact missing or conflicting evidence, and the next discriminating check. Do not give it a finding priority unless the defect is validated.

## Coverage ledger

```text
Review state
- Base: <sha or supplied boundary>
- Head: <sha or working-tree snapshot>
- Comparison: <merge-base, direct, parent, combined, pasted-only>
- Dirty state: <summary>

Coverage
- Changed paths inspected: <count/count>
- Changed symbols or artifacts classified: <count/count or method>
- Affected paths traced: <summary>
- Critical flows traced: <summary>
- Specialist lanes run: <list and triggers>
- Tests/checks run: <commands and results>
- History/policy/config/data/release surfaces: <summary>

Excluded or unavailable
- <surface and reason>

Unresolved
- <edge, assumption, environment, or runtime gap>

Completeness: complete | partial
```

## Disposition

- `request changes`: at least one validated P0-P2 defect survives. A partial review may request changes for a proven blocker.
- `approve`: the inventory and required review lanes are complete, no validated P0-P2 defect survives, and no material unresolved risk or policy blocker prevents approval.
- `comment`: only P3 findings, non-blocking policy notes, or decision questions remain after a complete review.
- `not assessed`: scope or evidence is too incomplete to judge the whole change and no validated blocker establishes `request changes`.

Never use `approve` for a partial review. If no finding survives, write `No validated findings.` and still report the validation and coverage limits.
