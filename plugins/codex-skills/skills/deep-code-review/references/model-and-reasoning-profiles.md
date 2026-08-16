# Model and reasoning calibration

Use this reference at the start of every review. The goal is to fit the orchestration to the active reviewer without changing what counts as evidence, a validated finding, or complete coverage.

## Run the startup gate

Before repository inspection or repository commands, determine the coordinator model and reasoning level from the current request. If either value is missing, ask one blocking question:

```text
Which model and reasoning level should coordinate this review (for example, Luna/max, Terra/high, or Sol/high)? Specialist lanes will route across Luna, Terra, and Sol by risk unless you want to restrict that pool.
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

| Coordinator family | Family fanout policy | Family nesting policy | Specialist routing | Orchestration emphasis |
|---|---|---|---|---|
| Luna | No skill-imposed cap; use every available worker slot and additional waves while disjoint work remains. | Permitted for independent nested subscopes within runtime policy. | Risk-routed across Luna, Terra, and Sol. | Use phase gates, explicit schemas, small evidence packets, coordinator-owned shared state, and deterministic completion checks. |
| Terra | No skill-imposed cap; use every available worker slot and additional waves while disjoint work remains. | Permitted for independent nested subscopes within runtime policy. | Risk-routed across Luna, Terra, and Sol. | Emphasize producer-to-consumer contracts, artifact provenance, configuration and release drift, and concise candidate packets. |
| Sol | No skill-imposed cap; use every available worker slot and additional waves while disjoint work remains. | Permitted for independent nested subscopes within runtime policy. | Risk-routed across Luna, Terra, and Sol. | Emphasize cross-boundary synthesis, acceptance behavior, adversarial falsification, and integration of specialist evidence. |
| Other or unknown | At most 2 concurrent lanes. | Prohibited. | Exact selected model and reasoning when controllable; otherwise record the runtime identity. | Use phase-gated execution, coordinator-only shared state, and conservative evidence slices. |

When the runtime exposes different model names, map only a clearly equivalent family. Otherwise retain the exact name and use `Other or unknown`.

Normalize the reasoning label to lowercase. Recognize only `low`, `medium`, `high`, `xhigh`, `max`, and `ultra`; retain any other exact label and use the `unknown or unrecognized` row.

| Reasoning level | Evidence-slice ceiling | Candidate validation plan |
|---|---|---|
| `low` | 3 files or 600 lines | Neutral coordinator re-check of every material candidate. |
| `medium` | 4 files or 1,000 lines | Independent material-candidate validation when available; otherwise neutral coordinator re-check. |
| `high` | 6 files or 1,500 lines | Independent material-candidate validation plus one bounded omission pass. |
| `xhigh` | 8 files or 2,000 lines | Independent validation of every supported candidate plus one bounded omission pass. |
| `max` | 8 files or 2,000 lines | Independent validation of every supported candidate, one bounded omission pass, and deterministic completion reconciliation. |
| `ultra` | 8 files or 2,000 lines | Independent validation of every supported candidate, one bounded omission pass, and deterministic completion reconciliation. |
| `unknown or unrecognized` | 4 files or 1,000 lines | Independent material-candidate validation when available; otherwise neutral coordinator re-check. |

Resolve and record the effective profile as follows:

1. For Luna, Terra, or Sol coordinators, set maximum concurrent lanes to every available worker slot after reserving the coordinator. Do not impose a numeric concurrency, total-agent, lane-count, or wave-count cap in the skill. Continue scheduling disjoint work while useful uncovered scope remains.
2. For another or unknown coordinator, use at most two concurrent lanes and prohibit nesting. Record `0` when independent workers are unavailable.
3. Permit nested delegation under Luna, Terra, and Sol coordinators for genuinely independent subscopes when runtime policy allows it. Preserve exclusive lane ownership at every depth.
4. Use the reasoning row's evidence-slice ceiling as a maximum, not a target. Reduce it for large or highly coupled files.
5. Copy the reasoning row's candidate validation plan into the review profile. If the requested validator is unavailable, use the stated coordinator fallback and record the evidence gap.
6. Select every delegated agent independently from the risk-routing matrix below. When explicit selectors are available, pass the exact `model` and `reasoning_effort` with a fork mode that permits overrides instead of relying on inheritance. If a routed model is unavailable, either use the coordinator model and record the deviation or mark the lane uncovered when the user required that specialist; never substitute silently. The coordinator still owns final integration.

For Luna at `max`, these rules resolve to all currently available worker slots, permitted nesting within runtime policy, risk-routed Luna/Terra/Sol descendants, and an eight-file or 2,000-line evidence ceiling. Load and follow [luna-max-whole-repository-audit.md](luna-max-whole-repository-audit.md); it is the controlling contract and may impose stricter evidence or ownership rules, but it must not add an arbitrary lane or agent cap.

Reasoning level changes scheduling and context control only. It does not permit speculative findings, weaker validation, broader mutation authority, or a false completeness claim.

## Route specialist models by risk

The selected model and reasoning level define the coordinator profile. They do not restrict which model may own a specialist lane. Unless the user narrows the pool, use all available Luna, Terra, and Sol specialists and route by the dominant risk in the path or end-to-end flow:

| Path or flow risk | Default specialist | Default effort | Review emphasis |
|---|---|---|---|
| Repository inventory, broad discovery, coverage reconciliation, evidence ledgers, delivery-state reconciliation | `gpt-5.6-luna` | `max` | Explicit schemas, bounded evidence packets, durable progress, and deterministic completeness. |
| Packages, manifests, generated copies, configuration, CI, installers, release artifacts, provenance or version drift | `gpt-5.6-terra` | `high` | Producer-to-consumer contracts, artifact identity, synchronization, packaging, and release integrity. |
| User-visible acceptance, authorization, trust boundaries, privileged mutation, concurrency, lifecycle, failure recovery, or cross-boundary behavior | `gpt-5.6-sol` | `high` | Reachable behavior, adversarial falsification, acceptance evidence, and integration across boundaries. |

For a critical-risk lane or independent validation of a material candidate, preserve the family selected by the risk matrix and elevate only its effort: keep a routed Luna specialist at `max`; elevate a routed Terra or Sol specialist to `ultra` when available, then fall back in order to `max`, `xhigh`, and `high`. Do not route by extension, directory name, or model prestige alone. Reconstruct the path's behavior and dominant failure mode first. If one path crosses multiple material risks, give it one primary discovery owner and create explicit cross-lane handoffs or independent validation work instead of overlapping discovery ownership.

Every lane still receives the exact frozen state, exclusive scope, output schema, and checkpoint path. Validate its candidates independently. Two models agreeing is correlated opinion unless an independent oracle and falsification attempt support the claim.

## Strict Luna/max protocol

For Luna at `max`, read [luna-max-whole-repository-audit.md](luna-max-whole-repository-audit.md) in full before repository inspection. It is the controlling orchestration contract for snapshot audits and repository-wide multi-agent reviews. Do not compress it into a generic lane plan or substitute the ordinary durable-state layout.

Use the strict fallback constraints in this file when the model is unknown. Use the complete Luna/max protocol only when Luna/max is selected or the user explicitly requests that structure.
