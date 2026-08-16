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
| Luna | Use phase gates, explicit schemas, small evidence packets, coordinator-owned shared state, and deterministic completion checks. For Luna at `max`, apply the strict protocol below. |
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

Use this protocol for Luna at `max`, and for the strict fallback when the model is unknown.

### Freeze and initialize

1. Verify the requested repository and ref before semantic inspection.
2. Record the branch, exact commit, initial dirty state, comparison authority, and prohibited mutations.
3. Create the durable state defined in [durable-review-state.md](durable-review-state.md).
4. Add the active phase, completed lanes, active lanes, queued lanes, candidate states, blockers, last completed action, and exact next action to the root index.
5. Reconcile every tracked first-party path to one production-area row or a reasoned exclusion. This path inventory is an accounting check, not a substitute for behavior tracing.

Only the coordinator writes the root index, root integration record, and any shared candidate or finding ledger. Each lane writes only its own checkpoint.

### Execute phase gates

Run these phases in order:

1. repository inventory and policy;
2. discovery lanes;
3. cross-boundary flow and shared-contract integration;
4. independent candidate validation;
5. final resnapshot, coverage reconciliation, and synthesis.

Do not promote discovery candidates during discovery. Do not begin synthesis while a material lane or candidate remains active, queued, or unexplained.

### Bound fanout and context

- Run no more than four subagents concurrently.
- Do not permit nested delegation. The coordinator alone schedules additional lanes and validation work.
- Assign one exclusive primary lane and one checkpoint file to each agent.
- Use the normal ceiling of eight newly opened files or about 2,000 newly loaded lines per evidence slice; reduce it for large or highly coupled files.
- Persist a returned lane result and update root state before processing another result or doing further semantic investigation.
- Keep full source, diffs, logs, and agent transcripts out of shared state. Store evidence pointers and discriminating output only.

### Require structured lane returns

Every discovery lane returns:

```text
Lane:
Primary scope:
Files or artifacts reviewed:
Out-of-lane dependencies inspected:
Commands and tests run:
Coverage gaps:
Candidate findings:
Rejected hypotheses:
Cross-lane edges:
Next bounded slice:
```

Every candidate includes:

```text
Candidate ID:
Provisional severity:
Primary and related locations:
Reachable trigger:
Execution or data path:
Expected behavior:
Actual behavior:
Concrete impact:
Source and runtime evidence:
Counter-evidence considered:
Remaining uncertainty:
Confidence:
```

Prefer no candidate over an unsupported candidate.

### Validate and finish

Assign material candidates to an independent validation pass that begins from the claimed trigger and attempts to disprove the defect. A candidate must end as `validated`, `disproved`, `unresolved`, `observation only`, or `stale at current head` before synthesis.

Finish only when the target is re-snapshotted, every in-scope path is reconciled, every production area and critical flow satisfies the normal completeness gate or is explicitly uncovered, every lane returned, every candidate has a terminal state, duplicate root causes are merged, shared contracts are integrated, and the final working-tree state is recorded. Stop delegation after these conditions are met. Do not begin fixes during the audit.
