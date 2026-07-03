# Report Contract

Preserve all existing script report sections:

```md
## Verdict
## Findings
## Repository Shape
## Repository Inventory
## Lifecycle Gate Matrix
## Documentation
## Scripts
## Validation
## Packaging
## Hygiene
## Commands Run
## Not Checked
```

## Repository Classification

Required before recommending foundations.

Include:

- scope: `single-repository`, `monorepo`, `polyrepo-set`, `source-plugin-mirror`, or `generated-vendor-subtree`
- purpose: library, service, CLI, app, docs, infra, skill/plugin, or mixed
- detected ecosystems
- package, service, docs, and generated/vendor boundaries
- confidence level and missing evidence

## Topology Inventory

Required when more than one package, service, app, docs site, or mirror root exists.

List each boundary with:

- path
- kind
- ecosystem
- manifest evidence
- whether it is root/shared or package-specific

## Lifecycle Gate Matrix

Required for every audit.

Columns:

- scope/path
- setup/bootstrap
- focused test
- full validation/CI
- lint/format
- typecheck/static analysis
- build/package
- runtime/server/dev
- docs/release
- CI coverage

Use `present`, `documented`, `missing`, or `not_applicable`.

## Ecosystem Assessment

Required for every detected ecosystem.

For each ecosystem, summarize:

- expected native commands
- detected commands
- missing gates
- false positives avoided
- severity rationale

## Findings

Each finding must include:

- severity
- scope/path
- evidence
- impact
- repo-native recommendation
- whether the finding is root/shared or package-specific
- whether the issue is proven, inferred, or not checked

## Recommended Foundation

Only include after classification.

Do not prescribe a generic tree before mapping:

- repo purpose
- primary ecosystem or ecosystems
- package boundaries
- runtime model
- existing commands
- CI coverage
- release/deployment expectations
