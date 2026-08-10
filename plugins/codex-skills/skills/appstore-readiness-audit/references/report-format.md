# Report format

Use this format so the user can act on the audit without confusing missing evidence with a pass.

## Contents

- [Report order](#report-order)
- [Scope block](#scope-block)
- [Finding shape](#finding-shape)
- [Evidence ledger](#evidence-ledger)
- [Reviewer handoff](#reviewer-handoff)
- [Review Notes draft](#review-notes-draft)

## Report order

1. Blocking and high-risk findings
2. Verdict and confidence
3. Evidence boundary
4. Gate summary
5. Required checks still unknown or not tested
6. Feature map and conditional modules
7. Reviewer handoff
8. Medium and informational observations
9. Disclaimer

Do not bury a blocker below a long checklist. If no blocker or high-risk finding survives verification, say so before the verdict.

## Scope block

```text
Audit target: <app and platform>
Repository: <path>
Source snapshot: <branch and commit, dirty state>
Release candidate: <bundle ID, version, build, configuration>
Artifact: <path and SHA-256, or not supplied>
App Store Connect evidence: <live read-only, dated export, local intended metadata, or unavailable>
Runtime evidence: <devices, simulators, TestFlight build, or unavailable>
Apple sources refreshed: <timestamp>
Excluded: <none or explicit exclusions>
Completeness: <complete or partial>
```

Do not include secrets, reviewer passwords, tokens, private keys, profiles, or sensitive diagnostics.

## Finding shape

```text
[BLOCKER] ASRA-2.1-001: Core purchase action can fail without visible recovery

Status: FAIL
Confidence: Confirmed
Basis: RUNTIME + APPLE_POLICY
Applies to: iOS, subscription purchase, selected storefronts

Evidence
- Candidate: <bundle ID, version, build, artifact hash>
- Runtime: <device, OS, steps, observed result>
- Project: <tight file and line reference when relevant>
- Apple: <direct current URL and short policy statement, or N/A when the basis does not depend on Apple policy or tooling>

Reviewer impact
<What App Review can see or be unable to do.>

Smallest resolution
<Direction only. The audit does not edit the app.>

Verification
<A check that distinguishes the current failure from corrected behavior.>
```

Use stable IDs by domain:

- `ASRA-2.1` for completeness and runtime behavior;
- `ASRA-BUILD` for project, signing, archive, and toolchain;
- `ASRA-PRIVACY` for data, SDK, manifest, permission, and tracking;
- `ASRA-ACCOUNT` for login and deletion;
- `ASRA-UGC` for social, creator, moderation, and children;
- `ASRA-COMMERCE` for IAP, subscriptions, and payment routing;
- `ASRA-METADATA` for product-page and review information;
- `ASRA-COMPLIANCE` for export, territories, agreements, and regulated features;
- `ASRA-QUALITY` for manual production controls that are not direct policy requirements.

Use `Confirmed`, `High`, or `Moderate` confidence. Keep a material Moderate concern in unresolved questions or validation gaps unless the evidence still supports a conservative hold.

## Evidence ledger

```markdown
| Gate | Status | Evidence | Gaps |
|---|---|---|---|
| Apple source freshness | PASS | Guidelines and submission pages retrieved on <date> | None |
| Project and Release configuration | PASS | <commands and files> | None |
| Release artifact | NOT_TESTED | No archive supplied | Archive identity and Validate App |
| Runtime completeness | NOT_TESTED | No candidate run | Clean launch and core flows |
| Privacy reconciliation | UNKNOWN | Local manifests inspected | Live App Privacy answers unavailable |
| Conditional policy | PASS | <activated modules and evidence> | None |
| Metadata and App Store Connect | UNKNOWN | Local intended metadata only | Live record unavailable |
| Reviewer simulation | NOT_TESTED | No demo account or clean run | Full reviewer journey |
```

For each `UNKNOWN` or `NOT_TESTED` item, state who or what can supply the missing evidence. Do not phrase missing evidence as a defect unless a required artifact or field is itself absent.

## Reviewer handoff

Report a concise handoff without secrets:

```text
Reviewer access: supplied and tested / supplied, not tested / unavailable
Core review path: <numbered route>
Purchases: <where to find them and expected state>
Permissions: <non-obvious reason and trigger>
Special configuration: <region, test data, feature state>
External dependency: <hardware, QR code, backend, attachment, or video>
Known limitations: <none or explicit limitation>
Review Notes byte count: <used>/<current limit>
```

State whether an independent clean-install rehearsal used only this handoff.

## Review Notes draft

Generate a draft only from verified facts. Use placeholders for secrets and tell the user to enter credentials directly in App Store Connect.

```text
Purpose
<What the app does in one short paragraph.>

Reviewer access
Username: <ENTER DIRECTLY IN APP STORE CONNECT>
Password: <ENTER DIRECTLY IN APP STORE CONNECT>
Account status: <confirmed non-expiring or unresolved>

Core review path
1. <Launch or sign-in step.>
2. <Navigation step.>
3. <Feature action.>
4. Expected result: <verified result.>

Purchases
<How to locate and exercise each reviewable product.>

Permissions
<Why and when each non-obvious permission appears.>

Special configuration or resources
<Region, test data, QR code, hardware, attachment, or demo video.>

Non-obvious behavior
<Feature flags, account state, regulated flow, or other reviewer knowledge.>

Contact
<Current review contact supplied in App Store Connect.>
```

If the draft contains sensitive information, save it outside version control. During each Apple source refresh, record the current Review Notes byte limit. Use the integer value without commas or units. Resolve `<skill-root>` to the absolute directory that contains the loaded `appstore-readiness-audit/SKILL.md`. Replace both placeholders before you present or run this command:

```bash
python3 "<skill-root>/scripts/check_review_notes.py" --max-bytes <review-notes-byte-limit> "/path/to/review-notes.txt"
```

The final command must contain the resolved absolute script path and a numeric `--max-bytes` value. Create a new command after each source refresh. The script reports only the UTF-8 byte count. It does not print the note content.
