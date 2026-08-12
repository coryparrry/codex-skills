# Risk-routed review lanes

Always run the compact core lane. Activate other lanes only when the change or affected system triggers them.

## Core lane

Establish requested behavior, observable change, preserved invariants, necessity of each changed area, affected callers and consumers, missing companions, applicable deterministic checks, and mergeability under repository policy.

## Specialist routing

| Trigger | Lane | Required questions |
|---|---|---|
| Ambiguous requirement, incomplete fix, alternate entry points | Specification and correctness | Does every relevant path satisfy the reconstructed behavior? Is the root cause fixed rather than one symptom? |
| New abstraction, helper, framework, duplicate logic, broad refactor | Architecture and reuse | Does dependency direction, ownership, and the established repository mechanism remain intact? Is each edit necessary? |
| Authentication, authorization, secrets, untrusted input, tenant or user data | Security and trust | What is attacker controlled? Which control protects which sink? Is the path reachable and the guard effective? |
| Shared state, async work, callbacks, events, locks, actors, retries | State and concurrency | What state is shared? Which operations interleave? How do cancellation, reentrancy, late completion, and teardown preserve the invariant? |
| Schema, migration, persistence, serialization, cache key, event format | Data and compatibility | Can old and new binaries, clients, events, schemas, and stored values coexist, roll forward, and roll back? |
| Filesystem, network, database, process, timeout, background work | Reliability and resources | What happens on partial failure, retry, restart, cancellation, duplicate execution, and resource cleanup? |
| Hot path, loops, queries, large data, allocation, cache, lock | Performance | What changed in asymptotic work, calls, queries, allocation, contention, or resource lifetime? Is the production trigger realistic? |
| New or changed tests, assertions, fixtures, mocks, skips, snapshots | Test oracle | Did the test fail before the patch? Is the expected result independent? Which realistic wrong implementation still passes? |
| Package, action, image, binary, build tool, generated dependency | Dependency and supply chain | Does it exist in the intended registry? Is the resolved version locked, necessary, supported, licensed, and from the expected maintainer? |
| CI, build, packaging, feature flag, environment, deployment, release | Operations | Does the exact production and release path receive the change? Are rollout, observability, failure recovery, and rollback viable? |
| Dead scaffolding, one-off utility, broad exception, swallowed failure | Maintainability and failure semantics | What concrete property is violated? Is failure hidden, code unreachable, or conceptual complexity materially increased? |

## Evidence extensions

For a security claim, record source, transformations, control, sink, attacker capability, privilege, preconditions, existing defense, and realistic impact.

For a concurrency claim, record shared state, operation A, operation B, feasible interleaving, expected invariant, synchronization, and reproduction or stress evidence.

For a performance claim, record before and after cost or call count, scaling dimension, production trigger, measurement or defensible model, and resource impact.

For a compatibility claim, record producer and consumer versions, stored or wire format, changed expectation, roll-forward behavior, rollback behavior, and affected deployed population.

Do not report "possible injection," "may race," "could be slow," or "might break compatibility" without these elements.
