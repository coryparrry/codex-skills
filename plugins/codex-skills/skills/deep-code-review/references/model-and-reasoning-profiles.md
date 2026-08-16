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

## Select the model profile

Treat model labels as orchestration inputs, not proof of quality.

| Model family | Orchestration profile |
|---|---|
| Luna | Use phase gates, explicit schemas, small evidence packets, coordinator-owned shared state, and deterministic completion checks. For Luna at `max`, load and follow [luna-max-whole-repository-audit.md](luna-max-whole-repository-audit.md). |
| Terra | Emphasize producer-to-consumer contracts, artifact provenance, configuration and release drift, and concise candidate packets. Use bounded parallel lanes for independent artifacts or flows. |
| Sol | Emphasize cross-boundary synthesis, acceptance behavior, adversarial falsification, and integration of specialist evidence. Coherent lanes may be broader, but durable state and coverage gates still apply. |
| Other or unknown | Use the strict fallback: phase-gated execution, coordinator-only shared state, no nested delegation, at most two concurrent lanes, and conservative evidence slices. |

When the runtime exposes different model names, map only a clearly equivalent family. Otherwise retain the exact name and use the strict fallback.

## Apply the reasoning profile

- **Low or medium:** reduce concurrent lanes and evidence-slice size. Run large scopes in durable waves. Do not summarize unreviewed work as complete; return `partial` if the requested scope cannot pass the normal completeness gate.
- **High or xhigh:** use the normal bounded-slice protocol, independent non-overlapping lanes when available, neutral validation for material candidates, and the omission pass.
- **Max:** use explicit phase entry and exit checks, deterministic coverage reconciliation, independent candidate validation when available, and a final completion checklist. Prefer more disjoint lanes over larger context packets.
- **Unknown or another label:** use the strict fallback and record the unrecognized value without translating it silently.

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
