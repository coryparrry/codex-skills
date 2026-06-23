---
name: auditing-repository-health
description: Use when auditing a repository before onboarding, planning, coding, debugging, cleanup, packaging, release, CI repair, adding a skill, checking missing scripts, or validating repository shape, documentation, scripts, validation gates, Git hygiene, generated files, and package mirror readiness.
---

# Auditing Repository Health

## Overview

Run a read-only repository health audit before trusting a repo for repeated work. The bundled script is the baseline; manual inspection is for ambiguous findings and repo-specific context.

## Run The Audit

From the repository being audited:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/auditing-repository-health/scripts/audit_repository_health.py" --repo "$PWD"
```

If working from this source checkout instead of an installed skill:

```bash
python3 skills/auditing-repository-health/scripts/audit_repository_health.py --repo "$PWD"
```

For automation or follow-on processing:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/auditing-repository-health/scripts/audit_repository_health.py" --repo "$PWD" --format json
```

## What The Tool Checks

| Area | Checks |
|---|---|
| Repository shape | README, instructions, docs, manifests, scripts directories, CI metadata, contribution/security surfaces. |
| Documentation | Markdown files, broken local Markdown links, duplicate-looking docs, unresolved public markers. |
| Scripts | `bootstrap`, `setup`, `update`, `server`, `test`, `cibuild`, and `console` responsibilities classified as `present`, `documented`, `missing`, or `not_applicable`. |
| Validation | Focused tests, reusable full-gate candidates, CI workflow presence, shell/Python test inventory. |
| Packaging | Skill source folders, `agents/openai.yaml`, and `plugins/codex-skills/skills` mirror parity when this is a skill repo. |
| Hygiene | Branch, dirty/untracked state, tracked generated files, ignored file sample, largest tracked files, Git object summary. |

## Report Contract

Lead with the script report. Preserve these sections when summarizing to the user:

```md
## Verdict
## Findings
## Repository Shape
## Documentation
## Scripts
## Validation
## Packaging
## Hygiene
## Commands Run
## Not Checked
```

Findings use `P0` to `P3` severity and include evidence, impact, and smallest practical fix shape. Treat `Ready to proceed: conditional` as normal when the repo is usable but lacks a foundation such as setup, test, CI, docs, or mirror checks.

## Manual Follow-Up

After running the script:

1. Inspect any `P0` or `P1` findings directly before recommending work.
2. Map script gaps to the repo's own conventions before proposing new names.
3. Keep `Not Checked` in the final audit; do not convert skipped network, install, or mutation checks into implied pass/fail results.
4. For skill/plugin repos, verify source and plugin mirror changes stay synchronized.

If script status looks ambiguous, read `references/script-responsibilities.md` before recommending fixes.

## Common Mistakes

| Mistake | Correct behavior |
|---|---|
| Listing ideal scripts without running the audit | Run the bundled auditor first, then interpret gaps. |
| Treating one passing command as repo health | Tie each command to the surface it proves and keep unverified areas visible. |
| Forcing GitHub workflow advice | Audit the repo foundations; GitHub is only relevant when repo-local evidence points there. |
| Hiding dirty state as noise | Report it so follow-on work can stay scoped. |
| Dropping `Not Checked` | Preserve skipped areas so readiness is not overstated. |
