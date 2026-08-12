# Swift Code Review

`swift-code-review` reviews Swift and Apple-platform changes. It covers SwiftUI, AppKit, concurrency, persistence, packages, Xcode configuration, and mixed-language code.

The skill finds reachable errors that a compiler or a passing test can miss. These errors include ownership, isolation, identity, and lifetime failures.

## Install

To install only this skill, run:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill swift-code-review
```

To install all skills, run:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill '*'
```

## Use

Use this prompt:

```text
Use $swift-code-review to review these Swift and SwiftUI changes for concrete correctness and regression risks.
```

Provide one of these review inputs:

- Files or paths
- Staged and unstaged changes
- A commit, branch, tag, or fixed point
- A pull request
- A pasted diff

The skill does not change code unless you also request fixes.

## What It Reviews

The skill first identifies the review scope, intended behavior, project rules, and active Swift environment.

Then it loads only the reference files that apply to the affected invariants.

| Changed surface | Review focus |
|---|---|
| Actors, tasks, callbacks, locks, streams, ARC | Isolation, transfer, cancellation, freshness, reentrancy, and teardown |
| SwiftUI and AppKit | Source of truth, identity, observation, async lifetime, state matrices, parent/child layout budgets, transactions, accessibility, windows, and bridges |
| Parsers, persistence, unsafe code, and public APIs | Representation, bounds, retries, side effects, migrations, runtime support, security, and resources |
| Packages, Xcode configuration, macros, and generated code | Build inputs, dependencies, tools, resources, compatibility, and generated behavior |
| AI-assisted changes | Missing assumptions and proof without treating authorship as a defect |

The skill reads relevant callers, alternate entry points, tests, failure paths, and teardown paths. It re-snapshots the changed-path inventory when the checkout changes and rechecks adjacent retained, incomplete, empty, failure, and replacement states after follow-up fixes. The displayed diff is not the complete contract.

## Findings

Each finding contains:

- Priority and confidence
- Change relation
- Exact locations
- Reachable trigger
- Broken invariant and impact
- Evidence and correction
- Validation or proof

The report also states its scope, completeness, validation gaps, and disposition.

Moderate-confidence concerns remain questions or validation gaps. If no material finding survives, the skill does not invent a comment.

## Skill Layout

```text
skills/swift-code-review/
  SKILL.md
  agents/
    openai.yaml
  references/
    concurrency-and-lifetime.md
    data-api-and-platform-boundaries.md
    evidence-and-ai.md
    swiftui-and-appkit.md
```

## Related Docs

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [Reference](reference.md)
- [Deep Code Review](deep-code-review.md)
- [Triage Review Comments](triage-review-comments.md)
