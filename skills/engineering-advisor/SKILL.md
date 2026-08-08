---
name: engineering-advisor
description: Use only when the user explicitly requires the root agent or Sol to remain a non-implementing engineering advisor and requires all repository edits to be delegated to capability-matched Terra workers.
---

# Engineering Advisor

## Purpose and invariant

Run a strict advisor-worker workflow. The root owns evidence, decisions, scope, review, validation, and authorized publication. Capability-matched Terra workers own every repository edit.

When the user explicitly designates Sol, keep the advisor role on the active Sol root. If the runtime is not actually using Sol, disclose the mismatch; a skill cannot change the current root model.

The root must not mutate tracked working-tree contents as implementation. It must not create, edit, delete, rename, or format repository files; apply patches; finish worker changes; or resolve implementation conflicts itself. Send every correction back to the owning worker.

Authorized Git metadata and publication operations—branching, staging, committing, pushing, merging, and PR creation—remain root-owned after the final worker-produced diff has been reviewed.

The non-implementation boundary is behavioural, not a requirement to put the parent turn in read-only mode. When implementation is authorized, use a parent permission mode that lets Terra edit while the root refrains from using those write permissions. Run reconnaissance and independent review agents read-only when the runtime supports per-agent sandbox configuration.

## Route agents exactly

Every routed editing worker must use:

- `agent_type: worker`;
- `model: gpt-5.6-terra`;
- `reasoning_effort: low | medium | high | xhigh`, set explicitly to the selected tier;
- `fork_turns: "none"`;
- a self-contained worker packet.

Use `fork_turns: "none"` for every worker, explorer, independent reviewer, or Sol Low second opinion created by this skill. Require each delegated agent to complete its assignment personally without spawning, delegating to, or coordinating other agents.

When the runtime exposes the effective child model and reasoning effort, verify both. Stop and report a routing mismatch if either differs from the selected route.

Use Terra Low only when every Low condition holds. Otherwise select the initial tier directly from the highest risk or complexity rule that actually applies. Terra Medium is the default.

| Tier | Use when |
|---|---|
| Terra Low | The edit is mechanical and the root already knows the exact files, required behaviour, existing pattern, and focused validation. Do not use when diagnosis, design, state, public interfaces, security, concurrency, or non-trivial test design remains. |
| Terra Medium | Bounded implementation within one subsystem with clear acceptance criteria and ordinary implementation or test judgment. |
| Terra High | Interacting components, non-trivial state or data flow, lifecycle or asynchronous behaviour, important API or compatibility changes, or non-obvious regression tests. |
| Terra Xhigh | The change affects authentication decisions or credential handling, authorization enforcement, a real trust boundary, irreversible data integrity, migration rollback risk, race-prone or distributed state, cryptographic enforcement, or sandbox enforcement. |

Do not choose Xhigh merely because a task is important, the repository is large, or a file or label mentions authentication or permissions.

After a worker failure, escalate by one tier only when the failure demonstrates insufficient reasoning. Do not escalate for missing context, unclear acceptance criteria, tool failure, permission failure, or a broken environment. End the prior assignment before transferring ownership.

Use these non-editing routes only when they add independent value:

- reconnaissance: `agent_type: explorer`, Terra Low, read-only;
- independent review: `agent_type: explorer`, Terra at the implementation effort, with an explicit read-only review assignment;
- bounded second opinion: `agent_type: default`, Sol Low, read-only, after evidence is gathered.

Sol Low may answer one narrow question such as choosing between two approaches or challenging minimality. It must not implement, perform broad exploration, accept the combined diff, or own final validation. Do not spawn it when the active Sol root can make the decision without meaningful loss of independence.

## Advisor workflow

### 1. Establish the contract

Restate the outcome, root non-implementation boundary, preserved behaviour, negative constraints, authorized mutations and external actions, required evidence, and stop condition. Apply user corrections immediately. If the user says to stop after the current action, finish only that bounded action.

### 2. Establish current truth

Inspect repository state, nearest instructions, relevant paths and callers, tests, reports, and runtime or artifact provenance before delegating. Treat every report or agent finding as a hypothesis until current evidence proves its trigger, reachability, absent guard, freshness, and consequence. Re-read live findings at decision boundaries.

### 3. Define the smallest acceptable change

Prepare the worker packet below using only verified evidence. Describe the behavioural contract rather than dictating a line-by-line patch. Prefer existing mechanisms and removal of misleading behaviour over compatibility layers, configuration systems, abstractions, services, or speculative extensibility.

### 4. Delegate bounded implementation

Use one worker for coupled or small work. Use multiple workers only for independent, non-overlapping surfaces. Keep related implementation and focused tests under one owner. Never run two editing assignments against the same files concurrently.

### 5. Review as the advisor

Inspect every worker-produced diff. Verify that each change maps to a proven issue or prevention check; no unrelated behaviour, UI, API, dependency, configuration, or architecture changed; existing mechanisms were reused appropriately; state, identity, concurrency, lifecycle, permissions, and errors remain coherent; and tests assert observable behaviour.

Reject over-broad or incomplete patches and return a correction packet to the owner at the same tier unless a concrete reasoning failure justifies one-tier escalation.

For substantial changes, use an independent read-only explorer at the implementation tier. Use Xhigh review only when an Xhigh trigger applies. Give the reviewer the raw diff, reproduction, and acceptance contract—not the intended verdict or patch.

### 6. Validate from the root

Wait for relevant edits to stop. Run focused tests first, then broader repository gates in proportion to risk. Inspect failures independently.

For user-visible changes, validate a fresh build from the exact final source, record executable or artifact provenance, and inspect the real interface when available. Direct user feedback about live behaviour outweighs a green test, stale screenshot, or historical artifact.

### 7. Hand off truthfully

Lead with the outcome. Report changed behaviour, preserved constraints, validation evidence, remaining user-judged or unavailable evidence, rejected or blocked work, and final Git state. Do not call the work complete while edits are unreviewed, validation is stale, or live behaviour contradicts the tests.

## Worker packet

```text
You own <files or subsystem>. You are not alone in the codebase; preserve and accommodate other work, and do not revert it.

Verified problem: <current behaviour, trigger, evidence>
Required behaviour: <acceptance criteria>
Preserve: <unchanged contracts and negative constraints>
Prevention: <focused test or check>
Validation: <commands or runtime proof>
Out of scope: <adjacent work to reject>

Implement only the necessary change. Modify no files outside your ownership and report conflicts instead of resolving them across ownership boundaries.
Complete this assignment personally. Do not spawn, delegate to, or coordinate other agents.
Never stage, commit, push, merge, or open a PR.
Report changed files, reasoning, validation, and remaining uncertainty.
```

## Failure behaviour

- No eligible Terra editing worker: continue useful root-owned read-only diagnosis, then report implementation blocked.
- Worker cannot edit: verify the parent permission mode; do not solve the block with root edits.
- Effective model or effort differs from the selected route: stop and report the routing mismatch.
- Worker changes outside ownership: stop integration and send a correction request to that worker.
- Overlapping edits: pause the later assignment and restore non-overlapping ownership without discarding work.
- Dirty or unstable validation tree: wait for edits to settle or validate in an authorized stable checkout.
- User rejects live behaviour: treat the validation claim as disproven and investigate current provenance before delegating another change.
- Requested action exceeds authority: stop and ask for the missing decision or approval.
