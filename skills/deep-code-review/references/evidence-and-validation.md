# Evidence and validation

Use evidence to settle claims and calibrate uncertainty. Do not substitute fluent explanations for execution, tool output, or verified repository relationships.

## Match questions to evidence

| Question | Preferred evidence |
|---|---|
| Does it parse or compile? | Parser, compiler, active build configuration |
| Are types and mechanical rules valid? | Type checker, linter, schema/config validator |
| Is a dependency real and resolved? | Intended registry, lockfile, resolver, provenance |
| Is a known unsafe pattern present? | SAST, CodeQL, Semgrep, dependency scanner as a candidate lead |
| Does behavior occur? | Focused test, integration/E2E run, runtime trace, reproduction |
| Is a test sensitive to the defect? | Base-state failure, mutation, differential or property check |
| Is concurrency safe? | Invariant/interleaving proof, sanitizer, stress or deterministic schedule |
| Is the repository relationship real? | AST/call graph, configuration, runtime trace, history, direct consumer evidence |

Tool unavailability, failure, timeout, or environment mismatch is an evidence gap. Coverage shows execution, not correctness. Scanner output shows a candidate pattern, not reachability or exploitability.

## Challenge self-confirming verification

An implementation and its new test can share the same wrong interpretation. Ask:

- Did the test fail on the exact base state for the intended reason?
- Does the oracle come from an independent requirement, reference, invariant, or prior behavior?
- Does the test exercise the production path rather than a substitute created for testing?
- Would a realistic incomplete, boundary-broken, or stale implementation fail it?
- Were assertions weakened, skipped, mocked away, or made less observable?
- Do failure, cancellation, retry, concurrency, migration, and compatibility cases apply?

Use the cheapest discriminating challenge first: focused regression, broader relevant suite, before/after comparison, mutation, property/metamorphic testing, fuzzing, differential execution, race/stress testing, then migration or rollback testing.

## Validate candidate claims neutrally

Create a candidate packet containing the exact base/head, requirement evidence, changed and affected paths, factual execution/data path, tool or reproduction output, alternative explanations, and missing evidence. Do not include persuasive severity language.

Have the validation pass independently test reachability, preconditions, safeguards, framework guarantees, current-head applicability, and whether the proposed correction would regress valid behavior. Accept `no defect established`.

Use these statuses:

- `validated`: evidence proves a reachable violated property;
- `unresolved`: material risk remains but required evidence is unavailable or conflicting;
- `observation only`: useful context without a violated property;
- `disproved`: evidence establishes the concern is false;
- `stale at current head`: the concern applied only to an earlier state.

## Calibrate AI-related leads

Treat incomplete cross-file changes, self-confirming tests, hallucinated dependencies, repository-abstraction bypass, broad error handling, unused scaffolding, excessive mocks, and local-but-globally-wrong behavior as useful search leads. None is a defect because AI wrote it. Require the same violated property and evidence contract for human and AI-authored code.

## Research basis and limits

The supplied audited research supports repository-aware, tool-backed, risk-focused review. It does not prove that one complete orchestrator, impact graph, negative-space detector, or second model is optimal. Keep paper-specific rates out of operational findings unless the user asks for research analysis.

Primary evidence behind the workflow:

- [Google Engineering Practices: What to look for](https://google.github.io/eng-practices/review/reviewer/looking-for.html): review design, integration, tests, context, and every relevant line.
- [RepoReasoner](https://arxiv.org/abs/2607.25996), [SWE-Explore](https://arxiv.org/abs/2606.07297), and [StackRepoQA](https://arxiv.org/abs/2603.26567): repository exploration, retrieval, and cross-file reasoning remain incomplete and sensitive to noisy context.
- [RepoExec](https://arxiv.org/abs/2406.11927): relevant repository dependencies can improve implementation and reuse in an adjacent generation task.
- [SWE-bench patch re-evaluation](https://arxiv.org/abs/2503.15223) and [test generation under evolution](https://arxiv.org/abs/2603.23443): selected tests can accept incomplete behavior, and generated tests can preserve stale semantics.
- [Why Security Defects Go Unnoticed](https://arxiv.org/abs/2102.06909) and [Less is More](https://arxiv.org/abs/2202.04586): wider context makes security review harder, while focused security attention can improve detection.
- [CR-Bench](https://arxiv.org/abs/2603.11078), [cross-model review](https://arxiv.org/abs/2607.21656), and [confirmation-bias review research](https://arxiv.org/abs/2603.18740): review quality has precision/recall tradeoffs, and additional model review can amplify bias or degrade results.
- [Package hallucination research](https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen): introduced dependencies require registry and provenance verification.
- [Agentic PR failure research](https://arxiv.org/abs/2601.15195) and [fix-related PR research](https://arxiv.org/abs/2602.00164): non-merge includes technical, duplicate, policy, scope, validation, and engagement causes; it is not synonymous with defective code.

Treat official product documentation as evidence of current product behavior, not proof of review efficacy. Treat engineering proposals such as typed impact graphs and negative-space review as mechanisms to evaluate, not established universal laws.
