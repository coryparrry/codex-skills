# Deep Repo-Wide Code Review for AI-Generated Code: Failure Modes, Evidence, and a Blueprint for an Extremely Strong Review Skill

## Executive findings

The central lesson from the research is that **AI-generated code should not be reviewed as merely “code written by a different author”**. It has a recognisable risk profile. Large language models are exceptionally good at producing locally plausible implementations, but repository-scale correctness depends on things that are often only weakly represented in the immediate coding context: architectural constraints, call-site assumptions, historical design decisions, deployment configuration, persistence semantics, security boundaries, concurrency behaviour, dependency policy, undocumented conventions, and behaviour encoded elsewhere in the repository. Recent repository-understanding research consistently finds that simply giving a model more tokens does not solve this problem; performance can actually deteriorate as irrelevant context grows, while graph- or structure-aware retrieval performs better. citeturn11view2turn2view5turn11view1

That distinction should shape the review system you build. A genuinely deep review is **not “put the whole repository into the context window and ask for bugs”**. It is a controlled investigation that first creates a map of the repository, identifies the behavioural change introduced by the patch, traces the transitive impact of that change through code and non-code artefacts, applies several independent review lenses, executes deterministic and dynamic checks, adversarially challenges the patch, and validates every AI-generated finding before presenting it. Repository-level work increasingly appears to involve two separate failure modes: an agent can fail because it never finds the relevant evidence, or it can find the evidence and still fail to synthesise the correct conclusion. A good review architecture must explicitly defend against both. citeturn2view5turn2view7turn11view2

The strongest design is therefore a **hybrid review system**:

> **LLMs for semantic investigation and hypothesis generation; repository graphs for scope and context; compilers/static analysers for deterministic facts; execution for behavioural evidence; specialised adversarial passes for hidden failure modes; and a final independent validator for every reported finding.**

That direction is also visible in current commercial tooling. GitHub's current Copilot review stack can gather full-project context, but GitHub explicitly warns that it is not guaranteed to identify every problem and should be supplemented by human review. GitHub now combines AI review with deterministic CodeQL-based code-quality analysis, dependency review, test coverage and merge gating rather than treating the language model as a complete reviewer. citeturn10view0turn9search4turn9search1

A second major finding is that **AI-authored pull requests are generally not rejected simply because maintainers dislike AI**. In empirical studies, explicit distrust of AI accounts for only a small fraction of documented rejection decisions. The larger problem is that AI contributions are frequently technically incomplete, test- or CI-breaking, unnecessarily broad, duplicative, misaligned with the requested task, inconsistent with repository contribution rules, or operationally unsuitable. One 2026 study of 600 rejected agent-created PRs found large numbers of abandoned/no-interaction PRs and duplicate PRs alongside CI failures and implementation defects; another study of fix-related AI PRs found incorrect/incomplete fixes, failed tests/builds/deployment, inactivity and fixes superseded by other work. citeturn3view0turn3view4

A third finding is particularly important for your skill: **passing the existing tests is nowhere near sufficient evidence of correctness**. An examination of SWE-bench patches found that some patches counted as benchmark successes still failed developer-written tests, while differential testing revealed behavioural differences between plausible patches and developer ground-truth implementations. Research into AI-generated tests also shows that generated tests can replicate old behavioural assumptions rather than correctly capture changed semantics. citeturn1search4turn6view7

The most important practical consequence is this:

**Your review skill should try to prove that the patch fits the repository, rather than merely trying to find suspicious lines in the patch.**

That means asking questions such as:

*What behaviour was intended? What behaviour actually changed? What else depends on that behaviour? What assumptions did callers make? What invariants existed before? What trust boundaries does the data cross? What happens during failure, cancellation, concurrency, migration and rollback? Did the patch use the repository's intended abstraction or invent another one? Do its tests prove the requirement or merely agree with the implementation? What did the author fail to change?*

Those questions address precisely the categories that repository-level AI systems and conventional diff-centric reviews tend to miss. citeturn2view7turn10view3turn8search2

There is also an important evidence-quality caveat. The human code-review literature includes established controlled and empirical studies, whereas many agent-specific results are necessarily recent 2025–2026 preprints studying rapidly changing tools. Their exact percentages should therefore not be treated as permanent characteristics of “AI”. The more durable findings are the recurring mechanisms: insufficient repository exploration, poor cross-file synthesis, test overfitting, weak handling of implicit requirements, security mistakes, duplicated existing functionality, failure to obey repository process, and an unfavourable precision/recall trade-off when AI reviewers are pushed to report everything. citeturn2view6turn11view3turn6view5

## The AI failure taxonomy

AI mistakes are best divided into **local implementation errors, repository-integration errors, behavioural/specification errors and verification errors**. The last three are the ones a normal “look at the diff” review is least equipped to catch.

