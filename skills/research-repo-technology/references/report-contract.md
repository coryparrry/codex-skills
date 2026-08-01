# Report contract

Use this structure unless the user requests another format.

## 1. Strategic recommendation

State the narrow overall direction in the first paragraph. Explain what to preserve, what to change, and why this combination is stronger than the main alternatives.

## 2. Repository baseline

Report:

- current strengths worth preserving;
- verified limitations and their evidence;
- relevant architecture, product, privacy, performance, and maintenance constraints;
- implementation-versus-documentation disagreements;
- unresolved hypotheses.

Link repository claims to exact local files and lines when useful.

## 3. Ranked opportunities

For every opportunity, include:

1. **Current limitation:** the observed repository gap and evidence.
2. **User value:** the concrete improvement, not an abstract capability.
3. **External evidence:** official documentation or source-level project evidence.
4. **Reusable unit:** dependency, component, protocol, algorithm, model, data structure, or design pattern.
5. **Integration point:** the exact subsystem or boundary in the repository.
6. **Decision:** adopt, adapt, build, or reject.
7. **Risks:** privacy, security, performance, licence, dependencies, maintenance, platform support, and migration where relevant.
8. **Confidence:** high, medium, or low, with the missing evidence that limits confidence.

Do not include an opportunity merely to fill a quota.

## 4. External project decision table

For each material project, summarize:

| Project or standard | Transferable unit | Decision | Licence or compatibility | Maintenance signal | Main reason |
| --- | --- | --- | --- | --- | --- |

Distinguish adopting a dependency from learning a pattern. A permissive licence does not by itself make a dependency operationally suitable.

## 5. Rejected alternatives

Name credible alternatives that were considered and rejected. Give the shortest concrete reason: wrong product boundary, redundant capability, excessive dependency or operational cost, privacy conflict, performance risk, incompatible licence, weak maintenance, or insufficient evidence.

## 6. Up to three bounded proofs of concept

Include one proof for each selected qualified opportunity, up to three. Include fewer, including none, when the evidence does not justify three opportunities, and state why the report stops there. Do not invent a weak opportunity or proof to fill this section.

For each selected opportunity, specify:

- **Question:** one uncertainty the experiment resolves.
- **Fixture:** the smallest representative repository slice or synthetic workload.
- **Method:** the comparison or instrumentation needed.
- **Success thresholds:** numerical or observable pass criteria.
- **Guardrails:** privacy, security, compatibility, resource, and non-mutation constraints.
- **Stop condition:** evidence that should end or defer the idea.
- **Follow-on decision:** what success and failure each authorize.

Keep each proof independently runnable and small enough to discard.

## 7. Evidence and closeout

State the branch and HEAD, local files and external sources inspected, incomplete evidence, whether research lanes completed, final working-tree state, and all validation that actually ran. Explicitly state the absence of repository or external mutations.
