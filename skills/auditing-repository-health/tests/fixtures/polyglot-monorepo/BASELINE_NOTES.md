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