| Failure mode | What it looks like in real code | Why it matters | Evidence |
|---|---|---|---|
| **Locally correct, globally wrong** | Function works by itself but violates assumptions in callers, sibling implementations or lifecycle flows | Tests scoped to the modified function may pass while the application fails elsewhere | Repository benchmarks show dependency context and multi-hop repository understanding materially affect correctness. citeturn2view7turn11view2 |
| **Reimplements an existing abstraction** | New parser/helper/client/cache/retry wrapper rather than using a repository utility | Creates duplicated behaviour, maintenance cost and subtly different semantics | RepoExec found models can produce functionally successful code while failing to use existing repository dependencies appropriately. citeturn2view7 |
| **Incomplete fix** | Visible symptom is corrected, root cause or another code path remains | Particularly common when issue text describes symptoms rather than invariant/expected behaviour | Incorrect or incomplete implementations are recurring reasons AI fix PRs remain unmerged. citeturn3view0turn3view4 |
| **Test overfitting** | Patch satisfies visible tests but does not reproduce intended behaviour more generally | Existing tests are only a sample of the specification | SWE-bench re-evaluation found apparently successful patches that failed developer tests or differed behaviourally under differential testing. citeturn1search4 |
| **Incorrect test oracle** | AI writes a test that passes because its expected output reflects its own implementation rather than the intended requirement | Produces a dangerous appearance of verification | Under semantic code changes, AI-generated tests showed substantial degradation and often retained assumptions consistent with the original programme. citeturn6view7 |
| **Happy-path bias** | Success path works; timeout, malformed input, cancellation, partial failure and recovery do not | Production failures disproportionately occur outside clean success paths | Security and coding studies repeatedly find vulnerable or defective generations despite apparently functional outputs. citeturn6view4turn6view5 |
| **Broad or inappropriate exception handling** | `except Exception`, swallowed exceptions, generic fallback behaviour | Hides defects and changes failure semantics | In a large study of verified AI-authored commits, broad exception handling was one of the most frequent detected problems. citeturn6view0 |
| **Unused/scaffolding artefacts** | Unused variables, parameters, imports, dead helper code, unfinished framework pieces | Often signals incomplete reasoning or abandoned implementation paths | Large-scale static analysis of AI-authored commits found unused variables/parameters among the dominant issue classes. citeturn6view0 |
| **Undefined/runtime reference errors** | Wrong symbol, missing import, variable used before assignment | Plausible-looking syntax hides basic runtime failures | Large-scale AI-commit analysis found undefined references and use-before-assignment defects; another multi-model study identified missing imports as a recurring correctable generation error. citeturn6view0turn6view2 |
| **Security regression** | Injection, traversal, unsafe deserialisation, weak validation, auth boundary mistakes | Generated code often follows plausible patterns without modelling attacker-controlled flows | Security studies have repeatedly found meaningful vulnerability rates in AI-generated code, and security-related AI PRs showed injection/path traversal and other weaknesses. citeturn6view4turn3view5turn4search28 |
| **Vulnerable “fix”** | Patch repairs the requested defect while introducing a new security weakness | The reviewer is psychologically focused on the original bug | A SWE-bench security analysis found LLM-generated fixes could introduce substantially more new vulnerabilities than developer patches, particularly as patch size and ambiguity increased. citeturn6view5 |
| **Hallucinated dependency/API** | Invented package name, nonexistent method, wrong version, obsolete API | Can cause build failures and, with nonexistent package names, supply-chain exposure | Package-hallucination research documents nonexistent dependencies and the resulting “slopsquatting” attack surface. citeturn4search4turn4search8turn4search12 |
| **Architecture violation** | Dependency flows backwards, service boundaries are crossed, layer responsibilities blur | Local code can compile while degrading the system structure | Repository-level research finds architectural dependency and invariant understanding remains difficult even for strong code agents. citeturn11view1turn11view2 |
| **Scope creep** | Bug fix includes cleanup, renames, refactoring and unrelated behaviour changes | Enlarges the verification space and increases review uncertainty | Rejected agentic PRs tend to be larger, touch more files and undergo more reviewer revision; maintainers favour small coherent changes. citeturn3view0 |
| **Configuration blindness** | Code is updated but CI, feature flag, manifest, policy, deployment or environment configuration is not | Runtime/deployment behaviour differs from local tests | Build, CI and deployment failures appear repeatedly in analyses of unmerged AI PRs. citeturn3view0turn3view4 |
| **Repository-policy violation** | Code works but violates contribution, verification, disclosure or workflow requirements | May result in a desk rejection before technical merits matter | A 2026 study found coding agents rarely proactively read repository AI-contribution rules and struggled especially with refusal/handoff requirements. citeturn11view3 |
| **Non-code omission** | Implementation changes but migration, docs, API definition, generated artefact, lockfile or deployment file does not | The missing part is absent from the diff, so diff review has nothing obvious to inspect | Google's engineering review guidance explicitly recommends considering the surrounding system rather than reviewing only the changed lines; current GitHub AI review also excludes some dependency-management artefacts, making separate review necessary. citeturn10view3turn10view0 |
| **Excessive complexity** | Abstraction, generic layer or factory added where a direct solution would suffice | Increases future defect surface and maintenance burden | Studies of generated Python classify maintainability, readability and unnecessary complexity among recurring inefficiencies, frequently co-occurring with logic/performance issues. citeturn6view1 |
| **Performance regression hidden by functional tests** | N+1 calls, repeated scans, unbounded collection, blocking I/O, wasteful allocation | Functional tests establish output, not operational cost | Performance-oriented AI PRs show relatively poor acceptance in empirical agentic-PR data, while generated-code studies identify performance inefficiency as a prominent category. citeturn3view0turn6view1 |
| **Incorrect comment or rationale** | Comment confidently explains behaviour that the code does not guarantee | Future maintainers may trust prose more than implementation | This is a general consequence of generation without execution evidence; self-generated hints have been observed to be irrelevant or incorrect in vulnerability-repair experiments. citeturn6view4 |
| **False-positive review finding** | Reviewer invents a bug, assumes a call path is reachable or misunderstands a framework guarantee | AI review itself can waste maintainer time and cause regressions | CR-Bench identifies a fundamental precision/recall trade-off: driving review agents to find more defects can substantially increase spurious comments. citeturn2view6 |
| **Self-review confirmation** | Same model re-reads its implementation but retains the same incorrect assumption | Independent-looking review is not necessarily independent reasoning | Cross-model review experiments find that second-pass review can improve some outputs but can also make already-correct output worse; effects depend strongly on reviewer/author combination. citeturn11view0 |

The large-scale “Debt Behind the AI Boom” study is especially useful because it studied code **in real GitHub repositories**, not merely benchmark snippets. Across more than 300,000 verified AI-authored commits, its static-analysis pipeline identified hundreds of thousands of introduced issues; **code smells represented 89.1% of the issues it identified**, and roughly a quarter of tracked AI-introduced issues remained in the latest code revision. Broad exception handling, unused variables and parameters, shadowing, protected-member access and undefined references were prominent classes. These findings do not mean AI is uniquely responsible for such mistakes—humans produce the same classes—but they give you high-value AI-review signatures to inspect deliberately. citeturn6view0

Security needs its own category rather than being folded into “correctness”. Controlled and repository-based studies show that models can generate vulnerable implementations even when they produce syntactically valid and functionally convincing code. In one user study, developers assisted by AI produced insecure solutions more often on most of the security tasks examined while also tending to believe their AI-assisted solutions were secure. Other empirical studies of Copilot-generated GitHub snippets have found security weaknesses spanning dozens of CWE categories. citeturn4search2turn4search28

A particularly dangerous mistake is **changing the test to agree with the code**. The patch can become self-validating:

```text
Requirement
   ↓
AI interprets requirement incorrectly
   ↓
AI writes implementation from that interpretation
   ↓
AI writes tests from the SAME interpretation
   ↓
Implementation and tests agree
   ↓
CI is green
   ↓
Actual requirement is still violated
```

