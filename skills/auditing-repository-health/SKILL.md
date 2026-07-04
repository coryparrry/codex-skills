---
name: auditing-repository-health
description: Use when auditing repository health, onboarding to a repo, checking multi-repo or monorepo setup, validating language-specific scaffolding, scripts, CI, docs, packaging, mirrors, Git hygiene, generated files, or missing developer lifecycle gates.
---

# Auditing Repository Health

## Overview

Run a read-only repository health audit before trusting a repo for repeated work. The script is the executable baseline; references provide judgement for repo topology and ecosystem setup.

## Required Workflow

1. Run the bundled auditor first.
2. Read the generated `Repository Inventory` and `Lifecycle Gate Matrix`.
3. Classify the repository before writing findings.
4. Read `references/report-contract.md`.
5. Read `references/repo-foundation-rubric.md` when recommending foundations.
6. Use `references/ecosystem-index.md` to choose only the relevant ecosystem overlays.
7. Inspect `Folder Structure` before recommending file moves, cleanup, or repo tree changes.
8. For monorepos and polyrepos, assess root/shared foundations separately from each package, service, app, docs root, or mirror root.
9. Preserve the existing report sections and add the inventory/classification sections when applicable.
10. Do not prescribe generic boilerplate, generic repo trees, or Scripts-to-Rule-Them-All filenames unless evidence shows that convention already fits the repo.
11. Every finding must name the affected path or scope and cite concrete evidence.

If you cannot identify package boundaries, say so explicitly and avoid package-specific recommendations.

## Run The Audit

From the repository being audited:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/auditing-repository-health/scripts/audit_repository_health.py" --repo "$PWD"
```

From this source checkout:

```bash
python3 skills/auditing-repository-health/scripts/audit_repository_health.py --repo "$PWD"
```

For automation:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/auditing-repository-health/scripts/audit_repository_health.py" --repo "$PWD" --format json
```

## Report Contract

Preserve these sections when summarizing:

```md
## Verdict
## Findings
## Repository Shape
## Repository Inventory
## Folder Structure
## Lifecycle Gate Matrix
## Documentation
## Scripts
## Validation
## Packaging
## Hygiene
## Commands Run
## Not Checked
```

Read `references/report-contract.md` before producing a final audit.

## Reference Routing

- Unclear script responsibility: read `references/script-responsibilities.md`.
- Foundation recommendations: read `references/repo-foundation-rubric.md`.
- Ecosystem-specific setup: read `references/ecosystem-index.md`, then only the matching `references/ecosystems/*.md` overlays.

## Common Mistakes

| Mistake | Correct behavior |
|---|---|
| Listing ideal scripts without running the audit | Run the bundled auditor first, then interpret gaps. |
| Treating root health as package health | Use the inventory and lifecycle matrix to inspect each package, service, docs root, or mirror root separately. |
| Forcing script filenames | Audit responsibilities and accept repo-native commands. |
| Recommending boilerplate before classification | Classify purpose, ecosystem, package boundaries, and CI coverage first. |
| Dropping `Not Checked` | Preserve skipped areas so readiness is not overstated. |
