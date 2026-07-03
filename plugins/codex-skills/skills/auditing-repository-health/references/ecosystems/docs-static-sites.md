# Docs and Static Sites

## Detection Artifacts

- `mkdocs.yml`
- `docusaurus.config.js`
- `docs/`
- `site/`
- `public/`

## Common Repo Shapes

- documentation site
- static handbook or knowledge base
- generated docs output with a source content tree

## Required Lifecycle Gates

- setup/bootstrap: install the site generator or documented equivalent
- focused test: docs render/build command and link checks when configured
- full validation/CI: build, render, and publish steps when the site ships

## Native Commands

- `mkdocs build`
- `npm run build`
- `npm run lint`
- `npm run test`
- link checker or docs-specific validation command

## CI Expectations

CI should render the same docs output and run link or build validation that contributors use locally.

## Package Boundary Rules

Do not treat generated output as source. Distinguish content, templates, and publish artifacts.

## Common False Positives

- Do not require a server/runtime command for a static docs site.
- Do not require an application deployment gate when the repo only publishes static pages.

## Severity Guidance

Missing render or link checks in a public docs site is usually P2. Broken publish instructions can be P1 when the docs are externally shipped.

## Good Finding Examples

- P2 scoped to `docs/`: `mkdocs.yml` exists, but no documented build or link-check command covers the site.

## Bad Finding Examples

- P2 at root: repo lacks a long-running server command even though the project is a static site.