This is not merely theoretical. Research on LLM-generated tests under software evolution found that semantic changes significantly reduce generated-test success and branch coverage, with evidence that many generated tests preserve behavioural assumptions from the old implementation. Separately, differential testing of supposedly solved SWE-bench issues found behaviour that diverged from developer solutions despite benchmark acceptance. citeturn6view7turn1search4

Your skill should therefore treat **“implementation and new test agree” as weak evidence**. Strong evidence is triangulated: requirement or invariant + implementation + pre-existing behaviour + independent test or execution all agree.

## Why these failures happen at repository scale

The deepest underlying problem is **local plausibility versus global constraint satisfaction**.

A language model is very good at answering:

> “Given this function, nearby files and this request, what code usually belongs here?”

A mature repository actually requires an answer to a much harder question:

> “What change satisfies the user's intended behaviour while preserving every relevant architectural, behavioural, security, compatibility, operational and historical invariant elsewhere in the system?”

Repository benchmarks increasingly demonstrate this gap. RepoExec found that full dependency context improves generated-code performance and that models may produce functionally correct implementations while failing to reuse appropriate repository dependencies. SWE-Explore separates repository-agent failure into exploration failure and synthesis failure: some agents never retrieve the evidence they require, while others retrieve it and still fail to reason correctly across it. citeturn2view7turn2view5

More context is not a complete solution. Recent repository-QA work reports that accuracy can deteriorate as the context window fills with irrelevant material; relevant code may technically be “inside the prompt” yet fail to receive sufficient attention. Structure-aware retrieval based on repository relationships performs more consistently than simply flattening files into a long context. citeturn11view2

That suggests your skill needs to maintain an explicit **architectural belief state**, rather than repeatedly searching files without memory. A 2026 architecture-understanding benchmark similarly argues that agents need explicit models of components, dependencies, exports, constraints and invariants. Even strong agents demonstrated only partial architectural understanding, particularly around constraints that have to be inferred across components. citeturn11view1

The review should therefore construct something conceptually like:

```text
Repository
├── components/modules
├── entry points
├── public interfaces
├── internal dependency edges
├── data stores and schemas
├── external systems
├── trust boundaries
├── ownership boundaries
├── lifecycle/state transitions
├── build and deployment paths
├── test-to-production relationships
└── known invariants + uncertainties
```

The important addition is **uncertainties**. A reviewer that cannot explain an architectural relationship should not silently assume it. It should mark that relationship unresolved and investigate it.

A second cause is **underspecified intent**. Issue descriptions frequently describe an observable symptom rather than all of the behaviour that must remain valid. Security research on generated fixes found worse vulnerability outcomes as changes became larger and issue descriptions became less concrete. Empirical studies of AI PRs likewise find incomplete and incorrect fixes among causes of non-merging. citeturn6view5turn3view4

The implication is that the reviewer should reconstruct the specification from multiple sources:

```text
Issue / ticket
        +
existing behaviour
        +
tests
        +
callers
        +
API contracts
        +
documentation
        +
historical commits/reverts
        +
repository conventions
        =
working behavioural specification
```

Tests must be only **one** input to that reconstruction.

A third cause is **pattern completion using priors that are almost, but not exactly, applicable**. This produces wrong package names, stale APIs, plausible framework calls, generic exception handling and code that resembles standard solutions but violates repository-specific conventions. Package hallucination studies and function-level error taxonomies provide direct examples, while repository-level dependency studies show a broader version of the problem: AI may ignore an existing project abstraction and independently recreate approximately the same behaviour. citeturn4search4turn6view2turn2view7

A fourth cause is **verification coupling**. When the same model generates the implementation, tests and subsequent self-review, all three can share the same faulty latent assumption. Security-repair research finds that providing concrete vulnerability information improves model repairs more reliably than having the model invent its own security hints; self-generated guidance can itself be wrong. Cross-model review experiments likewise show that a second reviewer can help, but not universally: a reviewer can also degrade good code. citeturn6view4turn11view0

That is why simply adding this instruction is insufficient:

> “Now carefully review your work and fix every issue.”

Your architecture should create **epistemic independence** between stages. The implementation interpretation should not automatically become the test oracle, and the reviewer's first hypothesis should not automatically become a reported defect.

A fifth cause is **salience**. Humans suffer from this too. When reviewing a bug fix, the obvious task consumes attention, making unrelated security, lifecycle and architectural properties easier to overlook. A controlled study of security-focused code review found that merely telling reviewers to focus specifically on security caused a very large increase in vulnerability detection; adding a checklist on top did not provide a similarly clear additional benefit. That suggests the mental **review lens itself** matters greatly. citeturn8search0turn8search7

This has a major design consequence:

**Do not build one enormous “check everything” prompt.**

Build distinct passes whose sole jobs are:

```text
Correctness
Architecture
Security
State & concurrency
Data & compatibility
Reliability
Performance
Testing
Dependencies & supply chain
Operations & deployment
Maintainability
```

Each reviewer should temporarily behave as if its category is the only important thing in the repository. That produces a different attention distribution than giving a single model a 150-item checklist.

There is also current product-level evidence against giant instruction documents. GitHub's guidance for Copilot custom instructions recommends short, focused and specific instruction sets, warns that very long files may cause instructions to be overlooked, and suggests starting with a limited set of instructions and iterating against real PR behaviour. citeturn10view1

Finally, AI introduces a **calibration problem**. Fluent output feels completed even when verification remains outstanding. An influential METR randomised study of experienced developers working in repositories they knew well found that developers expected AI to make them substantially faster and still perceived a speed-up after using it, while measured completion time in that early-2025 experiment was actually higher with AI. The result should not be generalised to all 2026 tools—METR's follow-on evidence shows the landscape moving—but it demonstrates that subjective confidence and productivity can be poorly calibrated to objective outcomes. citeturn12search1turn12search2

The code-review analogue is straightforward: **“this looks professional” and “the model seems confident” must contribute zero evidence to the final verdict.**

## Why AI-authored PRs are rejected — and what conventional review misses

One of the most useful findings from the GitHub research is that **“AI PR rejected” does not equal “AI code was bad.”** Rejection occurs at several different layers.

A 2026 empirical study manually analysed 600 rejected agentic pull requests. The largest category was reviewer abandonment/no meaningful human interaction, with 228 cases. Duplicate PRs accounted for 142 cases. Among more technical reasons were 99 CI/test failures, 19 incorrect implementations, 15 incomplete implementations, nine cases of misalignment with reviewer instructions, and smaller numbers involving licence issues, setup-only changes, wrong task descriptions or wrong target branches. citeturn3view0

