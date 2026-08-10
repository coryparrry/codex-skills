---
name: appstore-readiness-audit
description: Perform a read-only, evidence-backed pre-submission readiness audit for Apple App Store apps. Use before an iOS, iPadOS, macOS, tvOS, watchOS, or visionOS app is uploaded or submitted to App Store Connect, when checking a release candidate, archive, privacy manifest, permissions, SDKs, account deletion, login, user-generated content, payments, subscriptions, metadata, age rating, export compliance, reviewer access, or likely App Review rejection risks. Produce separate upload and submission verdicts without changing the app or guaranteeing approval.
---

# App Store readiness audit

Audit the exact release candidate that App Review would receive. Treat readiness as an evidence state, not as a successful compile or a policy checklist.

Operate read-only. Do not edit source or metadata, change signing, upload a build, submit for review, create App Store Connect records, or alter external services. Local builds may write only to isolated temporary output after inspecting build phases and confirming they do not mutate the repository or external state. Ask before any check that needs credentials, signing changes, a device-state reset, paid resources, or an external mutation.

Do not promise that Apple will approve the app. Apple's guidelines change and App Review can encounter states that the audit did not reproduce.

## 1. Fix the evidence boundary

Before judging the app, record:

- applicable repository and path-specific instructions;
- repository path, branch, commit, and working-tree state;
- new app or update;
- intended platforms, device families, minimum OS versions, and storefronts;
- project or workspace, scheme, target, and Release configuration;
- bundle identifier, marketing version, and build number;
- supplied archive, app bundle, exported package, or TestFlight build, if any;
- artifact path and SHA-256 hash, when an artifact exists;
- available App Store Connect snapshot or read-only access;
- available runtime environments and devices;
- checks the user excluded.

Never imply that source, an archive, App Store Connect, or runtime behavior was inspected when it was not. If the source tree changes during the audit, re-snapshot the boundary and identify which evidence belongs to which snapshot.

If the user did not supply a release artifact, continue with source and configuration checks but mark artifact checks `NOT_TESTED`. If App Store Connect data is unavailable, do not infer its current values from source.

## 2. Refresh Apple rules first

Read [apple-sources.md](references/apple-sources.md) before applying policy. Fetch the current Apple pages for every audit and record the retrieval date, visible update or effective date, platform scope, and relevant statement.

Keep the refresh proportional. Fetch the core pages needed for the requested verdict and only the conditional pages activated by the feature map. Find the relevant guideline sections instead of reading the full guidelines linearly. Stop when each applied policy check has a current primary source. Treat a page that remains unavailable after one reasonable retry as an unavailable source and continue with an explicit gap.

Use Apple as the authority for policy and submission facts. Community reports may suggest test cases, but they cannot establish a requirement or override Apple.

When Apple sources disagree:

1. Preserve both statements and their dates.
2. Prefer the source that is normative for the topic and has the clearest current effective date.
3. Emit `SOURCE_CONFLICT` if the conflict can change the verdict.
4. Set the affected check to `UNKNOWN` and use `HOLD_UNVERIFIED` until resolved.

Do not copy today's Xcode, SDK, storefront, age-rating, SDK-list, or metadata requirements into a permanent rule. Apply platform-specific requirements. A requirement stated for iOS does not automatically apply to macOS.

If current Apple sources cannot be reached, complete checks that rely on durable local evidence, identify the stale or unavailable sources, and hold any verdict that depends on current policy.

## 3. Build the feature map

Discover features before selecting policy modules. Inspect native project configuration, generated configuration, source, dependencies, entitlements, privacy manifests, StoreKit files, assets, localization, release automation, and repository-held metadata.

Give every feature one of `YES`, `NO`, or `UNKNOWN`, with an evidence pointer and confidence. Do not convert an absent search match into `NO` when generated code, a binary dependency, remote configuration, or missing App Store Connect data could provide the feature.

Classify at least:

