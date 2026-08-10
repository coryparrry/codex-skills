# Apple App Store Pre‑Submission Readiness Research

## Executive assessment

The most important conclusion from Apple’s current documentation is that **“App Store ready” should be treated as a release-engineering state, not as the point at which an app happens to compile or looks finished to its developer**. Apple explicitly asks developers, before submission, to test for crashes and bugs, complete all metadata, maintain current contact details, provide App Review with full access, keep back-end services live, and explain non-obvious functionality and purchases in Review Notes. Apple also states that this checklist does **not** guarantee approval because the App Review Guidelines are a living document. citeturn13view0turn16search17

This distinction matters in practice. Apple says **more than 40% of unresolved App Review issues are related to Guideline 2.1, App Completeness**, which includes crashes, placeholder content and incomplete information. In Apple's 2025 transparency report, 9,100,620 submissions were reviewed and 2,093,244 were rejected — roughly **23% of submissions**. Performance-related guidelines were cited in 1,354,418 rejection instances, far more than any other top-level guideline section. Multiple guidelines can apply to the same rejection, so those category figures should not be interpreted as mutually exclusive rejection counts. citeturn13view1turn13view2

That evidence strongly suggests that the proposed agent should not merely be a “policy checker”. It should be a **pre-release auditor and reviewer simulator** that combines:

1. source/configuration inspection;
2. Apple-policy classification;
3. release-build and archive validation;
4. runtime/manual test requirements;
5. privacy and SDK analysis;
6. App Store Connect metadata validation;
7. business/legal/compliance checks;
8. reviewer-access simulation;
9. evidence-backed GO/HOLD/NO-GO output.

A useful skill should also be **read-only by default**. Existing open-source App Store-review skills increasingly use that pattern: GitHub's `awesome-copilot` App Store reviewer tells the agent to make no code changes initially and to inspect the project, entitlements, privacy manifests, StoreKit configuration, onboarding and paywalls first; `app-store-review-risk` similarly emphasises file-backed findings without promising approval. Other projects divide review logic into Safety, Performance, Business, Design and Legal modules mirroring Apple's own guideline structure. citeturn17search2turn17search3turn17search1

**My recommended readiness definition is therefore:**

> **READY TO UPLOAD** means that no known blocking or high-risk App Review issue remains; the release configuration and archive have been validated; every core user journey has been tested on relevant real-device configurations; privacy, permissions, dependencies, payments and account behaviour agree with App Store Connect declarations; reviewer access has been rehearsed from a clean installation; and every claim is supported by evidence.

That wording intentionally avoids “will pass App Review”. Apple itself says following its pre-submission checklist does not guarantee approval, and community reports demonstrate that review can expose environment-specific or misunderstood edge cases even after extensive local testing. citeturn13view0turn16search11

As of **10 August 2026**, the proposed skill also needs an online freshness gate. Apple's current App Review Guidelines were last updated **8 June 2026**, and Apple currently requires App Store Connect uploads to be built using **Xcode 26 or later with the applicable version-26 SDK**. Apple's age-rating system has also changed substantially, and new social-media capability questions introduced on 9 July 2026 become mandatory for new submissions and updates beginning in **September 2026**. These are exactly the kinds of rules an embedded static checklist will eventually get wrong. citeturn16search17turn14view0turn14view2

## What “App Store ready” should mean before uploading

### The app must be a finished production release

Guideline 2.1 is stricter than “it works on my phone”. Apple says submissions should be final versions, URLs must work, temporary and placeholder content must be removed, apps should be tested on-device for bugs and stability, and incomplete binaries or binaries that crash or show obvious technical problems will be rejected. Apple explicitly directs beta software to TestFlight rather than the App Store. citeturn15view1

Your agent should therefore consider the following to be **NO-GO conditions before the first upload**:

| Area | NO-GO evidence | What the agent should require |
|---|---|---|
| Startup | Crash, hang, permanent spinner, unusable first screen | Successful cold launch from a clean install on supported/current OS configurations. Apple explicitly rejects crashing or obviously broken binaries. citeturn15view1 |
| Core feature | Primary advertised workflow cannot be completed | Demonstrated end-to-end success for every core workflow advertised in the description/screenshots. Metadata must accurately reflect the actual app. citeturn15view1 |
| Placeholder content | Lorem ipsum, “coming soon” in a supposedly finished core feature, empty web pages, unfinished imagery | Remove temporary content before submission. citeturn13view1turn15view1 |
| Links | Privacy, support, Terms, authentication callback or important content link fails | Test every externally reachable URL from a production-style device/network. Apple specifically identifies broken links as a common review issue. citeturn13view1 |
| Production services | Reviewer-facing API/backend is unavailable, development-only or inaccessible externally | Production services live and reachable throughout review. citeturn13view0turn15view1 |
| Review credentials | Login required but no working reviewer account is available | Non-expiring demo credentials or, where permitted, an Apple-approved fully featured demo mode. citeturn15view5turn13view0 |
| Purchases | IAP product cannot load, cannot be purchased, is hidden from reviewer, or has incomplete configuration | Every configured IAP intended for review must be complete, current, visible and functional, with exceptions explained in Review Notes. citeturn15view1 |
| Metadata | Screenshots, description, privacy statements or pricing claims do not represent the shipping build | Reconcile App Store metadata against the final release build. citeturn15view1 |

This should be one of the central philosophies of the skill: **no silent failures**.

A recent Apple Developer Forums case illustrates why. A developer reported an App Review rejection because an “Unlock Pro” action appeared non-responsive. The developer later identified a path where StoreKit product loading could return no product, causing the method to return after logging an error with no visible user feedback. The app appeared to work locally but could look completely broken to a reviewer encountering the edge case. This is anecdotal rather than Apple policy, but it is an excellent model for the type of bug a serious readiness agent should hunt for. citeturn16search11

The agent should consequently treat this pattern as a defect:

```text
User action
    ↓
async operation
    ↓
unexpected nil / network failure / empty result
    ↓
log only + return
    ↓
nothing visible happens
```

A production-safe equivalent is:

```text
User action
    ↓
visible loading state
    ↓
operation succeeds ───────────→ continue
    ↓ fails
visible explanation
    ↓
retry / recovery / alternative path
```

The same test should be applied to login, registration, password reset, purchases, restores, uploads, downloads, location lookup, QR scanning, authentication callbacks, push-registration dependent features, AI/API requests and any other async user action.

### Release configuration must be audited, not merely Debug configuration

As of 10 August 2026, Apple requires uploads to use **Xcode 26 or later and the applicable iOS 26, iPadOS 26, tvOS 26, visionOS 26 or watchOS 26 SDK**. Apple's requirements change over time, so this must be fetched at audit time rather than hard-coded indefinitely. citeturn14view0

