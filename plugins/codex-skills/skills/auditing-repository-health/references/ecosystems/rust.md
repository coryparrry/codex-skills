# Rust

## Detection Artifacts

- `Cargo.toml`
- `Cargo.lock`
- workspace members
- `src/`
- `tests/`

## Common Repo Shapes

- library crate
- binary crate in `src/main.rs`
- workspace with shared crates and package-specific tests

## Required Lifecycle Gates

- setup/bootstrap: usually `cargo fetch` or no explicit setup beyond the Rust toolchain
- focused test: `cargo test`
- full validation/CI: `cargo test`, `cargo clippy`, `cargo fmt --check`, and docs or build gates when relevant

## Native Commands

- `cargo test`
- `cargo clippy`
- `cargo fmt --check`
- `cargo build`
- `cargo doc`

## CI Expectations

CI should run the crate or workspace test command and the formatting or lint gate the repo documents.

## Package Boundary Rules

Treat workspace members as separate audit surfaces when commands or CI differ between crates.

## Common False Positives

- Do not require `Cargo.lock` in every library context without checking repo policy.
- Do not require external setup when the crate builds with the standard toolchain only.

## Severity Guidance

Missing tests or formatting gates in a shipped crate is usually P2. Missing clippy on a public or security-sensitive crate can be P1 if the repo relies on it.

## Good Finding Examples

- P2 scoped to `crates/api`: `Cargo.toml` exists, but no `cargo test` or equivalent crate-level command is documented.

## Bad Finding Examples

- P2 at root: repo lacks a lockfile even though the project policy says libraries may omit it.
