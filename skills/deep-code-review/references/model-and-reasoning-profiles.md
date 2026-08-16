# Model and reasoning calibration

Use this reference at the start of every review. The goal is to fit the orchestration to the active reviewer without changing what counts as evidence, a validated finding, or complete coverage.

## Run the startup gate

Before repository inspection or repository commands, determine the coordinator model and reasoning level from the current request. If either value is missing, ask one blocking question:

```text
Which model and reasoning level should coordinate this review (for example, Luna/max, Terra/high, or Sol/high)? If you want mixed-model specialist lanes, name those too.
```

Do not ask again when the current request already supplies both values. Do not use a value remembered from another task. Do not infer an effort level from a model name.

If the environment cannot obtain an interactive answer, record `model: unknown` and `reasoning: unknown`, use the strict fallback profile below, and disclose that choice. Do not claim that the fallback identifies the actual runtime.

Record this profile before semantic review:

```text
Coordinator model:
Reasoning level:
Mixed-model policy:
Review mode:
Orchestration profile:
Maximum concurrent lanes:
Nested delegation:
Evidence-slice ceiling:
Candidate validation plan:
Checkpoint location:
```

## Resolve the orchestration profile

Treat model and reasoning labels as orchestration inputs, not proof of quality. Resolve every recorded field from the two tables below before semantic review.

| Model family | Family fanout policy | Family nesting policy | Required subagent profile | Orchestration emphasis |
|---|---|---|---|---|
| Luna | No skill-imposed cap; use every available worker slot and additional waves while disjoint work remains. | Permitted for independent nested subscopes within runtime policy. | Luna at `max` for every descendant; no model or effort fallback. | Use phase gates, explicit schemas, small evidence packets, coordinator-owned shared state, and deterministic completion checks. |
| Terra | At most 4 concurrent lanes. | Prohibited. | Selected model and reasoning unless an explicitly requested mixed-model lane overrides it. | Emphasize producer-to-consumer contracts, artifact provenance, configuration and release drift, and concise candidate packets. |
| Sol | At most 6 concurrent lanes. | One child generation when runtime policy permits. | Selected model and reasoning unless an explicitly requested mixed-model lane overrides it. | Emphasize cross-boundary synthesis, acceptance behavior, adversarial falsification, and integration of specialist evidence. |
| Other or unknown | At most 2 concurrent lanes. | Prohibited. | Exact selected model and reasoning when controllable; otherwise record the runtime identity. | Use phase-gated execution, coordinator-only shared state, and conservative evidence slices. |

When the runtime exposes different model names, map only a clearly equivalent family. Otherwise retain the exact name and use `Other or unknown`.

Normalize the reasoning label to lowercase. Recognize only `low`, `medium`, `high`, `xhigh`, `max`, and `ultra`; retain any other exact label and use the `unknown or unrecognized` row.

| Reasoning level | Non-Luna lane cap | Reasoning nesting policy | Evidence-slice ceiling | Candidate validation plan |
|---|---:|---|---|---|
| `low` | 1 | prohibited | 3 files or 600 lines | Neutral coordinator re-check of every material candidate. |
| `medium` | 2 | prohibited | 4 files or 1,000 lines | Independent material-candidate validation when available; otherwise neutral coordinator re-check. |
| `high` | 4 | one child generation when the family permits | 6 files or 1,500 lines | Independent material-candidate validation plus one bounded omission pass. |
| `xhigh` | 5 | one child generation when the family permits | 8 files or 2,000 lines | Independent validation of every supported candidate plus one bounded omission pass. |
| `max` | 6 | one child generation when the family permits | 8 files or 2,000 lines | Independent validation of every supported candidate, one bounded omission pass, and deterministic completion reconciliation. |
| `ultra` | 6 | one child generation when the family permits | 8 files or 2,000 lines | Independent validation of every supported candidate, one bounded omission pass, and deterministic completion reconciliation. |
| `unknown or unrecognized` | 2 | prohibited | 4 files or 1,000 lines | Independent material-candidate validation when available; otherwise neutral coordinator re-check. |

Resolve and record the effective profile as follows:

1. For Luna, set maximum concurrent lanes to every available worker slot after reserving the coordinator. Do not impose a numeric concurrency, total-agent, lane-count, or wave-count cap in the skill. Continue scheduling disjoint work while useful uncovered scope remains. Every delegated agent at every depth must use Luna at `max`; if the runtime accepts explicit selectors, pass `model: gpt-5.6-luna` and `reasoning_effort: max` with a fork mode that permits overrides instead of relying on inheritance. If the runtime cannot guarantee that exact profile, do not substitute another model or effort and record the scope as blocked or uncovered.
2. For Terra, Sol, and other models, set maximum concurrent lanes to the minimum of the numeric family policy, non-Luna reasoning lane cap, and available worker slots after reserving the coordinator. Record `0` when independent workers are unavailable.
3. Permit nested Luna delegation for genuinely independent subscopes when runtime policy allows it. For other models, permit nesting only when both tables allow it. Preserve exclusive lane ownership at every depth.
4. Use the reasoning row's evidence-slice ceiling as a maximum, not a target. Reduce it for large or highly coupled files.
5. Copy the reasoning row's candidate validation plan into the review profile. If the requested validator is unavailable, use the stated coordinator fallback and record the evidence gap.
6. For explicitly requested mixed-model lanes, resolve each lane from its actual model and reasoning values. Do not use mixed-model descendants under a Luna coordinator because its delegated work is Luna/max-only. The coordinator still owns final integration.

For Luna at `max`, these rules resolve to all currently available worker slots, permitted nesting within runtime policy, Luna/max-only descendants, and an eight-file or 2,000-line evidence ceiling. Load and follow [luna-max-whole-repository-audit.md](luna-max-whole-repository-audit.md); it is the controlling contract and may impose stricter evidence or ownership rules, but it must not add an arbitrary lane or agent cap.

Reasoning level changes scheduling and context control only. It does not permit speculative findings, weaker validation, broader mutation authority, or a false completeness claim.

## Use mixed-model lanes deliberately

The selected model is the coordinator profile. Do not create a mixed-model review merely because multiple models exist. Use mixed-model lanes only when the user requests them or governing runtime policy already assigns them.

When model selection is available, align a lane with its work rather than treating diversity as evidence:

- use a synthesis-oriented profile for acceptance and cross-boundary behavior;
- use a provenance-oriented profile for package, manifest, generated-copy, and release integrity;
- use a structured evidence-ledger profile for broad discovery and delivery-state reconciliation.

Every lane still receives the exact frozen state, exclusive scope, output schema, and checkpoint path. Validate its candidates independently. Two models agreeing is correlated opinion unless an independent oracle and falsification attempt support the claim.

## Strict Luna/max protocol

For Luna at `max`, read [luna-max-whole-repository-audit.md](luna-max-whole-repository-audit.md) in full before repository inspection. It is the controlling orchestration contract for snapshot audits and repository-wide multi-agent reviews. Do not compress it into a generic lane plan or substitute the ordinary durable-state layout.

Use the strict fallback constraints in this file when the model is unknown. Use the complete Luna/max protocol only when Luna/max is selected or the user explicitly requests that structure.