Before an upload, Apple provides a specific Xcode `Validate App` process. Apple says this checks whether the archive meets minimum App Store requirements and performs standard App Store Connect checks. Validation also reviews signing certificate, provisioning profile and entitlements, and Apple instructs developers to fix validation issues before proceeding. citeturn14view5

The agent should make these separate checks:

| Release artefact | Audit |
|---|---|
| Bundle identifier | Must be the intended production identifier and match the corresponding App Store Connect record. Xcode validation fails when the record/bundle ID relationship is wrong. citeturn14view5 |
| Version/build | Confirm intended marketing version and unique build number for the release. Apple requires the build string to be incremented for subsequent uploads. citeturn18search16 |
| Release configuration | Build and run **Release**, not merely Debug. Look for release-only configuration mistakes, production URLs, compiler flags and feature flags. |
| Signing | Correct Apple Developer team, distribution signing, provisioning profile and supported target. Xcode's archive validation explicitly inspects signing information. citeturn14view5 |
| Entitlements | Compare compiled entitlements with genuinely used capabilities. Xcode validation includes entitlement inspection. citeturn14view5 |
| App capabilities | Verify Push Notifications, Sign in with Apple, associated domains, iCloud, Game Center and similar capabilities are configured consistently between app, identifier and App Store configuration where applicable. For example, Apple requires the Game Center entitlement and App Store Connect configuration for new iOS/iPadOS/tvOS apps offering Game Center. citeturn14view0 |
| App icon/assets | Verify production assets are actually part of the release target rather than present only in development assets/configuration. |
| Archive | Produce an App Store distribution archive and run Apple's `Validate App`; unresolved validation errors are an automatic HOLD. citeturn14view5 |

The agent should never report “READY” merely because `xcodebuild` succeeds. **Compilation success, archive success, Xcode validation and behavioural correctness are four different gates.**

### Apple-specific technical rules need explicit checks

Guideline 2.5 contains a number of technical constraints that can cause an otherwise polished app to fail review. Apple requires public APIs, restricts executable-code downloading and behaviour-changing code, restricts background services to their intended purposes, requires apps to function on IPv6-only networks, limits inappropriate power use, and requires explicit consent plus appropriate indication when recording user activity through capabilities such as microphone, camera or screen recording. citeturn16search17

The skill should therefore scan for:

**Private/non-public API risk.** Search source, linked binaries and suspicious selector/API use. Do not assert a private-API violation based solely on a string match; report uncertain matches as “Needs Verification”.

**Downloaded code and remote feature mutation.** Distinguish normal server-provided data/configuration from systems that effectively download executable code or radically alter native app functionality. Apple's rules contain particular exceptions for some hosted software experiences, but those experiences themselves receive additional policy obligations. citeturn15view3

**Background modes.** Compare each `UIBackgroundModes` entry and related entitlement against actual product functionality. Declaring capabilities “just in case” creates unnecessary review surface because Apple limits background services to their stated purposes. citeturn16search17

**Network assumptions.** Exercise core networking through IPv6-compatible networking and do not assume IPv4 literals or IPv4-only infrastructure. Apple's guideline explicitly requires IPv6-only functionality. citeturn16search17

**Battery/thermal behaviour.** Look for indefinite polling, runaway location updates, unnecessary background work, repeated network retries and similar patterns. Apple's performance rules prohibit apps that rapidly drain battery, generate excessive heat or run unrelated background processes. citeturn16search17

**Device/orientation/layout issues.** An app should be tested on every device family it declares support for, not just the developer's favourite iPhone. Community App Store-review projects repeatedly include iPad layout, safe-area and text-truncation checks because real rejection reports have involved those conditions. This is a community-derived testing priority rather than an Apple guarantee that a particular device will always be used. citeturn17search0

### The runtime test matrix should be deliberately adversarial

The agent cannot prove many of these conditions by static source inspection, so it must create a **manual/runtime evidence checklist** rather than silently assuming they pass.

For every core task, the audit should exercise at minimum:

| Test state | Why it matters |
|---|---|
| Clean first installation | Exposes missing initial state, onboarding, migration assumptions and unavailable credentials. Apple's accessibility guidance also treats first launch as a “common task”. citeturn18search20 |
| Relaunch after normal use | Tests persisted state and session restoration. |
| Foreground/background transition | Finds stale state, interrupted requests and permission/session changes. |
| No connection | Core flows should produce a recoverable error rather than hanging or doing nothing. |
| Slow/intermittent connection | Exposes timing assumptions and async silent failures. |
| Server 4xx/5xx/unexpected response | Error handling should be user-visible and recoverable. |
| Expired/invalid session | Auth flows should recover without trapping the user. |
| Permission denied | Apple says apps should respect permission settings and, where possible, provide alternatives instead of forcing unnecessary access. citeturn15view4 |
| Permission later revoked in Settings | Prevents crashes or permanently broken UI after state changes. |
| Small and large supported displays | Finds clipping, hidden actions and modal/popover problems. |
| iPad where supported | Finds navigation, layout and popover assumptions. |
| Dynamic Type/large text | Particularly important for production accessibility. Apple's Accessibility Nutrition Label criteria use common-task completion as the standard for claiming support. citeturn18search20 |
| VoiceOver/Voice Control sanity pass | Helps detect inaccessible controls and unnamed actions; accessibility metadata is currently voluntary but Apple says it will eventually become required for submission. citeturn18search20 |
| Dark appearance | Identifies unreadable hard-coded colours and invisible assets. |
| Localisation/long strings | Finds truncation and hard-coded layout assumptions. |
| Upgrade from the previous public build | Critical for updates: migrations and persisted state often differ from clean installs. |
| Log out → log in again | Ensures account lifecycle works repeatedly. |
| Delete account → fresh registration | Ensures deletion does not leave an unusable identity/session state. |
| Every purchase state | Purchase, cancellation, failure, restore, entitlement refresh, expired subscription where applicable and retry after StoreKit/network failure. Guideline 2.1 requires IAPs presented for review to function. citeturn15view1 |

For an agent skill, each manual item should have three states: **PASS with evidence / FAIL / NOT TESTED**. “Not tested” must not silently become a pass.

## Privacy, permissions and third-party code

### Privacy should be audited as a data-flow reconciliation problem

One of the highest-value improvements over ordinary App Store checklists would be to make the skill build a **data inventory**.

Apple requires developers to identify data collected by both the app and its third-party partners in App Store Connect and to keep those answers accurate and current. Apple specifically defines third-party partners to include services such as analytics and advertising SDKs. citeturn14view3turn14view4

The agent should reconcile five layers:

```text
Source code behaviour
       ↕
SDK / dependency behaviour
       ↕
PrivacyInfo.xcprivacy / Required Reason declarations
       ↕
Published privacy policy
       ↕
App Store Connect App Privacy answers
```

A mismatch anywhere should prevent a confident READY verdict.

