# Audit catalog

Activate checks from the feature map and platform scope. This catalog supplies questions and evidence targets. It does not make every line applicable to every app.

## Contents

- [Release identity and completeness](#release-identity-and-completeness)
- [Technical and platform integrity](#technical-and-platform-integrity)
- [Privacy, SDKs, and permissions](#privacy-sdks-and-permissions)
- [Accounts and authentication](#accounts-and-authentication)
- [User-generated content, children, and safety](#user-generated-content-children-and-safety)
- [Payments and subscriptions](#payments-and-subscriptions)
- [Metadata and reviewer access](#metadata-and-reviewer-access)
- [Territories, agreements, and regulated features](#territories-agreements-and-regulated-features)
- [Runtime evidence matrix](#runtime-evidence-matrix)

## Release identity and completeness

### Exact candidate

- Record repository commit and dirty state.
- Record bundle ID, version, build, platform, target, configuration, archive path, and SHA-256.
- Prove that runtime and metadata evidence belongs to that candidate.
- For an update, identify the previous public version and migration path.

### Production behavior

- Cold launch succeeds from a clean install.
- Every core and advertised journey completes.
- Login, registration, password reset, callback, purchase, restore, upload, download, AI request, and other async actions never fail with a log-only return or permanent spinner.
- Errors are visible, accurate, recoverable, and do not expose sensitive data.
- Production backends, callback URLs, support URLs, privacy URLs, and required content are live outside the developer network.
- Placeholder text, sample accounts, test endpoints, unfinished screens, debug menus, dormant features, and developer-only controls are absent from the production path.
- IAPs presented for review are complete, current, visible, and functional. Explain intentionally unavailable products in Review Notes.

### Build and archive

- Release uses the intended production bundle ID, service endpoints, flags, assets, and entitlements.
- Marketing version and build number match the intended App Store Connect version.
- Platform-specific SDK and submission requirements are current.
- Distribution signing, provisioning, app identifier capabilities, and compiled entitlements agree.
- App icons, launch assets, localizations, privacy manifests, embedded frameworks, and extensions are present in the produced bundle.
- Release compilation, tests, archive creation, Validate App, and upload processing are separate checks.
- Validation warnings remain visible; do not reduce the gate to exit code alone.

## Technical and platform integrity

- Use public APIs. Treat selector or symbol searches as leads until confirmed.
- Do not download executable code or materially change reviewed native behavior unless a current guideline exception applies.
- Justify every background mode and long-running activity through actual product behavior.
- Test IPv6-compatible networking and avoid IPv4-only assumptions or literals.
- Check retry loops, timers, polling, location use, media work, and background tasks for excessive power, heat, storage writes, or unrelated work.
- Obtain consent and show the expected system or in-app indication for recording microphone, camera, screen, or user activity where applicable.
- Exercise all declared device families, orientation rules, window sizes, focus or remote navigation, and extension limitations.

For Mac App Store targets, check sandboxing, container behavior, user-selected file access, app-group use, helper and login items, updater code, installers, license screens, privilege escalation, code outside the bundle, and processes that outlive the app. A non-Mac App Store distribution proof is not evidence for the Mac App Store candidate.

For extensions, widgets, App Clips, keyboards, notifications, and watch apps, check restricted APIs, content, entitlements, and advertising rules separately from the host app.

## Privacy, SDKs, and permissions

### Data inventory

For every data category, record:

| Field | Question |
|---|---|
| Source | Which screen, sensor, file, account, SDK, or service produces it? |
| Destination | First-party server, Apple service, device only, or named third party? |
| Purpose | Product function, analytics, diagnostics, advertising, personalization, or another purpose? |
| Identity | Is it linked to an account, person, or device? |
| Tracking | Is it combined across companies for tracking, advertising, or attribution? |
| Consent | What user action or system permission authorizes it? |
| Retention and deletion | How long is it kept and how can it be removed? |
| Declarations | Does the privacy policy, privacy manifest, and App Store Connect answer agree? |

Include analytics, crash reporting, remote configuration, attribution, advertising, authentication, cloud storage, AI providers, and transitive SDK behavior. Do not infer no collection from the absence of a first-party network client.

### Dependencies and privacy manifests

- Inventory package manifests, lockfiles, Pods, Carthage artifacts, XCFrameworks, embedded frameworks, React Native packages, Expo plugins, Flutter packages, and manually embedded binaries where present.
- Record dependency name, version, source, linkage, embedded binary identity, privacy manifest, signature evidence, declared data, and Required Reason API categories.
- Refresh Apple's listed SDK page. Apply manifest and signature blockers only to the stated new-app or update condition and dependency form.
- Locate every `PrivacyInfo.xcprivacy`, including manifests inside bundles and dependencies.
- Match Required Reason API use to applicable approved reasons. Do not use a fixed local list as current policy.
- Treat a manifest mismatch as a finding even if a file exists.
- Do not require a privacy manifest solely because the app has dependencies.

### Permissions and tracking

Check, when used, camera, microphone, photos, contacts, location, Bluetooth, calendars, reminders, motion and fitness, health, speech, tracking, local network, Face ID, media library, and platform-specific protected resources.

For each permission:

1. Confirm the API or generated capability is present.
2. Confirm the required native declaration is in the release product.
3. Check that the purpose string names the feature and the data use clearly.
4. Request at the point of need, not as an unexplained launch wall.
5. Test denial, later revocation, and a practical alternative where possible.
6. Reconcile collection and use with the privacy policy and App Store Connect.

When tracking is possible, inspect SDK initialization, data sent before ATT choice, denial behavior, feature gating, privacy labels, attribution, and fingerprinting risk. ATT API presence does not prove compliance.

## Accounts and authentication

- Explain why login is needed. Do not force non-account functionality behind registration without a product reason.
- Test correct and wrong credentials, duplicate account, email verification, password reset, expired session, logout, re-login, callback cancellation, network failure, deletion, and re-registration.
- Supply a non-expiring review account or an Apple-approved full demo mode when review needs login.
- Check third-party login against current Guideline 4.8 and document an equivalent login service or an applicable exception.
- If Sign in with Apple is used, inspect nonce and callback handling, private relay compatibility, account linking, and token revocation on deletion where required.

When account creation exists:

- users can initiate deletion in the app;
- the flow deletes the account rather than only deactivating it;
- associated personal data and user-generated content are handled as disclosed;
- auto-created and guest accounts receive the required treatment;
- additional confirmation, delayed completion, or legal retention has documented support;
- the post-deletion session is revoked and re-registration behavior is tested.

Do not fail a legally constrained or confirmation-based process without checking Apple's documented conditions and the app's evidence.

## User-generated content, children, and safety

When users can create, upload, redistribute, amplify, message, comment, review, or discover other users' content, check:

- filtering or prevention appropriate to the content;
- reporting from every relevant surface;
- timely moderation handling in the live service;
- blocking abusive users;
- published operator contact details;
- terms or community standards;
- age-rating and social-capability answers;
- creator-content purchase disclosure and age restriction where applicable;
- anonymous or random chat and other prohibited-use risks.

For Kids Category or child-directed apps, check parental gates, outbound links, purchases, advertising, analytics, data transfer, age treatment, and continued category obligations. Keep legal privacy review distinct from Apple policy review.

For medical or safety claims, verify methodology, accuracy support, disclaimers, regulatory clearance, and the entity behind high-risk functionality. Unsupported sensor-based diagnosis or treatment claims are blockers where Apple prohibits them.

## Payments and subscriptions

Classify each sale before applying a rule:

- digital content or functionality consumed in the app;
- physical goods or services consumed outside the app;
- qualifying person-to-person service;
- reader app content;
- eligible storefront-specific external purchase path;
- another documented exception.

For StoreKit products, reconcile:

- product ID in code, configuration, App Store Connect, and reviewer path;
- product and submission state;
- price, duration, trial, renewal, entitlement, and paywall copy;
- purchase success and exactly-once entitlement grant;
- cancellation, pending, failure, retry, restore, expiry, revocation, refund, family sharing, upgrade or downgrade, and relaunch states as applicable;
- server notification and receipt or transaction validation behavior when used;
- restore access for restorable purchases;
- purchased credit or currency expiry and loot-box odds where applicable;
- Paid Apps Agreement, banking, tax, and sandbox prerequisites;
- storefront-specific external links, entitlements, disclosures, and placement.

Searches for Stripe, a web checkout, or StoreKit are leads. Determine what is sold, where it is consumed, and the intended storefront before deciding compliance.

## Metadata and reviewer access

Reconcile the candidate with:

- app name, subtitle, description, keywords, category, and age rating;
- screenshots and previews for every required device class and localization;
- current UI, real in-use screens, and honest premium or purchase disclosure;
- What's New text for an update;
- app icon, IAP artwork, content rights, and fictional rather than real personal data in media;
- support URL, privacy URL, marketing URL, and contact route;
- App Privacy answers and accessibility declarations;
- price, availability, territories, release option, and pre-order claims;
- IAP and subscription metadata;
- review contact, credentials, notes, attachments, sample data, video, QR codes, hardware, and special configuration.

Write Review Notes that tell an uninformed reviewer how to reach each non-obvious feature and success state. Include purchase, permission, region, and hardware steps when applicable. Use the current byte limit from the Apple source refresh. Pass this value to `--max-bytes`. Resolve `scripts/check_review_notes.py` relative to the loaded `SKILL.md`, not the app repository.

Never copy live reviewer credentials into the audit report, source control, logs, screenshots, or test fixtures. Report only whether credentials were supplied, tested, and non-expiring.

## Territories, agreements, and regulated features

- Record intended storefronts before applying regional payment or compliance rules.
- Determine export compliance from actual encryption use. Separate system-provided transport encryption from custom or non-exempt cryptography.
- Reconcile DSA trader status from App Store Connect evidence; do not decide the developer's legal status.
- For paid apps or IAP, verify the required agreement and financial setup through supplied or read-only evidence.
- Route mainland China, South Korea, Vietnam, EU, UK, US, and other conditional properties only when territory and feature triggers apply.
- Route medical, finance, crypto, gambling, VPN, dating, alcohol, cannabis, government, news, reader, and other regulated categories to current Apple and legal evidence.
- Record licenses, regulatory documents, and content rights without making an unsupported legal conclusion.

## Runtime evidence matrix

Use the exact candidate and record device or simulator, OS, locale, network state, account state, permission state, build identity, result, and evidence location.

| Surface | Required states when applicable |
|---|---|
| Installation | Clean install, relaunch, update from previous public build |
| Lifecycle | Foreground, background, interruption, termination, state restoration |
| Network | Offline, slow, intermittent, timeout, empty response, 4xx, 5xx, malformed response |
| Authentication | Success, wrong credentials, reset, verification, expiry, logout, delete, re-register |
| Permissions | Not determined, allow, deny, revoke later, restricted state, recovery |
| Commerce | Load, purchase, cancel, pending, fail, restore, expire, revoke, refund, relaunch |
| Layout | Small and large supported screens, iPad or Mac window behavior, orientation, keyboard, popover |
| Accessibility | VoiceOver, Voice Control where applicable, larger text, contrast, color independence, reduced motion, captions or descriptions where applicable |
| Appearance and language | Light, dark, long localization, right-to-left when supported |
| Dependencies | Backend unavailable, callback failure, hardware absent, sample resource invalid |

Use `PASS`, `FAIL`, or `NOT_TESTED` for each scenario. A source inspection is not a runtime pass.
