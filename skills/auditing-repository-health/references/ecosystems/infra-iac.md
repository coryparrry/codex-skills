# Infrastructure and IaC

## Detection Artifacts

- `main.tf`
- `*.tf`
- `Pulumi.yaml`
- `Chart.yaml`
- Kubernetes manifests

## Common Repo Shapes

- Terraform infrastructure
- Pulumi infrastructure app
- Helm chart or Kubernetes deployment surface

## Required Lifecycle Gates

- setup/bootstrap: provider install, cloud auth, or documented environment bootstrap
- focused test: `terraform fmt -check`, `terraform validate`, chart lint, or a stack-specific equivalent
- full validation/CI: plan, policy, preview, or release gating when the repo changes live infrastructure

## Native Commands

- `terraform fmt -check`
- `terraform validate`
- `terraform plan`
- `helm lint`
- `pulumi preview`
- `kubectl` validation or manifest render command

## CI Expectations

CI should validate formatting and static correctness before any apply or release step.

## Package Boundary Rules

Treat infra roots, charts, and nested modules as separate ownership surfaces when the repo has multiple deployment units.

## Common False Positives

- Do not require app server commands for pure infrastructure repos.
- Do not require runtime tests when the repo only defines deployable infrastructure.

## Severity Guidance

Missing validate or lint steps in live infrastructure code is usually P1 or P2 depending on blast radius. Missing plan safety can be P1 when changes reach production.

## Good Finding Examples

- P1 scoped to `infra/network`: `main.tf` exists, but no documented `terraform validate` or equivalent gate protects the stack.

## Bad Finding Examples

- P2 at root: repo lacks a server command even though the project is only Terraform.
