# Apple App Store readiness skill: research delta and implementation path

Status: research only. This document does not create or implement the skill.

Date checked: 10 August 2026

This document accompanies the supplied deep research report,
'deep-research-report-5.md'. It records the verification pass, corrections that
must be made before implementation, and a concrete path for turning the
research into a reliable Codex skill.

## Executive conclusion

The report has the right product shape: a read-only, evidence-producing gate
that combines project inspection, Apple policy mapping, build and release
checks, runtime checks, metadata reconciliation, and reviewer simulation.

It should not become a skill specification unchanged. Four parts need tighter
boundaries first:

1. Source provenance must be explicit. Opaque research markers are not enough
   for a future skill that needs to explain why a finding exists.
2. Toolchain rules must be platform-specific. A single Xcode or SDK rule would
   produce false failures, especially for macOS.
3. Upload readiness and submission readiness must be separate verdicts.
4. Apple requirements, engineering heuristics, and untested assumptions must
   appear as different evidence classes.

The recommended v1 is a deterministic, read-only audit for native Xcode
projects, starting with iOS, iPadOS, and macOS. It should emit an evidence
ledger and a conservative verdict. It should never infer App Store Connect
state from source code and should never call an app ready when required checks
are still untested.

## Audit boundary

The supplied report is 1,234 lines long and contains 133 opaque 'turn...'
citation markers. It does not include a bibliography or direct source URLs.
Those markers were treated as prior research evidence, not as independently
verifiable citations.

The continuation pass checked the report's main claims against current Apple
documentation and repository conventions. It was a bounded root-only audit:

- no independent research lane was needed;
- the original report was left untouched;
- no skill, plugin metadata, repository catalogue, or external service was
  changed during the research pass.

This accompanying document is the first local artifact produced from that
research. It is still a planning document, not the skill itself.

## Findings that remain valid

### Apple review readiness is broader than a successful build

Apple's pre-submission guidance covers complete metadata, a tested binary,
working URLs, reviewer access, live services, review notes, and other
submission details. Apple also states that the checklist does not guarantee
approval.

[Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)

### Guideline 2.1 deserves priority

Apple says that more than 40 percent of unresolved issues relate to Guideline
2.1, which covers app completeness and software bugs. Apple's 2025
transparency report records 9,100,620 submissions reviewed and 2,093,244
rejected. That is a submission count, not an app-level probability of
rejection, so the skill must not present it as one.

