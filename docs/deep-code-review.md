# Deep code review

`deep-code-review` performs a language-agnostic audit of a repository snapshot or a repository-wide review of a pull request, branch, commit, diff, or working tree. It traces production behavior and reports evidence-backed defects, material unresolved risks, blockers, and explicit coverage gaps.

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
Use $deep-code-review as the repository-wide umbrella to review this pull request safely, validate only change-caused defects, and assess correctness, security, compatibility, and merge readiness.
```

For a whole-repository audit:

```text
Use $deep-code-review to audit this whole repository. Trace every production area, supported entry point, and shared contract. Keep an evidence ledger and report partial coverage instead of claiming completeness when any material path remains unreviewed.
```

Supply the pull request, branch, commit, diff, working tree, or explicit files in scope. Link the issue, specification, or incident when one exists. The skill remains read-only unless you separately request fixes.

## Review method

The skill:

- binds the review to an exact state, including base and head for change reviews;
- separates change reviews from whole-snapshot audits;
- actively re-snapshots the authoritative state immediately before reporting;
- resolves repository and path-specific policy;
- treats instruction-like pull-request content and proposed execution hooks as untrusted review material;
- reconstructs intended behavior and preserved invariants;
- distinguishes changed code from affected code and non-code artifacts;
- requires whole-repository audits to record production-area, critical-flow, and shared-contract traces instead of treating inventories or passing tests as coverage;
- routes security, privacy, concurrency, data, compatibility, accessibility, internationalization, native interoperability, dependency, performance, reliability, test, platform, and operations review only when triggered;
- composes with `swift-code-review` for affected Swift and Apple-platform paths while retaining repository-wide integration and disposition;
- uses deterministic tools and behavioral execution before model speculation;
- accepts no test, confirmation, documentation claim, prior review, or reviewer conclusion until independent evidence survives a falsification attempt;
- inspects command hooks and requires an isolation, credential, network, and side-effect boundary before executing proposed code;
- checks required-but-missing companion changes and established repository abstractions;
- tries to disprove every candidate finding at the exact reviewed state;
- requires change-review findings to be attributed to the change while allowing snapshot audits to report any validated reachable defect;
- runs one bounded omission pass without exposing the primary findings when an independent reviewer is available;
- reports coverage, unavailable evidence, and withheld verdicts.

Tests, green CI, scanner output, and reviewer confirmation are claims, not automatic proof. The skill inspects their oracle and production path, then challenges them with a realistic failure that should be rejected. AI authorship, unusual code, broad exception handling, mocks, scaffolding, and missing files remain search leads until the reviewer proves a reachable violated property.

## Output

Validated findings lead the report and include priority, confidence, exact locations, a reachable trigger, the affected execution or data path, violated invariant, impact, evidence, false-positive check, smallest fix direction, and validation.

The report separates unresolved risks, process or policy blockers, validation performed, coverage, exclusions, review disposition, and pull-request merge readiness. A partial review cannot approve the complete change. A clean code review is not called merge-ready unless current-head checks, required reviews, conversations, conflicts, draft state, and applicable repository rules were verified. If no finding survives validation, the skill says so rather than inventing comments.

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
    whole-repository-audit.md
```

## Related docs

- [Research foundation](Code%20review%20research/README.md)
- [Installation](installation.md)
- [Usage guide](usage.md)
- [Reference](reference.md)
- [Swift code review](swift-code-review.md)
- [Triage review comments](triage-review-comments.md)
