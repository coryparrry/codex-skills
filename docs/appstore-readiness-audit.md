# App Store readiness audit

`appstore-readiness-audit` checks an Apple app before upload or submission to App Store Connect. It treats the release candidate, current Apple rules, runtime behavior, privacy, metadata, and reviewer access as separate evidence surfaces.

## Install

To install only this skill, run:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill appstore-readiness-audit
```

To install all skills, run:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill '*'
```

## Use

Use this prompt from the Apple app repository:

```text
Use $appstore-readiness-audit to audit this release candidate for App Store submission readiness without changing it.
```

Provide the intended platforms, storefronts, and whether this is a new app or an update. Supply a release archive, App Store Connect export or read-only access, and runtime evidence when available. The skill records missing inputs as evidence gaps rather than guessing.

## What it audits

The skill refreshes current Apple sources before applying platform or feature rules. It then identifies the exact source snapshot and release candidate, including bundle ID, version, build, configuration, artifact path, and hash.

The audit covers:

- Release configuration, signing, entitlements, capabilities, archive, and Xcode validation
- Clean launch, core flows, production services, failure recovery, and reviewer access
- Data collection, third-party SDKs, privacy manifests, Required Reason APIs, permissions, and tracking
- Accounts, account deletion, third-party login, user-generated content, children, and regulated features
- In-App Purchase, subscriptions, payment routing, storefront rules, and commercial prerequisites
- App Store metadata, privacy answers, age ratings, export compliance, territories, and Review Notes
- Clean-install reviewer simulation using only the information supplied to App Review

Conditional checks run only when the app's feature map activates them. An imported framework or missing search result is a lead, not proof.

## Verdicts

The skill returns one result:

| Verdict | Meaning |
|---|---|
| `NO_GO` | A confirmed blocker exists. |
| `HOLD_UNVERIFIED` | Required evidence is missing, conflicted, untested, or high risk. |
| `READY_FOR_UPLOAD` | Local project, Release, artifact, and toolchain gates pass. App Store Connect or reviewer evidence may still be incomplete. |
| `READY_FOR_SUBMISSION` | Project, artifact, policy, runtime, privacy, metadata, commerce, compliance, and reviewer checks have current passing evidence. |

The report leads with findings and includes the audit boundary, feature map, evidence ledger, missing checks, reviewer handoff, and direct Apple sources. It does not use a readiness score or guarantee approval.

## Review Notes byte check

Apple measures App Review Notes in bytes. Check a local draft without printing its content:

```bash
python3 skills/appstore-readiness-audit/scripts/check_review_notes.py /path/to/review-notes.txt
```

Use `--json` for machine-readable output or `-` to read from standard input. Keep credentials out of source control and audit reports.

## Skill layout

```text
skills/appstore-readiness-audit/
  SKILL.md
  agents/
    openai.yaml
  references/
    apple-sources.md
    audit-catalog.md
    report-format.md
  scripts/
    check_review_notes.py
  tests/
    test_check_review_notes.py
```

## Related docs

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [Reference](reference.md)
- [Swift Code Review](swift-code-review.md)
