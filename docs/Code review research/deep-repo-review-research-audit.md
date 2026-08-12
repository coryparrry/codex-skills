# Audit of the Deep Repo-Wide Code Review Research

**Audit date:** 12 August 2026

**Materials audited:**

- `chatgpt-deep-research-report-5.md` — original research report
- `codex-research-delta-report-6.md` — correction and evidence delta

## Verdict

**The research is directionally strong, but the original report is not reliable enough to use unchanged as the factual foundation of a production skill.**

Its central recommendation is sound: a deep review should investigate the repository around a change, reconstruct intent, trace affected code and non-code artefacts, use deterministic tools, challenge tests, and require evidence for findings. The correction report substantially improves the work.

However, the two files should not remain as a baseline plus appendix. They should be replaced by one consolidated report because:

1. the original uses non-portable citation placeholders rather than a reproducible bibliography;
2. some statistics came from earlier paper versions;
3. several benchmark findings are generalised beyond the language, model, task, or dataset actually studied;
4. some static-analysis alerts are described too much like confirmed runtime defects or exploitable vulnerabilities;
5. official product documentation is sometimes used as evidence of efficacy rather than merely evidence of current product behaviour;
6. the proposed impact graph, negative-space review, coverage ledger, specialist routing, and adversarial validator are good engineering proposals, but the complete system has not been experimentally proven to be the optimal review architecture.

## Overall assessment

| Area | Assessment | Audit conclusion |
|---|---|---|
| Central thesis | Strong | Retain. A diff is not the whole behavioural change. |
| Repository exploration | Strong but indirect | Retain with scope. Most evidence comes from generation, repair, reasoning, or QA benchmarks rather than code-review trials. |
| Tests are not the specification | Strong | Retain. This is one of the best-supported conclusions. |
| Deterministic tools + model reasoning | Strong engineering principle | Retain, but do not claim GitHub product design proves effectiveness. |
| AI-specific failure taxonomy | Useful | Retain as a risk catalogue, not as a claim that every pattern is uniquely or disproportionately caused by AI. |
| PR rejection analysis | Supported within datasets | Retain with dataset boundaries and a distinction between non-merge and technical failure. |
| Security lane | Strongly justified | Retain. Scope scanner findings and benchmark vulnerability counts carefully. |
| Specialist review passes | Qualified | Retain as risk-routed lanes, not an always-on checklist. |
| Impact graph | Promising design inference | Retain and benchmark; do not label it empirically proven for review. |
| Missing-companion-change detector | Valuable hypothesis | Retain as a first-class experimental phase. |
| Independent validator | Sensible guardrail | Retain, but make it neutral, evidence-bound, and able to reject the first reviewer's claim. |
| Coverage ledger | Valuable governance mechanism | Retain as an auditable record, not proof that the review was correct. |
| Exact percentages | Fragile | Version, date, model, task, and dataset must accompany every percentage. |

# Material corrections

## 1. The complete architecture is recommended, not experimentally proven

The reports correctly combine several supported mechanisms:

- repository context matters;
- exploration and cross-file reasoning remain difficult;
- tests can accept incorrect patches;
- static and dynamic tools provide evidence that prose cannot;
- security-focused attention can improve detection;
- AI reviewers have a precision/recall and confirmation-bias problem.

No cited experiment compares the proposed full pipeline against alternatives and establishes it as the strongest or optimal architecture. The corrected wording should be:

> The evidence supports the need for repository-aware, tool-backed, risk-focused review. A risk-routed evidence orchestrator is a well-motivated architecture that now needs direct ablation and field evaluation.

## 2. Correct the `Debt Behind the AI Boom` statistics and interpretation

The current arXiv version is **v2, revised 26 April 2026**. It reports:

- approximately **302,600** analysed AI-attributed commits;
- **6,299** public GitHub repositories;
- **484,366** static-analysis findings;
- **89.3%** categorised as code smells;
- **22.7%** of tracked findings still present at the latest analysed revision.

The earlier values in the original report reflect paper-version drift.

More importantly, these findings must not be described as 484,366 confirmed defects. The study used ESLint, Pylint, and Semgrep; its security category includes active vulnerabilities and latent unsafe patterns. Its pipeline validation still leaves measurement noise. The study also:

- only covers public repositories with at least 100 stars;
- only analyses production Python, JavaScript, and TypeScript files;
- only identifies AI involvement when explicit Git metadata exists;
- can include mixed human/AI edits;
- excludes tests, documentation, configuration, generated artefacts, and vendored dependencies from its code-quality analysis;
- has no reliable human-only comparison group.

**Correct use:** evidence that identifiable AI-attributed commits can introduce persistent, tool-detectable code-level debt.

**Incorrect use:** proof that AI creates more defects than comparable human work, or that every scanner alert was a runtime bug.

