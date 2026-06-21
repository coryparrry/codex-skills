# Codex PR Packet Loop Autonomous Framework Design

Date: 2026-06-21

## Goal

Upgrade the experimental Codex PR packet loop from a thin manual skill suite into a solid autonomous loop framework that agents can follow through real multi-packet work without hidden human orchestration.

The framework stays entirely under `experimental/codex-pr-packet-loop/` for this pass. It does not promote skills into `skills/`, `plugins/codex-skills/skills/`, or package metadata.

## Problem

The current packet-loop skills have the right stage names, metadata, and basic CLI validation, but their instructions are too shallow for the workflow they are meant to control. They describe broad steps such as reserve a packet, run validation, review scope, and recommend merge order, but they do not yet define a strong autonomous protocol.

That weakness matters because this loop is stateful. Workers, reviewers, maintainers, and integrators can all mutate packet state, interpret PR state, and decide whether to retry, reslice, or stop. If those transitions are described as loose prose, agents will drift: they may implement adjacent packet work, trust worker summaries, skip stale lease recovery, update generated dashboards by hand, or merge/reject work without the required gate.

The target design treats the packet loop as a small distributed workflow system: stage skills are the human-readable interface, deterministic scripts own mechanical state transitions, and shared references define the protocol every skill must obey.

## Design Principles

- **Autonomous by contract.** Each skill states what it may do without asking, what it may recommend, and what requires a human stop.
- **State machine over narrative.** Packet status, lease state, PR state, review verdicts, and integration decisions are modeled as explicit transitions with preconditions and refusal behavior.
- **Router first.** Agents need a single entry skill that can inspect loop state and route to the next valid stage instead of guessing which packet skill to invoke.
- **Scripts own deterministic mechanics.** JSON validation, status transitions, lease expiry, dashboard generation, evidence indexing, and transition logs belong in CLI helpers where practical.
- **Skills own judgment.** Plan slicing, overlap classification, review verdicts, reslicing decisions, and merge-order recommendations remain visible in skills.
- **Worker claims are untrusted.** Worker success reports are treated as claims until review checks the packet record, diff, validation output, evidence files, and PR state.
- **Human gates are explicit.** Merge, force-push, branch deletion, PR closing, default-branch writes, destructive Git operations, and security-sensitive changes require direct human approval.
- **Promotion is out of scope.** The experimental framework must become testable before it is mirrored into the shipped skill bundle.

## Skill Topology

The suite should expose one controller/router skill and stage-specific skills.

| Skill | Responsibility |
|---|---|
| `codex-packet-loop` | Main router and controller. Inspect state, decide the next valid stage, run safe maintenance, and dispatch or recommend stage skills. |
| `codex-packet-loop-core` | Shared contract and deterministic CLI. Validate state, enforce transitions, manage leases, generate dashboards, and expose schema references. |
| `codex-packet-init` | Opt a repo into packet-loop state and verify the initial state is valid. |
| `codex-packet-slice` | Convert an approved plan into small packet records with dependencies, scope, risk, overlap notes, and validation routes. |
| `codex-packet-dispatch` | Select dependency-ready packets, enforce reserved-area and resource-lane constraints, create worker handoff prompts, and record leases. |
| `codex-packet-worker` | Execute exactly one leased packet in one worktree and record evidence before opening or preparing one PR. |
| `codex-packet-review` | Verify packet PRs against allowed scope, actual diff, validation evidence, overlap risk, and review feedback. |
| `codex-packet-integrate` | Sequence merge-eligible PRs, detect stale or overlapping work, recommend the next merge, and stop at human gates. |
| `codex-packet-maintain` | Run scheduled or manual maintenance: validate state, expire deterministic stale leases, repair safe drift, and report next actions. |

The router skill should be the default entry point for vague requests such as "continue the packet loop", "advance packet work", "check packet state", or "run packet automation". Stage skills still remain directly invokable when the user or another skill knows the exact stage.

## Shared References

Each stage skill should stay concise and load shared references only when needed.

