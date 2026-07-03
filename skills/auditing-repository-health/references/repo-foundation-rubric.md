# Repository Foundation Rubric

Use this reference after running the auditor and reading the repository inventory.

## Scope Contract

Classify the audit target as:

- single repository
- monorepo
- polyrepo set
- source/plugin mirror repository
- generated/vendor subtree

Do not apply monorepo rules to polyrepo audits or polyrepo rules to one checkout.

## Evidence Before Prescription

Do not recommend a repository tree, scripts, CI layout, package structure, or boilerplate until these are known:

- repo purpose
- primary ecosystem or ecosystems
- package boundaries
- runtime model
- existing commands
- CI coverage
- release/deployment expectations

If package boundaries cannot be identified, say so explicitly and avoid package-specific recommendations.

## Responsibilities, Not Filenames

Use `bootstrap`, `setup`, `update`, `server`, `test`, `cibuild`, and `console` as responsibility names only. Healthy repositories may express them through `Makefile`, `justfile`, package scripts, Gradle tasks, Cargo commands, SwiftPM commands, `bin/`, `tools/`, CI workflows, or documented custom commands.

Do not require exact Scripts-to-Rule-Them-All filenames unless the repository already uses that convention or a wrapper is clearly justified.

## Root Health Does Not Prove Package Health

Root health does not prove package health.

Root-level success does not prove nested package health in monorepos or source/plugin mirrors.

Check package-specific manifests, scripts, docs, and CI coverage before concluding the repo is healthy.

## Missing Best-Practice Files Are Usually Not Blockers

README, CONTRIBUTING, CODEOWNERS, SECURITY.md, issue templates, and PR templates are usually P2/P3 unless the repository is public, installable, regulated, security-sensitive, or critical production infrastructure.

## Baseline Foundations

Look for:

- README or equivalent entrypoint documentation
- license when code is redistributable
- contribution guide for shared or public work
- security policy for public, installable, production, or security-sensitive work
- code ownership or review routing when ownership is non-obvious
- issue and PR templates when external contribution flow exists
- agent instructions when agents are expected to work in the repo
- dependency manifests and lockfiles where the ecosystem expects them
- setup, focused test, and full validation responsibilities
- CI workflows or documented release gates
- generated-file ignore policy
- release or deployment instructions when artifacts ship
