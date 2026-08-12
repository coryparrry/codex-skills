# Deep Repo-Wide Code Review for AI-Generated Code

## Research delta and skill-design evidence

This is an additive continuation of `deep-research-report-5.md`. It preserves the original report as the baseline and replaces unresolved citation placeholders with direct primary-source links where those sources could be recovered.

Research boundary: 2026-08-12. The central question is: **what evidence is strong enough to design a repository-scale review skill for AI-generated changes?**

## Answer

The report's central design is supported with high confidence: a strong review skill must investigate repository context, policy, intent, architecture, callers, configuration, persistence, security boundaries, tests, and non-code artifacts rather than treating the diff as the whole problem.

The skill should be a **risk-routed evidence orchestrator**:

> discover applicable rules → reconstruct intent → build an impact graph → expand beyond the diff → run deterministic and specialist checks → test and falsify candidate findings → report only evidence-backed defects with uncertainty and coverage.

The most important qualification is that the available research supports the mechanisms, but not every percentage in the original report. Many agent-specific studies are recent preprints, benchmark-specific, model-specific, or limited to explicitly identifiable AI-authored changes. Their numbers belong in a versioned evidence ledger, not in permanent skill instructions.

## Baseline recovered

The supplied report argues that AI-generated code is often locally plausible but globally inconsistent. Its central 15-point contract is:

1. Never review only the diff.
2. Discover repository rules before reasoning about correctness.
3. Reconstruct intended behaviour.
4. Build an impact graph.
5. Inspect affected code outside the diff.
6. Treat tests as evidence, not as the complete specification.
7. Make deterministic claims with deterministic tools.
8. Run independent security, architecture, and test-quality passes.
9. Search for required-but-missing companion changes.
10. Falsify every candidate finding.
11. Give every defect an evidence path.
12. State uncertainty explicitly.
13. Maintain a coverage ledger.
14. Prefer a few proven findings over speculative volume.
15. Never alter code merely to satisfy an unproven reviewer concern.

Those principles remain coherent. The original report's inline citation markers were not directly actionable as a bibliography, so this continuation follows the important claims back to primary papers, official documentation, and direct research pages.

## Retained

### Repository-scale review is the correct boundary

RepoExec found that full dependency context improved executability, functional correctness, and dependency utilization in repository-level code-generation tasks. It also found that pretrained models sometimes reimplemented available dependencies instead of using them. This is evidence for checking repository abstractions and dependency usage, although the benchmark concerns Python function generation rather than code review.