[Apple App Review](https://developer.apple.com/app-store/review/)

[App Store Transparency Report 2025](https://www.apple.com/legal/app-store/transparency/2025/)

### A hybrid architecture is the right design

Static inspection alone cannot prove that an app launches cleanly, completes
its main flow, loads products, handles permissions, or gives reviewers access.
Manual testing alone is too inconsistent and leaves no durable explanation for
the result. The skill should combine:

- deterministic project and artifact inspection;
- policy classification based on the app's actual features;
- archive and release checks;
- runtime and manual checks;
- privacy, metadata, and reviewer-access checks;
- evidence-backed verdicts.

### Community precedent is useful but not authoritative

A read-only Apple reviewer skill already exists in the GitHub Awesome Copilot
collection. It is useful precedent for scope and review categories, but it is
not an Apple policy source. The future skill should use community material for
workflow ideas only.

[GitHub Awesome Copilot Apple App Store reviewer skill](https://github.com/github/awesome-copilot/blob/main/skills/apple-appstore-reviewer/SKILL.md)

## Corrections required before implementation

### 1. Make toolchain rules platform-specific

Do not encode a blanket rule that every app must use Xcode 26 or a version 26
SDK.

Apple's current submitting guidance says that, from 28 April 2026, submitted
apps for iOS and iPadOS must use the iOS and iPadOS 26 SDK or later. It gives
corresponding requirements for tvOS, visionOS, and watchOS. The page does not
establish the same minimum for macOS.

The skill should therefore keep separate rules for each platform. A macOS
finding should not inherit an iOS rule unless an Apple source explicitly says
so. The macOS minimum must be resolved from the current Apple source set before
the macOS branch becomes submission-gating.

There is also a source conflict to model. Apple's upload-builds help page still
contains an older Xcode and SDK table, while Apple's upcoming requirements page
describes Xcode 26 and version 26 SDK requirements. The skill needs source
precedence, retrieval dates, and a visible SOURCE_CONFLICT state instead of
silently choosing one page.

[Submitting your apps](https://developer.apple.com/app-store/submitting/)

[Upload builds](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/)

[Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/)

[App Store Connect release notes](https://developer.apple.com/help/app-store-connect/release-notes/)

### 2. Treat Xcode validation as one gate, not the whole result

Xcode's Validate App command performs an initial automated validation before
upload. It does not prove that the app's runtime behavior, metadata,
reviewer-access path, privacy answers, or storefront configuration are ready.

[Xcode Help: Validate your app](https://help.apple.com/xcode/mac/current/en.lproj/dev37441e273.html)

The skill should report archive and validation results as artifact evidence,
then keep runtime, policy, metadata, and reviewer checks separate.

### 3. Split the verdict model

Apple's App Store Connect statuses describe the state of versions and
submissions. They are not the same thing as an internal readiness decision.

The skill should use at least these internal verdicts:

| Verdict | Meaning |
| --- | --- |
| READY_FOR_UPLOAD | Required local artifact and project checks pass, but App Store Connect and review evidence may still be incomplete. |
| READY_FOR_SUBMISSION | Required project, artifact, policy, runtime, metadata, and reviewer-access checks have evidence. |
| HOLD_UNVERIFIED | A required check was not run, could not be observed, or depends on unavailable external state. |
| NO_GO | A blocking defect or policy violation has evidence. |

[App and submission statuses](https://developer.apple.com/help/app-store-connect/reference/app-information/app-and-submission-statuses)

This prevents a passing archive from being reported as approval readiness.

### 4. Apply third-party SDK rules conditionally

Apple's listed third-party SDK requirements apply to new apps that include a
listed SDK and to updates that add one. Required-reason API declarations apply
to the relevant API use, including code supplied by third-party SDKs. A
dependency without the listed manifest is not automatically a blocker.

The skill should identify the dependency, version, embedded binary, privacy
manifest, and required-reason declarations before producing a finding. It
should not turn every package or framework into a failure.

[Third-party SDK requirements](https://developer.apple.com/support/third-party-SDK-requirements/)

[Describing use of required reason API](https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api)

### 5. Preserve the account-deletion exception

For apps that let users create accounts, Apple requires account deletion in the
app for all users. Apple also documents cases where deletion can be completed
outside the app, such as when a process requires additional confirmation or
has a stated timeframe. Legal retention obligations can also limit what is
deleted immediately.

The skill should inspect the actual flow and record the exception evidence. It
should not fail every delayed or manual process without checking whether the
documented conditions apply.

[Offering account deletion in your app](https://developer.apple.com/support/offering-account-deletion-in-your-app/)

### 6. Separate policy facts from engineering heuristics

The report's controls around silent failures, hostile network conditions,
reviewer simulation, and accessibility are good engineering controls. They are
not all Apple-normative requirements. Each finding should identify its basis:

- APPLE_POLICY: directly required or described by Apple;
- APPLE_TOOLCHAIN: an Apple build or submission requirement;
- DETERMINISTIC: proven from the project or artifact;
- RUNTIME: observed during execution;
- MANUAL_HEURISTIC: a recommended quality control;
- UNKNOWN: evidence is missing or inconclusive.

That distinction makes the result useful without overstating what Apple
requires.

### 7. Measure Review Notes as bytes

App Store Connect limits Review Notes to 4,000 bytes. The implementation must
validate the encoded byte count, not only the number of visible characters.

[Platform version information](https://developer.apple.com/help/app-store-connect/reference/app-information/platform-version-information)

### 8. Keep conditional policy rules in the feature map

Rules for third-party login, user-generated content, payments, tracking,
account creation, medical claims, export compliance, and regional obligations
should activate from observed features and declared territories. A missing
feature signal should produce UNKNOWN, not a silent pass.

## Evidence ledger

This is the current disposition of the main research areas.

| Topic | Disposition | Confidence | Implementation consequence |
| --- | --- | --- | --- |
| Hybrid audit design | Supported as a design conclusion | High | Use deterministic, policy, artifact, runtime, and manual evidence together. |
| Guideline 2.1 priority | Verified in current Apple material | High | Make launch, loading, error, and core-flow checks prominent in v1. |
| Xcode 26 and SDK requirements | Verified for iOS, iPadOS, tvOS, visionOS, and watchOS; macOS rule unresolved | High | Use platform-specific rules and SOURCE_CONFLICT handling. |
| Account deletion | Verified, with delayed and legal-retention nuance | High | Inspect the full flow and its documented exception conditions. |
| Third-party login | Verified as a conditional requirement | High | Activate the check only when qualifying login features exist. |
| User-generated content | Verified as a conditional policy area | High | Check filtering, reporting, blocking, contact information, and moderation behavior when UGC exists. |
| Digital payment and storefront logic | Verified as a conditional policy area | High | Inspect what is sold, where it is consumed, and whether the correct payment path is used. |
| Privacy and SDK declarations | Verified as conditional | High | Correlate app behavior, privacy answers, manifests, and required-reason declarations. |
| DSA trader status | Verified as a current App Store Connect concern | High | Reconcile the answer from supplied App Store Connect data; do not infer it from source. |
| Accessibility labels | Verified as a current quality and platform concern | High | Treat accessibility passes as runtime or manual evidence, not as a static policy pass. |
| Archive and Validate App | Insufficient as a complete readiness proof | High | Keep archive evidence separate from submission readiness. |

## Proposed v1 contract

The first implementation should be narrower than the full report.

| Area | v1 boundary |
| --- | --- |
| Project types | Native Xcode projects and workspaces. |
| Platforms | iOS, iPadOS, and macOS, with separate toolchain rules. |
| Frameworks | Do not promise React Native, Flutter, Expo, or other framework-specific behavior until representative fixtures exist. |
| Inputs | Repository path, optional archive or exported app, target platforms, deployment targets, storefronts, new app or update, and optional App Store Connect metadata export. |
| App Store Connect | Support supplied data first. Live asc or API access can be an adapter, not a hidden requirement. |
| Runtime | Run only with tools guaranteed by the target Codex environment. If a required runtime check cannot run, report NOT_TESTED. |
| Mutation | Read-only. No upload, submission, metadata mutation, signing changes, or source edits. |
| Output | Evidence ledger, blocking findings, unresolved questions, verdict, and a concise reviewer handoff. |

The skill should accept an optional release artifact, but it must always record
which exact source, archive, app bundle, or export it inspected. When no
artifact is supplied, it should not imply that a release build was tested.

## Proposed pipeline

~~~mermaid
flowchart TD
    A["Repository and optional release artifact"] --> B["Deterministic project collectors"]
    A --> C["Artifact and archive collectors"]
    S["Apple source registry"] --> D["Policy and platform mapping"]
    B --> D
    C --> D
    D --> E["Feature map with explicit unknowns"]
    E --> F["Evidence ledger"]
    F --> G["Runtime and manual checks"]
    F --> H["App Store Connect reconciliation"]
    G --> I["Readiness gate"]
    H --> I
    I --> J{"Required evidence complete"}
    J -->|yes| K["READY_FOR_UPLOAD or READY_FOR_SUBMISSION"]
    J -->|no| L["HOLD_UNVERIFIED or NO_GO"]
~~~

The central design point is that every policy conclusion must point back to
both an observed app feature and a source entry. Missing observation is not
permission to pass.

## Implementation path

### Phase 0: freeze the contract

Define the exact v1 scope before writing collectors:

- native Xcode projects;
- iOS, iPadOS, and macOS;
- report-only operation;
- optional release artifact;
- optional supplied App Store Connect data;
- no automated submission.

Exit condition: a fixture can state its platform, app lifecycle, storefronts,
new-app or update status, and available evidence without relying on hidden
defaults.

### Phase 1: build a source registry

Create a small versioned registry with one entry per source. Each entry should
contain:

- canonical URL;
- topic and platform scope;
- retrieval date;
- source update date when available;
- precedence;
- policy statements extracted from the source;
- conflict status;
- fallback behavior when the page is unavailable.

The initial registry should cover App Review Guidelines, submission
requirements, upcoming requirements, App Store Connect release notes,
third-party SDK requirements, required-reason APIs, App Privacy, age rating,
accessibility, review information, export compliance, DSA trader status, and
regulated medical apps.

If two Apple pages disagree, preserve both entries and emit
SOURCE_CONFLICT. Do not hide the disagreement in prose.

### Phase 2: write deterministic collectors

Collectors should gather facts without deciding policy:

- Xcode projects, workspaces, schemes, targets, and Release settings;
- bundle identifier, version, build number, deployment target, and SDK;
- signing, entitlements, provisioning, and capabilities;
- Info.plist usage descriptions and URL schemes;
- privacy manifests and required-reason declarations;
- package manifests, dependency versions, and embedded binaries;
- StoreKit products and subscription identifiers;
- relevant source and resource indicators for accounts, onboarding, paywalls,
  permissions, tracking, analytics, UGC, network calls, and external
  processing;
- metadata files, screenshots, previews, URLs, and reviewer instructions when
  they are present in the supplied input.

Static patterns are leads unless the collector can prove the fact. For
example, an imported framework name can suggest tracking, but it does not prove
that the app tracks users.

### Phase 3: create the feature map

The policy engine should consume a normalized feature map rather than search
the whole repository separately for every rule.

Example:

~~~yaml
platforms:
  - ios
  - macos
accounts: true
account_creation: true
third_party_login: false
ugc: false
tracking: false
analytics: true
iap: true
subscriptions: true
ai_external_processing: true
territories:
  - uk
  - eu
  - us
~~~

Every field needs a value, evidence pointer, confidence, and an explicit
unknown state. The example is a schema illustration, not a default app
profile.

### Phase 4: define the evidence model

Every check should produce a structured finding. A useful minimum shape is:

~~~yaml
finding_id: "2.1.account-deletion"
title: "Account deletion is available to account-creating users"
status: "UNKNOWN"
basis: "APPLE_POLICY"
severity: "blocking"
evidence:
  - kind: "source"
    url: "https://developer.apple.com/support/offering-account-deletion-in-your-app/"
    retrieved: "2026-08-10"
  - kind: "runtime"
    value: "not tested"
confidence: "high"
resolution: "Run the account creation and deletion flow on the release candidate."
~~~

The status vocabulary should include PASS, FAIL, NOT_TESTED, UNKNOWN, and
NOT_APPLICABLE. NOT_TESTED must block READY_FOR_SUBMISSION for any required
check.

### Phase 5: add artifact and runtime gates

The release path should identify the exact candidate and then test the flows
that static inspection cannot prove:

- clean install, first launch, relaunch, update, and background recovery;
- offline, slow, timeout, empty, and server-error states;
- permission grant, denial, revocation, and later recovery;
- authentication, logout, expired session, and account deletion;
- StoreKit product loading, purchase, cancellation, restore, expiry, refund,
  and relaunch behavior;
- deep links, QR codes, hardware, external services, and handoff flows;
- accessibility labels and common tasks with assistive technology;
- reviewer credentials, demo mode, and any review-only instructions.

The result should record bundle identifier, version, build number, archive path,
artifact hash, install evidence, runtime environment, and the checks that were
not possible.

### Phase 6: reconcile App Store Connect data

Source code cannot prove the current App Store Connect record. When live access
is unavailable, the skill should say so and accept a supplied export or
snapshot.

Reconcile, where data is available:

- bundle identifier, version, and build;
- privacy policy and support URLs;
- screenshots and app previews;
- age rating and social features;
- App Privacy answers;
- in-app purchase identifiers and paywall mapping;
- export compliance;
- DSA trader status;
- regulated medical declarations;
- reviewer contact information, credentials, notes, and attachments;
- agreements, tax, and banking status when the integration exposes them.

Never infer these fields from source and report them as current App Store
Connect state.

### Phase 7: build fixtures and evaluations

The skill needs adversarial fixtures, not only a clean sample. Start with:

| Fixture | Expected coverage |
| --- | --- |
| Clean app | Baseline pass and artifact identity. |
| Missing account deletion | Conditional policy failure or hold. |
| Login wall without reviewer path | Reviewer-access finding. |
| Social login | Conditional login-policy branch. |
| In-app purchase without restore | StoreKit runtime finding. |
| Product loading failure with no user-visible state | Guideline 2.1 runtime finding. |
| UGC without reporting or blocking | UGC policy finding. |
| Missing permission usage description | Deterministic metadata finding. |
| Tracking SDK with incomplete declarations | Privacy and SDK finding. |
| Missing required-reason declaration | Conditional privacy finding. |
| Toolchain mismatch | Platform-specific build finding. |
| Metadata and binary mismatch | Reconciliation finding. |
| Missing reviewer credentials | Submission hold. |
| Valid account-deletion exception | False-positive control. |

Each fixture should assert not only the final verdict, but also the evidence
class, source link, severity, and explanation.

### Phase 8: package the skill later

Only after the contract, source registry, collectors, evidence model, runtime
strategy, and fixtures are stable should the repository package the skill.

The eventual release work will need:

- canonical source under skills/apple-app-store-readiness/;
- byte-identical plugin mirror under
  plugins/codex-skills/skills/apple-app-store-readiness/;
- the skill agent configuration;
- README, documentation, and skills.sh.json updates;
- plugin manifest version bump;
- mirror, validator, JSON, installer, and diff checks.

That packaging work is intentionally out of scope for this research
continuation.

## Open decisions

These questions should be resolved before implementation starts:

1. Is v1 limited to native Xcode projects, or will it also accept Swift
   Package Manager app layouts?
2. Is macOS a submission-gating platform in v1, or does it remain report-only
   until its current SDK rule is resolved from primary Apple sources?
3. Which App Store Connect input is guaranteed: live asc, API credentials,
   exported metadata, or no integration?
4. Which runtime tools are guaranteed in the target Codex environment?
5. Should the output include a non-mutating submission packet or Review Notes
   draft, and how should generated text be kept within the 4,000-byte limit?
6. How should the source registry refresh and surface changed or conflicting
   Apple guidance?

## Definition of solid

The skill is ready to build when it can do all of the following on fixtures:

- identify the exact app, platform, build, and evidence boundary;
- distinguish Apple policy from a quality heuristic;
- apply platform-specific toolchain rules;
- activate conditional checks from observed features;
- preserve UNKNOWN and NOT_TESTED instead of guessing;
- reconcile source, artifact, runtime, metadata, and App Store Connect evidence;
- explain every blocking result with a source and a resolution;
- avoid calling an app submission-ready when any required evidence is absent.

That is the concrete path from the current report to a skill that can be
trusted in a release workflow.
