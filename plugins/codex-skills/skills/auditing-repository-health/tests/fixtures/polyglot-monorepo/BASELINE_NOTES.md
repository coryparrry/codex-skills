# Baseline Notes

Baseline command:

```bash
python3 skills/auditing-repository-health/scripts/audit_repository_health.py --repo skills/auditing-repository-health/tests/fixtures/polyglot-monorepo --format json
```

Observed baseline failure:

- The report does not emit a repository topology inventory.
- The report does not list package, service, or docs boundaries.
- The report cannot distinguish root/shared validation from package-specific validation.
- The report cannot show that `packages/worker` lacks package-level test coverage while root and Go API validation exist.
- The report is therefore vulnerable to shallow root-only recommendations.

## Updated Forward Test

Updated command:

```bash
python3 skills/auditing-repository-health/scripts/audit_repository_health.py --repo skills/auditing-repository-health/tests/fixtures/polyglot-monorepo --format json
```

Observed updated behavior:

- The report emits `repository_inventory`.
- The report classifies the fixture as `monorepo`.
- The report emits package, service, and docs boundaries.
- The lifecycle matrix separates root/shared validation from package-specific validation.
- The lifecycle matrix marks `packages/api` test coverage present from CI evidence.
- The lifecycle matrix marks `packages/worker` focused tests missing.
