# Concurrency and Lifetime Review

Use this reference for actors, global actors, `Sendable`, transfer, tasks, callbacks, continuations, streams, locks, queues, event loops, ARC, and teardown.

## Contents

- [Environment and isolation](#environment-and-isolation)
- [Sendability and transfer](#sendability-and-transfer)
- [Tasks, cancellation, and freshness](#tasks-cancellation-and-freshness)
- [Callbacks, continuations, and streams](#callbacks-continuations-and-streams)
- [Locks, reentrancy, and state machines](#locks-reentrancy-and-state-machines)
- [ARC and teardown](#arc-and-teardown)
- [Adversarial checks](#adversarial-checks)

## Environment and isolation

Begin with isolation domains, not threads. For each mutable invariant, identify one owner:

- actor or global actor;
- custom executor or event loop;
- serial queue;
- lock or atomic transaction;
- task-local ownership;
- immutable snapshot;
- one-time transfer;
- framework-confined context.

Check the actual compiler, language mode, strict-concurrency level, default isolation, upcoming features, dependency annotations, and deployment target before interpreting a diagnostic.

Review:

- where isolation is declared versus inferred;
- protocol witnesses, overrides, existentials, and closure function types;
- global-actor inference cutoffs and `nonisolated` declarations;
- caller-context execution versus explicitly concurrent execution;
- legacy Objective-C, Combine, C, or pre-concurrency boundaries;
- executor hops that change ordering or teardown behavior.

Compiler enforcement prevents some data races. It does not prove freshness, cancellation, transaction atomicity, legal state transitions, idempotency, or safe teardown.

## Sendability and transfer

For `@unchecked Sendable`, require:

- a complete mutable-state inventory;
- the lock, actor, executor, immutability, or ownership rule;
- the public API operations that preserve the rule;
- nested classes, closures, delegates, pointers, and subclassing;
- version or compatibility rationale where applicable.

Do not accept tests as proof of unchecked sendability. Use them to challenge the stated invariant.

For `@Sendable` closures, inspect the full capture graph. A captured `let` reference can still lead to mutable storage.

For `sending` or region-based transfer, check:

- whether the source can use the value afterward;
- escaped aliases, caches, delegates, closures, or pointers;
- whether the operation transfers once or shares repeatedly;
- generic constraints and every call site.

Distinguish:

- `@preconcurrency`: compatibility staging and reduced static enforcement;
- `@unchecked Sendable`: a manual type-wide safety promise;
- `nonisolated(unsafe)`: an unsafe isolation escape;
- `assumeIsolated`: a runtime/executor assertion;
- `sending`: ownership transfer at an API boundary.

Do not treat these as interchangeable diagnostic suppressions.

## Tasks, cancellation, and freshness

Classify every task:

| Form | Review focus |
|---|---|
| `async let` | Structured scope, error propagation, and cancellation cooperation. |
| Task-group child | Bounded fan-out, child completion, cancellation, and group waiting. |
| `Task {}` | Context inheritance, deliberate ownership, result/error handling, and cancellation handle. |
| `Task.detached` | Lost actor/task-local inheritance, transfer, priority, and explicit ownership. |
| SwiftUI `.task` | View identity, disappearance, restart, cancellation cooperation, and side effects. |
| SwiftUI `.task(id:)` | Whether the ID is the logical request identity. |

Do not require a retained handle for every independent task. Require one when the caller must await, cancel, replace, or observe the work.

For each task, establish:

- creator and logical owner;
- whether it may outlive that owner;
- termination and error policy;
- cancellation request and observation points;
- state that can change across each `await`;
- side effects already committed before cancellation;
- bounded concurrency and back-pressure;
- whether the task or handle retains its owner indefinitely.

Cancellation is cooperative and is not freshness. An actor-safe assignment may still commit an old result to a newer query, route, item, or screen.

Use generation, identity, reservation, or version checks at the commit point when cancellation alone cannot prove relevance.

For timeout or race helpers, inspect the losing operation. A structured task group still waits for children that ignore cancellation.

## Callbacks, continuations, and streams

Document the callback contract before accepting an async bridge:

- zero, one, or multiple callbacks;
- success, error, completion, and cancellation channels;
- synchronous completion possibility;
- callback queue or executor;
- registration and delegate lifetime;
- replacement or concurrent request behavior;
- no-callback and owner-deallocation behavior.

A continuation must resume exactly once on every terminal path. `CheckedContinuation` diagnoses misuse; repeated resume traps under the current checked API, while missing resume strands the task and resources.

Prefer one synchronized bridge state when completion can race cancellation:

```text
idle
→ registered(continuation, cancellation token)
→ resumed | cancelled
```

Do not let two callbacks both observe `pending`. Do not unregister after success without coordinating the transition.

For `AsyncStream`, `AsyncThrowingStream`, and custom sequences, define:

- single or multiple consumers;
- buffering policy and maximum growth;
- drop/replay/multicast behavior;
- slow-consumer handling and producer demand;
- iterator rules;
- termination and cancellation;
- continuation ownership;
- whether producer work stops when the consumer ends.

## Locks, reentrancy, and state machines

Protect the complete business transition, not individual properties:

```swift
// Unsafe logical transaction despite individually locked access.
let old = store.value
store.value = old + 1
```

Prefer one lock-scoped mutation when the invariant is read-modify-write.

Check whether lock-held code can:

- invoke callbacks or user closures;
- release an object and run `deinit`;
- cancel synchronously;
- re-enter the same state machine;
- block, suspend, or call another lock.

Recursive locking can avoid one deadlock but does not prove ordering, starvation, or logical safety.

Rewrite stateful code as transitions:

| Current state | Event | Legal next state | Side effect | Duplicate/late policy |
|---|---|---|---|---|
| Idle | Start | Starting | Register | Handle synchronous completion. |
| Starting | Cancel | Finished | Unregister | Coordinate with completion. |
| Active | Value | Active/Finished | Deliver | Handle reentrant consumer. |
| Active | Failure | Finished | Fail waiters | Terminal transition once. |
| Finished | Late event | Finished | Ignore/assert/log | Never recreate state. |

Actors are reentrant across `await`. Revalidate any state read before suspension when another actor message can invalidate it.

## ARC and teardown

Choose capture policy from intended lifetime:

| Intent | Likely design |
|---|---|
| Work belongs to owner and should stop with it | Owner retains handle; explicit cancellation; avoid indefinite cycle. |
| Work must survive the initiating screen | Transfer to a longer-lived coordinator or service. |
| Work may finish but must not update a dead owner | Weak commit target or longer-lived result owner. |
| Closure provably cannot outlive owner | Strong or `unowned` only with an actual proof. |
| Required side effect must not vanish | Avoid reflexive weak capture; make ownership explicit. |

Review both leaks and premature release. `[weak self]` can prevent a cycle or silently drop required work.

Treat teardown as a separate path. Inspect tasks, timers, display links, observers, subscriptions, streams, delegates, callbacks, windows/scenes, and actor-isolated cancellation.

Do not rely only on `deinit` to cancel a cycle that prevents `deinit` from running. Prefer explicit `cancel()`, `stop()`, parent removal, or window/scene lifecycle.

## Adversarial checks

Select only checks that challenge the changed invariant:

- older operation completes after newer operation;
- cancellation before start, during suspension, during CPU work, and after side effect;
- callee ignores cancellation;
- callback completes synchronously, twice, after error, or never;
- cancellation races callback registration and completion;
- actor re-entry between read and write;
- listener removes itself or triggers another event;
- concurrent read-modify-write;
- already-cancelled task enters a cancellation handler;
- producer outruns consumer;
- second iterator or consumer appears;
- owner releases while work is active;
- cancelled task retains its object graph;
- teardown occurs from an unexpected executor;
- Debug and Release or oldest/current runtime differ.