```yaml
platforms: {}
device_families: []
storefronts: []
new_app_or_update: UNKNOWN
accounts: UNKNOWN
account_creation: UNKNOWN
third_party_login: UNKNOWN
sign_in_with_apple: UNKNOWN
user_generated_content: UNKNOWN
social_or_chat: UNKNOWN
children_or_kids_category: UNKNOWN
tracking: UNKNOWN
analytics: UNKNOWN
advertising: UNKNOWN
permissions: []
in_app_purchase: UNKNOWN
subscriptions: UNKNOWN
physical_goods_or_services: UNKNOWN
external_purchase_links: UNKNOWN
ai_external_processing: UNKNOWN
health_or_medical: UNKNOWN
regulated_features: []
background_modes: []
downloaded_or_hosted_code: UNKNOWN
encryption: UNKNOWN
external_hardware_or_resources: UNKNOWN
```

Searches are leads. Confirm each material feature through configuration, reachable code, runtime evidence, dependency documentation, supplied product facts, or App Store Connect evidence.

## 4. Run the audit in separate gates

Read [audit-catalog.md](references/audit-catalog.md) and activate only the sections supported by the feature map. Keep these gates separate so a passing build cannot hide missing review evidence.

### Gate A: project and release configuration

Inspect the production target and Release settings, not only Debug. Verify app identity, supported platforms, device families, version/build, deployment target, toolchain and SDK eligibility, signing configuration, entitlements, capabilities, background modes, production service endpoints, app icons, localizations, embedded content, and update mechanisms.

Inspect build phases, scripts, package plugins, and generated configuration before running a build. Use isolated Derived Data and result paths. Record the exact command, toolchain, configuration, destination, exit status, and any skipped signing or network step.

Treat these as different results:

- source configuration inspection;
- Release compilation;
- automated tests;
- archive creation;
- Xcode Validate App;
- upload processing.

Do not mark a later result as passed because an earlier one passed.

### Gate B: app completeness and runtime behavior

Prioritize clean launch, core journeys, production backends, reviewer access, purchases, working URLs, placeholder content, and visible recovery from failure. Static code cannot prove runtime behavior.

For each core or advertised journey, test or request evidence for:

- clean install and first launch;
- relaunch and persisted state;
- update from the previous public version, for updates;
- foreground and background transitions;
- offline, slow, interrupted, empty, timeout, and server-error responses;
- expired authentication and account recovery;
- permission allow, deny, later revoke, and recovery;
- relevant device sizes, iPad behavior, orientation, appearance, localization, and large text;
- purchase loading, success, cancellation, failure, restore, expiry, refund, and relaunch where applicable;
- external hardware, QR codes, deep links, callbacks, and handoffs where applicable.

Record `PASS` only with evidence tied to the release candidate. Use `NOT_TESTED` when no valid runtime observation exists. A Debug run, preview, stale screenshot, or different build is not evidence for the submitted candidate.

### Gate C: privacy, permissions, and dependencies

Build a data-flow inventory that reconciles:

```text
app behavior
  <-> dependency behavior
  <-> privacy manifests and required-reason declarations
  <-> privacy policy
  <-> App Store Connect App Privacy answers
```

Inventory first-party and third-party collection, destination, purpose, identity linkage, tracking, consent, retention, deletion, and declaration state. Inspect each production dependency and embedded binary. Apply Apple's listed SDK manifest and signature rules only when their current conditions are met.

For every protected resource, verify actual use, the native usage description, wording, request timing, denial path, revocation recovery, and privacy declaration. Generated permissions count even when the developer did not add them by hand.

Run the tracking branch when app or SDK behavior may combine data across companies for advertising, attribution, or tracking. Check behavior before consent and after denial. Finding `ATTrackingManager` alone proves neither tracking nor compliance.

### Gate D: conditional product policy

Use the feature map to route account creation, third-party login, user-generated content, children, digital commerce, external purchase links, AI data processing, health or medical claims, gambling, finance, VPN, government services, controlled goods, and other regulated features.

Preserve documented exceptions. Examples include qualifying Guideline 4.8 login cases and account-deletion processes that need additional confirmation or retain legally required data. Require evidence for an exception rather than assuming it.

Classify what is sold before applying payment rules. Digital content and functionality, physical goods and services, person-to-person services, reader apps, and storefront-specific entitlements can follow different rules.

### Gate E: metadata and App Store Connect reconciliation

