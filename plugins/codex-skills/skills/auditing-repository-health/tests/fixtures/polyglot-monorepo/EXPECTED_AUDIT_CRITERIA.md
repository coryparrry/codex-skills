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