| Reference | Purpose |
|---|---|
| `references/workflow-protocol.md` | End-to-end loop contract, actors, routing rules, and next-skill map. |
| `references/state-machine.md` | Statuses, allowed transitions, human-gated transitions, state probes, and refusal behavior. |
| `references/autonomy-policy.md` | Safe autonomous actions, recommend-only actions, and hard stop conditions. |
| `references/handoff-contracts.md` | Exact fields for slicer output, dispatch prompts, worker reports, review verdicts, integration recommendations, and maintenance reports. |
| `references/superpowers-plan-adapter.md` | How packet-loop consumes Superpowers plans, invokes `superpowers:writing-plans`, validates child plan shape, and hands plans to workers. |
| `references/evidence-contract.md` | Required evidence files, validation output shape, checksums or summaries, and how reviewers verify claims. |
| `references/overlap-policy.md` | File, area, interface, behavior, test, generated-file, dependency, and documentation overlap handling. |
| `references/recovery-playbook.md` | Stale lease recovery, blocked packet handling, failed validation loops, bad PRs, reslicing, and state repair. |
| `references/behavioral-evals.md` | Manual and scripted scenarios used to test whether agents follow the loop. |

The existing `state-contract.md`, source plan, overlap strategy, and template files should be folded into these focused references rather than duplicated in each `SKILL.md`.

## State Model

Structured state remains authoritative under `.codex/packet-loop/` in target repos:

- `.codex/packet-loop/manifest.json`
- `.codex/packet-loop/packets/<packet-id>.json`
- `.codex/packet-loop/events.jsonl`
- `.codex/packet-loop/evidence/<packet-id>/`
- `docs/superpowers/plans/packet-loop/<packet-id>-<slug>.md` as generated child implementation plans
- `docs/codex/packet-loop.md` as generated human-readable output

The manifest should include repository identity, default branch, target branch, active controller identity when known, packet order, current loop mode, dispatch policy, serialized resource lanes, and updated timestamp. There should be no default fixed active-worktree cap; dispatch is bounded by the dependency graph, review capacity, resource-lane capacity, and what the controller can actively monitor. A user- or repo-configured cap may exist only as an explicit override.

Each packet record should include:

- identity: `id`, `title`, `goal`
- lifecycle: `status`, `updated_at`, `status_reason`
- scope: `allowed_scope`, `expected_touched_areas`, `avoid_scope`, `reserved_areas`
- sequencing: `dependencies`, `blocked_by`, `parallel_safe`
- risk: `risk`, `overlap_notes`, `human_review_required`
- plan: `parent_plan_path`, `child_plan_path`, `source_plan_refs`, `plan_format_status`
- execution: `validation.commands`, `branch`, `worktree`, `lease`
- PR state: `pr.url`, `pr.number`, `pr.state`, `pr.head`, `pr.base`
- evidence: `evidence_paths`, `last_validation`, `worker_report`, `review_report`
- blockers: `blockers`, `needs_reslice_reason`

Dashboard Markdown is generated from JSON. Agents may summarize it, but must not treat it as authoritative when JSON exists.

## State Machine

The packet lifecycle should be explicit:

```text
candidate
ready
reserved
in-progress
pr-open
reviewing
needs-fix
blocked
needs-reslice
merge-eligible
merged
rejected
```

Allowed autonomous transitions:

```text
candidate -> ready
candidate -> blocked
candidate -> needs-reslice
ready -> reserved
reserved -> in-progress
reserved -> ready
in-progress -> pr-open
in-progress -> needs-fix
in-progress -> blocked
in-progress -> needs-reslice
pr-open -> reviewing
reviewing -> needs-fix
reviewing -> blocked
reviewing -> needs-reslice
reviewing -> merge-eligible
needs-fix -> reserved
needs-fix -> blocked
blocked -> ready
blocked -> needs-reslice
needs-reslice -> candidate
```

Human-gated transitions:

```text
merge-eligible -> merged
any live status -> rejected when useful work or an open PR would be discarded
any transition involving merge, force-push, branch deletion, PR closing, default-branch write, destructive Git operation, or security-sensitive change
```

Every transition should log an event with actor, prior status, new status, reason, timestamp, and evidence path when available. The CLI should enforce transitions where possible.

## Autonomous Controller Behavior

`codex-packet-loop` is the controller skill. It should run this loop when asked to advance work:

1. Resolve repo root and read repo instructions.
2. Load the core contract and validate packet state.
3. Run safe maintenance first: expire deterministic stale leases, regenerate dashboard, and report invalid records.
4. Inspect active leases, ready packets, PR-open packets, reviewing packets, blocked packets, and merge-eligible packets.
5. Choose the next safe action in priority order:
   - repair invalid deterministic state
   - review PR-open or stale packet PRs
   - dispatch dependency-ready packets that fit active monitoring and resource-lane capacity
   - prepare integration recommendation for merge-eligible packets
   - reslice or report blocked work when no safe autonomous action remains
6. Invoke or instruct the exact next stage skill.
7. Stop with a compact state report when a human gate, ambiguous product decision, repeated failure, or unsupported tool boundary is reached.

