# SwiftUI and AppKit Review

Use this reference for SwiftUI state, Observation, identity, lists, navigation, asynchronous work, layout, modifiers, transactions, accessibility, scenes, windows, AppKit lifecycle, and SwiftUI/AppKit bridges.

## Contents

- [Build the ownership and identity model](#build-the-ownership-and-identity-model)
- [Observation and rendering](#observation-and-rendering)
- [Asynchronous lifetime and navigation](#asynchronous-lifetime-and-navigation)
- [Layout, modifiers, and transactions](#layout-modifiers-and-transactions)
- [State matrices and composition budgets](#state-matrices-and-composition-budgets)
- [Accessibility and adaptation](#accessibility-and-adaptation)
- [AppKit interoperability](#appkit-interoperability)
- [Runtime qualification](#runtime-qualification)

## Build the ownership and identity model

Trace each mutable value:

```text
creation
→ owner
→ observers and bindings
→ mutation entry points
→ persistence or synchronization
→ destruction
```

Match state storage to ownership:

| Situation | Review expectation |
|---|---|
| Transient value owned by this view identity | Local state. |
| Reference model created and owned by the view | Retained local model appropriate to the framework generation and deployment target. |
| Model owned by parent or coordinator | Borrowed observation; do not create a duplicate child owner. |
| Parent value edited by child | Binding unless an explicit draft/commit state machine exists. |
| Shared dependency | Explicit environment or composition boundary rather than hidden singleton. |
| Persisted domain state | Persistence/context owner remains authoritative. |

Do not accept duplicated state synchronized through `onChange` unless divergence, commit, revert, external updates, and validation are explicit.

Identity must be stable and unique for the logical lifetime required by the receiver. Review:

- persisted entity ID versus array index or mutable value;
- insertion, deletion, sorting, filtering, and reordering;
- list, navigation, selection, focus, animation, and task identity;
- repeated destinations of the same type;
- `.id(...)` as intentional replacement versus refresh workaround;
- view identity versus model/store identity;
- task result identity at the commit point.

High-risk patterns include:

```swift
var id: UUID { UUID() }
ForEach(items, id: \.self)       // When equality-relevant fields mutate or duplicates are legal.
ForEach(items.indices, id: \.self)
.id(UUID())
```

## Observation and rendering

`body` describes UI and may run repeatedly. Reject uncontrolled side effects such as network work, analytics, persistence, notification registration, task creation, or meaningful I/O during `body` or repeated view construction.

Review the exact observed read set:

- stored properties read in `body`;
- computed properties that read broader state;
- bindings with broad getters;
- parent reads that invalidate large child trees;
- custom equality that hides meaningful updates or adds hot-path cost;
- sorting, filtering, formatting, or projection rebuilt on every evaluation.

Do not split every property into a separate object merely to narrow invalidation. Prefer a coherent domain owner and stable value projections.

Stored derived state creates synchronization obligations. Store it only when measured cost justifies a cache and invalidation cannot drift.

For model construction, check whether view-value recreation repeats expensive initialization, registration, or global side effects. Move meaningful ownership to a parent, scene, coordinator, dependency composition point, or lifecycle-aware operation.

`onAppear` is not a once-only hook. Repetition can result from navigation, tab changes, hierarchy reconstruction, scrolling, windows, and platform behavior.

## Asynchronous lifetime and navigation

Trace:

```text
view identity
→ event or .task trigger
→ task owner
→ request identity
→ dependency call
→ suspension
→ cancellation/restart
→ freshness check
→ isolated commit
→ observation invalidation
→ current hierarchy/entity
```

For button-created `Task`, inspect repeated taps, ownership, errors, cancellation, owner retention, result freshness, and whether work should survive dismissal.

For `.task` and `.task(id:)`, verify:

- the dependency cooperates with cancellation;
- child work remains structured;
- the ID represents the logical request;
- cancellation is not shown as failure;
- restart cannot duplicate an external side effect;
- shared models retain or discard results intentionally.

Navigation and optional child state commonly race:

```text
child starts work
→ parent removes child
→ framework binding write or effect completes
→ event arrives for missing or replacement child
```

Classify late events. A framework cleanup write, stale response, programmer error, and parent-owned completion require different handling. Do not hide every late event behind `guard child != nil else { return }`.

Review:

- one navigation source of truth;
- destination state completeness;
- dismissal cancellation and late commits;
- deep-link and restoration validity;
- stable/codable path elements when required;
- interactive versus programmatic dismissal;
- sheet, popover, window, and multi-scene lifetime.

## Layout, modifiers, and transactions

Review each visible and intermediate hierarchy:

```text
idle
loading placeholder
partial/cached content
fresh content
empty success
failure
retrying
cancelled
```

An invisible branch may still affect layout, alignment, preferences, hit testing, accessibility, focus, or animation.

Ask:

- is the branch absent, transparent, hidden, or zero-sized;
- which branch proposes and reports size;
- whether an overlay intercepts input;
- whether hidden content remains accessible;
- whether transition temporarily contains both branches;
- whether placeholder and content share compatible geometry.

## State matrices and composition budgets

When more than one state dimension can change, do not review only the named
states in isolation. Cross the dimensions that can be independently available:

| Dimension | Example states |
|---|---|
| Content | None, retained, fresh |
| Metadata or list | Unavailable, partial, exact |
| Freshness | Idle, loading, refreshing, failed |
| Selection or destination | None, current, removed, replaced |

The matrix need not enumerate impossible combinations, but it must include every
reachable combination that changes what the user can see or do. In particular,
verify retained content with an empty or incomplete list, and verify that a
refresh indicator or incomplete marker remains visible while old content is
shown. An empty collection or zero count is not automatically equivalent to no
content or a known-zero result; preserve the distinction in the model and view.

For fixed or bounded parents, calculate the layout budget rather than checking
each child in isolation:

```text
offered size
≥ header + content minimum + footer + padding
  + safe-area/reserved controls + overlays
```

Check every loading, retained, partial, empty, failure, and retry branch for
overflow, clipping, footer reachability, and scroll behavior. A child
`minHeight` or `fixedSize` can exceed the parent’s total content height even
when the child is locally valid. Prefer flexible sizing or an explicit scroll
region when the contract allows it; otherwise prove the parent budget for the
supported window sizes.

Treat modifier ordering as semantics, especially:

- `.id`;
- `.task` and `.task(id:)`;
- `.animation` and `.transaction`;
- `.equatable`;
- `.frame` and `.fixedSize`;
- `.background`, `.overlay`, `.clipShape`, and `.mask`;
- `.contentShape`, `.allowsHitTesting`, and `.disabled`;
- `.environment`;
- `.onChange`, `.onAppear`, and `.onDisappear`;
- navigation and presentation modifiers.

Review inherited transactions. A local animation does not necessarily neutralize a parent transaction. Structural insertion/removal can change transition identity even when final pixels look correct.

Environment values are dependencies. Locale, calendar, time zone, content size, accessibility settings, color scheme, scene phase, and custom environment values must invalidate cached output when relevant.

## Accessibility and adaptation

Treat accessibility and localization as behavior:

- VoiceOver labels, values, traits, focus order, and announcements;
- keyboard navigation, shortcuts, and focus;
- Dynamic Type and long localized strings;
- right-to-left layout;
- pluralization and locale-specific dates/numbers;
- reduced motion/transparency;
- high contrast and differentiate-without-color;
- pointer/touch target size;
- empty, loading, failure, and retry states;
- macOS menu and command discoverability.

Attach accessibility identifiers to the actionable control, not a convenient container, unless the test contract intentionally targets the container.

## AppKit interoperability

For windows and scenes, establish whether state belongs to the app, scene, window, document, or feature. Review:

- restoration and reopening;
- duplicate windows;
- focused-scene command targeting;
- work after last-window closure;
- termination save/cancel policy;
- menu-bar-only lifecycle;
- commands with no active window or document.

For AppKit views, controllers, delegates, notifications, KVO, target-action, and bindings, inspect:

- main-thread and application-lifecycle requirements;
- owner/delegate/observer lifetime, weak or assign relationships, and retain cycles;
- registration, removal, invalidation, and callbacks after teardown;
- `@objc` selector exposure, signature compatibility, and nullability assumptions;
- responder-chain and first-responder changes;
- view-controller containment, appearance, window attachment, and backing-layer state;
- synchronous delegate callbacks and reentrancy during mutation;
- whether AppKit state or the Swift model is authoritative.

For `NSViewRepresentable` and `NSViewControllerRepresentable`, inspect:

- coordinator and delegate ownership;
- cycles and stale callbacks;
- idempotent `make`, `update`, and `dismantle` behavior;
- synchronous callbacks during construction/update;
- main-thread requirements;
- AppKit state versus SwiftUI source of truth;
- first responder and responder chain;
- identity replacement and teardown ordering.

For commands, menus, and shortcuts, inspect focused values, disabled state, selection ownership, system conflicts, validation, async command ownership, and error reporting.

## Runtime qualification

Source inspection alone is insufficient when behavior depends on actual SwiftUI/AppKit ordering.

Use the exact fresh build and inspect relevant:

- cache-hit and non-cached paths;
- placeholder, intermediate, success, empty, and failure frames;
- retained content with incomplete metadata or an empty list;
- fixed-size parent and minimum-size child combinations, including footer reachability;
- transition and inherited animation;
- hit testing and pass-through;
- insert, delete, reorder, and selection;
- rapid navigation or dismissal during work;
- window close/reopen and focus;
- Dynamic Type, localization, RTL, VoiceOver, keyboard, and reduced motion.

Do not claim visual or interaction validation when it was unavailable. A final screenshot does not prove intermediate layout, animation, focus, hit testing, or task lifetime.