For example, a project may claim “no data collected” in App Store Connect while Firebase Analytics, an advertising SDK or another dependency sends identifiers or usage information. Apple makes developers responsible for the third-party code included in their apps and for understanding its data collection and use. citeturn13view3turn14view3

The skill should produce a data inventory resembling:

| Data/category | Source | Destination | Purpose | Linked to identity? | Tracking? | User consent | ASC declaration | Policy documented |
|---|---|---|---|---|---|---|---|---|
| Email address | Registration | First-party API | Account | Yes | No | User provides | Verify | Verify |
| Crash diagnostics | SDK | SDK vendor | Diagnostics | Determine | Determine | Determine | Verify | Verify |
| Advertising identifier | Ad SDK | Ad network | Advertising | Determine | Potentially | ATT required when tracking | Verify | Verify |
| Location | CoreLocation | First party/third party | Feature | Determine | Determine | System permission | Verify | Verify |

The agent should **not infer “no collection” merely because it cannot see a first-party HTTP request**. The dependency audit matters.

### Privacy policy is mandatory

Apple's current Guideline 5.1.1 requires **all apps** to provide a privacy-policy link both in App Store Connect metadata and somewhere easily accessible inside the app. The policy must identify collected data and its uses, address third-party protection, describe retention/deletion, and explain how users can revoke consent or request deletion. App Store Connect separately states that a privacy-policy URL is required for all apps. citeturn15view3turn15view4turn18search2turn18search7

The agent should therefore verify the **content**, not only the existence, of the policy.

A `200 OK` URL containing a generic one-paragraph template is not enough for a high-confidence audit if the actual app uses authentication, analytics, cloud storage, AI APIs or advertising that the policy never mentions.

### Permission declarations should be matched to actual functionality

Apple says permission-purpose strings must clearly and completely describe how data will be used, that apps should ask only for data relevant to core functionality, and that alternatives should be provided where possible. An app must respect a user's permission decision and must not manipulate users into providing unnecessary access. citeturn15view4

The skill should inspect, as applicable:

```text
Camera
Microphone
Photos
Contacts
Location – when in use
Location – always/background
Bluetooth
Calendars
Reminders
Motion/Fitness
Health
Speech recognition
Tracking
Local network
Face ID
Media library
```

For each capability it should determine:

**Is the API actually used? → Is the declaration present? → Does the wording accurately explain the use? → Is permission requested at the point of need? → What happens if it is denied? → Is the data included in privacy declarations where required?**

A useful warning is:

> **Permission declared but no matching feature found:** review entitlement/config-plugin output and remove unnecessary access where possible.

That is especially valuable for React Native, Flutter and Expo projects, where plugins or SDKs can generate native permissions developers did not consciously add. Community App Review tooling increasingly audits generated native configuration for exactly that reason. citeturn17search0turn17search15

### App Tracking Transparency needs a dedicated branch

Apple states that tracking users across apps/sites owned by other companies requires permission through App Tracking Transparency, that developers cannot gate functionality on allowing tracking, and that fingerprinting or deriving another identifier to track users after denial is prohibited. Apple also says apps referencing SDKs that engage in prohibited fingerprinting may be rejected. citeturn14view4

The skill should ask:

```text
Does the app or any SDK combine app data with third-party data
for advertising, attribution or cross-company tracking?
```

If yes, it should audit:

- ATT implementation and timing;
- `NSUserTrackingUsageDescription`;
- behaviour before consent;
- behaviour after denial;
- whether SDK initialisation transmits tracking-relevant data before consent;
- privacy label declarations;
- whether the app attempts alternative fingerprinting;
- whether a paywall or other functionality is conditional on ATT approval.

The correct audit is behavioural. Merely finding `ATTrackingManager` in source does not prove compliance.

### Privacy manifests and Required Reason APIs are now upload concerns

Since May 2024, Apple requires approved reasons for listed Required Reason APIs used by the app or third-party SDKs in order to upload new or updated apps. Apple also maintains a list of commonly used third-party SDKs for which a privacy manifest is required, with signatures additionally required in relevant cases where those SDKs are binary dependencies. The current list includes widely used packages such as Flutter, Capacitor, Cordova, Firebase components, GoogleSignIn, OneSignal, Alamofire and others. citeturn14view0turn13view3

The agent should therefore inventory:

```text
Package.swift / Package.resolved
Podfile / Podfile.lock
Frameworks
XCFrameworks
React Native packages
Expo/config plugins
Flutter packages
Manually embedded binaries
```

Then compare dependencies to Apple's **current** third-party SDK requirements page rather than maintaining only a fixed local list.

It should also find every `PrivacyInfo.xcprivacy`, inspect Required Reason API categories/reasons, and distinguish these situations:

| Result | Classification |
|---|---|
| Required Reason API found and correct approved reason documented | Pass |
| API found but no applicable reason evident | NO-GO / requires investigation |
| Apple-listed SDK included without required manifest | NO-GO |
| Required binary SDK signature absent/invalid | NO-GO |
| Manifest exists but declarations do not match observed APIs/data use | HOLD |
| No applicable Required Reason API/SDK requirement | Do **not** invent a requirement merely because no manifest was found |

That last point is important: the agent should avoid the simplistic rule “every app must contain `PrivacyInfo.xcprivacy`”. Apple's obligations are conditional on API/SDK usage. citeturn13view3turn14view0

### Account creation implies account deletion

Apple's rule is exceptionally clear: if an app supports account creation, users must be able to initiate account deletion from within the app. Apple says deleting an account means deleting the account record and associated personal data that is not legally required to be retained; merely deactivating an account is insufficient. A direct link to a web deletion page may be used to finish the process, but ordinary apps should not force users to call, email or go through customer support to request deletion. citeturn13view4

Apple also states that automatically generated/guest accounts require deletion capability, and apps using Sign in with Apple should revoke the user's tokens when the account is deleted. citeturn13view4

This should be a deterministic audit rule:

```text
Can user create an account?
        │
       YES
        │
Can deletion be initiated in-app?
        │
       NO ───────────────→ NO-GO
        │
       YES
        │
Does it delete the account rather
than merely deactivate it?
        │
       NO ───────────────→ NO-GO
        │
       YES
        │
Are associated user data and UGC
handled appropriately?
        │
      VERIFY
```

Apple additionally says that apps without significant account-based functionality should allow people to use the app without requiring a login. Community reports show developers being rejected under this rule when registration was imposed before non-account-based functionality, which is consistent with Apple's official wording. citeturn15view4turn16search0turn16search2

That gives the agent an important question beyond account deletion:

> **Why is an account necessary for this feature?**

If the answer is merely “because the developer wants registrations”, the agent should flag Guideline 5.1.1 risk.

## Feature-specific App Review policy gates

A good skill should first discover what the product actually does and then activate only the relevant policy modules. Reviewing every possible App Review rule with equal weight produces noise and makes developers ignore the output.

### Authentication and social login