The controller may autonomously:

- validate state
- expire stale leases for packets with no PR and expired TTL
- regenerate dashboards
- reserve ready packets when dependencies, overlap checks, and resource-lane constraints pass
- create worker handoff prompts
- recommend but not execute merges
- mark packets blocked or needs-reslice when evidence supports it

The controller must stop before:

- merge
- default-branch write
- force-push
- branch deletion
- PR closing
- discarding useful work
- security-sensitive tradeoff
- external submission beyond opening or updating a PR when the user has not authorized that action

## Thread-Derived Controller Pattern

Thread `019ee489-a02e-73b1-b60d-ea6350507d25` provides the closest local prototype for this framework. It coordinated multiple U-phase worktree threads, ran each through review gates, monitored their worktree status, steered only the lanes that drifted or blocked, and integrated completed results back into the primary branch.

The reusable pattern is:

1. Verify live repo state, current branch, existing plan, prior evidence, dirty files, and available worker tooling before dispatch.
2. Create one isolated worker thread/worktree per phase or packet, all starting from the same clean target state.
3. Give each worker a narrow packet boundary, known prior evidence, required gate workflow, validation route, stop conditions, branch/commit policy, and "do not push" rule unless pushing is explicitly authorized.
4. Poll active thread summaries and each worktree's `git status` repeatedly while workers run.
5. Inspect file names and diff shape before reading full diffs, so the controller can catch overlap or scope drift early without taking ownership of the worker's implementation.
6. Send steering messages only to workers that need intervention: detached HEAD commit policy, scope drift, unstable validation loops, evidence privacy leaks, or ambiguous blockers.
7. Keep the primary checkout clean until a worker has completed its packet gate and committed its scoped result.
8. Integrate completed packet commits serially, rechecking overlap and validation between integrations.
9. Run an integrated review/validation pass only after packet outputs are collected onto the target branch.
10. Treat slow or stuck auxiliary agents as bounded waits, then close or bypass them when their output is no longer worth blocking the loop.

This is not the exact final packet-loop style because packet-loop state should be structured and script-backed, not inferred only from thread messages and Git status. It is still a strong operating model for the controller skill: the controller must act as an active supervisor, not just a queue launcher.

## Thread-Derived PR Queue and Scheduler Pattern

Thread `019eea9e-364f-7523-baca-20b71e2bfac8` provides a strong prototype for plan slicing into PR packets and an orchestrator build order. It began as a request to split one large UIShot plan into 10-20 reviewable PRs, then evolved from a simple PR list into a dispatchable scheduler contract.

The reusable pattern is:

1. Create a PR packet template with title, goal, allowed areas, out-of-scope areas, implementation notes, validation command, risk, parallel safety, dependencies, branch name, expected PR size, and human-review-before-implementation flag.
2. Slice the source plan into small worktree-friendly PR packets, preferably one purpose, 1-4 files, under roughly 300 changed lines, exact validation commands, and explicit dependencies.
3. Add an orchestrator build plan above the packet list so the controller owns dispatch, dependency tracking, merge order, review readiness, and worker rebase timing.
4. Dispatch only after every dependency is merged into the integration base, not merely implemented in another worktree.
5. Do not impose an arbitrary active-worktree cap. Dispatch as many dependency-ready packets as the controller can actively monitor, subject to review capacity, overlap risk, and serialized resource lanes.
6. Serialize scarce validation or proof lanes. In the UIShot prototype, XCTest and Computer Use each had a single active lane; workers could implement and run static checks in parallel but had to request the lane before running those commands.
7. Merge one PR at a time. After each merge, tell active downstream workers the new base commit and whether they must rebase.
8. Treat non-parallel-safe packets as speculative only when the controller has an explicit rebase/merge gate.
9. Mark coordinator-owned final closeout packets as not suitable for blind parallel agents when their proof depends on the final combined state.

The packet-loop framework should preserve this shape while moving the source of truth from ad hoc Markdown into script-backed packet JSON. Human-readable queue and build-order Markdown can still be generated or maintained as handoff artifacts, but JSON remains authoritative.

## Superpowers Plan Adapter Pattern

The packet loop should sit alongside Superpowers, not replace it. The main controller receives a large approved Superpowers implementation plan, uses `superpowers:writing-plans` to produce one Superpowers-compatible child plan per packet, and verifies each child plan before dispatch. Worker worktrees then execute normal Superpowers plans, so `superpowers:subagent-driven-development`, `superpowers:executing-plans`, `superpowers:test-driven-development`, code review, verification, and finishing-branch behavior keep working as intended.