[On the Impacts of Contexts on Repository-Level Code Generation](https://arxiv.org/abs/2406.11927)

SWE-Explore provides newer evidence that exploration itself is a bottleneck. Its benchmark contains 848 issues across 10 languages and 203 open-source repositories. File-level retrieval is relatively strong, while line-level recall and ranking remain difficult. Its ground truth is derived from successful agent trajectories, so it should be treated as evidence about useful exploration paths rather than an absolute specification of every relevant line.

[SWE-Explore: Benchmarking How Coding Agents Explore Repositories](https://arxiv.org/abs/2606.07297)

**Design consequence:** the skill needs a context-selection and impact-expansion phase. “Read the whole repository” is neither a practical nor a validated substitute.

### Deterministic tools must complement model reasoning

Current GitHub documentation describes a hybrid code-review product: project-context gathering, AI review, CodeQL analysis, dependency review, coverage, and optional merge rules. GitHub also documents fallback behaviour, excluded files, and the fact that AI review comments do not themselves approve a pull request or block merging.

[GitHub Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review), [review-excluded files](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/review-excluded-files), [dependency review](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/reviewing-dependency-changes-in-a-pull-request), and [GitHub Code Quality](https://docs.github.com/en/code-security/concepts/code-quality/code-quality)

**Design consequence:** compiler, test, static-analysis, dependency, configuration, schema, and runtime evidence should be first-class inputs. A model's explanation is not a substitute for a failing check or a reproduced path.

### Tests are evidence, not the specification

An empirical re-evaluation of SWE-bench found that running all relevant tests caused an average 7.8% of apparently plausible patches to fail developer-written tests. Differential comparison found behavioural differences from the developer patch in 29.6% of cases, and 28.6% of those divergent cases were manually judged certainly incorrect.

[Are “Solved Issues” in SWE-bench Really Solved Correctly?](https://arxiv.org/abs/2503.15223)

Independent work on test generation under software evolution found that generated tests can remain aligned with old behaviour after semantic changes. In that study, more than 99% of failing semantic-altering-change tests passed the original program while still executing the modified region, showing that execution and coverage are not enough to prove that a test expresses the new requirement.

[Evaluating LLM-Based Test Generation Under Software Evolution](https://arxiv.org/abs/2603.23443)

**Design consequence:** the skill should run all relevant tests, compare old and new behaviour where possible, and escalate high-risk changes to mutation, property, fuzz, or differential testing. A test added in the same patch is evidence, not an independent oracle.

### Independent specialist reasoning is useful when it is targeted

In a controlled vulnerability-detection experiment with 150 participants, explicitly directing reviewers to focus on security substantially increased detection. Adding a security checklist did not reliably produce another improvement. Broader code-review research finds that checklist effects depend on task complexity.

[Less is More: Supporting Developers in Vulnerability Detection during Code Review](https://arxiv.org/abs/2202.04586) and [Do explicit review strategies improve code review performance?](https://link.springer.com/article/10.1007/s10664-022-10123-8)

**Design consequence:** specialist lenses should be selected by risk. Always running every possible checklist creates noise and cost; never running a security, concurrency, migration, or test-oracle lens creates blind spots.

## Confirmed

### Repository policy discovery is an independent failure mode

A 2026 study of coding-agent compliance with open-source contribution rules found that agents proactively read policy files in only 3.5% of runs when those files were not always injected into context. Reminders, quoted policy text, and feedback improved verification and disclosure, but unaided refusal and handoff behaviour remained weak.

[A First Look at Coding Agents' Compliance with AI Contribution Rules](https://arxiv.org/abs/2607.26819)

This confirms the report's rule-discovery requirement. It does **not** justify concatenating every instruction file into the prompt. A separate AGENTS.md study found no general task-success improvement and more than 20% inference cost from context files, while another small study found lower runtime and output-token use. The evidence is mixed because the studies measure different repositories, task types, and outcomes.

[Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988) and [On the Impact of AGENTS.md Files on Efficiency](https://arxiv.org/abs/2601.20404)

**Implementation rule:** discover broadly, resolve precedence, load narrowly, and record the rule-resolution result.

### AI-authored PR failure is not only an anti-AI attitude

One study analysed 33,596 agent-authored pull requests from five coding agents and reported 71.48% merged. Its manual rejection analysis started with 600 cases, but 38 were inaccessible, leaving 562 classified cases. Reviewer abandonment, duplicate work, CI/test failure, incorrect changes, and incomplete fixes all appeared in the taxonomy.

[Where Do AI Coding Agents Fail?](https://arxiv.org/abs/2601.15195)

A separate fix-related study analysed 8,106 PRs: 65.0% merged, 26.1% closed without merge, and 8.9% open. In a manual sample of 326 closed-but-unmerged PRs, the leading causes were the issue being resolved by another PR at 22.1%, test failures at 18.1%, and incorrect or incomplete fixes at 15.3%. Build failures were 2.1% and deployment failures 3.1% in that fix-only sample.

[Why Are AI Agent–Involved Pull Requests (Fix-Related) Remain Unmerged?](https://arxiv.org/abs/2602.00164)

**Design consequence:** review must examine technical correctness, test readiness, duplication, status, inactivity, scope, and repository workflow—not just suspicious lines.

### Security needs a separate generation-and-validation model

A large SWE-bench security study used oracle retrieval to separate retrieval failure from patch-generation failure. In one Llama setup, 135 newly introduced vulnerabilities were manually validated in generated patches compared with 12 in developer patches. The result is serious but bounded: it is model-, benchmark-, retrieval-, and analyzer-specific, and it does not establish a universal multiplier for AI-generated patches.

[How Safe Are AI-Generated Patches?](https://arxiv.org/abs/2507.02976)

A separate study of security-related agent PRs identified 675 security PRs from a larger AI-PR dataset. Semgrep reported at least one potential issue in 104 of them. Among 219 closed-but-unmerged security PRs, explicit distrust in AI-written code accounted for 1.8% of the manual taxonomy. That percentage must not be generalized to all AI PRs or all rejection decisions.

[Insights into Security-Related AI-Generated Pull Requests](https://arxiv.org/abs/2604.19965)

**Design consequence:** security review should include independent static analysis, dependency and registry checks, taint/data-flow reasoning, trust-boundary analysis, and manual reachability validation. Patch size may be a risk signal, but the sources do not justify a universal patch-size rule.

### Differential testing is a practical new lane

DiffTestGen uses changed-code analysis, call graphs, documentation, and generated tests to expose behavioural differences between program versions. In a recent preprint evaluation over 463 PRs, it reported behavioural differences in 78.2% of PRs and higher union coverage than baselines. This is promising research, not a production guarantee, but it directly supports the report's proposal to compare old and new behaviour instead of relying only on the changed tests.

[DiffTestGen: Change-Directed LLM-Based Testing](https://arxiv.org/abs/2607.16024)

## Corrected

### Correct the Debt Behind the AI Boom figures

The current version of the study reports approximately 302.6k verified AI-authored commits, 6,299 repositories, and 484,366 detected issues. Code smells account for 89.3%, correctness issues 6.0%, and security issues 4.7%. 22.7% of tracked issues survive in the latest repository version.

The earlier figures in the supplied report—304,362 commits, 89.1% code smells, and 24.2% surviving issues—are version drift, not evidence that the conclusion changed. The study also has important limits: public repositories with at least 100 stars, Python/JavaScript/TypeScript only, explicitly traceable AI commits only, no human-only baseline, possible mixed AI/human commits, and static-analysis false positives.

[Debt Behind the AI Boom: A Large-Scale Empirical Study of AI-Generated Code in the Wild](https://arxiv.org/abs/2603.28592)

### Narrow the “AI distrust” claim

The 1.8% figure is valid only within the security-related PR dataset and its manual rejection taxonomy. It supports the narrower claim that explicit AI distrust was uncommon in that sample. It does not support a universal claim about all maintainers, repositories, agents, or PR types.

### Separate benchmark success from repository correctness

The SWE-bench re-evaluation has a minor version/reporting discrepancy around the exact resolution-rate inflation, with versions reporting approximately 6.2–6.4 percentage points. The durable conclusion is stable: changed-test-only evaluation can overestimate correctness. The skill should cite the methodological result rather than hard-code one percentage.

### Treat source maturity as part of the evidence

Several high-value sources are 2025–2026 preprints or benchmark papers. They are useful for design hypotheses, but should be tagged with publication status, dataset version, model, language, and task boundary. Official product documentation establishes current product behaviour and limitations, not independent efficacy.

## New

### Architecture should carry uncertainty, not only edges

Recent architecture research models a repository as a partially observable system with cross-cutting invariants and configuration-driven wiring. The study is explicitly preliminary: one language, one procedural pattern, one prompt, a small set of codebases, and a single run. Its value is not a general performance number; its value is the design vocabulary.

[Theory of Code Space: Do Code Agents Understand Software Architecture?](https://arxiv.org/abs/2603.00601)

The skill should therefore represent edges such as:

- caller and callee;
- data-flow and trust-boundary flow;
- configuration and runtime registration;
- persistence and migration;
- generated source and generator;
- public API and compatibility consumer;
- test and behaviour under test.

Each edge should carry provenance and confidence. An inferred edge must not be presented as a verified fact.

### Negative-space review deserves its own phase

The sources support inspecting context around a change, but the specific “missing companion change” detector remains largely an engineering hypothesis. It should be implemented as a first-class phase and evaluated directly against seeded defects:

- missing registration;
- missing migration or rollback;
- missing configuration or feature flag;
- missing generated artifact;
- missing lockfile or dependency policy update;
- missing authorization or telemetry change;
- missing test or documentation for a public behaviour change.

This phase is likely to provide more unique value than another generic style checklist because it targets changes that are absent from the diff.

### AI fingerprints should remain candidate signals

Large-scale studies support checks for broad exception handling, unused scaffolding, undefined references, redundancy, mock-heavy tests, and nonexistent packages. None of these is automatically a defect. A broad exception may be intentional at a boundary; a mock may be required for isolation; duplication may be a deliberate compatibility adapter.

The detector should ask: **what concrete behaviour, security property, maintenance invariant, or repository convention does this signal violate?** If it cannot answer that question, it should remain an observation or be omitted.

[More Code, Less Reuse](https://arxiv.org/abs/2601.21276), [Are Coding Agents Generating Over-Mocked Tests?](https://arxiv.org/abs/2602.00409), and [Package Hallucinations](https://www.usenix.org/system/files/conference/usenixsecurity25/sec25cycle1-prepub-742-spracklen.pdf)

### Validator prompts need anti-confirmation controls

Cross-model review research found asymmetric results: a second model can improve one direction and degrade another. Security-review research found that framing a patch as “bug-free” reduced detection substantially. Separate research also finds that highly directive prompts can make models overcorrect and label correct code as defective.

[Cross-Model LLM Code Review](https://arxiv.org/abs/2607.21656), [Measuring and Exploiting Confirmation Bias](https://arxiv.org/abs/2603.18740), and [Systematic Overcorrection in Requirement Conformance Judgement](https://arxiv.org/abs/2603.00539)

The validator should receive the neutral change, requirements, evidence, and reproduction—not the first reviewer’s conclusion or an instruction to find a defect. It must have an explicit “no defect established” outcome.

## Contradicted or qualified

### “More context is better” is contradicted

RepoExec supports useful dependency context, but context research also finds that irrelevant tokens can degrade performance. A recent maximum-effective-context study reports task-dependent degradation well below advertised context windows. These findings support structured retrieval, not maximal prompt size.

[Context Is What You Need](https://arxiv.org/abs/2509.21361)

### “Specialist checklists always improve review” is not supported

Security-focused attention improves detection in one controlled experiment, but additional checklists do not always add signal. Specialist lanes should be routed by risk and measured for precision and reviewer burden.

### “Passing the tests establishes correctness” is contradicted

The SWE-bench, test-evolution, and differential-testing results directly contradict this assumption. Existing tests are evidence of some behaviours under some inputs. They are not proof of intent, compatibility, security, migration safety, performance, or negative space.

### “Review rejection is mostly anti-AI sentiment” is contradicted

The 1.8% security-PR result is narrow, but both broader PR studies identify technical, process, duplicate, inactivity, and validation causes. The skill should optimize for mergeability and evidence quality rather than trying to detect reviewer sentiment.

## The 15-point design contract, mapped to evidence

| # | Contract | Evidence status | Implementation requirement |
|---:|---|---|---|
| 1 | Do not review only the diff | Confirmed | Snapshot repository and expand to affected paths. |
| 2 | Discover rules | Confirmed | Resolve policy files before semantic review; record loaded and unloaded rules. |
| 3 | Reconstruct intent | Supported design inference | Read issue, history, docs, callers, tests, and public API; state acceptance criteria and unknowns. |
| 4 | Build an impact graph | Supported design inference | Use typed edges and confidence, including config and persistence edges. |
| 5 | Inspect outside the diff | Confirmed | Review callers, dependents, registration, generators, migrations, and consumers. |
| 6 | Tests are evidence, not spec | Confirmed | Run all relevant tests and seek independent behavioral evidence. |
| 7 | Deterministic claims use tools | Confirmed | Prefer compiler, test, static, dependency, schema, and runtime evidence. |
| 8 | Run independent specialist passes | Qualified | Route lenses by risk; measure noise and incremental value. |
| 9 | Search missing companion changes | New design emphasis | Add a negative-space phase and seed it in evaluation. |
| 10 | Falsify every finding | Confirmed | Verify reachability, preconditions, reproduction, current-head applicability, and alternative explanations. |
| 11 | Evidence path for every defect | Confirmed | Require source path, affected path, evidence, reproduction, and validation. |
| 12 | State uncertainty | Confirmed | Separate verified, inferred, contradicted, unresolved, and not-applicable states. |
| 13 | Coverage ledger | Supported evaluation principle | Record paths, tools, lanes, exclusions, and unresolved questions. |
| 14 | Prefer proven findings | Confirmed | Optimize precision and actionability, not comment count. |
| 15 | Do not change code to satisfy an unproven concern | Confirmed safety principle | A finding may recommend validation or a design question; it must not force speculative edits. |

## Implications for the skill design

### 1. Intake and provenance

Always capture:

- repository and remote;
- base and head commits;
- branch and working-tree state;
- changed and generated files;
- language, compiler, runtime, and dependency versions;
- available test, build, lint, static-analysis, and security commands;
- applicable policy files and their precedence.

The report should be bound to an exact head. A later review of a different head is a new evidence state.

### 2. Policy resolver

The resolver should discover `AGENTS.md`, contribution guides, security policy, local READMEs, CI definitions, code owners, package policy, and path-specific instructions. It should produce a compact matrix:

| Rule | Applies to | Source | Required action | Loaded? | Conflict |
|---|---|---|---|---|---|
| Required check | Path or package | Exact file and section | Command or observable condition | Yes/no | Yes/no |
| Forbidden change | Path or branch | Exact file and section | Reject or escalate | Yes/no | Yes/no |
| Convention | Scope | Exact file and section | Review lens | Yes/no | Yes/no |

This makes policy compliance auditable without flooding the model with irrelevant prose.

### 3. Intent and invariant reconstruction

The skill should write down:

- requested behaviour;
- observable before/after behaviour;
- preserved invariants;
- new invariants;
- failure, cancellation, retry, ordering, migration, and rollback expectations;
- public compatibility requirements;
- unresolved interpretation questions.

If intent cannot be established, the correct output is an uncertainty or clarification finding—not a speculative defect.

### 4. Impact graph and negative space

The graph should include changed paths and affected paths. It should explicitly look for required-but-missing changes in registration, configuration, generated code, persistence, migrations, tests, docs, telemetry, feature flags, dependencies, and deployment artifacts.

### 5. Risk-routed specialist lanes

Always run the core lane. Add specialist lanes only when triggered:

- security and trust boundaries;
- concurrency, lifecycle, cancellation, and reentrancy;
- architecture and dependency direction;
- persistence, migration, and compatibility;
- dependency and supply chain;
- test oracle and differential behaviour;
- performance and resource lifetime;
- repository policy and release process.

Each lane must return candidate claims plus evidence requirements. It must not directly turn a hypothesis into a finding.

### 6. Deterministic evidence layer

The orchestrator should prefer tools in this order where available:

1. parse/build/compiler checks;
2. focused and full relevant tests;
3. static analyzers and type checkers;
4. dependency, lockfile, license, and registry checks;
5. schema/configuration validation;
6. runtime reproduction, tracing, or differential execution;
7. model reasoning for interpretation and hypothesis generation.

Tool unavailability must be recorded rather than silently treated as a pass.

### 7. Finding and validator contract

Every reportable finding should contain:

```text
id
claim
severity
confidence
changed_path
affected_path
preconditions
evidence
reproduction
why_existing_tests_miss_it
validation_run
expected_fix_shape
uncertainty
status
```

The validator must independently check the claim, not merely rewrite it. It should be allowed to downgrade, reject, or mark the finding unresolved.

## Evaluation plan

Build a benchmark from four evidence classes:

1. historical bugs, reverts, CVEs, and rejected reviews;
2. seeded cross-file, configuration, migration, concurrency, dependency, and test-oracle defects;
3. correct but unusual implementations and harmless refactors;
4. misleading comments, incomplete tests, and missing companion changes.

Measure:

- precision and recall;
- severity-weighted recall;
- actionability;
- false-positive and reviewer-burden rate;
- cross-file and missing-change detection;
- tool-backed finding ratio;
- reviewer acceptance;
- escaped defects;
- regressions introduced by review fixes;
- coverage completeness;
- runtime, token, and tool cost.

Run ablations in this order:

1. diff-only;
2. diff plus repository rules;
3. rules plus impact graph;
4. graph plus deterministic tools;
5. specialist routing;
6. adversarial validator;
7. full system.

The skill is successful only if the full system improves real-defect recall without creating an unacceptable false-positive burden. More comments are not an improvement.

## Evidence ledger

| Claim | Status | Best evidence | Scope and date | Confidence |
|---|---|---|---|---|
| Dependency-aware repository context improves code-generation outcomes | Verified in benchmark | [RepoExec](https://arxiv.org/abs/2406.11927) | Python repository/function tasks; 2024–2025 versions | Medium |
| Repository exploration and line-level retrieval remain bottlenecks | Verified in benchmark | [SWE-Explore](https://arxiv.org/abs/2606.07297) | 848 issues, 10 languages, 203 repositories; 2026 preprint | Medium |
| Agents often fail to proactively read contribution policies | Verified in study | [AI Contribution Rules](https://arxiv.org/abs/2607.26819) | 106 issues, 49 repositories, four models; 2026 preprint | Medium |
| More instruction context is not universally beneficial | Contradicted as a universal claim | [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988) and [efficiency study](https://arxiv.org/abs/2601.20404) | Different repositories and outcomes; 2026 preprints | Medium |
| AI-authored code contains persistent static-analysis debt | Verified within dataset | [Debt Behind the AI Boom](https://arxiv.org/abs/2603.28592) | 302.6k commits, 6,299 repos, Python/JS/TS; 2026 version | Medium |
| Agent PR non-merges include technical and workflow causes | Verified within datasets | [Failed Agentic PRs](https://arxiv.org/abs/2601.15195), [Fix PRs](https://arxiv.org/abs/2602.00164) | Five-agent GitHub datasets; 2026 studies | Medium |
| AI patches can introduce new security vulnerabilities | Verified in controlled benchmark | [AI-Generated Patches](https://arxiv.org/abs/2507.02976) | SWE-bench, Llama and agentic repair setups | Medium |
| Explicit AI distrust was uncommon in one security-PR taxonomy | Verified within subset | [Security-Related AI PRs](https://arxiv.org/abs/2604.19965) | 219 closed security PRs; 2026 preprint | Medium |
| Existing tests do not establish complete patch correctness | Verified | [SWE-bench re-evaluation](https://arxiv.org/abs/2503.15223) | SWE-bench patches and test configurations; 2025/2026 | High |
| Generated tests can retain stale behavioural assumptions | Verified in benchmark | [Test Generation Under Evolution](https://arxiv.org/abs/2603.23443) | 22,374 program variants, eight LLMs; 2026 preprint | Medium |
| Differential test generation is promising for PR review | Preliminary evidence | [DiffTestGen](https://arxiv.org/abs/2607.16024) | 463 PRs; 2026 preprint | Low–medium |
| Explicit security attention can improve human detection | Verified controlled experiment | [Less is More](https://arxiv.org/abs/2202.04586) | 150 participants and two vulnerability classes | Medium |
| Review checklists have task-dependent effects | Verified in study | [Explicit review strategies](https://link.springer.com/article/10.1007/s10664-022-10123-8) | Professional developer review tasks | Medium |
| Cross-model review is asymmetric | Preliminary evidence | [Cross-Model Review](https://arxiv.org/abs/2607.21656) | 116 LiveCodeBench tasks; no tool execution | Low–medium |
| Positive framing can suppress security detection | Preliminary evidence | [Confirmation Bias](https://arxiv.org/abs/2603.18740) | 250 CVE/patch pairs; 2026 preprint | Medium |
| AI review needs precision/recall and noise evaluation | Benchmark design evidence | [CR-Bench](https://arxiv.org/abs/2603.11078) | 584 tasks, 174 verified subset; 2026 preprint | Medium |

## Unresolved

These questions could materially change the implementation and should be tested before the skill is considered production-ready:

1. **Causal value of the impact graph.** Does graph-based expansion improve real-review recall after controlling for token budget and model capability?
2. **Human baseline for AI debt.** How much of the observed static-analysis debt exceeds comparable human-authored commits in the same repositories and periods?
3. **Current-model drift.** Do the 2025–2026 failure modes persist across the exact models and tool versions the skill will use?
4. **Review cost.** What false-positive rate and latency can maintainers tolerate before the skill becomes a burden?
5. **Tool degradation.** How should the skill behave when the compiler, test suite, CodeQL, dependency registry, or runtime is unavailable?
6. **Cross-language validity.** Most evidence is concentrated in Python, JavaScript, TypeScript, or general benchmark code. The repository's languages may require different graph and validation rules.
7. **Non-code artifacts.** The missing-change detector needs repository-specific examples involving CI, release metadata, migrations, generated files, documentation, and configuration.
8. **Validator independence.** A second model may share the first model's blind spot. The benchmark must compare model diversity, prompt diversity, deterministic validation, and human review.

## Closeout

Materials inspected: the supplied `deep-research-report-5.md`, the continuation skill and its source-routing and delta-contract references, the repository's continuation documentation, and the direct primary sources linked above.

Execution shape: root-only research. No independent subagent lanes were available in this runtime, so the result does not claim multi-agent coverage.

Evidence boundary: current through 2026-08-12. Several sources are recent preprints; exact percentages should remain versioned and scoped.

Artifact status: this is a new saved continuation. The original report is preserved and should not be overwritten.
