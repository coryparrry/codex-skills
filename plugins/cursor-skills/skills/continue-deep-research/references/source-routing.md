# Source routing

Choose sources according to the question. Prefer the most direct authoritative evidence and inspect the exact supporting section.

## Software, languages, and code review

Prioritize:

1. Normative specifications, language evolution proposals, and official documentation.
2. Source code and tests for actual implementation behavior.
3. Issue trackers, pull requests, code-review threads, and release notes for regressions, rationale, and version availability.
4. Maintainer forum posts or conference material for design context.
5. Independent technical analysis only after the primary record is understood.

Check compiler, language, SDK, dependency, and platform versions; feature flags; warning versus error behavior; accepted proposal versus shipped implementation; and whether a report concerns intended semantics, a bug, a diagnostic limitation, or a local style rule.

### Swift code-review example

For a reported Swift issue:

- recover the exact review claim and surrounding code rather than researching a paraphrase;
- identify the Swift language mode, compiler and Xcode version, platform SDK, build settings, strict-concurrency level, and relevant annotations;
- inspect the accepted Swift Evolution proposal or official language documentation;
- inspect relevant `swiftlang/swift` source, tests, issues, pull requests, and release notes;
- use Swift Forums to recover design rationale, while distinguishing discussion from an accepted or implemented rule;
- separate compile-time legality, diagnostic quality, runtime behavior, API design, and team convention;
- note whether the conclusion changes across Swift versions or isolation regions;
- link the exact proposal, issue, pull request, test, documentation section, or review comment that supports the finding.

## Standards and protocols

Use the normative specification, errata, version history, conformance tests, and implementation notes. Separate required behavior from optional guidance and deployed convention.

## Academic and scientific research

Use the original paper, dataset, methods, preregistration, code, corrections or retractions, systematic reviews, and meaningful replications. Check sample, controls, effect size, uncertainty, external validity, conflicts, and whether a preprint was later revised.

## Security research

Use vendor advisories, upstream source and fixes, CVE records, authoritative vulnerability databases, release notes, and defensive validation. Distinguish affected versions, exploitability conditions, observed impact, theoretical weakness, and remediated state.

## Legal, regulatory, medical, and financial research

Treat accuracy as high stakes and browse current authoritative sources by default. Prefer statutes, regulations, court or regulator records, official clinical guidance, product labels, filings, audited statements, and primary datasets. State jurisdiction, effective date, population, and professional-advice limits where relevant.

## Current events and public claims

Use primary records, official statements, transcripts, filings, datasets, and independent reputable reporting. Compare event dates with publication dates. Treat early accounts and anonymous claims as provisional.

## Product, market, and user research

Use raw research artifacts, methodology, sample characteristics, analytics definitions, official pricing or product documentation, filings, and direct competitive evidence. Check selection bias, survivorship bias, metric definitions, regional differences, and date-sensitive availability.

## Source-quality tests

For every material source, ask:

- Does it directly support this exact claim?
- Is it primary, authoritative, current, and applicable to the relevant version or scope?
- Is the quoted or summarized section representative of the full source?
- Does the source report observation, interpretation, policy, intent, or measured behavior?
- Is there a correction, superseding version, conflict, or incentive that changes its weight?
