# Deep code review

`deep-code-review` performs a language-agnostic, repository-wide review of a pull request, branch, commit, diff, or working tree. It investigates affected behavior beyond changed lines and reports only evidence-backed defects, material unresolved risks, merge blockers, and explicit coverage gaps.

## Install

Install only this skill:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill deep-code-review
```

Install the full bundle:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill '*'
```

## Use

Run the skill from the repository you want to review:

```text
Use $deep-code-review to review this pull request across the repository for validated correctness, security, compatibility, and mergeability risks.
```

Supply the pull request, branch, commit, diff, working tree, or explicit files in scope. Link the issue, specification, or incident when one exists. The skill remains read-only unless you separately request fixes.

## Review method

The skill:

- binds the review to an exact base and head;
- resolves repository and path-specific policy;
- reconstructs intended behavior and preserved invariants;
- distinguishes changed code from affected code and non-code artifacts;
- routes security, concurrency, data, compatibility, dependency, performance, reliability, test, and operations review only when triggered;
- uses deterministic tools and behavioral execution before model speculation;
- checks required-but-missing companion changes and established repository abstractions;
- tries to disprove every candidate finding at the current head;
- reports coverage, unavailable evidence, and withheld verdicts.

Tests and scanner output are evidence, not automatic proof. AI authorship, unusual code, broad exception handling, mocks, scaffolding, and missing files remain search leads until the reviewer proves a reachable violated property.

## Output

Validated findings lead the report and include priority, confidence, exact locations, a reachable trigger, the affected execution or data path, violated invariant, impact, evidence, false-positive check, smallest fix direction, and validation.

The report separates unresolved risks, process or policy blockers, validation performed, coverage, exclusions, and disposition. A partial review cannot approve the complete change. If no finding survives validation, the skill says so rather than inventing comments.

## Skill layout

```text
skills/deep-code-review/
  SKILL.md
  agents/
    openai.yaml
  references/
    evidence-and-validation.md
    impact-and-negative-space.md
    report-format.md
    risk-lanes.md
```

## Related docs

- [Research foundation](Code%20review%20research/README.md)
- [Installation](installation.md)
- [Usage guide](usage.md)
- [Reference](reference.md)
- [Swift code review](swift-code-review.md)
- [Triage review comments](triage-review-comments.md)
