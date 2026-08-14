# Impact and negative-space review

Use this reference to trace affected behavior without reading the repository indiscriminately.

## Build the impact model

Classify each changed artifact as behavior, API, data/schema, security boundary, state/lifecycle, dependency/build, configuration/deployment, test/verification, documentation/contract, or claimed refactor.

Expand only through relevant typed relationships:

| Relationship | What to establish |
|---|---|
| caller to callee | Changed inputs, outputs, errors, timing, ownership, and side effects |
| interface to implementation | Every implementation and dispatch path that carries the contract |
| publisher to consumer | Event shape, ordering, replay, versioning, and delivery guarantees |
| schema to migration to serializer to client | Stored and wire compatibility, rollback, and old data |
| config to registration to runtime component | Defaults, production values, feature flags, and startup wiring |
| source to transform to control to sink | Trust boundary, validation, authorization, and dangerous operation |
| test to production path | Whether the test exercises the real behavior and a valid oracle |
| generator input to generated output | Whether outputs were regenerated and reviewed |
| public contract to consumer | Source, binary, protocol, CLI, SDK, or plugin compatibility |
| code to history or ADR | Prior incident, revert, invariant, or accepted design rationale |

Record every edge as verified static, verified runtime, verified configuration, verified history, inferred semantic, or unresolved. Do not treat inferred edges as equivalent to tool or runtime evidence.

## Select context progressively

Start with the full changed-path inventory and whole changed files. Expand to direct callers and consumers, then only to critical transitive paths. Prefer symbol search, repository-aware tooling, configuration parsing, history, and runtime traces over lexical similarity alone.

Stop when a boundary is demonstrated safe through a stable contract, exhaustive consumer set, validated adapter, runtime evidence, or unaffected invariant. Record why expansion stopped.

## Search negative space

Ask: given the intended change, what companion artifact or proof would normally be expected but is absent?

| Observed change | Inspect for missing companions |
|---|---|
| Environment variable or config key | Validation, defaults, sample config, deployment values, docs, secret handling |
| Database field or stored value | Migration, old data, rollback, serializer, indexes, fixtures |
| Enum or state | Exhaustive consumers, persistence, API/client/UI mappings, fallback behavior |
| API or event field | Schema, generated clients, consumers, versioning, replay, compatibility tests |
| Dependency | Registry existence, lockfile, license, provenance, build image, SBOM, existing alternative |
| Authorization rule | Every entry point, background job, audit path, tenant boundary, denial behavior |
| Timeout, retry, or error type | Units/defaults, cancellation, idempotency, catch sites, telemetry, retry classification |
| Feature flag | Default, rollout, ownership, production values, cleanup plan |
| Metric, log, or event | PII/cardinality, naming, dashboards or alerts where repository practice requires them |
| Generator input | Regenerated outputs and verification of generated differences |

Absence is an investigation trigger, not a finding. Establish applicability and impact.

## Run the counterfactual reuse check

Search for the repository mechanism a maintainer would normally reuse: retry policy, serializer, permission framework, transaction wrapper, cache service, generated client, command runner, or error mapper. Compare contracts and ownership. Report bypass only when the existing mechanism applies and the new path causes correctness, security, compatibility, operational, or material maintenance harm.
