# Risk-routed review lanes

Always run the compact core lane. Activate other lanes only when the change or reviewed system triggers them.

## Core lane

For a change review, establish requested behavior, observable change, preserved invariants, necessity of each changed area, affected callers and consumers, missing companions, applicable deterministic checks, and mergeability under repository policy.

For a snapshot audit, establish supported behavior, reachable entry points and sinks, invariants, cross-area contracts, failure paths, trust boundaries, missing operational or verification companions, and applicable deterministic checks. Judge snapshot risk and completeness, not mergeability.

## Compose repository and platform review

Use `deep-code-review` as the umbrella when the request is repository-wide or crosses languages, services, build systems, or deployment surfaces. It owns the exact-state inventory, cross-language contracts, coverage ledger, integration pass, deduplication, and final disposition.

When affected paths include Swift, Objective-C interoperability, Xcode project state, Swift packages, SwiftUI, AppKit, UIKit, Apple persistence, signing, entitlements, or Apple runtime behavior, route those paths through `swift-code-review` as a specialist lane. A focused Swift or Apple-only request may invoke `swift-code-review` directly. When both skills participate, return specialist evidence and candidate findings to the umbrella review instead of issuing a competing disposition. If the specialist is unavailable, continue with the applicable generic lanes and record the missing specialist coverage.

## Specialist routing

| Trigger | Lane | Required questions |
|---|---|---|
| Ambiguous requirement, incomplete behavior, alternate entry points | Specification and correctness | Does every relevant path satisfy the reconstructed behavior? For a change, is the root cause fixed rather than one symptom? |
| New abstraction, helper, framework, duplicate logic, broad refactor | Architecture and reuse | Does dependency direction, ownership, and the established repository mechanism remain intact? Is each edit necessary? |
| Authentication, authorization, secrets, untrusted input, tenant or user data | Security and trust | What is attacker controlled? Which control protects which sink? Is the path reachable and the guard effective? |
| Personal data, analytics, logging, telemetry, retention, consent, deletion | Privacy and data governance | What data is collected, inferred, retained, transmitted, or exposed? Are purpose, consent, minimization, redaction, deletion, and access boundaries preserved? |
| Cryptography, randomness, hashing, certificates, signatures, keys, trust stores | Cryptography and signing | Is the primitive appropriate, current, correctly parameterized, and used through the repository's trusted key and certificate lifecycle? |
| Shared state, async work, callbacks, events, locks, actors, retries | State and concurrency | What state is shared? Which operations interleave? How do cancellation, reentrancy, late completion, and teardown preserve the invariant? |
| Schema, migration, persistence, serialization, cache key, event format | Data and compatibility | Can old and new binaries, clients, events, schemas, and stored values coexist, roll forward, and roll back? |
| User interface, interaction, copy, locale, time, number, input method | UX, accessibility, and internationalization | Can supported users perceive, operate, and understand every state? Are focus, semantics, contrast, motion, localization, formatting, text expansion, and bidirectional layout preserved? |
| Unsafe memory, FFI, native handle, ABI, ownership transfer, binary layout | Native safety and interoperability | Which component owns each allocation and handle? Are bounds, lifetimes, alignment, representation, error, and cleanup contracts valid across the boundary? |
| Language, compiler, framework, SDK, or platform-specific behavior | Language and platform semantics | Which exact version and configuration defines the behavior? Do primary documentation, active toolchain, and supported-runtime evidence agree? |
| Filesystem, network, database, process, timeout, background work | Reliability and resources | What happens on partial failure, retry, restart, cancellation, duplicate execution, and resource cleanup? |
| Hot path, loops, queries, large data, allocation, cache, lock | Performance | What changed in asymptotic work, calls, queries, allocation, contention, or resource lifetime? Is the production trigger realistic? |
| Tests, assertions, fixtures, mocks, skips, snapshots | Test oracle | Is the expected result independent and does the test exercise the production path? For a change, did it fail before the patch? Which realistic wrong implementation still passes? |
| Package, action, image, binary, build tool, generated dependency | Dependency and supply chain | Does it exist in the intended registry? Is the resolved version locked, necessary, supported, licensed, and from the expected maintainer? |
| CI, build, packaging, feature flag, environment, deployment, release | Operations | Does the exact production and release path receive the change? Are rollout, observability, failure recovery, and rollback viable? |
| Dead scaffolding, one-off utility, broad exception, swallowed failure | Maintainability and failure semantics | What concrete property is violated? Is failure hidden, code unreachable, or conceptual complexity materially increased? |

## Evidence extensions

For a security claim, record source, transformations, control, sink, attacker capability, privilege, preconditions, existing defense, and realistic impact.

For a concurrency claim, record shared state, operation A, operation B, feasible interleaving, expected invariant, synchronization, and reproduction or stress evidence.

For a performance claim, record before and after cost or call count, scaling dimension, production trigger, measurement or defensible model, and resource impact.

For a compatibility claim, record producer and consumer versions, stored or wire format, changed expectation, roll-forward behavior, rollback behavior, and affected deployed population.

Do not report "possible injection," "may race," "could be slow," or "might break compatibility" without these elements.