If an app uses a third-party/social login provider such as Google, Facebook, X, LinkedIn, Amazon or WeChat to create or authenticate the user's **primary app account**, Apple requires an equivalent alternative login service satisfying its specified privacy characteristics: limited collection of name/email, an option to keep email private, and no collection of app interactions for advertising without consent. Apple provides exceptions for cases such as apps using only their own account system, certain enterprise/education accounts, government identification and clients for specific third-party services. citeturn15view3

The agent should not implement the inaccurate blanket rule:

> “Google login exists → Sign in with Apple is always mandatory.”

Instead it should classify the account model against Guideline 4.8, document whether an exception applies and then recommend Sign in with Apple where it is the appropriate equivalent option. citeturn15view3

Authentication tests should additionally include wrong password, expired session, password reset, email verification, duplicate account, third-party callback cancellation, network failure, account deletion and re-registration.

### User-generated content and social features

Apple requires apps containing user-generated content or social networking features to include:

- filtering of objectionable material;
- reporting of offensive content with timely responses;
- the ability to block abusive users;
- published contact information. citeturn15view0

The agent therefore needs a UGC classifier. Comments, posts, public profiles, chat, uploaded images/video, reviews, community feeds and creator content can all trigger this audit.

A useful evidence matrix is:

| UGC control | Pass condition |
|---|---|
| Report content | A reviewer can report content from the relevant surface |
| Block user | A user can block an abusive account |
| Moderation/filtering | There is a credible mechanism appropriate to the content type |
| Contact | Published route for contacting the operator |
| Enforcement | Report/block actions actually reach the production moderation system |
| Terms/community rules | Users can understand prohibited behaviour |
| Age treatment | Mature or social content is accurately represented in age-rating responses |

The current age-rating questionnaire is particularly important here. Apple's July 2026 update defines a “social media capability” as the ability to redistribute, amplify or interact with UGC through a social feed or similar discovery system. Those questions are available now and become mandatory for App Store submissions and updates beginning in **September 2026**. An audit performed on 10 August 2026 should therefore mark them **UPCOMING / PREPARE NOW**, rather than incorrectly saying they are already mandatory today. citeturn14view2

### Age ratings and children

Every App Store app requires an age rating; an Unrated app cannot be published through the App Store. Apple's current questionnaire includes content descriptors, in-app controls and capabilities and can produce region-specific ratings. citeturn14view1

Apple's current system reflects new age-rating categories on version-26 operating systems, and updated age-rating questions have already become part of the submission workflow. citeturn14view0turn14view1

For an agent, the age-rating audit should derive likely questionnaire responses from actual features. It should detect things such as:

```text
UGC / social feeds
Chat or messaging
Web browsing
Gambling or simulated gambling
Loot boxes
Violence
Sexual/mature themes
Medical/wellness content
Advertising
Parental controls
Age assurance
User-generated media
```

Then compare these against App Store Connect answers.

Apps choosing the Kids category receive additional restrictions. Apple requires appropriate parental gates around external links/purchases and applies stricter privacy and advertising requirements. citeturn16search17

### Digital purchases and subscriptions

The payment audit should be feature-aware rather than simply searching for Stripe.

Apple's Guideline 3.1.1 says digital functionality or content unlocked inside the app — examples include subscriptions, game currency, levels, premium content and full-version unlocks — generally must use In-App Purchase. Apple also requires a restore mechanism for restorable IAPs and prohibits purchased credits/currency from expiring. Loot boxes must disclose odds. citeturn15view2

External-purchase rules are now storefront-dependent. The current guidelines explicitly distinguish the United States storefront from other regions and describe StoreKit external-purchase-link entitlements for eligible storefronts. An agent must therefore ask **where the app will be distributed** before asserting that a particular link or payment button is allowed or forbidden. citeturn15view2

For every IAP/subscription, the agent should verify:

| Check | Evidence |
|---|---|
| Product exists | App Store Connect product identifier matches code |
| Agreement state | Paid Apps Agreement active where needed. Apple says the agreement must be active to test IAPs in sandbox. citeturn18search13 |
| Product loads | Real StoreKit/sandbox/TestFlight test |
| Purchase succeeds | Entitlement granted exactly once |
| Cancellation | App recovers from user cancellation |
| Failure | Visible recovery/error rather than no-op |
| Restore | Restorable products can be restored as required. citeturn15view2 |
| Relaunch | Existing entitlement restores correctly |
| Subscription state | Active/expired/revoked/refunded states behave correctly |
| Paywall claims | Price, duration, trial and benefits accurately match StoreKit/App Store configuration |
| Reviewer visibility | Review can reach and exercise purchase flow |
| Review Notes | Non-obvious purchase configuration explained |

Apple specifically says a confusing business model or unclear IAP can delay review or lead to rejection. citeturn15view2

### Physical goods and other payments

The agent should distinguish digital purchases from physical goods/services and other guideline exceptions rather than applying IAP rules globally. It should classify the product being sold first, then apply the current Guideline 3 rules and storefront-specific exceptions. Because Apple's commerce requirements have materially changed in recent years and can vary by storefront, this module should always refresh the official guideline at run time. citeturn15view2

### AI and third-party data sharing

The current privacy guidelines require careful disclosure and permission for sharing personal data with third parties. Apple's current App Review Guidelines explicitly treat third-party services and data processors as part of the developer's responsibility, and privacy declarations must include third-party collection. citeturn14view3turn15view4

For an AI-enabled app, the agent should therefore ask:

```text
What user content is sent?
Does it contain account/profile information?
Does it contain health, financial, location or other sensitive data?
Which model/provider receives it?
Is the transfer explained to the user?
Is appropriate permission obtained?
Is it covered in the privacy policy?
Is it accurately represented in App Privacy declarations?
How long does the provider retain it?
Can the feature operate without unnecessary data?
```

The key audit principle is not “AI is prohibited”; it is **data transfer, consent, disclosure and product claims must be accurate and compliant**.

### Minimum functionality, clones and spam

Guideline 4 is not merely an aesthetics guideline. Apple can reject apps that are essentially repackaged websites, template variations, duplicates or part of saturated/spam-style portfolios. Community tools routinely flag “minimum functionality” and spam risk because these are difficult to identify through compilation or automated tests alone. Apple's Guidelines include specific rules against spam, copycats and misleading products. citeturn16search17turn17search0

The agent should therefore ask qualitative questions such as:

> What native/product value does this app provide that justifies an App Store app?

> Is this substantially indistinguishable from another app published by the same developer?

> Is the app primarily a thin website wrapper?

> Are multiple near-identical branded apps being submitted rather than a single configurable product?

These should normally be `HIGH / MANUAL REVIEW` rather than deterministic blockers, because design and minimum-functionality judgement is contextual.

### Platform-specific branches

A comprehensive skill cannot assume “iOS app” means every Apple app follows identical implementation requirements.

It should branch by target:

