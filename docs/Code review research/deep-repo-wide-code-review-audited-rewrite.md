# Deep Repository-Wide Code Review for AI-Generated Changes

## Audited research synthesis and evidence-based skill blueprint

**Research boundary:** 12 August 2026

**Status:** Consolidated rewrite after auditing `chatgpt-deep-research-report-5.md` and `codex-research-delta-report-6.md`

**Purpose:** Establish the strongest defensible research foundation for a skill that reviews a pull request, commit, branch, patch, or repository-wide change deeply rather than commenting only on the visible diff.

---

## Executive conclusion

The central conclusion survives audit:

> **AI-generated code should not be reviewed only as a set of changed lines. It should be reviewed as a proposed behavioural change to a repository.**

A repository-scale review must establish what was intended, what actually changed, what other code and non-code artefacts depend on that behaviour, which invariants may have been disturbed, what evidence verifies the change, and what uncertainty remains.

The strongest defensible design is a **risk-routed evidence orchestrator**:

```text
exact change state
    ↓
repository rules and contribution policy
    ↓
intent and invariant reconstruction
    ↓
repository map + typed impact graph
    ↓
core review + risk-triggered specialist lanes
    ↓
deterministic analysis + behavioural execution
    ↓
neutral, adversarial validation of candidate findings
    ↓
coverage and uncertainty ledger
    ↓
high-signal final report
```

The evidence strongly supports the **components** of this design:

- repository exploration and cross-file reasoning remain difficult for current models;
- relevant dependency and structural context can improve repository-level work;
- adding more noisy context is not a reliable substitute for selecting relevant context;
- passing visible tests does not establish complete patch correctness;
- AI-generated or AI-modified tests can encode stale or self-consistent but wrong behaviour;
- AI-authored PRs fail for technical, coordination, policy, duplication, inactivity, and validation reasons;
- security needs explicit attention and independent evidence;
- AI reviewers have meaningful false-positive, confirmation-bias, and signal-to-noise risks;
- deterministic tools and execution answer questions that model prose cannot settle.

The evidence does **not** yet prove that the full orchestrator above is the optimal review architecture. The impact graph, negative-space detector, risk router, coverage ledger, and adversarial validator are well-motivated engineering mechanisms that must be evaluated directly through ablations and real repository defects.

The correct research claim is therefore:

> **The literature supports repository-aware, tool-backed, risk-focused review. A risk-routed evidence orchestrator is a strong proposed architecture whose incremental value must be demonstrated empirically.**

---

# 1. Evidence standard used in this report

A recurring weakness in AI research summaries is that all sources are treated as if they prove the same kind of claim. They do not. This report separates five evidence classes.

| Label | Evidence class | What it can establish | What it cannot establish |
|---|---|---|---|
| **D — Direct** | Code-review, PR, testing, repository-reasoning, or security-review evidence | Behaviour observed in the studied review or repository task | Universal behaviour outside the studied models, repositories, languages, dates, or prompts |
| **I — Indirect** | Adjacent code generation, repair, retrieval, or human-review evidence | A plausible mechanism or useful design signal | That the same effect size transfers unchanged to an automated review skill |
| **G — Guidance** | Official engineering or review-practice guidance | A documented professional review principle or recommended practice | An experimentally measured effect or proof that the practice is optimal |
| **P — Product** | Current official product documentation | What a current product does, excludes, or warns about | Independent proof that the product design is effective |
| **H — Hypothesis** | Engineering synthesis proposed here | A concrete architecture or control worth testing | An established empirical result before direct evaluation |

Every percentage should be interpreted with its:

- paper version and date;
- model and agent harness;
- dataset and repository selection;
- programming languages;
- task definition;
- prompt and tool availability;
- evaluation method;
- publication status.

Recent 2025–2026 preprints are useful evidence, but their exact rates should live in a versioned evidence ledger rather than permanent skill instructions.

---

# 2. The correct review boundary: affected behaviour, not changed text

A diff tells the reviewer **where text changed**. It does not fully identify **what behaviour is affected**.

```text
Changed code  = files and lines in the patch
Affected code = code, configuration, data, interfaces, operations, and consumers
                whose assumptions may no longer hold
```

A change to one symbol can affect:

- callers and callbacks;
- callees and external services;
- interface implementations and sibling implementations;
- serializers, schemas, migrations, and persisted data;
- configuration defaults and production manifests;
- feature flags and runtime registration;
- authentication and authorisation boundaries;
- retries, cancellation, transactions, and lifecycle state;
- tests, fixtures, mocks, generated clients, and generated code inputs;
- public APIs and compatibility consumers;
- logging, metrics, tracing, alerting, and rollback behaviour;
- repository contribution and release policy.

Google's engineering review guidance independently advises reviewers to inspect overall design, integration with the system, edge cases, concurrency, complexity, tests themselves, documentation, every assigned line, and the wider system context rather than relying only on the narrow view presented by a review tool. Tests “do not test themselves”; the reviewer must determine whether they are valid and would fail when the code is broken. **[G]**

Source: [Google Engineering Practices — What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html)

Human security-review evidence shows why this broader context matters. A Chromium OS case-control study compared 516 reviews that identified security defects with 374 reviews where security defects escaped. Defects requiring execution reasoning or larger context were more likely to be missed, and the likelihood of detection declined as more directories were involved. **[D]**