Adapter rules:

1. The controller may slice only from an approved Superpowers implementation plan, not from a raw spec unless the user explicitly asks to create plans first.
2. Child plans must use the standard Superpowers implementation-plan header, including the required sub-skill line.
3. Child plans must carry parent plan path, source task or section references, packet id, branch name, dependencies, allowed files, out-of-scope files, validation commands, resource lanes, and evidence requirements.
4. The controller verifies each child plan for required header, task checkbox syntax, no placeholders, exact file paths, exact validation commands, dependency references, and packet metadata before creating or dispatching the packet.
5. Packet JSON stores the child plan path and source references. Workers receive the child plan path as their primary instruction, not an ad hoc prompt.
6. A large Superpowers task may split into multiple child plans only when each child plan preserves a complete test-implementation-validation loop. The adapter must never split RED from GREEN or send a dependency consumer before its producer is merged.
7. The controller owns orchestration around those child plans: dependency graph, worktree assignment, serialized resource lanes, worker supervision, review, and integration.

## Stage Skill Contracts

### Init

`codex-packet-init` creates the state directory, manifest, empty packet directory, event log, and generated dashboard. It refuses to overwrite existing state without explicit approval. It ends by reporting the next valid stage: slice an approved plan or run the controller.

### Slice

`codex-packet-slice` reads an approved Superpowers implementation plan and creates one Superpowers-compatible child implementation plan per packet. It must use `superpowers:writing-plans` for the child plan shape, then verify the resulting child plans before packet records are marked ready. It must classify dependencies, parallel safety, overlap risk, allowed scope, avoid scope, validation commands, resource-lane needs, and likely human-review requirements. It should also produce or update a human-readable packet queue/build-order artifact when useful, but packet JSON remains authoritative. It should propose packet boundaries before writing records when the plan is broad or ambiguous.

### Dispatch

`codex-packet-dispatch` picks ready packets only after checking dependencies, monitoring capacity, serialized resource-lane availability, live reserved areas, expected overlap, worker route availability, and child plan validity. Its output is a worker handoff that names the packet id, child plan path, worktree, branch, validation command, resource lane requests, allowed scope, avoid scope, evidence requirements, stop conditions, and report path.

### Worker

`codex-packet-worker` runs only in the assigned worktree for the leased packet. It validates the lease, reads the packet child plan, invokes the Superpowers execution skill named by that child plan, transitions to `in-progress`, implements the smallest packet-scope change, runs the packet validation route, fixes only packet-caused failures, records evidence, and prepares or opens one PR. It stops after two failed fix attempts with the same root cause or immediately when scope expands beyond the packet.

### Review

`codex-packet-review` treats worker output as claims. It verifies the diff, PR metadata, packet record, evidence files, validation freshness, overlap risk, and allowed scope. It produces exactly one verdict: `needs-fix`, `blocked`, `needs-reslice`, or `merge-eligible`. It should never mark work merge-eligible on worker summary alone.

### Integrate

`codex-packet-integrate` builds a merge matrix for merge-eligible packets, checks stale branches, detects overlap, recommends a serial merge order, and stops for approval. After the human confirms a merge has happened, it may update only that packet's state and then revalidate remaining packets.

### Maintain

`codex-packet-maintain` is safe for scheduled runs. It validates state, expires deterministic stale leases, regenerates dashboards, reports invalid records, and identifies the next safe stage. It should not make judgment-heavy repairs unless the evidence is deterministic.

## Evidence Contract

Each worker packet should write evidence under `.codex/packet-loop/evidence/<packet-id>/`.

Required evidence:

- `worker-report.md`: what changed, files touched, validation run, result, concerns, and next requested stage
- `validation-<timestamp>.txt`: command, cwd, exit code, and output summary or full output when short
- `diffstat-<timestamp>.txt`: changed files and diffstat against the packet base
- `scope-check.json`: declared allowed scope, actual touched files, and pass/fail

Review evidence:

- `review-report.md`: verdict, checks performed, exact reason, required fix or integration note
- `pr-state.json`: PR number, URL, branch, base, state, and review/CI summary when available

Integration evidence:

- `merge-matrix.md`: candidate order, overlap categories, stale/conflict status, and recommendation
- `integration-report.md`: human-gated action requested or post-merge state update performed

Maintenance evidence:

- `maintenance-report.md`: expired leases, invalid records, repairs performed, next safe action

Evidence file names can vary by timestamp, but packet records must store their paths so reviewers can inspect them.

## Behavioral Validation