| Target | Additional audit focus |
|---|---|
| iOS/iPadOS | Supported device families, orientation, permissions, background modes, StoreKit, iPad presentation, App Clips/extensions where present |
| macOS App Store | Sandbox/distribution behaviour and Mac-specific guideline requirements |
| watchOS | Watch-specific capabilities, dependent/independent architecture, tiny-screen interaction and unsupported advertising contexts |
| tvOS | Focus/navigation, remote interaction and tvOS-specific metadata/privacy format |
| visionOS | Immersive behaviour, motion information where required, platform-specific interaction |
| Extensions/widgets/App Clips | Entitlements, restricted APIs/content and whether capabilities such as advertising are improperly included outside the main binary |

Apple's guidelines, for example, prohibit display advertising in extensions, App Clips, widgets, notifications, keyboards and watchOS apps even where advertising is allowed in the main binary. citeturn15view2

## App Store Connect, metadata, legal and operational readiness

### Metadata is part of the product under review

Apple's Guideline 2.3 says metadata — including privacy information, descriptions, screenshots and previews — must accurately represent the core app experience. Apple prohibits hidden/dormant/undocumented functionality and requires new functionality and product changes to be specifically described in Notes for Review. Screenshots should show the app in use rather than merely a title screen, login page or splash screen. citeturn15view1

This means the readiness agent should compare claims **semantically**, not just check whether fields are non-empty.

For example:

```text
Screenshot says: "Unlimited AI exports"
          ↓
Agent finds: export requires a subscription after 3 uses
          ↓
Check screenshot/description clearly communicates the purchase requirement
          ↓
Otherwise flag Guideline 2.3 risk
```

Apple explicitly requires featured items, levels, subscriptions and similar paid elements shown in App Store materials to make additional-purchase requirements clear. citeturn15view1

The metadata audit should cover at least:

| App Store item | Audit |
|---|---|
| App name | Accurate, distinctive and compliant |
| Subtitle | Accurate summary |
| Description | Every material claim corresponds to shipping functionality |
| Keywords | Relevant and non-deceptive |
| Category | Represents the app's primary function |
| Age rating | Matches actual capabilities/content |
| Screenshots | Current UI, actual in-use experience, correct supported device classes |
| App previews | Current build and honest behaviour if supplied |
| Support URL | Live and leads to genuine contact/support information. citeturn18search14 |
| Privacy policy | Live, accessible and matches actual data practice. citeturn15view4turn18search7 |
| Copyright | Correct rights holder/year |
| Content rights | Third-party material appropriately licensed |
| Pricing | Intended price and territory |
| Availability | Intended storefronts |
| Review information | Complete reviewer contact/access instructions |
| What's New | Required for updates and should accurately explain material changes. citeturn15view5 |

App Store Connect maintains a formal list of required app/version properties, including app information such as age rating, bundle ID, SKU and content rights, together with platform-version information such as Support URL and App Review Information. Some country/feature-specific properties are conditional. citeturn18search0turn18search6

### Review Notes should be generated as a first-class artefact

Apple allows App Review Notes of up to 4,000 bytes and specifically asks developers to include app-specific settings, test registration/account details and other information needed to test the app. Demo credentials must not expire. citeturn15view5

A good skill should automatically generate a draft like this:

```text
APP REVIEW NOTES

Purpose
[One-paragraph description of what the application does.]

Reviewer access
Username: [non-expiring review account]
Password: [review password]

Important:
This account is reserved for App Review and will remain active
throughout the review period.

Core review path
1. Launch the application.
2. Sign in using the credentials above.
3. Open [tab/screen].
4. Select [feature].
5. Perform [action].
6. Expected result: [result].

Purchases
[Explain each IAP/subscription that App Review needs to locate.]
[Explain any configured product intentionally not visible and why.]

Permissions
[Explain any permission whose purpose may not be obvious.]

Special configuration
[Region/account state/QR code/hardware/test data.]

Hardware or external dependency
[Instructions, sample QR code, accessory information or demo video.]

Non-obvious behaviour
[Feature flags, specialised workflow, regulated functionality, etc.]

Contact
[Name]
[Email]
[Phone]
```

Apple specifically requests such explanations for non-obvious functionality and IAPs and says required hardware/resources such as sample QR codes should be made available to reviewers. citeturn13view0turn13view1

A powerful agent rule would be:

> **If the auditor required developer knowledge to discover or understand a feature, assume the reviewer may require that explanation in Review Notes.**

### The reviewer journey should be rehearsed from zero knowledge

This should be an explicit final test:

```text
New device / clean installation
             ↓
No internal developer knowledge
             ↓
Only information supplied in App Store Connect
             ↓
Can reviewer reach every reviewable feature?
             ↓
Can reviewer understand what success looks like?
             ↓
Can reviewer exercise every relevant IAP?
             ↓
Can reviewer recover from permissions/network errors?
             ↓
Does any account/backend/hardware dependency stop them?
```

Apple's own common-issues guidance says incomplete review information causes problems and asks developers to supply credentials, special configurations and, where necessary, demonstration videos or hardware. citeturn13view1

Reddit reports reinforce how fragile reviewer-access assumptions can be. One developer described a reviewer successfully logging in, deleting the review account and then encountering problems attempting to create another account. This is anecdotal and does not establish an Apple review procedure, but it is a useful warning that the review account and account lifecycle should survive behaviour outside the developer's “happy path”. citeturn16search4

### Export compliance should be decided before submission

Apple says any app using or incorporating encryption must determine export-compliance requirements. This includes standard encryption and operating-system cryptography; depending on the implementation, documentation may or may not be required. Apple provides an `Info.plist` mechanism for declaring exempt/non-exempt encryption and avoiding repeated questions where appropriate. citeturn16search1turn16search6turn16search16

This matters even for ordinary apps because HTTPS itself involves encryption, although Apple's documentation explains that OS-provided encryption such as HTTPS through `NSURLSession` is typically exempt from documentation-upload requirements. The agent should therefore **classify rather than guess**. citeturn16search16

If App Store Connect shows a build as `Missing Compliance`, Apple requires the developer to answer the encryption questions or supply the relevant documentation before it can be submitted. citeturn16search13

### Agreements, banking and tax should be resolved early for monetised apps

To offer In-App Purchases, Apple's current App Store Connect documentation requires the Account Holder to accept the Paid Apps Agreement and supply banking and tax information; Apple says the agreement needs to be Active to test IAPs in sandbox. citeturn18search13

Apple similarly says receiving payment requires a Paid Apps Agreement and appropriate financial details. citeturn18search5turn18search8turn18search10

The skill should consequently flag this before the release team discovers it after finishing the app:

```text
App is paid OR contains IAP?
           ↓ yes
Paid Apps Agreement active?
           ↓
Banking/tax complete as applicable?
           ↓
IAP sandbox test actually works?
```

### EU DSA status is now part of operational readiness