Another 2026 study specifically examining closed-but-unmerged fix-related AI PRs found incorrect/incomplete fixes, failed tests, build and deployment failures, low-priority or obsolete fixes, inactivity, incomplete review and fixes superseded by other work. The distribution also varied considerably by agent, demonstrating that “AI PR failure” is not a single technical phenomenon. citeturn3view4

A large security-focused study of more than 33,000 identified AI-generated PRs examined 219 rejected security-related contributions. Among PRs for which a reason could be determined, reasons included introducing bugs or breaking APIs, poor design, inadequate value, test failures or insufficient coverage, style/formatting, implementation by another contributor and lack of community interest. Only **1.8% of the manually classified rejected security PRs were attributed to explicit distrust of AI-written code**. Another study of Claude Code contributions similarly found explicit AI distrust in only a small minority of rejected contributions. These figures are dataset-specific, but they argue strongly against assuming that maintainers reject AI contributions primarily because they are AI-generated. citeturn3view5turn2view2

The practical lesson is that your skill should review **mergeability**, not merely code quality.

A PR can contain correct source code and still be unacceptable because it:

| Merge risk | What a deep reviewer should investigate |
|---|---|
| Solves the wrong problem | Compare issue intent, tests, reproduction and actual changed behaviour |
| Duplicates existing work | Search open/closed PRs, TODOs, neighbouring implementations and recent history |
| Is too broad | Determine whether every touched file is required by the requested behaviour |
| Breaks CI/build | Reproduce the actual repository build and CI-relevant commands |
| Breaks deployment | Inspect packaging, images, IaC, manifests, migrations and environment requirements |
| Violates contribution rules | Read `CONTRIBUTING`, `AGENTS.md`, repository instructions, CODEOWNERS and workflow policy |
| Breaks an API | Trace all call sites and externally observable contracts |
| Has weak tests | Evaluate the oracle, negative cases and whether tests would fail for realistic incorrect implementations |
| Adds unjustified dependency | Verify package existence, version, licence, maintenance, lockfile and whether an existing dependency suffices |
| Creates maintenance burden | Detect duplicate abstractions, unnecessary complexity and divergence from local conventions |

Those categories reflect the recurring coordination, correctness and integration failures found in the empirical AI-PR literature. citeturn3view0turn3view4turn11view3

The other half of the problem is **what ordinary reviews miss before merge**.

Conventional review tends to be diff-centric. Google's own engineering review guidance explicitly tells reviewers to consider design and functionality, think about user impact and edge cases, inspect concurrency where relevant, question unnecessary complexity, review tests rather than simply trusting that tests exist, and read the surrounding file/system rather than only the modified lines. citeturn10view3

Security research shows why this matters. A Chromium OS case-control study found that vulnerabilities requiring comparatively little context were more likely to be identified during review, while defects requiring broader context or execution reasoning—including areas such as input validation, resource lifetime and authorisation management—were more likely to escape. Detection probability also declined as defects spanned more files/directories. citeturn8search2

That means **cross-file defects are exactly where a deep skill can add the most value**.

A normal review can easily see this:

```diff
- timeout = 10
+ timeout = config.timeout
```

A deep review asks:

```text
Where is config.timeout populated?
What happens if it is unset?
What units does the caller expect?
Can it be zero or negative?
Does the serialization format change?
Does every deployment populate the value?
Does a default exist in Helm/Terraform/Docker/environment config?
Do retry loops multiply this timeout?
Does cancellation still interrupt the operation?
Could this now become unbounded?
Are documentation and sample config correct?
```

Most of those questions concern files **not in the patch**.

The same applies to function signatures. Suppose AI changes:

```python
def fetch_user(user_id: str) -> User | None:
```

to:

```python
async def fetch_user(user_id: str) -> User | None:
```

A shallow review verifies that the implementation awaits the network request.

A repository-wide review asks:

```text
Every caller?
Indirect callbacks?
Interface/protocol implementations?
Mocks?
Test fixtures?
Command handlers?
Framework registration?
Thread/event-loop ownership?
Cancellation semantics?
Transactions spanning the call?
Latency behaviour?
Public API compatibility?
Generated clients?
```

The defect may exist twenty files away from the changed function.

Tests are another major blind spot. Google's guidance explicitly notes that tests themselves need review; they do not validate their own correctness. Research comparing test-code review patterns also suggests that automated CI does not eliminate the need for thoughtful test inspection and may shift reviewer attention towards more superficial concerns. citeturn10view3turn7search5

AI makes that particularly important because **the new test may be part of the bug**. Your skill should ask:

> “Would this test reject a realistic wrong implementation?”

rather than:

> “Does the test pass?”

For a bug fix, deliberately construct an alternative implementation that contains the suspected bug. If the new test still passes, the test does not prove the fix.

There is another blind spot in modern AI review systems themselves: **file exclusions and separate tool domains**. GitHub's current Copilot code-review documentation states that certain file types and dependency-management files are excluded from Copilot review, while GitHub provides separate dependency-review functionality for dependency changes. Therefore “Copilot reviewed this PR” does not logically mean all repository artefacts relevant to the PR received equivalent analysis. citeturn10view0turn9search1

Your skill should explicitly review artefacts that source-oriented reviewers commonly underweight:

```text
package manifests and lockfiles
database migrations
schemas
OpenAPI/GraphQL/protobuf definitions
CI workflows
Dockerfiles
Kubernetes manifests
Terraform/CloudFormation
feature flags
environment examples
permissions/policy files
CODEOWNERS
generated-code inputs
serialization formats
cache keys
logging/metrics/tracing
documentation containing behavioural contracts
```

That list is an engineering inference from the evidence above: repository-level correctness includes build/deployment/configuration and cross-file behaviour, whereas current AI review products themselves separate or exclude some of these artefacts. citeturn3view4turn10view0turn10view3

## Evidence-based principles for a much stronger review

The research points towards several design principles that should be treated as non-negotiable.

**First: review the change as a graph, not a diff.**

Start from every changed symbol and traverse relationships in both directions:

```text
                     callers
                       ↑
tests ← interface ← CHANGED SYMBOL → callees → external dependency
                       ↓
                 schema / state
                       ↓
             config / deployment
```

For each changed symbol, retrieve callers, callees, implementations of the same interface, sibling implementations, tests, configuration, data definitions and public consumers. Structure-aware retrieval is supported by repository-QA research, and dependency context has been shown to improve repository-level generation. citeturn11view2turn2view7

