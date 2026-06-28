# Go

## Detection Artifacts

- `go.mod`
- `go.sum`
- `cmd/`
- `internal/`
- `main.go`

## Common Repo Shapes

- CLI with `cmd/<tool>`
- library module with packages under `internal` or sibling directories
- service with a single `main` package and integration checks

## Required Lifecycle Gates

- setup/bootstrap: usually `go env`, `go mod download`, or no explicit setup beyond the toolchain
- focused test: `go test ./...` or package-scoped `go test`
- full validation/CI: `go test ./...`, `go vet`, lint, and packaging or release steps when used

## Native Commands

- `go test ./...`
- `go test ./pkg/...`
- `go vet ./...`
- `go fmt ./...`
- `golangci-lint run`
- `go build ./...`

## CI Expectations

CI should run the same module or package test commands and any lint/static-analysis gate the repo documents.

## Package Boundary Rules

Use `cmd/` for executable surfaces and `internal/` for shared library boundaries. Do not force setup instructions when the module has no external runtime setup.

## Common False Positives

- Do not require a separate bootstrap script for a normal Go module.
- Do not treat the absence of a root shell wrapper as a problem when `go test ./...` is documented.

## Severity Guidance

Missing tests in a shipped Go service or CLI is usually P2. Missing vet/lint on a critical module can rise to P1 when regressions are likely.

## Good Finding Examples

- P2 scoped to `cmd/api`: `go.mod` exists, but no documented `go test ./...` or equivalent gate covers the executable package.

## Bad Finding Examples

- P2 at root: repo lacks `setup.sh` even though the module is a standard Go module with no extra setup.