Apple requires developers to declare Digital Services Act trader status. For apps distributed in the EU, qualifying traders must provide and verify contact information which Apple publishes on the product page; Apple notes that developers still need to declare trader status even when not distributing through the EU App Store. citeturn13view5

Apple's current Upcoming Requirements history also notes that apps without the required verified trader status are not available in the EU until the requirement is satisfied. citeturn14view0

The agent should therefore ask:

```text
Which storefronts?
        ↓
EU included?
        ↓
Developer's DSA status established?
        ↓
If trader: verification complete?
```

The agent should not decide legally whether someone is a “trader”. Apple itself says that is the developer's assessment and advises seeking legal advice when uncertain. citeturn13view5

### Country-specific and regulated-app requirements need conditional routing

App Store Connect's current required-property documentation includes conditional requirements around areas such as mainland China availability, South Korea, Vietnam and regulated medical devices for apps meeting certain criteria in the EU/EEA, UK or US. citeturn18search6

The correct skill behaviour is therefore:

```text
Feature + category + intended territories
                 ↓
       conditional compliance router
                 ↓
specific Apple/regulatory checklist
```

rather than loading every regional rule for every weather or productivity app.

This is especially important for medical, finance/crypto, gambling, VPN/security, children's, dating, alcohol/cannabis-related, government-services and other regulated or safety-sensitive apps because Apple's broader Guideline 5 also requires compliance with applicable local law in every place where the app is distributed. citeturn15view3

### Accessibility should be included even though its new metadata is not yet mandatory

Apple's Accessibility Nutrition Labels are **voluntary to start as of the current documentation**, but Apple says they will eventually be required for new apps and updates. Apple asks developers to assess accessibility per supported device and says all “common tasks” must work with a feature before claiming that feature's support. citeturn18search20

This makes accessibility an ideal **production-readiness gate** even where it is not currently an automatic App Review blocker.

The skill should test:

```text
VoiceOver
Voice Control where applicable
Larger Text / Dynamic Type
Dark interface
Differentiate without colour alone
Contrast
Reduced Motion
Captions where applicable
Audio descriptions where applicable
```

But it should distinguish:

**Policy blocker:** functionality is so inaccessible/broken that the app cannot reasonably be used as represented.

**Quality issue:** accessibility deficiency that may not independently cause rejection.

**Metadata blocker:** developer declares an Accessibility Nutrition Label that the tested app does not actually satisfy. Apple requires those declarations to remain accurate. citeturn18search20

## Recommended dedicated agent skill

The research strongly supports building the skill as a **multi-stage preflight system** rather than a giant prose copy of Apple's Guidelines. Existing GitHub implementations are moving in the same direction: one project separates 31 checks into layout, permissions, UGC, privacy, quality, business and metadata categories; another mirrors Apple's five guideline sections; `app-store-review-risk` emphasises target-aware and file-backed reasoning; and GitHub's community App Store reviewer explicitly starts read-only. citeturn17search8turn17search1turn17search2turn17search3

### Recommended identity and trigger

```yaml
name: apple-app-store-readiness
description: >
  Performs a read-only, evidence-backed pre-submission audit of an
  Apple-platform application before it is uploaded to App Store Connect.
  Reviews source code, release configuration, privacy, permissions,
  dependencies, payments, authentication, user-generated content,
  metadata, legal/compliance requirements and reviewer accessibility.
  Produces a GO/HOLD/NO-GO decision and does not guarantee App Review approval.
```

Trigger phrases should include concepts such as:

```text
Is my app App Store ready?
Check before App Store upload
App Review preflight
Prepare this app for App Store Connect
Will Apple reject this?
Audit App Store compliance
Review privacy manifest
Check my IAP before submission
Check my iOS app for review
Production readiness for App Store
```

### Freshness gate

This should run first.

```text
FETCH CURRENT:
- App Store Review Guidelines
- Upcoming Requirements
- Third-party SDK requirements
- App Store Connect age-rating guidance
- Relevant App Store Connect metadata requirements

RECORD:
- retrieval date
- App Review Guidelines last-updated date
- minimum accepted Xcode/SDK
- upcoming rules within the next 90 days

STOP:
- if project is built below Apple's current submission minimum
```

As of this research on 10 August 2026, that would record App Review Guidelines updated 8 June 2026, Xcode 26/version-26 SDK minimums, and the September 2026 mandatory social-media age-rating questionnaire change. citeturn16search17turn14view0turn14view2

### Project discovery

The skill should inspect without modifying:

```text
*.xcodeproj
*.xcworkspace
project.pbxproj
Info.plist files
*.entitlements
PrivacyInfo.xcprivacy
Package.swift
Package.resolved
Podfile
Podfile.lock
Cartfile / embedded frameworks if present
*.storekit
asset catalogs
configuration files
localisation files
authentication/onboarding code
settings/account screens
paywall/purchase code
data/analytics layer
network clients
permission requests
UGC/report/block/moderation surfaces
privacy/support/Terms URLs referenced in project
App Store metadata stored in repository
screenshots/previews if available
CI/release configuration
```

Framework discovery should support native Swift/Objective-C plus React Native, Expo, Flutter and other wrappers. Current community skills already support several of these ecosystems and show that a useful audit needs framework awareness rather than assuming a single Xcode-native architecture. citeturn17search1turn17search15

### Feature classifier

Before interpreting rules, produce:

```yaml
platforms:
  ios: true
  ipad: true
  macos: false

features:
  accounts: true
  account_creation: true
  third_party_login: true
  sign_in_with_apple: true
  ugc: false
  social_feed: false
  tracking: false
  analytics: true
  advertising: false
  camera: true
  microphone: false
  photos: true
  location: false
  iap: true
  subscriptions: true
  physical_goods: false
  health: false
  children: false
  ai_external_processing: true
  background_modes: [...]
  push_notifications: true

territories:
  eu: true
  uk: true
  us: true
```

Every conditional rule should follow from this feature map.

### Static code and configuration audit

The static pass should look for deterministic or strongly inferable problems:

```text
BUILD / RELEASE
□ Current Xcode/SDK submission baseline
□ Correct bundle ID
□ Version/build configured
□ Production Release configuration
□ Correct targets/device families
□ Signing/profile/entitlements consistent
□ App icon/assets configured
□ Archive validates in Xcode

APP COMPLETENESS
□ No obvious placeholder content
□ No public TODO/unfinished core experience
□ No developer-only test screen reachable in production
□ No hidden/dormant product feature conflicting with review notes
□ All support/privacy URLs reachable

PRIVACY
□ Data inventory constructed
□ All dependencies inventoried
□ Privacy manifests audited
□ Required Reason APIs audited
□ Apple-listed SDK manifest/signature requirements checked
□ Privacy policy matches behaviour
□ ASC privacy answers supplied for reconciliation
□ ATT branch activated when applicable

PERMISSIONS
□ Each protected API has matching declaration
□ Each purpose string accurately describes use
□ Permission requested at appropriate point
□ Denial paths exist
□ No unnecessary permission dependency

ACCOUNTS
□ Login necessary where required
□ Account deletion if account creation exists
□ Delete means delete, not only deactivate
□ Social-login Guideline 4.8 checked
□ Sign in with Apple token revocation where applicable

PAYMENTS
□ Digital-vs-physical classification
□ IAP required/used correctly
□ Storefront-specific external-link rules checked
□ Restore support
□ Subscription/paywall copy
□ Product identifiers/configuration

UGC
□ Filter/moderation capability
□ Reporting
□ Blocking
□ Published contact
□ Age-rating implications

TECHNICAL
□ Public API review
□ Downloaded-code review
□ Background mode justification
□ IPv6 assumptions
□ recording indicators/consent
□ power-intensive patterns
```