The existing validation script should keep checking frontmatter, `agents/openai.yaml`, and CLI tests, but the new framework also needs behavioral scenarios.

Initial scenarios:

1. **Router finds next stage.** Given initialized state with ready packets, the router validates state and selects dispatch.
2. **Dispatch blocks overlap.** Given two ready packets with colliding reserved areas and one live lease, dispatch refuses the colliding packet.
3. **Worker stops on scope expansion.** Given a packet whose implementation needs avoid-scope files, the worker marks blocked or needs-reslice rather than editing them.
4. **Review distrusts worker summary.** Given a PR that claims success but touches outside allowed scope, review returns needs-fix or needs-reslice.
5. **Maintenance expires stale lease.** Given an expired lease with no PR and no recent evidence, maintain returns the packet to ready and logs the repair.
6. **Integration stops before merge.** Given merge-eligible packets, integrate produces a merge recommendation and does not merge.
7. **Recovery reslices bad packet.** Given repeated validation failure caused by packet boundary mismatch, review or maintain routes to needs-reslice with a reason.
8. **Controller supervises active workers.** Given multiple active packet leases, the controller polls thread summaries and worktree dirt, detects one drifting packet, sends a scoped steering message, and leaves non-drifting packets alone.
9. **Scheduler has no fixed worktree cap.** Given many dependency-ready packets, the controller does not stop at an arbitrary global worker count; it dispatches only as far as active monitoring, review capacity, overlap constraints, and resource lanes allow.
10. **Validation lanes serialize scarce tools.** Given two packets that both need an XCTest or Computer Use lane, the controller lets implementation continue in parallel but grants only one matching validation/proof lane at a time.
11. **Slicer emits valid Superpowers child plans.** Given a large approved Superpowers implementation plan, slice creates child plans with the required header, task checkboxes, source references, packet metadata, exact validation commands, and no placeholders.
12. **Worker executes child plan, not ad hoc packet prose.** Given a ready packet with a child plan path, dispatch tells the worktree to execute that plan with the required Superpowers execution skill.

These scenarios may start as deterministic CLI tests plus prompt-level fixtures. A later real eval should run agents through a small repo trial and grade traces, tool calls, state mutations, and artifacts.

## Inspiration Adapted

The design borrows structural patterns from three reference skill systems:

- `obra/superpowers`: mandatory skill routing, hard gates, checklists, handoff artifacts, verification before completion, and subagent-driven execution.
- `garrytan/gstack`: router-style entrypoints, explicit skill routing tables, workflow preflight state, and generated skill packets that keep repeated rules consistent.
- `EveryInc/compound-engineering-plugin`: phase-based workflows, state-machine Git reasoning, script-first deterministic processing, and clear separation between planning, execution, proof, and integration.

This framework should not copy their bulk directly. It should adapt the deeper idea: a skill suite must be detailed enough that the agent knows what to invoke, what state to trust, when to stop, and what artifact proves each claim.

## Acceptance Criteria

- The experimental suite has a first-class `codex-packet-loop` controller skill.
- Every stage skill references the shared workflow protocol and names its next valid stage.
- The shared state-machine reference defines statuses, transitions, human gates, and refusal behavior.
- The shared handoff and evidence contracts define required artifacts for dispatch, worker, review, integration, and maintenance.
- The CLI or validation script checks that required references and routing hooks exist.
- Deterministic state operations use scripts where supported rather than hand-editing JSON.
- The validation suite includes behavioral scenarios beyond static metadata checks.
- The controller workflow includes active worker supervision: polling thread state, checking worktree dirt, steering drifting workers, and integrating completed packet outputs serially.
- The scheduler model has no default fixed active-worktree cap and includes serialized resource lanes for scarce validation or visual proof tools.
- Packet slicing produces and verifies Superpowers-compatible child implementation plans before dispatch, preserving normal Superpowers execution inside each worktree.
- The design remains scoped to `experimental/codex-pr-packet-loop/` and does not modify shipped skill mirrors.

## Implementation Defaults

- Create a new top-level controller skill named `codex-packet-loop`. Keep `codex-packet-loop-core` focused on shared contract, references, CLI, and tests.
- Implement behavioral scenarios first as Python fixture tests for deterministic state transitions, plus prompt fixture files for later agent-trace evals.
- Workers prepare one PR by default. They may open or update a PR only when direct user instructions or repo-local packet-loop configuration explicitly allow that external action.
- Refactor `packet_loop.py` only where needed to add clear subcommands for state transitions, evidence indexing, and dashboard generation. Avoid a broad CLI rewrite during the first framework upgrade.
