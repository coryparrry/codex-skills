# Docker and Services

## Detection Artifacts

- `Dockerfile`
- `docker-compose.yml`
- `docker-compose.yaml`
- `.env.example`
- `healthcheck`

## Common Repo Shapes

- service packaged as a container
- local compose stack for dependencies
- app with container release and local runtime parity

## Required Lifecycle Gates

- setup/bootstrap: image build, compose pull, or documented environment setup
- focused test: container build or service-specific smoke command
- full validation/CI: build, health check, integration test, and publish gates when the service ships

## Native Commands

- `docker build`
- `docker compose up`
- `docker compose test`
- `docker compose down`
- migration command for schema changes

## CI Expectations

CI should validate the image or compose flow that developers use locally and include any health or migration checks required to ship.

## Package Boundary Rules

Treat a lone `Dockerfile` as release packaging when there is no local compose stack. Do not force compose rules onto a pure image-only repo.

## Common False Positives

- Do not require compose when a single `Dockerfile` is only release packaging.
- Do not require a long-running server command for a build-only container.

## Severity Guidance

Missing health checks or integration coverage in a shipped service is usually P2. Missing migration documentation can be P1 when it affects deployment safety.

## Good Finding Examples

- P2 scoped to `services/api`: `docker-compose.yml` exists, but no documented integration or health-check command covers the stack.

## Bad Finding Examples

- P2 at root: repo lacks `docker compose up` even though it only builds a release image.