**Second: distinguish discovery from judgement.**

SWE-Explore's separation of exploration and synthesis suggests a strong architecture:

```text
Discovery agent
    ↓
collects evidence only
    ↓
Reasoning agent
    ↓
forms hypotheses
    ↓
Validation agent + tools
    ↓
attempts to falsify hypotheses
    ↓
Reporter
```

Do not have one free-running model search, decide, repair and report everything in the same stream. That makes it difficult to distinguish “I could not find evidence” from “I found evidence that the defect does not exist”. citeturn2view5

**Third: use specialised review passes rather than an enormous checklist.**

The security-review experiment in which explicit security focus dramatically improved vulnerability identification is compelling evidence that reviewer attention is task-sensitive. Combined with current guidance that very long AI instruction files may be overlooked, this favours small specialised review lenses orchestrated by a core controller. citeturn8search0turn10view1

A strong set is:

| Lens | Questions that should dominate the pass |
|---|---|
| **Specification and correctness** | Does every behaviour match the reconstructed requirement? What edge and negative cases differ? |
| **Architecture** | Does the patch respect layering, ownership and dependency direction? Did it bypass an existing abstraction? |
| **Security** | What input is attacker controlled? Where are trust boundaries? Can authentication, authorisation or tenant isolation be bypassed? |
| **State and concurrency** | What invariants must hold across transactions, threads/tasks and retries? What can race? |
| **Data and compatibility** | Are schemas, serialisation, migrations and public APIs backward/forward compatible? |
| **Reliability** | What happens on timeout, cancellation, partial failure, restart and retry? Is the operation idempotent? |
| **Performance** | What changed in asymptotic work, database round trips, network calls, allocation, locking and caching? |
| **Tests** | Is the oracle independent? What bug would make this test fail? What realistic bug would still pass? |
| **Dependencies** | Is every new package real, necessary, supported, compatible and acceptable under project policy/licensing? |
| **Operations** | Does deployment/config/observability/rollback still work? |
| **Maintainability** | Did AI duplicate code, over-generalise, add dead scaffolding or increase conceptual complexity? |

The categories correspond to defect patterns documented in AI-generation, security, repository-level reasoning and human-review research. citeturn6view0turn6view1turn6view5turn8search2

**Fourth: separate deterministic questions from semantic questions.**

Do not spend expensive probabilistic reasoning on questions that tools can answer exactly.

```text
Compiler/type checker      → Does this type-check?
Linter                      → Does it violate mechanical conventions?
CodeQL/static analysis      → Does it match known vulnerability/quality patterns?
Dependency scanner          → Is this dependency vulnerable?
Package registry/lockfile   → Does the dependency/version actually exist?
Test runner                 → Does observed behaviour pass this test?
Coverage                    → What code executed?
Mutation testing            → Do tests distinguish broken implementations?
Git                         → What did this code previously do?
AST/call graph              → Who calls this symbol?
LLM                         → What does the evidence mean?
```

GitHub's current product design follows the same broad principle by pairing AI review with deterministic CodeQL-based quality/security analysis and separate dependency review. citeturn0search7turn9search4turn9search1

**Fifth: test behaviour adversarially, not merely positively.**

For code in the affected execution paths, the skill should automatically consider the following classes when applicable:

| Adversarial dimension | Examples |
|---|---|
| Input boundaries | empty, zero, negative, maximum, huge, Unicode, malformed |
| Security | traversal, injection, unexpected encoding, forged identifier, tenant crossover |
| Timing | timeout, cancellation, slow dependency, clock skew, expiry boundary |
| Concurrency | duplicate request, interleaving, race, simultaneous update |
| Failure | partial write, downstream 500, connection reset, restart midway |
| Retry | duplicated side effect, replay, non-idempotent operation |
| Persistence | old schema/new binary, new schema/old binary, rollback |
| Resource behaviour | leaks, unbounded loop/queue/memory, file/socket cleanup |
| Ordering | out-of-order messages, repeated events, stale version |
| Configuration | unset, invalid, default, old deployment config |

Security-fix studies show that unclear requirements and broader changes correlate with higher vulnerability risk, while human review research finds that execution- and context-dependent defects are harder to spot. citeturn6view5turn8search2

**Sixth: make test quality a first-class review target.**

A high-quality test should satisfy more than coverage. The review should evaluate:

```text
Does the test fail before the patch?
Does it pass after the patch?
Does the assertion reflect an independent requirement?
Does it exercise the actual production path?
Would a realistic broken implementation make it fail?
Are failure and boundary cases represented?
Are mocks hiding the integration that actually broke?
Has the implementation been changed merely to satisfy a brittle test?
Did the patch remove/weaken/skip any existing assertion?
```

Passing visible tests is insufficient, as demonstrated by SWE-bench re-evaluation and generated-test studies. Mutation testing, differential testing and property-based/metamorphic checks are particularly useful because they challenge whether the test suite distinguishes meaningful behavioural differences rather than merely achieving line coverage. citeturn1search4turn6view7turn4search11

**Seventh: deliberately examine history.**

Current code is often incomprehensible without understanding *why* it is strange. A deep reviewer should inspect `git blame` and relevant history around changed code, especially when it encounters apparently redundant validation, unusual ordering, duplicated-looking branches or seemingly unnecessary compatibility code. Repository understanding includes design rationale and lifecycle flows that may require multi-hop evidence rather than syntax alone. citeturn5search24turn11view2

Useful historical questions include:

```text
Was similar code previously reverted?
Was this guard added after an incident?
Has this component had security fixes before?
Was this abstraction created specifically to avoid a previous bug?
Did an earlier migration establish a compatibility constraint?
Are there TODOs explaining an incomplete transition?
Did a prior PR deliberately reject the approach AI is now reintroducing?
```

This is one of the areas in which an automated review can go materially deeper than a rushed human diff review because repository search and history traversal can be systematic.

**Eighth: do not automatically trust a second AI reviewer.**

An independent critic is valuable, but recent cross-model evidence shows strongly asymmetric results: one model reviewing another can significantly improve results in some pairings while making good output worse in others. CR-Bench likewise shows that greater recall can come at the cost of review noise. citeturn11view0turn2view6

Therefore:

```text
Reviewer discovers potential defect
           ↓
Validator tries to disprove it
           ↓
tool/execution evidence where possible
           ↓
only then report it
```

The validator should be asked:

> “Assume this finding is wrong. Locate evidence that would invalidate it.”

That is materially better than:

> “Is the review correct?”

