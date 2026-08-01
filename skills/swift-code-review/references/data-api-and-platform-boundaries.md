# Data, API, and Platform Boundaries

Use this reference for value/reference semantics, parsers, unsafe memory, external input, persistence, errors, retries, public API, package/build boundaries, compatibility, security, and performance.

## Contents

- [Value semantics and hidden references](#value-semantics-and-hidden-references)
- [Representation and parsing](#representation-and-parsing)
- [Unsafe memory and interoperability](#unsafe-memory-and-interoperability)
- [Errors, retries, and side effects](#errors-retries-and-side-effects)
- [Persistence](#persistence)
- [API and compatibility](#api-and-compatibility)
- [Packages, builds, macros, and generated code](#packages-builds-macros-and-generated-code)
- [Security and privacy](#security-and-privacy)
- [Performance and resource policy](#performance-and-resource-policy)
- [Adversarial checks](#adversarial-checks)

## Value semantics and hidden references

A `struct`, `let`, or `Self`-returning API does not guarantee deep value semantics. Inspect nested classes, closure registries, delegates, caches, queues, pointers, and custom copy-on-write storage.

Distinguish physical storage sharing from observable shared mutation. Standard collections and `Data` may share storage while preserving logical values through copy-on-write.

For fluent value APIs:

- inventory every mutation route;
- include generic, protocol-extension, convenience, callback, and deprecated paths;
- copy mutable backing context before mutation;
- preserve all mutable properties during copy;
- check atomic snapshot behavior;
- verify equality/hash identity;
- add sibling-independence coverage.

Challenge with:

```text
create base
→ derive A with option X
→ derive B with option Y
→ prove base, A, and B are independent
→ mutate A through every modifier family
→ prove prior A state survives and B remains unchanged
```

## Representation and parsing

Do not interchange:

- grapheme count, Unicode scalars, UTF-8 bytes, and protocol length;
- integer conversion, truncation, wrapping, clamping, and exact conversion;
- collection index, byte offset, reader index, and persisted position;
- requested representation and actual emitted representation.

Measure the bytes or representation actually written. Validate bounds before partially mutating output.

For incremental parsers, define states and test:

- zero bytes and EOF;
- partial header and partial body;
- multiple frames;
- malformed, negative, overflowing, and oversized lengths;
- trailing data;
- repeated or encoded keys;
- slices with non-zero start indices;
- compaction/reallocation after index capture;
- reentrant input during delivery;
- whether failure rolls back or consumes input;
- incomplete versus invalid complete input.

Preserve external distinctions until the decoder has enough target-type context. Do not normalize away duplicates, ordering, encoded delimiters, missing versus empty, or invalid versus incomplete input unless the protocol defines that loss.

Never let untrusted external input reach a force unwrap, precondition, or `fatalError` unless the public contract proves it is programmer misuse rather than input failure.

## Unsafe memory and interoperability

For `Data`, buffers, and pointers, inspect:

- empty buffers;
- alignment, bounds, initialization, and deinitialization;
- pointer lifetime within borrowing closures;
- escaping pointers or aliases;
- mutation or reallocation while borrowed;
- copy independence;
- integer-controlled allocation;
- release-optimization differences;
- platform-specific Foundation behavior.

Prefer the narrowest unsafe scope and the highest-level operation that expresses the required bytes.

For C, C++, Objective-C, and foreign callbacks, establish:

- ownership and nullable-pointer conventions;
- calling convention and imported integer widths;
- buffer/length pairing;
- callback lifetime and thread/executor entry;
- Swift value escape beyond its lifetime;
- error-code translation;
- availability and generated-header behavior.

The compiler cannot infer a complete foreign ownership protocol.

## Errors, retries, and side effects

Classify errors by meaning:

- cancellation;
- transport or authentication;
- server rejection;
- decoding or domain validation;
- persistence;
- partial success;
- programmer invariant violation.

Treat `try?`, empty `catch`, and silent `guard` as suspicious when they erase required behavior or recovery.

For retry, define:

- which request, body, serializer, callback, and side effect repeats;
- whether a prior attempt may have succeeded despite a lost response;
- idempotency key or at-most-once mechanism;
- local state already committed;
- completion and analytics delivery count;
- retry budget and reset;
- authentication-refresh overlap;
- cancellation of future attempts.

Give highest scrutiny to purchases, account changes, database migrations, deletion, messages, uploads, keychain writes, webhooks, and other irreversible effects.

Represent partial success explicitly when external and local commits can diverge:

```text
not started
→ external commit pending
→ external committed / local commit pending
→ complete | recovery required
```

Make converging terminal paths idempotent.

## Persistence

Review:

- context ownership and confinement;
- managed models crossing actors/contexts;
- stable IDs or immutable snapshots for transfer;
- transaction and save boundaries;
- uniqueness, merge, deletion, and stale snapshot behavior;
- async work referencing deleted objects;
- partial write and crash recovery;
- file coordination and sandbox access;
- production versus in-memory test-store differences.

For SwiftData and Core Data, do not infer mobility from the model's surface type. Review the owning context and transfer object IDs or values according to framework rules.

Test migration from the previous production schema, not only a clean store:

- new required fields and missing values;
- enum changes;
- uniqueness conflicts;
- large real datasets;
- interrupted migration;
- rollback/recovery and downgrade policy.

## API and compatibility

Review the call site:

- name reveals side effects, cost, isolation, and completion;
- argument labels disambiguate policy;
- defaults reduce duplication without hiding behavior;
- cancellation and typed failure remain visible;
- synchronous-looking API does not create unowned work;
- properties do not hide I/O or linear cost.

Inspect:

- protocol requirement versus extension overload;
- existential/generic dispatch;
- public access accidentally widened;
- source, ABI, API, runtime, and behavior compatibility separately;
- compiler and package support floors;
- deployment availability and back-deployed metadata/symbols;
- generated interfaces and API/ABI reports;
- all construction and transport paths for new configuration.

Requested configuration may differ from normalized, negotiated, or runtime-resolved state. Report and expose the actual bound address, port, TLS state, locale, or other effective value where that is the contract.

Compilation on the newest SDK does not prove the oldest supported runtime.

## Packages, builds, macros, and generated code

For `Package.swift` and dependency-resolution changes, inspect:

- tools version, Swift language mode, platforms, products, targets, and target membership;
- version ranges, exact pins, branches, revisions, local paths, binary targets, checksums, and provenance;
- direct and transitive resolution changes in `Package.resolved`;
- conditional dependencies, compiler definitions, unsafe flags, linker settings, and Debug/Release differences;
- processed versus copied resources, localization, collisions, and bundle lookup;
- downstream source, runtime, deployment, and toolchain compatibility.

Treat a manifest as executable build policy, not static metadata. Verify the resolved graph rather than assuming the textual requirement selected the intended version.

For build tools, command plugins, macros, and generated sources, establish:

- which code runs on the host and which ships in the target;
- inputs, outputs, permissions, sandbox/network access, determinism, and caching;
- trust and update boundaries for executable dependencies;
- macro implementation/compiler compatibility and expansion behavior at call sites;
- ownership of generated files and whether they are checked in;
- incremental, clean, archive, and distribution-build behavior;
- diagnostics and failure behavior when generation is unavailable or stale.

Do not update dependency resolution or regenerate tracked artifacts merely to inspect a change. Use isolated outputs where supported and report validation that would mutate the checkout.

## Security and privacy

Derive review depth from trust and data boundaries, not authorship.

Inspect:

- authorization and authentication;
- URL, redirect, and deep-link validation;
- trust evaluation and certificate handling;
- secure random generation;
- secrets and sensitive payloads in source, logs, analytics, defaults, crash reports, URLs, or prompts;
- keychain accessibility;
- path traversal, bookmarks, and security-scoped resource lifetime;
- untrusted decoding and decompression limits;
- integer-controlled allocation;
- web content/message handlers;
- token-refresh races;
- package/tool execution and dependency provenance.

Use minimal, redacted diagnostics. Do not add production logging merely to make a review easier.

## Performance and resource policy

Locate the frequency multiplier:

- every `body` evaluation or list row;
- byte, frame, image, request, keystroke, or animation tick;
- observation change;
- main-actor or lock-held execution;
- unbounded task or stream fan-out.

Check repeated formatter/decoder/regex creation, conversions, type erasure, broad observation, equality cost, actor/queue hops, whole-value copies, synchronous I/O, and unbounded buffering.

A performance finding needs:

- hot path and expected frequency;
- worst-case input;
- concrete allocation/copy/lock/executor/resource cost;
- measurement or a credible measurement plan;
- semantic comparison before and after.

Do not report speculative micro-optimizations.

## Adversarial checks

Select relevant checks:

- Unicode and composed characters;
- exact maximum and one beyond;
- 32-bit or signed-width boundaries;
- partial/malformed/duplicate/trailing input;
- buffer compaction and index invalidation;
- empty buffer and misalignment;
- retry after ambiguous external success;
- repeated terminal completion;
- process termination between external and local commit;
- schema migration from production data;
- deletion during async work;
- concrete versus existential dispatch;
- oldest compiler/SDK/runtime and Release build;
- large upload/download/image and slow consumer;
- aggregate memory limit, not only per-item limit;
- sensitive logs and crash payloads.
