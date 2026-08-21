---
name: luna-advisor
description: Use when Luna is the active implementation agent and a task needs one bounded, read-only Sol advisory packet because its ambiguity, complexity, verification weakness, or consequence exceeds a clear Luna-only lane.
---

# Luna Advisor

Use this skill when Luna remains the main implementation agent and a task needs
stronger judgment than a clear Luna-only lane provides. It is conditional, not
a mandatory preflight for every Luna task. The skill is repo-agnostic and does
not implement provider-specific or benchmark-specific behavior.

When `luna-advisor` is active, its specific Luna-as-implementer contract
governs over generic advisor or coordinator routing guidance. It does not
override system, developer, repository, or user instructions, authority,
authorization, or safety boundaries. Sol remains read-only and advisory.

## Model and authority gate

First verify the active root model from runtime or task metadata. The contract
is active only when the main agent is Luna, such as `gpt-5.6-luna`. This skill
cannot change the current root model. If the active model is missing or is not
Luna, disclose the exact mismatch, do not claim that this workflow is active,
and stop before spawning Sol or implementing.

Keep the normal user authorization boundary. Luna owns the final scope,
implementation, diff review, and validation. The Sol advisor is read-only and
must not edit files, stage or commit, push, open a PR, perform external
mutations, or delegate to another agent.

Use collaboration subagent tools for Sol. Never use Codex app thread tools for
this workflow.

## Route the task before advice

After the model gate, first decide whether the task needs Sol. Stay Luna-only
when the requested outcome, bounded scope, implementation approach, preserved
constraints, and objective validation are known; the work is local and
reversible; and mistakes are cheap to detect or recover. A large repository,
long prompt, ordinary multi-file edit, or desire for reassurance does not by
itself require Sol. Record the Luna-only decision and continue without
spawning an advisor.

Before applying these triggers, resolve product intent and authorization. If
the requested behavior, authority to change it, or an external or destructive
scope decision is unresolved, ask the user first. Sol must not decide those
questions, even when the user explicitly asks for Sol advice.

After that gate, invoke exactly one Sol advisor when any of these conditions
applies:

- multiple viable approaches have material tradeoffs Luna should not choose
  without stronger judgment;
- current evidence cannot yet bound the implementation safely;
- unfamiliar or cross-cutting architecture, provider, or integration behavior
  matters;
- a narrow evidence pass leaves the root cause uncertain in subtle debugging;
- security, authentication or authorization, concurrency, data integrity,
  migration or rollback, compatibility, production, or release-critical
  judgment is involved;
- success cannot be verified strongly, or a wrong implementation would be
  expensive;
- Luna has a materially failed or contradictory attempt, or another bounded
  check cannot reduce the uncertainty; or
- the user explicitly requests Sol advice.

Do not use Sol to decide unresolved product intent or authorize scope. Ask the
user instead. Do not consult Sol merely for a permission, tool, or environment
failure unless it exposes a technical decision. The skill may activate before
implementation or mid-task when one of these triggers first appears. If no
trigger remains after evidence gathering, keep the Luna-only decision.

## Gather evidence before advice

Only when the routing gate triggers, Luna must inspect enough current state to
make the prompt self-contained. Include all of the following:

- the concrete requested outcome and acceptance criteria;
- verified current behavior, relevant code or artifacts, and the evidence for
  any failure or gap;
- the exact candidate files, modules, or responsibility boundary;
- user constraints, authorization, and behavior that must be preserved;
- every user-specified preservation or failure invariant, copied into the
  prompt so it can be traced to preservation and validation evidence;
- known unknowns and implementation choices that need advice;
- available deterministic tests, commands, or observable checks;
- external-system, security, lifecycle, reliability, compatibility, or data
  boundaries that the advisor must respect.

Choose the Sol effort from this evidence. Use Sol Low only for one narrow
decision between well-defined options when the relevant files, scope,
behavior, and approach are already known; the work is local and reversible;
the evidence and checks are complete and deterministic; and no material
design, security, cross-system, state or lifecycle, compatibility, or
reliability judgment remains. Use Sol Medium when ambiguity spans multiple
concerns, the diagnosis or approach remains unresolved, or the consequences
are meaningful. Integration or runner-style work with unresolved design
belongs in Medium. When uncertain, choose Medium.

Immediately before composing or spawning Sol, and only after this trigger gate
fires, read [the Sol advisory packet reference](references/sol-advisory-packet.md).
Clear Luna-only work must not read that reference.

If the gate triggered, spawn exactly one advisor with the selected effort and
retain the returned advisor handle or ID:

```text
advisor_handle = spawn_agent({
  agent_type: "default",
  model: "gpt-5.6-sol",
  reasoning_effort: "low" | "medium",
  fork_turns: "none",
  prompt: <the completed Sol prompt below>
})
```

Use that exact retained handle or ID for any later
`collaboration.followup_task`. Never target a different advisor or spawn a
replacement.

Do not spawn a reviewer, critic, second advisor, or nested agent. The Sol
assignment must explicitly say that it is read-only and advisory only.
If the collaboration tool is unavailable, report the advisory path as blocked;
do not substitute a Codex app thread, another model, or an unbounded local
implementation.

## Accept the execution packet

Accept Sol's response only when it gives every field below with concrete,
bounded instructions that Luna can follow without guessing. The required
prompt template and packet fields live in the reference loaded above.

Before accepting it, Luna verifies that every user-specified preservation or
failure invariant appears in `preserve` and maps to a relevant `validation` or
`success_evidence` item when it is testable. Reject any packet that omits,
weakens, or leaves an invariant unmapped.

If the packet is incomplete, ambiguous, or leaves Luna to infer scope, do not
start implementation. Use `collaboration.followup_task` on the same Sol
advisor to request only the missing bounded instructions, quoting the missing
fields and the original evidence. Do not create another advisor. If Sol
identifies unresolved product intent or authorization, stop and ask the user.
If the follow-up is still incomplete, stop and report the missing packet
fields.

## Implement and validate

After accepting the packet, Luna implements it directly and only within the
accepted scope. Review the complete diff for accidental expansion, preserve
unrelated dirty work, and run the packet's validation plus any proportionate
final checks. Do not treat Sol's advice as proof that the change works. If the
task began Luna-only and a trigger appears during implementation, stop and
activate this workflow before continuing.

If implementation reveals contradictory evidence, a missing user decision,
an unsafe expansion, or a failed assumption in the packet, stop. Send the raw
new evidence to the same Sol advisor with `collaboration.followup_task` and
request a bounded correction or a stop decision. Do not silently reinterpret
the packet. Allow at most one bounded follow-up total per invocation or task,
whether it completes the initial packet or addresses the first invalidated
premise. After that follow-up is used, stop if the issue remains unresolved;
do not start an advice loop.

Luna owns final integration and validation. Report the active-model check, the
routing decision (Luna-only or Sol-assisted), and, when Sol was used, its model
and effort, packet decision, changed scope, exact validation results, and any
unresolved or unavailable evidence. Never claim the Luna-main/Sol-advisor
contract was active when the model gate failed.