The second wording encourages agreement; the first encourages falsification.

**Ninth: require evidence for every finding.**

An AI reviewer should be forbidden from reporting statements such as:

> “This may cause race conditions.”

without explaining:

```text
Shared state:         X
Writer:               file/function A
Concurrent writer:    file/function B
Missing synchroniser: Y
Reachable execution:  Z
Failure interleaving: …
Impact:               …
Evidence/confidence:  …
```

Likewise, a security finding should contain the attacker-controlled source, transformation, sink, guard and exploit preconditions. A performance finding should name the changed cost model. A compatibility finding should name the consumer whose expectation changed.

This requirement directly attacks the precision problem identified by CR-Bench. citeturn2view6

## Blueprint for an extreme repo-wide review skill

The skill I would build is **an orchestrator, not a monolithic reviewer**.

Its internal pipeline should look approximately like this:

```text
                   ┌─────────────────────┐
                   │  Change / PR / SHA  │
                   └──────────┬──────────┘
                              ↓
                   ┌─────────────────────┐
                   │ Repository rules    │
                   │ & intent discovery  │
                   └──────────┬──────────┘
                              ↓
                   ┌─────────────────────┐
                   │ Architecture map    │
                   │ + dependency graph  │
                   └──────────┬──────────┘
                              ↓
                   ┌─────────────────────┐
                   │ Diff → impact graph │
                   └──────────┬──────────┘
                              ↓
       ┌──────────────────────┼─────────────────────────┐
       ↓                      ↓                         ↓
 Correctness            Security/state          Architecture/API
       ↓                      ↓                         ↓
       ├─────────── specialised review passes ─────────┤
       ↓                      ↓                         ↓
 Tests/perf            Dependencies             Ops/reliability
       └──────────────────────┬─────────────────────────┘
                              ↓
                   ┌─────────────────────┐
                   │ Deterministic tools │
                   │ + execution/fuzzing │
                   └──────────┬──────────┘
                              ↓
                   ┌─────────────────────┐
                   │ Adversarial finding │
                   │ validation          │
                   └──────────┬──────────┘
                              ↓
                   ┌─────────────────────┐
                   │ Coverage + risk     │
                   │ ledger              │
                   └──────────┬──────────┘
                              ↓
                   ┌─────────────────────┐
                   │ Evidence-backed     │
                   │ final review        │
                   └─────────────────────┘
```

That architecture follows the empirical distinction between repository exploration and synthesis, the advantage of structure-aware retrieval, the benefit of dedicated review focus, and the precision/recall problem observed in code-review agents. citeturn2view5turn11view2turn8search0turn2view6

The operational phases should be as follows.

| Phase | The skill must do | Required output before moving on |
|---|---|---|
| **Repository policy discovery** | Read repository-level and path-specific instructions; `README`, `CONTRIBUTING`, `AGENTS.md`, code-owner rules, security policy, CI definitions, lint/build/test configuration and relevant ADRs | Repository rules and commands; unresolved policy questions |
| **Intent reconstruction** | Read issue/PR description, changed tests, documentation, related code and reproduction information; compare base/head behaviour | Explicit intended behaviour and preserved invariants |
| **Repository mapping** | Identify components, entry points, boundaries, important dependencies, storage, APIs, test layout, build/deploy path | Compact architecture map |
| **Change classification** | Categorise each modified file/symbol by behavioural role | Change inventory |
| **Impact expansion** | Traverse callers, callees, interfaces, siblings, consumers, schemas, config, tests, external contracts | Impact graph |
| **Risk calculation** | Elevate changes touching auth, money, permissions, persistence, concurrency, external API, schema, dependency/build or many modules | Review-depth decision |
| **Specialised lenses** | Run independent correctness, security, architecture, concurrency/state, data/API, reliability, performance, test, dependency and ops reviews | Candidate findings with evidence |
| **Deterministic validation** | Build, lint, type-check, static analyse, dependency-scan, secret-scan and execute appropriate tests | Tool evidence |
| **Behavioural challenge** | Negative tests, property tests, fuzzing, differential tests, mutation tests, concurrency/race checks where appropriate | Behavioural evidence |
| **Finding falsification** | A separate critic attempts to disprove every candidate issue | Validated/suppressed findings |
| **Coverage accounting** | Record changed files, impacted files inspected, paths tested, artefacts excluded and unresolved assumptions | Review coverage ledger |
| **Final reporting** | Report only useful, evidence-backed issues; separate blockers from uncertainty | Actionable review |

The policy-discovery phase is more important than it might appear. A 2026 study of AI-contribution rules found agents proactively opened non-automatic repository rule files in only a very small proportion of unaided runs, and compliance problems persisted particularly around workflow/refusal/handoff requirements. Your skill should therefore make repository-instruction discovery **deterministic and mandatory**, not something the model remembers to do when convenient. citeturn11view3

The skill should also explicitly look for **AI fingerprints**, not because they prove AI authorship, but because the research identifies them as useful high-risk patterns:

```text
broad exception handling
unused scaffolding
invented or unnecessary dependency
duplicate implementation of repository utility
new abstraction with one consumer
placeholder/TODO behaviour
tests mirroring implementation too closely
tests weakened to make a fix pass
hard-coded fallback
silent error swallowing
missing configuration counterpart
old/deprecated API usage
large unrelated cleanup in a small bug fix
comments asserting behaviour not established by code
new mock that bypasses the integration being changed
hand-written protocol/schema logic that already exists elsewhere
```

Broad exception handling and unused code are prominent in large-scale AI-code analysis; dependency hallucination has direct empirical support; and repository benchmarks specifically identify failure to use existing project dependencies as a meaningful quality defect beyond functional correctness. citeturn6view0turn4search4turn2view7

The impact-expansion engine is arguably the most important technical component. For **every changed public or internally shared symbol**, the reviewer should expand outward until either a boundary is proven safe or the path reaches a known terminal.

For example:

```text
changed DB model
   ↓
migration
   ↓
repository/DAO
   ↓
service
   ↓
API serializer
   ↓
API contract
   ↓
client
   ↓
cache
   ↓
background job
   ↓
observability/reporting
```

The review should not stop because the changed model's unit tests pass.

Likewise:

```text
changed permission helper
   ↓
all callers
   ↓
every entry point reaching each caller
   ↓
authentication state available at those points
   ↓
tenant/resource ownership check
   ↓
error behaviour
   ↓
audit trail
```