Apple's official Guidelines support each of these major policy groups, while current open-source agent skills demonstrate the practicality of scanning project/configuration files before a developer initiates App Store submission. citeturn13view0turn15view0turn15view2turn15view3turn15view4turn17search3

### Build and archive gate

Where Xcode tooling is available, the skill should request or execute read-only build commands appropriate to the project, then require an actual App Store archive validation.

Community `app-store-review-risk` tooling also uses Xcode project/build-setting inspection as part of evidence gathering, but Apple's own `Validate App` remains the authoritative minimum-distribution check. citeturn17search2turn14view5

Suggested sequence:

```text
Discover workspace/project and schemes
            ↓
Inspect release build settings
            ↓
Build Release configuration
            ↓
Run automated tests
            ↓
Create App Store archive
            ↓
Xcode "Validate App"
            ↓
No validation errors?
       ┌────┴─────┐
      no         yes
      ↓            ↓
   NO-GO      continue
```

### Runtime reviewer simulation

Static review must then hand off to a runtime checklist.

For every feature, construct:

```yaml
test:
  name: "Purchase Pro subscription after clean install"
  precondition:
    - fresh installation
    - review/demo account
    - no existing subscription
  steps:
    - launch
    - login
    - open paywall
    - purchase
  expected:
    - product loads
    - system purchase UI appears
    - successful transaction unlocks entitlement
    - entitlement survives relaunch
  failure_tests:
    - product request fails
    - purchase cancelled
    - network disconnected
  evidence:
    - automated_test: null
    - manual_result: NOT_TESTED
    - screenshot_or_log: null
```

The critical rule:

```text
NOT_TESTED ≠ PASS
```

This makes the agent honest about the limits of source-code analysis.

### Metadata and App Store Connect pack

The skill should either read exported/App Store Connect information supplied by the developer or generate an explicit list of information it still needs.

It should build a pre-submission package containing:

```text
App identity
Version/build
Primary category
Age rating assessment
Content-rights assessment
Description
Keywords
Screenshots/device coverage
Support URL
Privacy-policy URL
App Privacy reconciliation
Pricing
Territories
IAP/subscription inventory
Review contact
Demo credentials
Review Notes
DSA status
Encryption/export determination
Regulated-app declarations where applicable
Paid Apps Agreement status if monetised
```

Apple's own App Store Connect reference identifies required properties and App Review information and explicitly requires working review credentials for apps where login is necessary. citeturn18search6turn15view5

### Severity model

I recommend four severities:

| Severity | Meaning | Examples |
|---|---|---|
| **BLOCKER** | Strong evidence the build should not be uploaded/submitted | Crash; Xcode validation error; required review account unavailable; core IAP broken; mandatory account deletion absent; Apple-listed SDK missing required manifest; clear policy-prohibited payment path |
| **HIGH** | Plausible rejection or inability to review; developer must resolve or supply evidence | Metadata/function mismatch; permission flow unclear; review backend not production-tested; UGC control not proven; social-login exception uncertain |
| **MEDIUM** | Production-quality issue that could become review trouble depending on impact | Poor offline handling; layout clipping on edge device; accessibility failure; confusing error state |
| **INFO** | Improvement/future preparation | Accessibility Nutrition Labels not yet completed while voluntary; September 2026 questionnaire preparation |

This is preferable to a single numerical “87% ready” score, which creates false precision.

### Evidence standard

Every finding should look like:

```text
[BLOCKER] ASR-PRIVACY-004
Account creation exists but no in-app account deletion route was found.

Evidence
- Sources/Auth/RegisterView.swift:42
- Sources/Settings/AccountView.swift:1-210
- Searched routes/actions for delete-account functionality: none found

Apple basis
Guideline 5.1.1(v): apps supporting account creation must offer
account deletion within the app.

Why this matters
Apple explicitly treats account deletion as a submission requirement.

Required resolution
Add an easy-to-find account deletion initiation path. It must delete
the account rather than merely deactivate it, subject to legally
required retention.

Verification
1. Create review account.
2. Delete from Settings.
3. Confirm session revoked.
4. Confirm backend account/data deletion behaviour.
5. Confirm Sign in with Apple token revocation if used.

Status
OPEN
```

Apple's current account-deletion rules directly support that logic. citeturn13view4turn15view4

The same evidence structure should apply to every finding. This avoids the common AI-agent problem of inventing vague warnings such as “Apple may reject this” without showing exactly where the concern came from.

### Final decision rules

The skill should finish with one of only three submission decisions:

```text
NO-GO
Any BLOCKER exists.

HOLD
No blockers, but one or more HIGH findings or mandatory
runtime/compliance evidence remains unverified.

READY TO UPLOAD
No BLOCKER/HIGH findings remain, Apple freshness checks pass,
release/archive validation passes, mandatory metadata/compliance
is complete, and required manual review scenarios have PASS evidence.
```

Then print:

```text
Decision: READY TO UPLOAD
Confidence: HIGH

Known blockers: 0
High-risk findings: 0
Medium findings: 3
Manual tests incomplete: 0
Apple guideline freshness checked: 10 Aug 2026
Archive validation: PASS
Reviewer simulation: PASS
Privacy reconciliation: PASS
IAP reconciliation: PASS
Metadata reconciliation: PASS

Important:
This means no known readiness blocker was identified.
It is not a guarantee of App Review approval.
```

The disclaimer is not boilerplate; Apple's own pre-submission guidance explicitly says its checklist cannot guarantee approval. citeturn13view0

## Production-ready master checklist and recommended go/no-go standard

The following is the checklist I would ultimately encode as the skill's final gate.

### Release integrity

