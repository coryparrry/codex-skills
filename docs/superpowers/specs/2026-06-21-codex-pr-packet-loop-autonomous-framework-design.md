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
| `codex-packet-dispatch` | Select ready packets, enforce active lease limits, reserve scope, create worker handoff prompts, and record leases. |
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
- `docs/codex/packet-loop.md` as generated human-readable output

The manifest should include repository identity, default branch, target branch, active packet limit, active controller identity when known, packet order, current loop mode, and updated timestamp.

Each packet record should include:

- identity: `id`, `title`, `goal`
- lifecycle: `status`, `updated_at`, `status_reason`
- scope: `allowed_scope`, `expected_touched_areas`, `avoid_scope`, `reserved_areas`
- sequencing: `dependencies`, `blocked_by`, `parallel_safe`
- risk: `risk`, `overlap_notes`, `human_review_required`
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
   - dispatch ready packets within active lease limits
   - prepare integration recommendation for merge-eligible packets
   - reslice or report blocked work when no safe autonomous action remains
6. Invoke or instruct the exact next stage skill.
7. Stop with a compact state report when a human gate, ambiguous product decision, repeated failure, or unsupported tool boundary is reached.

The controller may autonomously:

- validate state
- expire stale leases for packets with no PR and expired TTL
- regenerate dashboards
- reserve ready packets when dependencies and overlap checks pass
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

## Stage Skill Contracts

### Init

`codex-packet-init` creates the state directory, manifest, empty packet directory, event log, and generated dashboard. It refuses to overwrite existing state without explicit approval. It ends by reporting the next valid stage: slice an approved plan or run the controller.

### Slice

`codex-packet-slice` reads an approved plan and creates packet records small enough for reviewable PRs. It must classify dependencies, parallel safety, overlap risk, allowed scope, avoid scope, validation commands, and likely human-review requirements. It should propose packet boundaries before writing records when the plan is broad or ambiguous.

### Dispatch

`codex-packet-dispatch` picks ready packets only after checking dependencies, active lease limit, live reserved areas, expected overlap, and worker route availability. Its output is a worker handoff that names the packet id, worktree, branch, validation command, allowed scope, avoid scope, evidence requirements, stop conditions, and report path.

### Worker

`codex-packet-worker` runs only in the assigned worktree for the leased packet. It validates the lease, transitions to `in-progress`, implements the smallest packet-scope change, runs the packet validation route, fixes only packet-caused failures, records evidence, and prepares or opens one PR. It stops after two failed fix attempts with the same root cause or immediately when scope expands beyond the packet.

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
- The design remains scoped to `experimental/codex-pr-packet-loop/` and does not modify shipped skill mirrors.

## Implementation Defaults

- Create a new top-level controller skill named `codex-packet-loop`. Keep `codex-packet-loop-core` focused on shared contract, references, CLI, and tests.
- Implement behavioral scenarios first as Python fixture tests for deterministic state transitions, plus prompt fixture files for later agent-trace evals.
- Workers prepare one PR by default. They may open or update a PR only when direct user instructions or repo-local packet-loop configuration explicitly allow that external action.
- Refactor `packet_loop.py` only where needed to add clear subcommands for state transitions, evidence indexing, and dashboard generation. Avoid a broad CLI rewrite during the first framework upgrade.