This is specifically the kind of large-context authorisation reasoning human review research has found difficult, and architecture-oriented agent research identifies cross-component invariants as a continuing challenge. citeturn8search2turn11view1

A useful conceptual distinction is **changed code versus affected code**.

```text
Changed code  = files in the diff
Affected code = everything whose assumptions may no longer hold
```

Your reviewer should optimise for the second set.

The skill also needs a **change-omission detector**. Most code-review systems ask, “What is wrong with what changed?” A much deeper question is:

> **“Given this change, what should probably also have changed but did not?”**

Examples include:

```text
new environment variable     → sample config / deployment values / docs
new database column          → migration / rollback / serializer / fixtures
new enum value               → exhaustive consumers / persistence / frontend
new API field                → schema / clients / compatibility tests
new dependency               → lockfile / licence / build image / SBOM
new metric                   → dashboards/alerts where project practice requires it
new feature flag             → default / rollout / removal plan
changed auth rule            → all entry points / tests / audit behaviour
changed timeout              → retries / callers / configuration
changed error type           → catch sites / HTTP translation / telemetry
renamed event                → publishers / consumers / replay compatibility
```

This is an inference from repository-level and cross-file review evidence rather than a published fixed checklist, but it directly addresses the reason diff-only review is structurally incomplete. citeturn10view3turn11view2turn8search2

The review should maintain a **coverage ledger** so that “deep review” becomes auditable.

A final report might say:

```text
Changed files inspected:           17 / 17
Changed symbols inspected:         43 / 43
Directly dependent files traced:   61
Critical transitive paths traced:  auth, checkout, webhook retry
Relevant test suites executed:     8
Static/security analyses:          CodeQL, typecheck, dependency scan
Schema/migration artefacts:        inspected
Deployment/config artefacts:       inspected
History examined:                  9 relevant commits, 2 prior reverts

Unresolved:
- downstream behaviour of vendor SDK X cannot be verified locally
- production-only feature flag configuration unavailable
```

That is much stronger than an AI stating:

> “I reviewed the repository thoroughly.”

The first is an evidence claim. The second is rhetoric.

The skill's findings should also use a strict schema. For example:

```text
Severity:
Confidence:
Category:

Claim:
Impact:

Evidence:
- file/symbol
- relevant call/data path
- repository invariant that is violated

Trigger/preconditions:

Reproduction or failing test:
[command or minimal scenario]

Why existing tests miss it:

Suggested remediation:

Validation:
- compiler/static result
- dynamic result
- independent reviewer result

Remaining uncertainty:
```

Severity and confidence should remain separate. A potentially catastrophic authentication defect with uncertain reachability is **high severity / lower confidence**, not automatically a blocker. A trivially reproducible data-loss path is **high severity / high confidence**.

For security findings, add:

```text
source → transforms → security control → sink
attacker capability
required privilege
cross-tenant impact
reachability
```

For concurrency findings:

```text
state
operation A
operation B
interleaving
expected invariant
actual invariant violation
synchronisation present/absent
```

For performance:

```text
before complexity/calls
after complexity/calls
input scaling dimension
production-relevant trigger
measured or reasoned impact
```

This forces the model away from vague “could be a problem” reviews, which is important because code-review-agent benchmarks show the cost of low precision and excessive comments. citeturn2view6

The core orchestrator instruction itself should remain compact. Rather than a giant skill file containing every rule, I would structure it approximately as:

```text
deep-review/
    SKILL.md                    # orchestration and non-negotiables
    repo-discovery.md
    architecture-review.md
    correctness-review.md
    security-review.md
    state-concurrency-review.md
    api-data-review.md
    test-review.md
    dependency-review.md
    performance-review.md
    reliability-review.md
    operations-review.md
    finding-validator.md
```

The orchestrator loads only relevant specialist instructions after the risk map is established. That fits current evidence that focused review attention works better than undifferentiated attention and current GitHub guidance that overly long instruction sets can be overlooked. citeturn8search0turn10view1

A good `SKILL.md` would have non-negotiables similar to:

```text
MISSION

Determine whether the proposed change is safe and appropriate for this
repository, not merely whether the changed lines look correct.

NON-NEGOTIABLE RULES

1. Never review only the diff.
2. Discover repository rules before judging the implementation.
3. Reconstruct intended behaviour before testing correctness.
4. Build an impact graph from changed symbols.
5. Inspect affected code even when it is outside the diff.
6. Treat tests as evidence, never as the specification.
7. Validate deterministic claims with deterministic tools.
8. Run independent security, architecture and test-quality passes.
9. Search for required-but-missing companion changes.
10. Attempt to falsify every finding before reporting it.
11. Never report a defect without evidence and a plausible execution path.
12. State all unresolved uncertainty.
13. Produce a coverage ledger.
14. Prefer a few proven findings over many speculative comments.
15. Never alter code merely to satisfy the reviewer without proving the
    resulting behaviour against the repository's intended contract.
```

The principles in this contract are supported collectively by repository-level retrieval research, human code-review evidence, AI-code defect studies, modern review benchmarks and current GitHub review guidance. citeturn11view2turn8search0turn6view0turn2view6turn10view0

One additional feature could make this unusually strong: **counterfactual review**.

For each significant AI-authored design decision, ask:

> “What would a competent maintainer of this repository have reused instead?”

Then search for that thing.

If AI writes:

```python
for attempt in range(3):
    try:
        ...
```

search for the repository's retry abstraction.

If it creates:

```python
class NewJSONEncoder:
```

search existing serialisation policy.

If it performs:

```python
if user.role == "admin":
```

search the actual permission framework.

If it opens a transaction directly, search the application's transaction/context abstraction.

RepoExec's finding that models can satisfy functional tests while improperly reimplementing existing dependencies makes this a particularly AI-relevant review strategy. citeturn2view7

The skill should similarly include a **negative-space review**:

> “What evidence would I expect to see in this PR if this change were genuinely complete?”

For a database change: migration tests.
For a security fix: adversarial regression test.
For public API change: compatibility evidence.
For dependency introduction: lockfile and dependency review.
For retry semantics: duplicate-side-effect testing.
For performance work: benchmark or measurement.
For concurrency fix: stress/race test.
For error-handling change: failure-path test.

Absence does not automatically prove a defect, but it tells the reviewer where to investigate.

## How to validate that the skill is actually excellent

The final trap would be building an impressive review prompt and judging it by whether its reports *sound* thorough.

Do not evaluate it that way.

The skill itself needs a benchmark.