Source: [Why Security Defects Go Unnoticed during Code Reviews?, arXiv:2102.06909](https://arxiv.org/abs/2102.06909)

The implication is not that every review must read every repository file. It is that the reviewer must identify and trace the **relevant behavioural surface** rather than stopping at the patch boundary.

---

# 3. Why repository-scale AI work fails

## 3.1 Exploration failure

The model may never retrieve the evidence required to judge the change.

Typical symptoms:

- it reads the changed file but not callers;
- it finds a similarly named helper instead of the actual runtime path;
- it misses path-specific instructions;
- it fails to inspect a migration, manifest, generated schema, or registration file;
- it does not inspect recent history or a prior revert;
- it searches by lexical similarity and misses structural relationships.

SWE-Explore evaluates how coding agents navigate repositories across 848 issues, 10 languages, and 203 repositories. File-level retrieval is substantially easier than fine-grained line retrieval and ranking, supporting the conclusion that repository exploration is an independent bottleneck. Its ground truth is based on successful trajectories, so it describes useful exploration evidence rather than a perfect map of every relevant line. **[D/I]**

Source: [SWE-Explore, arXiv:2606.07297](https://arxiv.org/abs/2606.07297)

A 2026 contribution-policy benchmark found that agents proactively opened relevant rule files outside always-loaded instruction files in only 3.5% of runs. This demonstrates that rule discovery itself cannot safely be left to model initiative. **[D]**

Source: [A First Look at Coding Agents' Compliance with AI Contribution Rules, arXiv:2607.26819](https://arxiv.org/abs/2607.26819)

## 3.2 Synthesis failure

The model may retrieve the right evidence but still fail to combine it correctly.

Typical symptoms:

- it sees a caller and callee but misses the changed invariant between them;
- it identifies all files in a path but simulates state incorrectly;
- it notices a compatibility layer but assumes it is redundant;
- it sees configuration and code but misses deployment-specific wiring;
- it interprets one test as the complete specification;
- it confuses correlation in history with architectural intent.

RepoReasoner evaluates cross-file output prediction and call-chain prediction. Even with oracle context, the strongest tested model achieved 69.1% Pass@1 on output prediction; call-chain prediction showed high precision but low recall, and longer retrieved context did not consistently improve performance because added noise could outweigh added evidence. **[D]**

Source: [RepoReasoner, arXiv:2607.25996](https://arxiv.org/abs/2607.25996)

This distinction matters operationally:

```text
No evidence found ≠ evidence the defect does not exist
Evidence retrieved ≠ evidence correctly understood
```

A deep-review skill should record both retrieval coverage and reasoning uncertainty.

## 3.3 Local plausibility versus global constraint satisfaction

A model is often strong at predicting what code usually belongs near a function. A mature repository imposes a harder requirement:

> Satisfy the requested behaviour while preserving every relevant architectural, behavioural, security, compatibility, operational, and historical invariant.

RepoExec found that relevant dependency context improved executability, functional correctness, and dependency utilisation in repository-level Python function-generation tasks. It also observed models reimplementing available dependencies rather than using repository abstractions. This is indirect but useful evidence for checking whether a patch bypasses existing project mechanisms. **[I]**

Source: [On the Impacts of Contexts on Repository-Level Code Generation, arXiv:2406.11927](https://arxiv.org/abs/2406.11927)

## 3.4 Noisy context and the limits of “read everything”

More context is not universally better.

StackRepoQA evaluates repository-level questions derived from real developer questions across 134 Java projects. Graph-based retrieval improved performance more than file-level retrieval in that study, but the best configuration still reached only approximately 64%, and performance was lower on post-training-cutoff questions. **[D/I]**

Source: [Beyond Code Snippets: Benchmarking LLMs on Repository-Level Question Answering, arXiv:2603.26567](https://arxiv.org/abs/2603.26567)

CodeStruct and CodexGraph provide additional evidence that structure-aware access can improve efficiency, reduce brittle line-based interaction, and support precise repository navigation. These systems are not code-review trials, but they strengthen the case for exposing semantic entities and relationships rather than flattening files into raw text. **[I]**

Sources:

- [CodeStruct, arXiv:2604.05407](https://arxiv.org/abs/2604.05407)
- [CodexGraph, arXiv:2408.03910](https://arxiv.org/abs/2408.03910)

The defensible conclusion is:

> **Select, structure, and progressively expand context. Do not assume that fitting the repository into a context window means the model will reason over it correctly.**

---

# 4. Corrected taxonomy of AI-associated review risks

These failure classes are not necessarily unique to AI. Humans produce many of the same defects. They are included because AI generation, agentic workflows, and AI review make them recurrent or especially important to inspect.

| Failure class | What it looks like | Why a shallow review misses it | Review response | Evidence status |
|---|---|---|---|---|
| **Exploration failure** | Relevant caller, policy, config, schema, or history is never opened | The patch appears self-contained | Maintain a typed impact map and unresolved-evidence list | Direct/indirect |
| **Cross-file synthesis failure** | Evidence is retrieved but the changed invariant is misunderstood | Each individual file looks plausible | Reconstruct the path and state transition explicitly | Direct |
| **Locally correct, globally wrong** | Function passes unit tests but violates caller, lifecycle, API, or deployment assumptions | Local tests validate only one boundary | Trace consumers and production path | Direct/indirect |
| **Wrong or underspecified intent** | Patch solves a symptom, not the requirement or invariant | Issue text may describe only the visible failure | Reconstruct intent from issue, behaviour, tests, callers, docs, and history | Engineering synthesis |
| **Incomplete fix** | One path is repaired while another path or root cause remains | Reviewer follows the same visible reproduction | Enumerate all entry points and equivalent paths | Direct PR evidence |
| **Missing companion change** | Code changes but migration, config, generated client, docs, rollback, or registration does not | The defect is partly absent from the diff | Run negative-space review | Hypothesis supported by cross-file evidence |
| **Test overfitting** | Patch satisfies selected tests but differs from intended behaviour | Green CI appears conclusive | Run broader tests and independent behavioural checks | Direct |
| **Self-confirming test oracle** | Implementation and new test share the same mistaken interpretation | Test and code agree with each other | Derive oracle independently; mutation/differential challenge | Direct/indirect |
| **Weakened verification** | Test skipped, assertion relaxed, mock added, or failure swallowed | CI becomes green | Compare test strength before/after and exercise production path | Product guidance + direct test evidence |
| **Basic deterministic defect** | Missing import, undefined name, type mismatch, unreachable code, lint/build failure | Fluent code looks credible | Compiler, type checker, linter, test runner | Direct real-world static-analysis evidence |
| **Broad or silent error handling** | Bare catch, generic fallback, swallowed exception | Happy path still works | Trace failure semantics and observability | Direct static-analysis evidence; signal, not automatic defect |
| **Security boundary failure** | Injection, traversal, unsafe deserialisation, auth/tenant bypass | Requires attacker and data-flow model | Source-control-sink and reachability analysis | Direct/indirect security evidence |
| **Vulnerable repair** | Requested bug is fixed while a new vulnerability is introduced | Attention stays on the original failure | Independent security lane and scanner validation | Direct benchmark evidence |
| **Hallucinated dependency or API** | Nonexistent package, wrong method, stale version | Syntax is plausible | Registry/API/version verification | Direct security evidence |
| **Repository abstraction bypass** | New retry, parser, cache, permission check, transaction wrapper, serializer | New code may be functionally adequate | Counterfactual reuse search | Indirect repository-generation evidence |
| **Architecture violation** | Dependency direction, ownership, or layer boundary is crossed | Compilation does not encode all architectural constraints | Architecture lane with provenance-backed edges | Direct/indirect repository-reasoning evidence |
| **Concurrency/state failure** | Race, reentrancy, duplicate side effect, stale state, broken cancellation | May need interleaving reasoning | State invariant and schedule analysis | Human-review and repository-reasoning evidence |
| **Compatibility or migration failure** | Old/new binaries, schemas, events, clients, or stored data disagree | Current unit tests use one version | Compatibility matrix and rollback tests | Engineering principle |
| **Performance/resource regression** | N+1 calls, repeated scans, blocking I/O, unbounded queue, leaked resource | Functional outputs remain correct | Before/after cost model and measurement | PR and generated-code evidence; often indirect |
| **Scope creep** | Fix contains unrelated refactor, naming, or cleanup | Each edit may be individually reasonable | Necessity test for every touched area | Direct PR evidence |
| **Policy/process failure** | Wrong branch, missing disclosure, unrun checks, CLA/licence issue | Source code can be correct | Deterministic policy resolver | Direct |
| **Duplicate/obsolete work** | Another PR already solved it or repository direction changed | Code quality is irrelevant to mergeability | Search current issue/PR/history state | Direct PR evidence |
| **AI review false positive** | Reviewer assumes reachability, misses framework guarantee, invents race/security issue | Fluent explanation appears authoritative | Evidence schema and neutral validator | Direct review-benchmark evidence |
| **Confirmation-biased validation** | Second reviewer inherits first reviewer's conclusion | “Independent” review repeats the same premise | Neutral evidence packet and explicit no-defect outcome | Direct/preliminary |

---

# 5. Tests are evidence, not the complete specification

This conclusion has some of the strongest support in the evidence base.

## 5.1 Benchmark success can overstate correctness

A SWE-bench re-evaluation found that, under its studied configurations:

- an average 7.8% of apparently plausible patches failed developer-written tests when a broader relevant suite was run;
- 29.6% of patches exhibited behavioural differences from the developer patch under differential comparison;
- 28.6% of those divergent cases were manually judged certainly incorrect.

The exact values are tied to the study version and setup. The durable result is that changed-test-only or limited-test evaluation can count incomplete or behaviourally wrong patches as solved. **[D]**

Source: [Are “Solved Issues” in SWE-bench Really Solved Correctly?, arXiv:2503.15223](https://arxiv.org/abs/2503.15223)

## 5.2 Generated tests can preserve stale semantics

A 2026 study covering 22,374 program variants and eight LLMs found that semantic-altering changes substantially reduced generated-test success. More than 99% of failing tests in that semantic-change subset passed the original program while still executing the modified region, indicating that the tests frequently retained old behavioural assumptions. **[D]**

Source: [Evaluating LLM-Based Test Generation Under Software Evolution, arXiv:2603.23443](https://arxiv.org/abs/2603.23443)

## 5.3 The self-validating patch problem

```text
requirement
    ↓
model interprets requirement incorrectly
    ↓
model writes implementation from that interpretation
    ↓
model writes tests from the same interpretation
    ↓
implementation and tests agree
    ↓
CI is green
    ↓
actual requirement remains violated
```

The review must ask:

- Did the new test fail before the patch?
- Does its expected result come from a requirement independent of the implementation?
- Does it exercise the production path rather than a substitute created for the test?
- Would a realistic wrong implementation fail it?
- Which realistic wrong implementations would still pass?
- Were any assertions removed, weakened, skipped, or moved behind a mock?
- Do failure, boundary, compatibility, cancellation, retry, and concurrency cases matter?

## 5.4 Stronger behavioural challenge

Use the least expensive technique that can distinguish the intended behaviour:

1. focused regression test;
2. broader relevant suite;
3. before/after execution comparison;
4. mutation testing against likely wrong implementations;
5. property or metamorphic testing;
6. generated boundary and negative cases;
7. fuzzing;
8. differential testing against a reference, prior version, or independent implementation;
9. concurrency/race/stress testing;
10. migration and rollback compatibility testing.

DiffTestGen is promising evidence for change-directed differential test generation. Its 2026 preprint evaluated 463 PRs and reported behavioural differences in 78.2% of PRs, with greater combined coverage than its baselines. This is preliminary research, not a guarantee that every reported difference is a bug or that the method is production-ready. **[I]**

Source: [DiffTestGen, arXiv:2607.16024](https://arxiv.org/abs/2607.16024)

---

# 6. Why AI-authored PRs are not merged

A deep reviewer must examine **mergeability**, not only source-code defects.

## 6.1 Broad agentic-PR evidence

One MSR 2026 study analysed 33,596 agent-authored PRs from five agents and reported a 71.48% merge rate in that dataset. The qualitative analysis sampled 600 rejected PRs; 38 were inaccessible, leaving 562 categorised cases. Major categories included:

- reviewer abandonment or no meaningful review;
- duplicate work;
- CI/test failure;
- unwanted or mis-scoped changes;
- incorrect or incomplete implementations;
- agent misalignment;
- licence or contribution requirements.

Non-merged PRs also tended to touch more files, change more lines, and have more failed CI checks, although the reported size effects were not enormous. **[D]**

Source: [Where Do AI Coding Agents Fail?, arXiv:2601.15195](https://arxiv.org/abs/2601.15195)

## 6.2 Fix-related PR evidence

A separate MSR 2026 study analysed 8,106 fix-related AI-agent PRs:

- 65.0% were merged;
- 26.1% were closed without merge;
- 8.9% remained open at collection time.

Its manual sample of 326 closed, unmerged PRs found that another PR already resolving the issue, test failures, and incorrect or incomplete fixes were leading causes. Build and deployment failures existed but were less common in that sample. **[D]**

Source: [Why Are AI Agent–Involved Pull Requests (Fix-Related) Remain Unmerged?, arXiv:2602.00164](https://arxiv.org/abs/2602.00164)

The agent-specific merge rates in these datasets should not be treated as permanent model rankings. They reflect particular agents, repositories, task selection, dates, and workflows.

## 6.3 The anti-AI claim must remain narrow

A study of security-related AI PRs classified explicit distrust in AI-written code as 1.8% of one closed security-PR rejection taxonomy. That supports only the narrow statement that explicit distrust was uncommon in that subset. It cannot be generalised to all PRs or implicit maintainer attitudes. **[D]**

Source: [Insights into Security-Related AI-Generated Pull Requests, arXiv:2604.19965](https://arxiv.org/abs/2604.19965)

## 6.4 Mergeability review matrix

| Merge risk | What the reviewer should establish |
|---|---|
| Wrong problem | Compare issue intent, reproduction, current behaviour, changed behaviour, and acceptance criteria |
| Duplicate or superseded work | Inspect open/closed PRs, linked issues, recent commits, TODOs, and maintainer direction |
| Obsolete change | Confirm the base and head still contain the reported problem |
| Excessive scope | Prove why each touched area is necessary for the requested outcome |
| CI/build failure | Run repository-defined checks on the exact head |
| Deployment/runtime failure | Inspect packaging, manifests, IaC, environment, startup, migrations, and release path |
| Contribution-policy breach | Resolve `AGENTS.md`, `CONTRIBUTING`, templates, security policy, CODEOWNERS, CLA/licence, and path rules |
| API/compatibility break | Identify every consumer and version combination affected |
| Weak verification | Audit test oracle and production-path coverage |
| New dependency risk | Verify existence, version, lockfile, licence, maintenance, provenance, and necessity |
| Maintenance burden | Detect duplicate abstractions, dead scaffolding, over-generalisation, and convention drift |

A closed or unmerged PR is not automatically defective code. The final report should separate:

- **technical defect**;
- **process/policy blocker**;
- **coordination or duplication issue**;
- **unresolved reviewer state**;
- **no established defect**.

---

# 7. Real-world AI-attributed code debt: corrected interpretation

The current version of `Debt Behind the AI Boom` is arXiv v2, revised 26 April 2026. It reports:

- approximately 302,600 analysed AI-attributed commits;
- 6,299 public GitHub repositories;
- 484,366 static-analysis findings;
- 89.3% categorised as code smells;
- 6.0% categorised as correctness issues;
- 4.7% categorised as security issues;
- 22.7% of tracked findings still present at the latest analysed revision.

Prominent tool-detected classes included broad exception handling, unused variables or parameters, undefined references, and possible use before assignment. **[D]**

Source: [Debt Behind the AI Boom, arXiv:2603.28592v2](https://arxiv.org/abs/2603.28592)

These figures need important limits:

- the repositories were public and had at least 100 stars;
- analysis covered production Python, JavaScript, and TypeScript files;
- AI attribution required explicit Git metadata;
- some commits may mix human and AI edits;
- tests, documentation, configuration, generated artefacts, and vendored dependencies were excluded from the code-quality analysis;
- static analysis can produce false positives;
- the security class includes active vulnerabilities and latent unsafe patterns;
- the study did not provide a reliable human-only baseline.

Therefore:

> The study is evidence that explicitly attributable AI commits can introduce persistent, tool-detectable code-level debt. It is not proof that all 484,366 findings were runtime defects, that AI causes more debt than comparable human work, or that the result generalises to every language and repository.

The review skill can use the recurring patterns as **triage signals**, but must not report them without proving a violated property.

---

# 8. Security requires an independent lane

Security should not be hidden inside general correctness because the evidence, threat model, and validation requirements differ.

## 8.1 Generated repairs can introduce new vulnerabilities

A large SWE-bench security study used oracle retrieval to reduce retrieval uncertainty and examined vulnerabilities introduced during patch generation. In one standalone Llama setup, the researchers manually validated 135 newly introduced vulnerabilities in generated patches compared with 12 in developer patches. The result is serious but bounded to the studied model, benchmark, retrieval setup, patch set, and analysis pipeline. It is not a universal multiplier for AI patches. **[D]**

Source: [How Safe Are AI-Generated Patches?, arXiv:2507.02976](https://arxiv.org/abs/2507.02976)

## 8.2 Scanner alerts are not automatically exploitable vulnerabilities

The security-related PR study identified 675 PRs classified as security-related. Semgrep reported at least one potential issue in 104 of them, with recurring alert classes including regex inefficiency, injection, and path traversal. The review must distinguish:

- scanner match;
- unsafe pattern;
- reachable vulnerability;
- exploitable vulnerability with realistic attacker capability.

**[D]**

Source: [Insights into Security-Related AI-Generated Pull Requests, arXiv:2604.19965](https://arxiv.org/abs/2604.19965)

## 8.3 Package hallucination is a supply-chain risk

The USENIX Security 2025 package-hallucination study evaluated 16 code-generating LLMs over 576,000 samples in Python and JavaScript. It found nonexistent package recommendations across the tested models and demonstrated the resulting package-confusion threat. Its aggregate rates depend on the tested models and prompts, but the underlying risk is well established. **[D]**

Source: [We Have a Package for You!, USENIX Security 2025](https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen)

Every introduced dependency should therefore be checked against:

- the correct registry;
- exact package and namespace;
- requested and resolved version;
- lockfile;
- provenance and maintainer identity;
- licence compatibility;
- vulnerability and deprecation state;
- repository policy;
- whether an existing dependency or internal abstraction already solves the problem.

## 8.4 Security finding contract

A security finding should identify:

```text
attacker-controlled source
    → transformations
    → trust-boundary/security control
    → sink or protected action

attacker capability
required privilege
reachability
exploit preconditions
cross-user or cross-tenant impact
defence already present
tool or runtime evidence
remaining uncertainty
```

“Potential injection” is not a complete finding. The validator must establish whether attacker-controlled data reaches a dangerous operation without an effective guard.

---

# 9. Focused review attention and specialist lanes

A controlled experiment with 150 participants found that explicitly asking reviewers to focus on security increased the probability of vulnerability detection eightfold. Adding a tailored security checklist did not provide a statistically clear further improvement. **[D]**

Source: [Less is More: Supporting Developers in Vulnerability Detection during Code Review, arXiv:2202.04586](https://arxiv.org/abs/2202.04586)

This supports **focused attention**, not a universal rule that more checklists or more model passes are always better.

The skill should run:

- a compact core lane on every change;
- specialist lanes only when triggered by the change and affected system;
- a measurement loop that determines whether each lane adds true findings or only cost and noise.

## 9.1 Core lane — always run

The core lane asks:

- What is the requested behaviour?
- What observable behaviour changed?
- Which invariants must remain true?
- Are all changed areas necessary?
- Which callers, consumers, data, config, and tests are affected?
- What should also have changed?
- What deterministic checks apply?
- Is the PR mergeable under repository policy?

## 9.2 Risk triggers

| Trigger | Specialist lane |
|---|---|
| Authentication, authorisation, permissions, secrets, untrusted input, tenant data | Security and trust boundaries |
| Shared mutable state, async/task lifecycle, callbacks, locks, actors, events, retries | State, concurrency, cancellation, and reentrancy |
| Schema, migration, persistence, serialisation, event format, cache key | Data, migration, and compatibility |
| Public API, protocol, CLI, plugin, SDK, generated client | API and consumer compatibility |
| New or changed package, action, image, binary, or build tool | Dependency and supply chain |
| Network, filesystem, database, process, timeouts, retries, background work | Reliability and resource lifetime |
| Hot path, loops, large data, database queries, caching, allocation, locking | Performance |
| CI, packaging, deployment, feature flag, environment, observability | Operations and release |
| New tests, changed assertions, mocks, fixtures, skips, snapshots | Test oracle and verification |
| New abstraction, helper, framework, duplicate-looking logic, broad refactor | Architecture, reuse, and maintainability |

Patch size can raise risk, but the evidence does not justify one universal file-count or line-count threshold. Risk should depend on semantics, criticality, coupling, reversibility, and available verification.

---

# 10. Recommended review architecture

This section describes the proposed system. It is an **engineering synthesis**, not a claim that the complete pipeline has already been proven optimal.

```text
                    ┌────────────────────────┐
                    │ Change / PR / SHA      │
                    │ exact base + exact head│
                    └───────────┬────────────┘
                                ↓
                    ┌────────────────────────┐
                    │ Policy and provenance  │
                    │ resolver               │
                    └───────────┬────────────┘
                                ↓
                    ┌────────────────────────┐
                    │ Intent + invariant     │
                    │ reconstruction         │
                    └───────────┬────────────┘
                                ↓
                    ┌────────────────────────┐
                    │ Repository map + typed │
                    │ impact graph           │
                    └───────────┬────────────┘
                                ↓
                  ┌─────────────┴──────────────┐
                  ↓                            ↓
          core review lane             risk-triggered lanes
                  └─────────────┬──────────────┘
                                ↓
                    ┌────────────────────────┐
                    │ Deterministic evidence │
                    │ and execution          │
                    └───────────┬────────────┘
                                ↓
                    ┌────────────────────────┐
                    │ Behavioural challenge  │
                    │ and negative space     │
                    └───────────┬────────────┘
                                ↓
                    ┌────────────────────────┐
                    │ Neutral finding        │
                    │ validation             │
                    └───────────┬────────────┘
                                ↓
                    ┌────────────────────────┐
                    │ Coverage, exclusions,  │
                    │ uncertainty ledger     │
                    └───────────┬────────────┘
                                ↓
                    ┌────────────────────────┐
                    │ Evidence-backed report │
                    └────────────────────────┘
```

## Phase 0 — bind the review to an exact state

Capture:

- repository and remote;
- base commit and head commit;
- branch and working-tree state;
- submodules and generated artefacts;
- language, compiler, runtime, package-manager, and dependency versions;
- available build, test, lint, type, static-analysis, security, and release commands;
- CI status and relevant logs;
- issue, PR, incident, or specification identifiers.

A later head is a new evidence state. Findings must state which head they apply to.

**Output:** review provenance record.

## Phase 1 — deterministic policy discovery

Discover applicable:

- root and path-specific `AGENTS.md` files;
- `CONTRIBUTING` and pull-request templates;
- security policy;
- CODEOWNERS and ownership boundaries;
- local READMEs and architecture decision records;
- build, test, lint, formatting, release, and CI definitions;
- dependency, licence, disclosure, handoff, and generated-file rules.

Resolve precedence and applicability before semantic review.

```text
Rule | Applies to | Source | Required action | Loaded? | Conflict? | Evidence
```

RepoComplianceBench demonstrates why this cannot rely on agent initiative. Mixed AGENTS.md studies also warn against flooding the model with every context file. **Discover broadly, load narrowly, record precisely.**

Sources:

- [RepoComplianceBench, arXiv:2607.26819](https://arxiv.org/abs/2607.26819)
- [Evaluating AGENTS.md, arXiv:2602.11988](https://arxiv.org/abs/2602.11988)
- [On the Impact of AGENTS.md Files on Efficiency, arXiv:2601.20404](https://arxiv.org/abs/2601.20404)

**Output:** policy matrix, commands, conflicts, unresolved rules.

## Phase 2 — reconstruct intent and invariants

Build a working behavioural specification from:

```text
issue / task / incident
        +
observable base behaviour
        +
existing tests
        +
callers and consumers
        +
public API and data contracts
        +
documentation
        +
recent history, reverts, and rationale
        +
repository conventions
        =
working intent and invariant model
```

Record:

- requested behaviour;
- before and after observable behaviour;
- preserved invariants;
- new invariants;
- failure and recovery expectations;
- cancellation, retry, ordering, and idempotency expectations;
- migration and rollback expectations;
- compatibility requirements;
- unresolved interpretation questions.

If intent cannot be established, the correct result is an uncertainty or design question—not an invented defect.

**Output:** acceptance criteria and invariant ledger.

## Phase 3 — construct a compact repository map

Map only enough structure to review the change safely:

- modules/components and ownership;
- entry points and public interfaces;
- dependency direction;
- data stores, schemas, and migrations;
- external systems;
- trust boundaries;
- state machines and lifecycle flows;
- build, test, packaging, deployment, and release paths;
- generated sources and generators;
- observability and operations surfaces.

Every relationship should carry provenance:

```text
verified static edge
verified runtime edge
verified configuration edge
verified historical rationale
inferred semantic edge
unresolved relationship
```

**Output:** compact architecture map with uncertainties.

## Phase 4 — classify the change and build a typed impact graph

Classify each changed symbol or artefact:

- behaviour;
- API/interface;
- data/schema;
- security boundary;
- state/lifecycle;
- dependency/build;
- config/deployment;
- tests/verification;
- documentation/contract;
- refactor-only claim.

Expand from changed symbols through relevant typed edges:

```text
caller ↔ callee
interface ↔ implementation
publisher ↔ consumer
schema ↔ migration ↔ serializer ↔ client
config ↔ registration ↔ runtime component
source ↔ transform ↔ control ↔ sink
test ↔ production path
generator input ↔ generated output
public contract ↔ compatibility consumer
code ↔ relevant historical rationale
```

Stop expansion when a boundary is demonstrated safe, not merely when a token budget feels large.

The impact graph is a hypothesis-backed mechanism. Its causal value must be measured against simpler retrieval under equal model, token, and tool budgets.

**Output:** changed/affected inventory, evidence-backed edges, unresolved edges.

## Phase 5 — risk routing

Calculate review depth from semantics rather than one universal size threshold.

High-risk triggers include:

- authentication, money, permissions, secrets, privacy, or tenant isolation;
- persistence, migration, or irreversible state;
- concurrency, retry, cancellation, or distributed workflows;
- public API, protocol, event, or storage-format changes;
- dependencies, build, packaging, or release paths;
- broad cross-module impact;
- weak or unavailable deterministic verification;
- ambiguous intent;
- history of incidents or reverts in the same area.

**Output:** selected specialist lanes and reason for each.

## Phase 6 — specialist investigation

Each lane returns **candidate claims plus required evidence**, not final findings.

| Lane | Dominant questions |
|---|---|
| Specification/correctness | Does the change satisfy the reconstructed behaviour across all relevant paths? |
| Architecture/reuse | Does it respect ownership and dependency direction? What existing mechanism should have been reused? |
| Security | What is attacker controlled? Where are trust boundaries and authorisation decisions? |
| State/concurrency | What state is shared? Which operations interleave? What invariant can break? |
| Data/compatibility | Do old/new schemas, binaries, events, clients, and stored values coexist safely? |
| Reliability | What happens on timeout, cancellation, partial failure, retry, restart, and rollback? |
| Performance | What changed in asymptotic work, queries, calls, allocation, locking, caching, or resource lifetime? |
| Tests | Is the oracle independent? Which realistic broken implementation still passes? |
| Dependencies | Is the package real, necessary, supported, locked, licensed, and policy-compliant? |
| Operations | Will config, deploy, feature flags, observability, rollback, and release still work? |
| Maintainability | Did the patch add duplication, dead scaffolding, unnecessary abstraction, or conceptual complexity? |

**Output:** candidate finding packets and evidence gaps.

## Phase 7 — deterministic evidence layer

Use deterministic tools before asking a model to speculate about questions those tools answer directly.

```text
parser / compiler          → syntax and compilation
static type checker        → type contracts
linter                     → mechanical rules
CodeQL / SAST / Semgrep    → known patterns and data-flow candidates
package registry           → package and version existence
lockfile / resolver        → resolved dependency graph
licence scanner            → licence metadata
schema/config validator    → structural validity
unit/integration/E2E tests → observed behaviour
coverage                   → executed code, not correctness
mutation testing           → test sensitivity to broken variants
fuzzer/property tests      → boundary and invariant challenge
race/thread sanitizer      → observable concurrency failures
git history/blame          → prior behaviour and rationale clues
AST/call graph             → structural relationships
runtime trace              → actual execution path
LLM reasoning              → interpretation, hypothesis, synthesis
```

Tool unavailability, failure, timeout, and environmental mismatch must be recorded. They are not passes.

Current GitHub documentation illustrates the same broad separation of concerns: Copilot code review, deterministic CodeQL-based Code Quality, dependency review, coverage, and rulesets are complementary but separate product surfaces. Copilot review excludes dependency-management files, and GitHub explicitly warns that Copilot can miss issues and make mistakes. **[P]**

Sources:

- [About GitHub Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review)
- [Review AI-generated code](https://docs.github.com/en/copilot/tutorials/review-ai-generated-code)
- [GitHub Code Quality](https://docs.github.com/en/code-security/concepts/code-quality/code-quality)

**Output:** tool evidence and environment limitations.

## Phase 8 — behavioural challenge

Challenge affected paths where relevant:

| Dimension | Examples |
|---|---|
| Input boundary | empty, zero, negative, max, huge, Unicode, malformed, duplicate |
| Security | traversal, injection, encoding, forged identifier, tenant crossover |
| Timing | timeout, cancellation, slow dependency, clock skew, expiry boundary |
| Concurrency | duplicate request, interleaving, simultaneous update, reentrancy |
| Failure | partial write, downstream error, reset, crash, restart midway |
| Retry | duplicated side effect, replay, non-idempotent operation |
| Persistence | old schema/new binary, new schema/old binary, rollback |
| Resource | leak, unbounded loop/queue/memory, file/socket cleanup |
| Ordering | out-of-order, repeated, stale, replayed event |
| Configuration | missing, invalid, default, legacy, production-only value |
| Compatibility | old client/new server, new client/old server, stored legacy data |

The challenge must be proportional to risk. Do not automatically fuzz or mutation-test every trivial documentation change.

**Output:** reproduced failures, disproved hypotheses, and untested high-risk scenarios.

## Phase 9 — negative-space review

Ask:

> **Given the intended change, what evidence or companion change would normally be expected, but is absent?**

| Observed change | Companion areas to inspect |
|---|---|
| New environment variable | sample config, deployment values, validation, docs, secrets policy |
| New database field | migration, rollback, old data, serializer, fixtures, indexes |
| New enum value | exhaustive consumers, persistence, API/client/UI mappings |
| New API field | schema, generated clients, compatibility tests, documentation |
| New dependency | lockfile, licence, build image, SBOM, policy, existing alternative |
| New metric/log/event | naming, cardinality/PII, dashboards or alerts where project practice requires |
| New feature flag | default, rollout, ownership, cleanup/removal plan |
| Changed authorisation rule | every entry point, background jobs, audit behaviour, tenant boundaries |
| Changed timeout | retries, cancellation, caller assumptions, config units/defaults |
| Changed error type | catch sites, API translation, telemetry, retry classification |
| Renamed event or stored value | publishers, consumers, replay, migration, backwards compatibility |
| Changed generator input | regenerated outputs and verification of generated diff |

Absence is not automatically a defect. It is an investigation trigger.

This phase is an engineering hypothesis supported by cross-file and non-code review evidence. It needs direct seeded-defect and historical-defect evaluation.

**Output:** required-but-missing candidates with applicability evidence.

## Phase 10 — neutral adversarial validation

A second model is not automatically an independent source of truth.

Cross-model review research over 116 LiveCodeBench tasks found asymmetric effects: one author/reviewer pairing improved results while the reverse pairing degraded them. The experiment had no tool execution and is too narrow for universal conclusions, but it directly contradicts the assumption that another model always improves correctness. **[D, preliminary]**

Source: [Cross-Model LLM Code Review, arXiv:2607.21656](https://arxiv.org/abs/2607.21656)

Confirmation-bias and overcorrection studies show that framing can suppress real detections or induce false defects. **[D, preliminary]**

Sources:

- [Measuring and Exploiting Confirmation Bias in LLM-Based Code Review, arXiv:2603.18740](https://arxiv.org/abs/2603.18740)
- [Systematic Overcorrection in Requirement Conformance Judgement, arXiv:2603.00539](https://arxiv.org/abs/2603.00539)

The validator should receive:

- exact base/head state;
- neutral requirement and repository evidence;
- factual ingredients of the candidate claim;
- reproduction or tool output;
- an explicit `no defect established` outcome.

It should independently test:

- reachability;
- preconditions;
- alternative explanations;
- framework or language guarantees;
- existing safeguards;
- whether the issue still exists at the current head;
- whether the proposed remediation would create a regression.

Candidate statuses:

```text
validated
downgraded
unresolved
observation only
disproved
stale at current head
```

**Output:** validated, suppressed, or unresolved candidate findings.

## Phase 11 — coverage and uncertainty ledger

A deep review must be auditable.

Example:

```text
Review state
- Base:  8f3b...
- Head:  2b7c...

Coverage
- Changed files inspected:           17 / 17
- Changed symbols classified:        43 / 43
- Direct dependants traced:          61
- Critical transitive paths traced:  auth, checkout, webhook retry
- Relevant suites run:               8
- Static/security checks:            typecheck, CodeQL, dependency scan
- Schema/migration artefacts:        inspected
- Deployment/config artefacts:       inspected
- Relevant history:                  9 commits, 2 prior reverts

Excluded or unavailable
- production feature-flag values unavailable
- vendor SDK behaviour not reproducible locally
- load environment unavailable

Unresolved
- one inferred runtime registration edge
- rollback compatibility not exercised
```

A coverage ledger proves what was investigated. It does not prove that the conclusions are correct.

**Output:** explicit coverage, exclusions, tool failures, and unresolved assumptions.

## Phase 12 — final report

Report only:

- validated defects;
- material unresolved risks that require a decision or unavailable evidence;
- process/policy blockers;
- concise coverage and test evidence.

Do not convert every observation into a requested code change.

---

# 11. Counterfactual reuse review

AI can produce a functioning local implementation while bypassing the repository's established mechanism. For each significant design decision, ask:

> **What would a competent maintainer of this repository probably reuse instead?**

Then search for it.

Examples:

```text
manual retry loop           → repository retry abstraction
new JSON encoder            → serialization policy or existing codec
role string comparison      → permission framework
raw transaction             → transaction/context abstraction
new cache dictionary        → cache service and invalidation policy
hand-written API model      → generated schema/client pipeline
custom process launcher     → command execution wrapper
new error translation       → central error mapper
```

RepoExec provides indirect evidence that models can produce functionally successful code while failing to use available repository dependencies appropriately. The reviewer must still prove why the existing abstraction applies; reuse is not automatically preferable when isolation, compatibility, or ownership boundaries justify duplication.

---

# 12. Finding contract

Every reportable finding should use a strict evidence schema.

```text
id:
category:
severity:
confidence:
status:

claim:
impact:

changed_path:
affected_path:

preconditions:
execution_or_data_path:
violated_invariant_or_contract:

evidence:
- source location
- caller/consumer/config/history evidence
- deterministic tool result
- runtime or test result

reproduction:
why_existing_tests_miss_it:

expected_fix_shape:
validation_performed:
remaining_uncertainty:
```

## 12.1 Severity and confidence are separate

- A potentially catastrophic authorisation defect with uncertain reachability can be **high severity / low confidence**.
- A reproducible but low-impact logging defect can be **low severity / high confidence**.
- “High severity” alone must not turn an unresolved hypothesis into a blocker.

## 12.2 Concurrency finding extension

```text
shared state:
operation A:
operation B:
possible interleaving:
expected invariant:
actual violation:
synchronisation present or absent:
reproduction/stress evidence:
```

## 12.3 Performance finding extension

```text
before cost/call count:
after cost/call count:
input scaling dimension:
production trigger:
measurement or defensible model:
resource impact:
```

## 12.4 Compatibility finding extension

```text
producer version:
consumer version:
stored/wire format:
changed expectation:
roll-forward behaviour:
rollback behaviour:
affected deployed population:
```

A vague statement such as “this may cause a race condition” is not a reportable defect without shared state, concurrent operations, a feasible interleaving, and a violated invariant.

---

# 13. Revised 15-point skill contract

```text
MISSION

Determine whether the proposed change is safe, complete, appropriate,
and mergeable for this repository—not merely whether the changed lines
look plausible.

NON-NEGOTIABLES

1. Bind every review to an exact base and head.
2. Resolve applicable repository rules before semantic judgement.
3. Reconstruct intended behaviour and preserved invariants.
4. Classify changed artefacts and route review depth by semantic risk.
5. Build a provenance-backed impact model beyond the diff.
6. Inspect affected code and required-but-missing companion changes.
7. Treat tests as evidence, never as the complete specification.
8. Use deterministic tools for deterministic claims.
9. Activate focused specialist lanes only when relevant and measure their value.
10. Challenge high-risk behaviour through negative, differential, property,
    mutation, fuzz, concurrency, migration, or rollback checks as appropriate.
11. Treat every candidate finding as unproven until reachability, preconditions,
    and alternative explanations are checked.
12. Give every reported defect a concrete evidence and execution path.
13. Separate severity, confidence, status, and remaining uncertainty.
14. Produce a coverage ledger, including unavailable tools and excluded paths.
15. Prefer a few validated, actionable findings over speculative volume;
    never force a code change merely to satisfy an unproven reviewer concern.
```

This contract intentionally contains durable process principles rather than paper-specific percentages.

---

# 14. Evaluation plan

The skill cannot be judged by whether its reports sound comprehensive. It needs a benchmark and continuous field evaluation.

## 14.1 Benchmark classes

| Class | Purpose |
|---|---|
| Historical production bugs | Test whether the skill catches defects that escaped the real process |
| Reverted or rejected PRs | Test architecture, intent, scope, and process understanding |
| CVEs and security fixes | Test trust-boundary and data-flow reasoning |
| Cross-file seeded defects | Test traversal and synthesis |
| Configuration-only defects | Test non-source artefact review |
| Migration/API compatibility defects | Test temporal and consumer compatibility |
| Concurrency/state defects | Test interleaving and lifecycle reasoning |
| Test-oracle defects | Test whether the reviewer audits verification itself |
| Hallucinated or unnecessary dependencies | Test registry and reuse investigation |
| Missing companion changes | Test negative-space review |
| Correct but unusual code | Measure false-positive resistance |
| Harmless large refactors | Test whether size alone produces invented concerns |
| Misleading comments | Test whether executable evidence beats prose |
| Repository-rule traps | Test discovery and precedence resolution |

## 14.2 Metrics

Measure:

- confirmed-defect recall;
- precision;
- severity-weighted recall;
- actionability and reproducibility;
- reviewer acceptance;
- false-positive burden and engineer time lost;
- cross-file detection rate;
- missing-change detection rate;
- tool-backed finding ratio;
- regression caused by acting on review advice;
- escaped-defect rate;
- coverage completeness;
- policy-compliance detection;
- runtime, token, tool, and infrastructure cost;
- latency to first useful finding;
- duplicated findings across lanes.

CR-Bench contains 584 tasks and a 174-task verified subset and evaluates precision, recall, F1, usefulness, and signal-to-noise. Its initial experiments show that pushing a reviewer to search harder can improve recall while reducing signal quality. The exact scores are model- and prompt-specific; the durable lesson is that comment volume is not a success metric. **[D]**

Source: [CR-Bench, arXiv:2603.11078](https://arxiv.org/abs/2603.11078)

## 14.3 Ablation sequence

Compare equal-budget variants:

```text
A. diff only
B. diff + whole changed files
C. B + repository rules
D. C + targeted repository retrieval
E. D + typed impact graph
F. E + deterministic tools
G. F + risk-routed specialist lanes
H. G + behavioural challenge
I. H + neutral validator
J. full system + negative-space review + coverage ledger
```

For every stage, measure:

- additional true findings;
- additional false positives;
- findings uniquely attributable to the stage;
- tokens, runtime, and tool cost;
- whether the stage changes severity or confidence rather than finding a new issue.

This answers the essential question:

> Does the extra complexity prevent more real defects, or only produce more process and prose?

## 14.4 Adversarial clean-code set

Include correct code containing constructs that often trigger superficial warnings:

- intentional broad exception handling at a documented boundary;
- safe parameterised raw SQL;
- deliberate lock-free design with proven ownership;
- intentional duplication across an isolation or compatibility boundary;
- validated dynamic import;
- required legacy API;
- apparently unused callback invoked by framework convention;
- defensive compatibility branch preserved for old stored data.

Reward the reviewer for:

> Investigated; no defect established.

## 14.5 Negative-space set

Seed:

- enum value without one exhaustive consumer;
- field change without migration;
- API response change without generated schema/client update;
- configuration value without production manifest;
- permission change without background-job caller;
- dependency manifest update without lockfile;
- retry change without idempotency protection;
- generator input change without regenerated output;
- event rename without replay compatibility.

## 14.6 Version and drift controls

Record for every benchmark run:

- exact model and model date/version;
- agent harness and tool versions;
- prompt/skill revision;
- repository base/head;
- dependency and runtime environment;
- network availability;
- retry count and sampling settings.

Re-run a stable benchmark set when any of those changes materially.

## 14.7 Continuous learning corpus

Feed back:

```text
false positive reported by the skill
false negative that escaped the skill
review fix that caused a regression
PR rejected for a reason the skill missed
candidate finding disproved by a maintainer
production incident linked to an approved change
```

This creates a local corpus of precision, recall, process, and repair failures.

---

# 15. Evidence ledger

| Claim | Best evidence | Scope | Status | Confidence for skill design |
|---|---|---|---|---|
| Relevant repository dependency context improves generation and reuse | [RepoExec](https://arxiv.org/abs/2406.11927) | Python repository/function generation | Indirect benchmark | Medium |
| Exploration and fine-grained localisation remain bottlenecks | [SWE-Explore](https://arxiv.org/abs/2606.07297) | 848 issues, 10 languages, 203 repos | Direct adjacent benchmark | Medium |
| Cross-file reasoning remains difficult even with oracle context | [RepoReasoner](https://arxiv.org/abs/2607.25996) | Seven models; repository reasoning | Direct benchmark | Medium–high |
| Structured retrieval can outperform file-level retrieval in repository QA | [StackRepoQA](https://arxiv.org/abs/2603.26567) | 1,318 questions, 134 Java projects, two LLMs | Direct adjacent benchmark | Medium |
| Structure-aware tools can improve agent efficiency/effectiveness | [CodeStruct](https://arxiv.org/abs/2604.05407), [CodexGraph](https://arxiv.org/abs/2408.03910) | Coding-agent benchmarks, not review | Indirect | Medium |
| Agents often fail to discover contribution policy | [RepoComplianceBench](https://arxiv.org/abs/2607.26819) | 106 issues, 49 repos, four frontier models | Direct | Medium–high |
| More instruction context is not universally beneficial | [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988), [AGENTS.md efficiency study](https://arxiv.org/abs/2601.20404) | Different task sets and outcomes | Mixed direct evidence | Medium |
| Limited test configurations can overstate patch correctness | [SWE-bench re-evaluation](https://arxiv.org/abs/2503.15223) | SWE-bench patches | Direct | High |
| Generated tests can retain stale semantics after behaviour changes | [Test generation under evolution](https://arxiv.org/abs/2603.23443) | 22,374 variants, eight LLMs | Direct benchmark | Medium–high |
| Change-directed differential testing is promising | [DiffTestGen](https://arxiv.org/abs/2607.16024) | 463 PRs; preprint | Preliminary | Low–medium |
| Agent PR non-merges include technical, process, duplicate, and engagement causes | [Failed agentic PRs](https://arxiv.org/abs/2601.15195) | 33,596 PRs; 562 accessible manual cases | Direct dataset | Medium–high |
| Fix-related PR non-merges often involve prior resolution, tests, and incomplete fixes | [Fix-related PR study](https://arxiv.org/abs/2602.00164) | 8,106 PRs; 326 manual cases | Direct dataset | Medium–high |
| Explicit AI distrust was uncommon in one security-PR taxonomy | [Security-related AI PRs](https://arxiv.org/abs/2604.19965) | Closed security-related subset | Direct but narrow | Medium for narrow claim only |
| AI-attributed commits can introduce persistent static-analysis debt | [Debt Behind the AI Boom v2](https://arxiv.org/abs/2603.28592) | Public ≥100-star Python/JS/TS repos; explicit Git traces | Direct dataset | Medium |
| AI repair can introduce new security vulnerabilities | [How Safe Are AI-Generated Patches?](https://arxiv.org/abs/2507.02976) | SWE-bench and studied Llama/agent setups | Direct benchmark | Medium |
| Package hallucinations create supply-chain risk | [USENIX package hallucinations](https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen) | 16 LLMs, Python/JavaScript, 576k samples | Peer-reviewed direct | High for existence; medium for rates |
| Security-focused attention can improve human review detection | [Less is More](https://arxiv.org/abs/2202.04586) | 150 participants, selected vulnerability tasks | Controlled direct | Medium–high |
| Context-heavy security defects are more likely to escape human review | [Chromium OS case-control study](https://arxiv.org/abs/2102.06909) | One major project; security defects | Direct | Medium–high |
| AI code review has a precision/recall and signal-to-noise trade-off | [CR-Bench](https://arxiv.org/abs/2603.11078) | 584 tasks; 174 verified subset; initial model experiments | Direct benchmark | Medium |
| A second model can improve or degrade code depending on pairing | [Cross-model review](https://arxiv.org/abs/2607.21656) | 116 tasks; no tool execution | Preliminary direct | Low–medium |
| Review framing can induce confirmation bias | [Confirmation-bias study](https://arxiv.org/abs/2603.18740) | 250 CVE/patch pairs, four models | Preliminary direct | Medium |
| Directive conformance prompts can create overcorrection | [Overcorrection study](https://arxiv.org/abs/2603.00539) | Requirement-conformance judgement | Preliminary direct | Medium |
| A hybrid platform can separate AI review, deterministic analysis, dependency review, and gates | [GitHub Copilot review](https://docs.github.com/en/copilot/concepts/agents/code-review), [Code Quality](https://docs.github.com/en/code-security/concepts/code-quality/code-quality) | Current product behaviour | Product evidence only | High for behaviour, none for causal efficacy |
| Dedicated negative-space review improves defect detection | No direct study located | Proposed missing-companion phase | Hypothesis | Unknown; benchmark required |
| The exact typed impact graph improves review under equal budget | Adjacent graph/retrieval evidence only | Proposed review architecture | Hypothesis | Unknown; ablation required |
| A coverage ledger improves correctness | Governance/evaluation reasoning | Proposed mechanism | Hypothesis | Unknown for correctness; high for auditability |

---

# 16. Remaining unresolved questions

1. **Causal value of the impact graph.** Does it improve real-review recall after controlling for model, tokens, tools, and runtime?
2. **Negative-space precision.** How often does a missing-companion detector find real omissions versus project-specific optional work?
3. **Human baseline.** Which observed AI-associated defect patterns exceed matched human-authored changes in the same repositories and periods?
4. **Current-model drift.** Which 2025–2026 failure modes persist for the exact models and agent harnesses used by the skill?
5. **Validator independence.** Which combination of model diversity, prompt neutrality, deterministic evidence, and execution most reduces shared blind spots?
6. **Risk routing.** Which triggers reliably identify when specialist lanes add value?
7. **Cross-language validity.** How should the graph, static analysis, concurrency model, and compatibility checks differ by language and framework?
8. **Non-code artefacts.** Which CI, deployment, generated-code, policy, documentation, and release omissions are most common in the target repositories?
9. **Operational tolerance.** What false-positive rate, latency, and cost will maintainers tolerate before ignoring the reviewer?
10. **Unavailable tooling.** When compilers, tests, registries, runtime environments, or production configuration are unavailable, which verdicts must be withheld?
11. **Review-induced regression.** How often does acting on a plausible but wrong AI finding make correct code worse?
12. **Field effectiveness.** Does the skill reduce escaped production defects and rejected PRs in real use, not merely improve benchmark scores?

---

# Conclusion

The strongest lesson is not “make the model think harder” or “put the whole repository in context.” It is:

> **Build a review process that cannot silently substitute plausibility for evidence.**

A deep repository review should finish because it can show:

- the exact change state it reviewed;
- the rules and intent it resolved;
- the affected paths and relationships it traced;
- the deterministic checks and behavioural challenges it ran;
- the candidate findings it disproved;
- the evidence supporting every remaining finding;
- the areas it could not verify;
- the cost and coverage of the investigation.

That is the difference between an AI that comments on a diff and a review system that conducts a reproducible software investigation.
