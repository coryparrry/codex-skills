# Expected Audit Criteria

The updated skill must produce an audit that:

- classifies this fixture as a polyglot monorepo
- detects the Node workspace root
- detects the Go API package at `packages/api`
- detects the Python worker package at `packages/worker`
- detects the docs package at `docs`
- detects the Docker service surface at repository root
- separates root/shared lifecycle gates from package-specific gates
- maps the root `pnpm test` and CI workflow as shared validation evidence
- maps `go test ./...` from the workflow to `packages/api`
- reports that `packages/worker` has no package-level test command or CI coverage
- does not force `script/test`, `script/cibuild`, or other exact Scripts-to-Rule-Them-All filenames
- does not treat a missing root `scripts/validate.sh` as proof that no validation gate exists

## Forward-Test Evidence

Verified against `/tmp/polyglot-updated.json` from:

```bash
python3 skills/auditing-repository-health/scripts/audit_repository_health.py --repo skills/auditing-repository-health/tests/fixtures/polyglot-monorepo --format json | python3 -m json.tool > /tmp/polyglot-updated.json
```

Observed output confirmed that:

- `repository_inventory` is present.
- `repository_inventory.classification` is `monorepo`.
- `repository_inventory.ecosystems` includes `docker`, `go`, `node`, and `python`.
- `repository_inventory.boundaries` includes the Node workspace root, Docker service surface, docs site, Go package, and Python package.
- `lifecycle_gate_matrix.rows["."]` marks shared focused test coverage as present with `package.json:test` evidence.
- `lifecycle_gate_matrix.rows["packages/api"]` marks focused test coverage as present with `.github/workflows/ci.yml:go test ./...` evidence.
- `lifecycle_gate_matrix.rows["packages/worker"]` marks focused test coverage as missing.
