# Apple source registry

Use this registry at the start of every audit. Fetch only current Apple sources, record the retrieval date, and quote or paraphrase the smallest statement needed for each check. Do not treat the dates or requirements captured during skill development as permanent.

## Contents

- [Source rules](#source-rules)
- [Core sources](#core-sources)
- [Conditional sources](#conditional-sources)
- [Conflict handling](#conflict-handling)
- [Freshness record](#freshness-record)

## Source rules

Use sources in this order for the topic they govern:

1. App Review Guidelines for review policy.
2. A dated Apple submission or upcoming-requirements notice for a toolchain effective date.
3. App Store Connect Help for field requirements, limits, statuses, and operational steps.
4. Apple Developer Support or framework documentation for implementation-specific requirements.
5. Apple release notes for a change that has not yet reached another page.

Do not resolve a contradiction by list order alone. Compare platform scope, publication or update date, effective date, and whether the page is normative for the claim.

Use community material only to design tests or find failure modes. Label it `MANUAL_HEURISTIC`; do not cite it as Apple policy.

## Core sources

| Topic | Current source | Use |
|---|---|---|
| App Review policy and pre-submission checklist | [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) | Refresh the guideline text, update date, completeness rules, reviewer access, metadata, privacy, business, design, and legal requirements. |
| Current upload baseline | [Submitting apps and games](https://developer.apple.com/app-store/submitting/) | Resolve minimum SDK requirements separately for each stated platform and record the effective date. Do not infer an unstated macOS minimum. |
| Scheduled changes | [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/) | Record requirements already in force and changes becoming effective within 90 days. |
| App Store Connect changes | [App Store Connect release notes](https://developer.apple.com/help/app-store-connect/release-notes/) | Check recent field, questionnaire, submission, and processing changes. |
| Build upload requirements | [Upload builds](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/) | Compare upload tooling and platform requirements with dated submission notices. Preserve conflicts. |
| Archive validation | [Validate an archive](https://help.apple.com/xcode/mac/current/en.lproj/dev37441e273.html) | Establish what Xcode Validate App checks. Do not treat validation as runtime or policy proof. |
| App Review information | [Platform version information](https://developer.apple.com/help/app-store-connect/reference/app-information/platform-version-information) | Refresh reviewer contact, credential, Notes, metadata, and field-limit requirements. Count Notes in UTF-8 bytes when Apple specifies bytes. |
| App and submission states | [App and submission statuses](https://developer.apple.com/help/app-store-connect/reference/app-information/app-and-submission-statuses) | Keep Apple's operational statuses separate from internal readiness verdicts. |
| Required properties | [Required, localizable, and editable properties](https://developer.apple.com/help/app-store-connect/reference/required-localizable-and-editable-properties/) | Identify required metadata by platform, version state, territory, and feature. |

## Conditional sources

Load a source when the feature map activates its topic.

| Trigger | Apple source | Checks |
|---|---|---|
| Any data collection or third-party code | [App privacy details](https://developer.apple.com/app-store/app-privacy-details/) | Reconcile data types, purposes, identity linkage, tracking, and third-party behavior. |
| Listed SDK or embedded dependency | [Third-party SDK requirements](https://developer.apple.com/support/third-party-SDK-requirements/) | Refresh the listed SDKs and conditions for privacy manifests and signatures. Do not fail every dependency. |
| Required Reason API use | [Describing use of required reason API](https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api) | Match observed API categories to approved reasons in the relevant privacy manifests. |
| Tracking or advertising | [User privacy and data use](https://developer.apple.com/app-store/user-privacy-and-data-use/) | Check ATT, pre-consent behavior, denial behavior, and prohibited workarounds. |
| Account creation | [Offering account deletion](https://developer.apple.com/support/offering-account-deletion-in-your-app/) | Check in-app initiation, deletion outcome, Sign in with Apple token revocation, timing, confirmation, and legal-retention exceptions. |
| Age-sensitive content or social features | [Set an app age rating](https://developer.apple.com/help/app-store-connect/manage-app-information/set-an-app-age-rating/) | Reconcile the current questionnaire, regional ratings, controls, and capabilities. |
| Accessibility declarations | [Accessibility Nutrition Labels](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/manage-accessibility-nutrition-labels/) | Verify each claimed feature per platform and common task. Do not turn voluntary metadata into a policy blocker. |
| Digital goods, subscriptions, or external purchase links | [App Review Guidelines, section 3](https://developer.apple.com/app-store/review/guidelines/#business) | Classify what is sold, where it is consumed, storefront rules, restore behavior, and allowed exceptions. |
| In-App Purchase | [In-App Purchase overview](https://developer.apple.com/help/app-store-connect/manage-in-app-purchases/overview-for-configuring-in-app-purchases/) | Reconcile products, identifiers, review state, and commercial prerequisites. |
| Encryption | [Export compliance overview](https://developer.apple.com/help/app-store-connect/manage-app-information/overview-of-export-compliance/) | Classify encryption and required answers or documentation. Do not equate HTTPS with non-exempt custom encryption. |
| EU availability | [Digital Services Act trader requirements](https://developer.apple.com/help/app-store-connect/manage-compliance-information/manage-european-union-digital-services-act-trader-requirements/) | Reconcile declared trader status and verification. Do not make the legal determination for the developer. |
| Privacy policy | [App Review Guidelines, section 5.1](https://developer.apple.com/app-store/review/guidelines/#privacy) | Verify that the in-app and metadata links exist and that the policy matches collection, sharing, retention, consent, and deletion. |
| Mac App Store | [App Review Guidelines, section 2.4.5](https://developer.apple.com/app-store/review/guidelines/#performance) | Check sandboxing, packaging, installers, login items, downloaded code, update mechanisms, privileges, and bundle contents. |

For medical, finance, gambling, VPN, children, government, controlled goods, dating, news, reader apps, creator content, streaming, or other regulated features, route to the applicable current guideline subsection and App Store Connect property documentation. Record any external legal conclusion as user-supplied or legal evidence, not as an agent inference.

## Conflict handling

Use this record when two Apple pages differ:

```yaml
topic: "minimum SDK for <platform>"
status: SOURCE_CONFLICT
sources:
  - url: "<url>"
    retrieved: "YYYY-MM-DD"
    visible_updated: "<date or unavailable>"
    effective: "<date or unavailable>"
    statement: "<short paraphrase>"
  - url: "<url>"
    retrieved: "YYYY-MM-DD"
    visible_updated: "<date or unavailable>"
    effective: "<date or unavailable>"
    statement: "<short paraphrase>"
impact: "<affected check and platform>"
resolution: "<authoritative confirmation needed>"
```

If the conflict affects eligibility, use `UNKNOWN` for the check and `HOLD_UNVERIFIED` for submission readiness.

## Freshness record

Start the audit with:

```yaml
retrieved_at: "YYYY-MM-DDTHH:MM:SSZ"
app_review_guidelines:
  url: "https://developer.apple.com/app-store/review/guidelines/"
  visible_updated: "<date or unavailable>"
platform_requirements:
  ios: "<current statement and effective date>"
  ipados: "<current statement and effective date>"
  macos: "<current statement or UNKNOWN>"
  tvos: "<current statement and effective date>"
  watchos: "<current statement and effective date>"
  visionos: "<current statement and effective date>"
upcoming_within_90_days: []
source_conflicts: []
unavailable_sources: []
```

Store the source URL beside every policy finding. Do not use an opaque research marker as the final citation.
