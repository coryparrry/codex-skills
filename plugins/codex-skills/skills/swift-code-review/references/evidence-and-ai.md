# Evidence and AI-Assisted Swift Review

Use this reference when a finding needs primary support, a repository precedent, or calibration for AI-authored changes. Recheck time-sensitive status before relying on it.

## Contents

- [Evidence hierarchy](#evidence-hierarchy)
- [AI-assisted changes](#ai-assisted-changes)
- [Primary language and framework sources](#primary-language-and-framework-sources)
- [Repository cases](#repository-cases)
- [AI research limits](#ai-research-limits)

## Evidence hierarchy

Use evidence according to what it can establish:

| Evidence | Establishes | Does not establish |
|---|---|---|
| Official Swift, compiler, Swift Evolution, and Apple documentation | Language, API, and framework contract. | Defect frequency in applications. |
| Current repository code and tests | Reachability and behavior in this checkout. | Behavior on untested platforms or schedules. |
| Merged repository correction | A mechanism occurred and a change was accepted. | AI causation, prevalence, or release status. |
| Merged design/performance change | A difficult contract or useful design boundary. | A pre-existing defect. |
| Open or closed-unmerged investigation | A plausible unresolved boundary. | An accepted diagnosis or fix. |
| AI/code-generation study | Measured model, dataset, or adoption behavior within its sample. | Swift-specific concurrency, ownership, or SwiftUI defect rates unless directly studied. |

Prefer current code and primary contracts. Treat review comments, issue reports, generated explanations, and repository precedents as hypotheses until verified against the scoped change.

For a repository case, record:

- exact PR or issue;
- relevant review comment;
- merged/open/closed status;
- whether the correction appears in the merged diff;
- release/tag status when known;
- last verification date;
- narrow reusable mechanism.

Merge is not release proof. A merged PR does not imply every review comment was accepted.

## AI-assisted changes

Apply the same correctness standard to human- and AI-authored code. Do not infer authorship from style or inflate severity because a model participated.

Increase context recovery and validation when provenance is incomplete. Ask the code or change description to make these assumptions reviewable:

- ownership and lifetime;
- isolation and transfer;
- ordering, cancellation, and freshness;
- callback count and executor;
- identity and source of truth;
- representation and numeric limits;
- retry, side effects, and partial success;
- toolchain, SDK, dependency, and deployment versions.

Use these as hypotheses, not findings:

- diagnostic appeasement through unsafe annotations, nested tasks, weak captures, force unwraps, or silent error handling;
- mixed-era or invented APIs;
- success-only implementation and tests;
- unstructured-task inflation;
- value/reference confusion;
- tutorial-grade logging, trust, parsing, or resource limits;
- unnecessary protocols, factories, adapters, repositories, and manager types.

Require a full re-review after substantial regeneration because the new diff may change assumptions outside the repaired line.

Do not automatically require:

- an actor for every mutable class;
- a handle for every deliberately independent task;
- `[weak self]` for every closure;
- a protocol for every dependency;
- tests as proof of unchecked sendability;
- zero warnings achieved by suppression;
- fewer lines at the cost of explicit state.

## Primary language and framework sources

Verify current behavior rather than freezing version claims:

- [Swift releases](https://www.swift.org/blog/)
- [Swift Evolution proposals](https://github.com/swiftlang/swift-evolution/tree/main/proposals)
- [Approachable Concurrency vision](https://github.com/swiftlang/swift-evolution/blob/main/visions/approachable-concurrency.md)
- [SE-0338: execution of non-actor-isolated async functions](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0338-clarify-execution-non-actor-async.md)
- [SE-0414: region-based isolation](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0414-region-based-isolation.md)
- [SE-0420: inheritance of actor isolation](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0420-inheritance-of-actor-isolation.md)
- [SE-0423: dynamic actor isolation enforcement](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0423-dynamic-actor-isolation.md)
- [SE-0449: nonisolated global-actor cutoff](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0449-nonisolated-for-global-actor-cutoff.md)
- [Apple `Task`](https://developer.apple.com/documentation/swift/task)
- [Apple `CheckedContinuation`](https://developer.apple.com/documentation/swift/checkedcontinuation)
- [Apple SwiftUI model data](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app)
- [Apple `Identifiable`](https://developer.apple.com/documentation/swift/identifiable)
- [Apple SwiftUI lists](https://developer.apple.com/documentation/swiftui/displaying-data-in-lists)
- [Apple diagnostics for memory, thread, and crash issues](https://developer.apple.com/documentation/xcode/diagnosing-memory-thread-and-crash-issues-early)

Use the actual generated interface when documentation and compiler behavior differ.

## Repository cases

These cases demonstrate mechanisms, not prevalence or AI causation:

| Case | Mechanism |
|---|---|
| [SwiftNIO #385](https://github.com/apple/swift-nio/pull/385) | Buffer compaction, stored indices, EOF, unsafe-pointer scope, notification ordering, and reentry. |
| [SwiftNIO #675](https://github.com/apple/swift-nio/pull/675) | Explicit state machine for reentrant decoding and adversarial frame tests. |
| [SwiftNIO #1902](https://github.com/apple/swift-nio/pull/1902) | Encoded byte length, integer bounds, transactional cursor movement, and error meaning. |
| [SwiftNIO #2230](https://github.com/apple/swift-nio/pull/2230) | Back-pressure, synchronous cancellation, destructor/callback work under locks, and strategy contracts. |
| [SwiftNIO #2645](https://github.com/apple/swift-nio/pull/2645) | Scheduling order, starvation, shutdown, allocation, and benchmark validity. |
| [TCA #1036](https://github.com/pointfreeco/swift-composable-architecture/pull/1036) | Crash repair that initially broke lazy list construction. |
| [TCA #2255](https://github.com/pointfreeco/swift-composable-architecture/pull/2255) | Historical snapshot equality versus live mutable state. |
| [TCA #3136](https://github.com/pointfreeco/swift-composable-architecture/pull/3136) | Thread-safe storage with a logically racy split read-modify-write. |
| [TCA #3638](https://github.com/pointfreeco/swift-composable-architecture/pull/3638) | Pre-concurrency closure type erasing the isolation contract during teardown. |
| [Kingfisher #2519](https://github.com/onevcat/Kingfisher/pull/2519) | Producer cancellation plus commit-point guarding. |
| [Kingfisher #2550](https://github.com/onevcat/Kingfisher/pull/2550) and [#2555](https://github.com/onevcat/Kingfisher/pull/2555) | Structurally present SwiftUI branches, intermediate layout, and transition identity. |
| [Kingfisher #2551](https://github.com/onevcat/Kingfisher/pull/2551) and [#2554](https://github.com/onevcat/Kingfisher/pull/2554) | Value-looking views sharing reference-backed context through alternate mutation routes. |
| [Vapor #2180](https://github.com/vapor/vapor/pull/2180) | Preserve supported external representation semantics until target-type decoding. |
| [Vapor #3160](https://github.com/vapor/vapor/pull/3160) | Actual bound runtime state versus requested configuration. |
| [Alamofire #2716](https://github.com/Alamofire/Alamofire/pull/2716) | Retry, serializer replay, state reset, and completion timing. |
| [AsyncHTTPClient #621](https://github.com/swift-server/async-http-client/pull/621) and [#709](https://github.com/swift-server/async-http-client/pull/709) | Sendability migration across compiler support floors and compatibility wrappers. |
| [AsyncHTTPClient #806](https://github.com/swift-server/async-http-client/pull/806) | `with`-style resource lifetime, caller isolation, result transfer, cancellation, and shutdown. |

Label unresolved examples accurately:

- [SwiftNIO #2501](https://github.com/apple/swift-nio/pull/2501): closed draft, not an adopted API.
- [Swift Async Algorithms #276](https://github.com/apple/swift-async-algorithms/pull/276): open retention/cancellation concern as last verified in the source research.
- [Swift Async Algorithms #369](https://github.com/apple/swift-async-algorithms/pull/369): open legacy-runtime state/lock proposal as last verified in the source research.
- [Alamofire #3976](https://github.com/Alamofire/Alamofire/pull/3976): open nested-error metadata precedence concern as last verified in the source research.

Recheck these statuses before using them.

## AI research limits

Use these sources narrowly:

- [SwiftEval](https://arxiv.org/abs/2505.24324): supports Swift-specific evaluation rather than translated language benchmarks; it does not measure repository-scale concurrency or SwiftUI review defects.
- [UICoder](https://machinelearning.apple.com/research/uicoder): supports compiler and rendered-behavior feedback for generated UI code.
- [Athena](https://machinelearning.apple.com/research/athena): supports structured intermediate representations for app generation; it does not justify abstraction inflation.
- [AIDev](https://arxiv.org/abs/2602.09185): provides a large agent-authored PR dataset; acceptance and review metadata are not long-term correctness.
- [AI agents in Android/iOS development](https://arxiv.org/abs/2602.12144): platform-level adoption evidence does not prove every iOS change is Swift.
- [Copilot security study](https://arxiv.org/abs/2310.02059): supports security validation of generated code within its studied languages and sample; do not transfer its rates to Swift.

Do not claim a ranked Swift-specific taxonomy of AI-introduced defects without a representative Swift dataset, provenance, denominator, and control group.