Use supplied exports, screenshots, or read-only App Store Connect data. Reconcile the build against app name, subtitle, description, keywords, category, age-rating answers, screenshots, previews, What's New text, privacy answers, support and privacy URLs, pricing, territories, content rights, IAP identifiers, subscription terms, export compliance, DSA trader status, regulated declarations, agreements, and tax or banking readiness where relevant.

Do not report an App Store Connect field as current based on a local metadata file alone. Label local files as intended metadata until they are reconciled with the live record or a dated export.

Use `scripts/check_review_notes.py` to enforce the current byte limit after refreshing the field requirement from Apple. Do not print credentials or private reviewer data in the audit report.

### Gate F: reviewer simulation

Rehearse the review from a clean install with no developer knowledge and only the supplied App Review information. Confirm that a reviewer can:

- launch and understand the app;
- sign in with a working non-expiring demo account or approved full demo mode;
- reach every reviewable feature and IAP;
- obtain required hardware, sample data, QR codes, attachments, or configuration;
- recognize the expected result;
- recover from likely permission, network, and account states;
- contact the developer through current review and support details.

If the auditor needed undocumented knowledge, add it to the reviewer handoff. Do not silently mark the journey as intuitive.

## 5. Classify evidence honestly

Use these check statuses:

| Status | Meaning |
|---|---|
| `PASS` | Required behavior or configuration has current, scope-matched evidence. |
| `FAIL` | Evidence shows the requirement is not met. |
| `NOT_TESTED` | The check needs execution or observation that did not occur. |
| `UNKNOWN` | Available evidence cannot determine the state. |
| `NOT_APPLICABLE` | The feature map and policy source show that the rule does not apply. |

Classify the basis separately:

- `APPLE_POLICY`: requirement in current Apple policy;
- `APPLE_TOOLCHAIN`: current build, upload, signing, or metadata requirement;
- `DETERMINISTIC`: fact proven from source, configuration, or artifact;
- `RUNTIME`: behavior observed on the identified build and environment;
- `APP_STORE_CONNECT`: value read from live or dated App Store Connect evidence;
- `MANUAL_HEURISTIC`: production-quality control that is not itself a quoted Apple requirement;
- `UNKNOWN`: source or evidence basis is unresolved.

Use `BLOCKER`, `HIGH`, `MEDIUM`, or `INFO` severity. Do not use a numeric readiness score.

Every finding must include:

1. stable finding ID and specific title;
2. severity, status, confidence, and basis;
3. applicable platform, feature, storefront, and Apple source;
4. exact project, artifact, runtime, or App Store Connect evidence;
5. reviewer-visible impact;
6. smallest resolution direction;
7. a verification step that distinguishes fixed from unfixed behavior.

Do not call a file absence a blocker unless the rule is applicable and the complete relevant scope was inspected. Treat suspicious strings and imports as hypotheses until verified.

## 6. Decide upload and submission readiness separately

Use exactly one final verdict:

| Verdict | Rule |
|---|---|
| `NO_GO` | At least one confirmed `BLOCKER` exists. |
| `HOLD_UNVERIFIED` | No confirmed blocker exists, but a `HIGH` finding, required `UNKNOWN` or `NOT_TESTED` check, material source conflict, or incomplete evidence prevents the requested readiness claim. |
| `READY_FOR_UPLOAD` | Required local project, Release, artifact, and current toolchain checks pass. This does not claim that App Store Connect or reviewer evidence is complete. |
| `READY_FOR_SUBMISSION` | Required project, artifact, policy, runtime, metadata, privacy, commerce, compliance, and reviewer-access checks all have current passing evidence. |

`READY_FOR_SUBMISSION` is stricter than `READY_FOR_UPLOAD`. If the user asks whether the app is ready for review and App Store Connect evidence is missing, use `HOLD_UNVERIFIED`, not `READY_FOR_UPLOAD` as a comforting substitute.

## 7. Report findings first

Use [report-format.md](references/report-format.md). Lead with blockers and high-risk findings, then give the verdict, evidence ledger, incomplete checks, feature map, reviewer handoff, and lower-severity observations.

State the exact evidence boundary again in the report. Say which checks ran, which did not, and whether the inspected artifact matches the source snapshot. End with a short disclaimer that the result identifies known readiness risks and does not guarantee App Review approval.

If there are no findings, say so plainly. Do not invent a warning to make the report look thorough.