CR-Bench is particularly relevant because it treats code review as a precision/recall problem rather than simply asking whether an AI can produce comments. The research highlights the trade-off between finding more true defects and generating more useless or incorrect reports, making measures such as precision, recall, F1, usefulness and signal-to-noise appropriate for review systems. citeturn2view6

Your benchmark should contain several classes of examples:

| Benchmark class | Purpose |
|---|---|
| Historical production bugs from the repository | Tests whether the skill catches things humans actually missed |
| Previously reverted PRs | Tests architectural/process understanding |
| Security fixes/CVEs | Tests trust-boundary and data-flow reasoning |
| Cross-file seeded defects | Tests repository traversal |
| Configuration-only defects | Tests non-source review |
| Migration/API compatibility defects | Tests temporal compatibility |
| Concurrency/state bugs | Tests non-local execution reasoning |
| Test-oracle defects | Tests whether the reviewer audits tests themselves |
| Hallucinated/unnecessary dependencies | Tests package and reuse investigation |
| Correct but unusual code | Measures false-positive resistance |
| Large harmless refactor | Tests whether size alone creates fake findings |
| Deliberately misleading comments | Tests whether evidence beats prose |

Historical defects are particularly valuable because they let you ask the strongest possible question:

> **Could this skill have prevented bugs that really escaped the existing engineering process?**

The most meaningful metrics are not simply “number of comments”.

Track:

| Metric | Why it matters |
|---|---|
| **Confirmed defect recall** | How many known defects did it catch? |
| **Precision** | How many reported issues were genuinely issues? |
| **Severity-weighted recall** | Missing an auth bypass matters more than missing dead code |
| **Actionability** | Could an engineer reproduce and fix the finding? |
| **Reviewer acceptance** | Do maintainers agree with the finding? |
| **False-positive burden** | How much engineer time does the skill waste? |
| **Cross-file detection rate** | Does “deep review” really outperform diff review? |
| **Missing-change detection** | Does it identify artefacts that should have changed but did not? |
| **Tool-backed finding ratio** | How often are findings independently supported? |
| **Regression caused by review fixes** | Does acting on the reviewer ever make correct code worse? |
| **Escaped-defect rate** | What still reaches production after review? |
| **Coverage completeness** | Did the review actually traverse the high-risk impact graph? |

CR-Bench directly supports measuring precision, recall and usefulness rather than optimising only for maximum issue discovery, while cross-model reviewing research demonstrates why reviewer-induced regressions should also be measured. citeturn2view6turn11view0

You should also benchmark **ablation versions** of the skill:

```text
A: diff only
B: diff + whole files
C: repository retrieval
D: repository graph
E: graph + specialist lenses
F: graph + specialists + deterministic tools
G: full system + adversarial validator
```

Then measure what each extra stage actually catches.

This would answer an extremely important question empirically:

> “Is the complexity of the deep reviewer buying us additional defect detection, or merely creating more words?”

Structure-aware repository research suggests graph/context improvements should matter, but your own repository-specific benchmark is what should determine the final architecture. citeturn11view2turn2view7

A second evaluation should deliberately test **precision under adversarial clean code**. Give the reviewer perfectly valid changes containing constructs that often trigger superficial AI warnings:

```text
intentional broad-looking exception handling with documented boundary
safe raw SQL using properly parameterised API
deliberate lock-free structure
intentional duplicate code across isolation boundary
validated dynamic import
required legacy API
seemingly unused callback invoked by framework convention
```

The skill should be rewarded for saying:

> “Investigated; no defect.”

rather than inventing a comment.

That is crucial because a code-review tool with excellent recall but low precision eventually gets ignored. CR-Bench's empirical precision/recall trade-off makes this a first-order design concern rather than a cosmetic one. citeturn2view6

A third benchmark should test whether the model can find **missing changes**, which standard defect datasets rarely measure well. Seed changes such as:

```text
add enum value but leave one consumer exhaustive
alter DB field but omit migration
change API response but leave generated client schema stale
add configuration value but omit production manifest
change permission semantics but omit background-job caller
add dependency to manifest without lockfile
change retry behaviour without idempotency protection
```

These are exactly the cases in which the bug exists partly in **what is absent**, not in an obviously erroneous changed line.

A fourth benchmark should measure **repository rule compliance**. The 2026 AI-contribution-rule study demonstrates that instruction discovery and compliance cannot safely be assumed. Your benchmark should plant requirements in different repository locations—root instructions, path-specific instructions, contribution docs, CI policy, architecture docs—and verify whether the reviewer actually discovers and applies them. citeturn11view3

Finally, continually feed three kinds of real-world failure back into the benchmark:

```text
a reviewer comment that turned out to be wrong
a defect that reviewers failed to catch
a PR that was rejected for a reason the skill failed to predict
```

That gives you a continuously improving local corpus of **false positives, false negatives and process failures**.

The resulting system is fundamentally different from today's typical AI code review.

A conventional AI review often looks like:

```text
diff
 ↓
LLM
 ↓
comments
```

The strongest system supported by the research looks more like:

```text
                       Repository rules
                              ↓
Issue/specification → Repository map ← Git history
                              ↓
                         Change model
                              ↓
                    Transitive impact graph
                              ↓
        ┌─────────────────────┼────────────────────┐
        ↓                     ↓                    ↓
   specialised           deterministic        behavioural
    reasoning               analysis           execution
        ↓                     ↓                    ↓
        └──────────────── candidate findings ─────┘
                              ↓
                    adversarial falsification
                              ↓
                     evidence consolidation
                              ↓
                       coverage ledger
                              ↓
                   high-signal final review
```

That architecture addresses the main failure mechanisms identified across the literature: repository exploration failures, failure to synthesise distributed evidence, AI-generated technical debt, vulnerable fixes, incorrect or stale test semantics, architecture/dependency misuse, contribution-rule violations, human difficulty with context-heavy defects and AI reviewer false positives. citeturn2view5turn6view0turn6view5turn6view7turn2view7turn11view3turn8search2turn2view6

The most important design principle is therefore not **“make the model review harder.”** It is:

> **Make the review process incapable of confusing plausibility with evidence.**

A deep repository review should not finish because the model has run out of concerns. It should finish because it can show what it mapped, what it followed, what it executed, what it tried to break, what evidence supports each remaining finding, which findings were disproved, and which parts of the repository or runtime environment remain uncertain. That is the difference between an AI that *comments on code* and an AI system capable of conducting something much closer to a **software investigation**. citeturn10view3turn11view2turn2view6
