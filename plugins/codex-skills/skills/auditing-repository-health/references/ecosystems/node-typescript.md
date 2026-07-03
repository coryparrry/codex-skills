# Node, TypeScript, JavaScript

## Detection Artifacts

- `package.json`
- `package-lock.json`
- `pnpm-lock.yaml`
- `yarn.lock`
- `packageManager`
- workspace settings
- `tsconfig.json`
- `vite.config.*`
- `next.config.*`

## Common Repo Shapes

- app or service with `dev`, `test`, `build`, and `lint`
- workspace repo with package-level scripts and a root orchestrator
- library with a small root surface and package-specific commands

## Required Lifecycle Gates

- setup/bootstrap: `npm install`, `pnpm install`, `yarn install`, or documented equivalent
- focused test: `npm test`, `pnpm -r test`, `vitest`, `node --test`, or package-specific command
- full validation/CI: lint, typecheck, build, and release gates when the repo ships code

## Native Commands

- `npm test`
- `npm run lint`
- `npm run typecheck`
- `npm run build`
- `npm run dev`
- `pnpm -r test`
- `pnpm -r lint`
- `pnpm -r build`

## CI Expectations

CI should exercise the same workspace-aware gates the repo documents locally. Package filters and recursive commands count when they are the native repo convention.

## Package Boundary Rules

Treat workspace package scripts as package-specific evidence. Do not require a root script when package scripts already cover the responsibility.

## Common False Positives

- Do not require a root `test` script when workspace packages already expose tests.
- Do not report missing `npm run dev` for libraries or build-only packages.

## Severity Guidance

Missing validation in a shipped workspace app is usually P2. Missing package-level typecheck or build coverage can be P1 when the package is production-facing.

## Good Finding Examples

- P2 scoped to `packages/web`: `package.json` exists but no workspace or package-level test command is documented for that package.

## Bad Finding Examples

- P2 at root: repo lacks `npm test` even though `pnpm -r test` and package scripts cover the workspace.