Primary source: [Debt Behind the AI Boom, arXiv:2603.28592v2](https://arxiv.org/abs/2603.28592)

## 3. Narrow the 1.8% “AI distrust” claim

The 1.8% value comes from one manual rejection taxonomy for **closed, security-related AI PRs**. It means explicit distrust of AI-written code represented 1.8% of the categories in that particular subset.

It does not establish that:

- only 1.8% of all AI PRs are rejected because of AI;
- maintainers generally do not distrust AI;
- implicit distrust or review avoidance is absent;
- the same distribution applies outside security PRs, the sampled repositories, or the studied agents.

**Correct use:** explicit AI distrust was uncommon in this particular security-PR taxonomy.

**Incorrect use:** maintainers reject AI PRs almost entirely for technical reasons.

Primary source: [Insights into Security-Related AI-Generated Pull Requests, arXiv:2604.19965](https://arxiv.org/abs/2604.19965)

## 4. Treat Semgrep results as potential issues unless manually validated

The security-PR study identified 675 security-related PRs and reported that 104 had at least one Semgrep alert. That is useful evidence of recurring patterns, but a Semgrep alert is not automatically an exploitable vulnerability.

The rewritten report should use wording such as:

> Semgrep flagged potential security issues in 104 of 675 security-related PRs, with recurring alert classes including regex inefficiency, injection, and path traversal.

It should not say that 104 PRs were proven vulnerable unless the individual findings were manually validated for reachability and exploitability.

## 5. Separate non-merge from technical rejection

The broad agentic-PR study analysed 33,596 PRs and reported a 71.48% merge rate. Its qualitative phase began with 600 rejected PRs; 38 were inaccessible, leaving 562 categorised cases. The largest categories included reviewer abandonment and duplicate work, alongside CI/test failures and incorrect or incomplete implementations.

That evidence supports the report's call to review **mergeability** as well as code correctness. It does not support treating every closed PR as evidence of defective code. A PR may be unmerged because it is duplicate, obsolete, unwanted, inactive, on the wrong branch, or never meaningfully reviewed.

Primary source: [Where Do AI Coding Agents Fail?, arXiv:2601.15195](https://arxiv.org/abs/2601.15195)

## 6. Preserve the fix-related PR figures, but keep them dataset-specific

The fix-related study reports:

- 8,106 fix-related AI-agent PRs;
- 65.0% merged;
- 26.1% closed without merge;
- 8.9% open;
- a manual sample of 326 closed, unmerged PRs.

In the sample, another PR already resolving the issue, test failures, and incorrect or incomplete fixes were leading causes. These figures are correctly reported in the delta, but they are properties of the AIDEV-POP fix-related subset and its collection date—not permanent rates for Codex, Copilot, Devin, Cursor, Claude Code, or AI coding in general.

Primary source: [Why Are AI Agent–Involved Pull Requests (Fix-Related) Remain Unmerged?, arXiv:2602.00164](https://arxiv.org/abs/2602.00164)

## 7. Keep “tests are evidence, not the specification”

This is one of the strongest parts of the research.

The SWE-bench re-evaluation found that some patches accepted by benchmark configurations failed broader developer-written tests, while differential execution found behavioural differences from developer patches. The exact percentages are tied to the paper version and evaluation setup, but the durable conclusion is clear:

> Passing the tests selected by a benchmark or PR is not equivalent to satisfying the complete intended behaviour.

The test-evolution study also found that generated tests can preserve old semantics after a behaviour-changing edit. This strongly supports independent test-oracle review, before/after comparison, mutation testing, property testing, and targeted differential testing.

Primary sources:

- [Are “Solved Issues” in SWE-bench Really Solved Correctly?, arXiv:2503.15223](https://arxiv.org/abs/2503.15223)
- [Evaluating LLM-Based Test Generation Under Software Evolution, arXiv:2603.23443](https://arxiv.org/abs/2603.23443)

## 8. Replace the weakest “maximum effective context” evidence

The original and delta reports are right that more context is not automatically better. The strongest support should come from repository-specific evidence rather than relying heavily on a broad, single-author “maximum effective context” preprint.

Better repository-grounded evidence includes:

- RepoReasoner: longer retrieved contexts did not consistently improve repository-level reasoning; for some models, added noise reduced performance.
- StackRepoQA: graph-based retrieval improved repository QA more than file-level retrieval, but gains remained modest and performance dropped on unseen questions.
- SWE-Explore: file discovery and fine-grained localization remain distinct bottlenecks.
- RepoExec: relevant dependency context improves repository-level generation and dependency use.

**Correct conclusion:** select and structure context; do not flatten the repository into one prompt.

**Overclaim to avoid:** a graph will necessarily outperform every other retrieval strategy for every code review.

Primary sources:

- [RepoReasoner, arXiv:2607.25996](https://arxiv.org/abs/2607.25996)
- [Beyond Code Snippets / StackRepoQA, arXiv:2603.26567](https://arxiv.org/abs/2603.26567)
- [SWE-Explore, arXiv:2606.07297](https://arxiv.org/abs/2606.07297)
- [RepoExec, arXiv:2406.11927](https://arxiv.org/abs/2406.11927)

## 9. Qualify the impact graph

Research supports the value of dependency context, structured repository access, graph-based retrieval, callers/callees, and cross-file reasoning. It does not directly prove that the exact proposed impact graph is the best review representation.

The impact graph should therefore be described as a **typed evidence model to evaluate**, with edges such as:

- caller → callee;
- interface → implementation;
- input source → transformation → sink;
- configuration → registration → runtime component;
- schema → migration → serializer → consumer;
- generator input → generated output;
- public API → compatibility consumer;
- test → production path;
- commit or ADR → design rationale.

Every edge should record its source and confidence. Static analysis, runtime tracing, configuration parsing, generated metadata, and model inference must not be treated as equally certain.

## 10. Keep negative-space review, but label it as a hypothesis

The “what should also have changed but did not?” phase is one of the most valuable original ideas. It targets defects that are absent from a diff:

- missing migration;
- missing registration;
- stale generated client;
- missing production configuration;
- missing permission check in another entry point;
- missing rollback path;
- missing lockfile or licence update;
- missing test of a public behavioural contract.

The evidence establishes that cross-file and non-code context matters. It does not directly establish the recall, precision, or cost of a dedicated missing-change detector. Keep it as a first-class phase, but explicitly benchmark it with seeded and historical omissions.

## 11. Risk-route specialist lanes

The controlled security-review experiment found that explicitly focusing reviewers on security greatly improved vulnerability detection, while adding a security checklist did not produce a clear further benefit.

This supports focused attention. It does not prove that running ten independent model passes on every PR is efficient or more accurate. The corrected design should:

- always run a compact core correctness/integration pass;
- activate security, concurrency, migration, compatibility, dependency, performance, reliability, or operations lanes when evidence triggers them;
- measure each lane's incremental true-positive yield, false-positive burden, latency, and token/tool cost.

Primary source: [Less is More: Supporting Developers in Vulnerability Detection during Code Review, arXiv:2202.04586](https://arxiv.org/abs/2202.04586)

## 12. Do not use GitHub product structure as independent efficacy evidence

Current GitHub documentation shows that its platform offers complementary capabilities:

- Copilot code review with project-context gathering;
- separate deterministic CodeQL-based Code Quality checks;
- separate dependency review;
- coverage and ruleset gates;
- risk-sensitive Lite and Balanced review effort;
- explicit warnings that Copilot can miss issues and make mistakes.

This is useful as an implementation precedent and description of current product boundaries. It is not an independent experiment proving that the proposed hybrid architecture is more effective.

A further correction: dependency-management files are excluded from Copilot code review. Dependency review is a separate feature. Avoid wording that implies one Copilot pass reviews those artefacts through CodeQL and dependency review automatically.

Primary documentation:

- [About GitHub Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review)
- [GitHub Code Quality](https://docs.github.com/en/code-security/concepts/code-quality/code-quality)
- [Reviewing dependency changes](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/reviewing-dependency-changes-in-a-pull-request)

## 13. Keep repository-policy discovery, with one important nuance

RepoComplianceBench found that agents proactively opened relevant policy files outside always-loaded instruction files in only 3.5% of runs. This strongly supports deterministic policy discovery and precedence resolution.

However, instruction-context studies are mixed: one found no general success benefit and more than 20% inference cost, while another smaller study found runtime and output-token savings. The correct operational rule is:

> Discover broadly, resolve precedence deterministically, load only the applicable rules, and record what was and was not loaded.

Primary sources:

- [A First Look at Coding Agents' Compliance with AI Contribution Rules, arXiv:2607.26819](https://arxiv.org/abs/2607.26819)
- [Evaluating AGENTS.md, arXiv:2602.11988](https://arxiv.org/abs/2602.11988)
- [On the Impact of AGENTS.md Files on Efficiency, arXiv:2601.20404](https://arxiv.org/abs/2601.20404)

## 14. Treat AI fingerprints as triage signals, not findings

Patterns such as broad exception handling, unused scaffolding, excessive mocking, duplicate utilities, and new one-off abstractions can be high-value review prompts. They do not prove a defect.

A reportable finding must identify the violated property:

- incorrect behaviour;
- unreachable or dead path;
- hidden failure;
- repository abstraction bypass;
- security boundary violation;
- measurable maintenance or performance harm;
- explicit repository-policy breach.

Without that evidence, the pattern should remain a search lead or be omitted.

## 15. Keep package-hallucination checks, scope the rates

The USENIX Security 2025 study provides strong evidence that code-generating models can recommend nonexistent packages and that this creates a package-confusion or “slopsquatting” opportunity. Its reported rates depend on the 16 models, prompts, languages, and sampling setup used in the study.

The skill should verify every introduced dependency against the intended registry and lockfile. It should not use the paper's aggregate percentages as a current universal rate for every model.

Primary source: [We Have a Package for You!, USENIX Security 2025](https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen)

## 16. Neutralise the validator

Cross-model review evidence is asymmetric and narrow: one author/reviewer pairing improved results while the reverse pairing degraded them in a 116-task setting without tool execution. Other studies show that positive or directive framing can suppress detection or cause overcorrection.

Therefore the validator should not receive a prompt such as:

> Confirm that this bug exists and explain why it is severe.

It should receive:

- the exact code state;
- requirement and repository evidence;
- the proposed claim's factual ingredients, without persuasive framing;
- reproduction steps where available;
- an explicit `no defect established` outcome.

It should independently test reachability, preconditions, alternative explanations, framework guarantees, and current-head applicability.

Primary sources:

- [Cross-Model LLM Code Review, arXiv:2607.21656](https://arxiv.org/abs/2607.21656)
- [Measuring and Exploiting Confirmation Bias in LLM-Based Code Review, arXiv:2603.18740](https://arxiv.org/abs/2603.18740)
- [Systematic Overcorrection in Requirement Conformance Judgement, arXiv:2603.00539](https://arxiv.org/abs/2603.00539)

## 17. Keep precision and signal-to-noise as first-order metrics

CR-Bench contains 584 tasks and a 174-task verified subset. Its initial experiments show a trade-off between finding more hidden issues and producing lower-signal review output. The exact model results are benchmark- and prompt-specific, but the evaluation lesson is durable:

> A reviewer is not improved merely by producing more comments.

Measure precision, recall, severity-weighted recall, usefulness, signal-to-noise, actionability, reviewer acceptance, and regressions caused by acting on incorrect review advice.

Primary source: [CR-Bench, arXiv:2603.11078](https://arxiv.org/abs/2603.11078)

# Claims that should be removed or rewritten

| Original tendency | Required rewrite |
|---|---|
| “Research proves the full orchestrator is the strongest design.” | “Research motivates the components; the full architecture requires direct evaluation.” |
| “GitHub combines Copilot review, CodeQL, dependency review, and merge gating in one stack.” | “GitHub offers separate complementary product surfaces; Copilot review excludes dependency files.” |
| “484,366 AI defects were found.” | “The study reported 484,366 tool-detected code-level issues, with validation noise and no human-only baseline.” |
| “Security PRs introduced vulnerabilities in 104 cases.” | “Semgrep reported potential issues in 104 security-related PRs.” |
| “Only 1.8% of AI PRs are rejected because of distrust.” | “Explicit AI distrust was 1.8% in one closed security-PR rejection taxonomy.” |
| “More context makes performance worse.” | “Additional noisy context can reduce performance in some repository tasks and models; relevant structured context can improve it.” |
| “Graph retrieval is proven best for deep review.” | “Graph-based retrieval is promising and has improved adjacent tasks; its causal value for review must be benchmarked.” |
| “A second model independently verifies the first.” | “A second model is another fallible reviewer; independence must come from neutral framing, different evidence, tools, and falsification.” |
| “Broad exceptions, mocks, duplication, or scaffolding are AI defects.” | “They are triage signals that require a concrete violated property before reporting.” |
| “Passing tests does not matter.” | “Passing tests is necessary evidence in many workflows, but not sufficient proof of complete correctness.” |

# Final audit conclusion

The original work has the right ambition and many of the right mechanisms. Its most valuable ideas are:

- review affected behaviour, not only changed lines;
- reconstruct intent before judging correctness;
- distinguish changed code from affected code;
- search for missing companion changes;
- use focused review lanes;
- treat tests as evidence rather than an oracle;
- combine semantic reasoning with deterministic and dynamic evidence;
- validate findings adversarially;
- report coverage and uncertainty;
- optimise for proven, actionable findings rather than comment volume.

The corrected report should present those ideas in five evidence classes:

1. **Directly supported:** demonstrated in code-review, PR, testing, or repository-reasoning studies.
2. **Indirectly supported:** demonstrated in adjacent generation, repair, retrieval, or human-review research.
3. **Official engineering guidance:** a documented practice recommendation, not an empirical effect estimate.
4. **Current product behaviour:** established by official documentation but not an efficacy study.
5. **Engineering hypothesis:** a proposed mechanism that must be benchmarked before being treated as a requirement.

That distinction makes the research substantially more trustworthy without weakening the proposed skill. It also gives the future skill an honest evaluation target: prove that each additional stage buys real defect detection, not merely more process and more words.