| Requirement | Ready when |
|---|---|
| Production build | Release configuration builds successfully |
| Apple toolchain | Build meets Apple's **current** Xcode/SDK submission requirement; today that is Xcode 26+ and applicable version-26 SDK. citeturn14view0 |
| Archive | App Store archive produced |
| Validation | Xcode `Validate App` passes with all issues corrected. citeturn14view5 |
| Bundle ID | Matches intended App Store Connect app record. citeturn14view5 |
| Signing/entitlements | Distribution signing and entitlements are correct and justified. citeturn14view5 |
| Core journeys | Every advertised/core workflow has been tested from a clean installation |
| Crash state | No known crash/hang/obvious technical defect; Apple explicitly rejects these. citeturn15view1 |
| Temporary content | No placeholder/unfinished public content. citeturn13view1turn15view1 |
| Error handling | No important user interaction can fail silently |
| Back end | Production reviewer-facing services are live and externally reachable. citeturn13view0 |

### Privacy and security

| Requirement | Ready when |
|---|---|
| Privacy policy | Public, working, present inside app and App Store Connect and accurately describes practices. citeturn15view4 |
| Data inventory | First-party + third-party collection identified |
| ASC privacy | Answers agree with actual app/SDK behaviour. citeturn14view3 |
| SDK inventory | Every production dependency known |
| SDK manifests/signatures | Current Apple requirements satisfied. citeturn13view3 |
| Required Reason APIs | Used APIs have applicable approved reasons. citeturn14view0 |
| ATT | Correct where tracking occurs; no tracking workaround/fingerprinting. citeturn14view4 |
| Permissions | Every request is justified, accurately explained and gracefully denied. citeturn15view4 |
| Account deletion | Present and functional whenever account creation exists. citeturn13view4 |

### Product-policy compliance

| Requirement | Ready when |
|---|---|
| Login necessity | Non-account features are not unnecessarily forced behind registration. citeturn15view4 |
| Third-party login | Guideline 4.8 equivalent login/exception correctly handled. citeturn15view3 |
| UGC | Filter/report/block/contact requirements fulfilled where applicable. citeturn15view0 |
| Digital commerce | StoreKit/IAP rules and relevant storefront exceptions applied. citeturn15view2 |
| IAP quality | Products complete, visible and functional. citeturn15view1 |
| Age rating | Answers accurately represent app content/capabilities; app is not Unrated. citeturn14view1 |
| Social capability | July 2026 questionnaire change assessed now; September 2026 requirement prepared for. citeturn14view2 |
| IP/content rights | App has rights to distributed third-party material as required by Apple. citeturn16search17 |
| Minimum functionality/spam | No obvious template clone, misleading product or duplicate-app strategy. citeturn16search17 |

### Store listing and reviewability

| Requirement | Ready when |
|---|---|
| Description | Matches actual production feature set |
| Screenshots/previews | Show current real app functionality, not merely splash/login screens. citeturn15view1 |
| Purchase claims | Clearly identify paid/premium elements. citeturn15view1 |
| Support URL | Working and contains real contact route. citeturn18search14 |
| Privacy URL | Working. citeturn18search7 |
| Review contact | Current name/email/phone supplied. citeturn15view5 |
| Demo credentials | Working and non-expiring where login is required. citeturn15view5 |
| Review Notes | Tell reviewer how to reach every non-obvious feature/IAP. citeturn13view0 |
| Hardware/resources | QR code/accessory/video/instructions available where needed. citeturn13view1 |
| Reviewer rehearsal | Independent clean-install reviewer can complete all relevant journeys using only supplied instructions |

### Commercial and territorial readiness

| Requirement | Ready when |
|---|---|
| Paid Apps Agreement | Active if needed for paid app/IAP. citeturn18search13turn18search22 |
| Tax/banking | Required commercial details complete. citeturn18search5turn18search8 |
| Export compliance | Encryption classification completed and documentation attached where required. citeturn16search6turn16search13 |
| DSA | Trader status assessed and required EU information verified. citeturn13view5 |
| Territorial rules | Conditional requirements checked for all chosen storefronts. citeturn18search6 |
| Regulated category | Required medical/other regulatory declarations completed where applicable. citeturn18search6 |

### Quality confidence

| Requirement | Ready when |
|---|---|
| TestFlight | Release candidate has received realistic beta testing before App Review; Apple directs beta software to TestFlight rather than submitting unfinished versions. citeturn15view1 |
| Device matrix | Supported device classes tested |
| Network matrix | Offline, slow, interrupted and server-error behaviour tested |
| Permission matrix | Allow/deny/revoke behaviour tested |
| Lifecycle | First install, relaunch and update paths tested |
| Authentication | Login/logout/reset/delete/re-register scenarios tested |
| Commerce | All relevant purchase states tested |
| Accessibility | Common tasks sanity-tested using appropriate accessibility features; current Accessibility Nutrition Labels are voluntary initially but planned to become mandatory later. citeturn18search20 |
| No unknowns | Every mandatory manual check has explicit evidence rather than being assumed |

The most important final rule for the skill should be:

> **Do not ask “Can this app probably pass?” Ask “What evidence proves that each rejection surface has been resolved?”**

That is the substantial difference between a generic Apple-guidelines chatbot and a genuinely useful App Store release agent.

The GitHub ecosystem is already converging on pieces of this model — guideline modules, privacy audits, static scanning, simulator/runtime testing and evidence-linked findings — but no static agent can infer every reviewer-visible state from source alone. Recent tools explicitly describe the value of simulator-driven review because runtime issues can escape code review, while other tools focus on build artefacts and privacy/entitlement scanning. The strongest design is therefore **hybrid: deterministic checks + semantic policy review + real runtime evidence + App Store Connect reconciliation**. citeturn17search15turn17search2turn17search3

Apple's own numbers justify making App Completeness and production behaviour the highest-priority gates: more than 40% of unresolved review issues fall under Guideline 2.1, and Apple's 2025 transparency report shows Performance was by far the largest top-level rejection-guideline category. citeturn13view1turn13view2

So the ideal dedicated skill is not:

```text
Read Apple's guidelines → search code → say "looks compliant"
```

It is:

```text
Refresh current Apple rules
        ↓
Understand app, features, targets and territories
        ↓
Inspect source + generated native configuration + dependencies
        ↓
Map features to applicable Apple policies
        ↓
Audit privacy, permissions, accounts, payments and UGC
        ↓
Build the actual Release candidate
        ↓
Archive + Apple Validate App
        ↓
Exercise adversarial runtime test matrix
        ↓
Reconcile behaviour ↔ privacy ↔ metadata ↔ StoreKit ↔ policy
        ↓
Simulate reviewer from a clean installation
        ↓
Generate Review Notes and missing App Store Connect items
        ↓
BLOCKER / HIGH / MEDIUM / INFO findings with evidence
        ↓
NO-GO / HOLD / READY TO UPLOAD
```

That workflow most closely reflects what Apple's current documentation actually demands while incorporating the most useful lesson from GitHub, Reddit and Apple Developer Forums: **App Review failures often occur not because a developer never read the rules, but because the production build, reviewer environment, metadata or an untested edge state does not behave the way the developer assumed it would.** Apple's own completeness statistics, official pre-submission checklist and community rejection reports all point in the same direction. citeturn13view0turn13view1turn16search4turn16search11