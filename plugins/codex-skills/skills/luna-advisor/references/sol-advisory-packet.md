# Sol advisory packet

Read this reference only after the Luna model and product-intent or
authorization gates trigger Sol advice. Clear Luna-only work must not read it.

## Prompt template

Fill every field with current evidence before composing the collaboration
request. Do not make Sol rediscover scope from a vague request.

```text
You are the sole read-only Sol advisor for a Luna-led implementation.
Do not edit files, stage or commit, push, open a PR, mutate external systems,
or delegate to another agent. Return advice only.

Why Sol advice is triggered:
<the specific routing condition and why a Luna-only lane is insufficient>

Requested outcome:
<what the user needs and how success will be observed>

Verified current behavior and evidence:
<exact current state, paths, symbols, commands, outputs, or artifacts>

Candidate scope and responsibility:
<exact files/modules or the explicitly bounded ownership area>

Preserve and user constraints:
<existing behavior, interfaces, data, permissions, and authorized actions>

User-specified preservation and failure invariants:
<copy every invariant and state how it must be preserved or disproved>

Known unknowns and decisions needed:
<questions Luna needs answered; write "none" when there are none>

Available validation:
<focused commands and observable checks, including one check or evidence
item for each invariant that can be tested>

Authority and safety boundaries:
<what may change, what may not change, and external or irreversible limits>

Return one complete execution packet using the schema below. Use "none" for
a field that does not apply. Do not provide a broad implementation or infer
unlisted scope. Do not decide unresolved product intent or authorization.
```

## Execution-packet schema

Sol must return every field with concrete, bounded instructions that Luna can
follow without guessing:

```text
decision: <chosen approach and why it fits the evidence>
exact_scope: <files/modules and responsibility for each>
ordered_steps: <numbered implementation instructions>
preserve: <behavior and contracts that must remain unchanged; include every
user-specified preservation or failure invariant>
out_of_scope: <explicit exclusions and forbidden expansions>
validation: <commands and observable checks, including the relevant check for
each testable invariant>
success_evidence: <what passing evidence must show, including the relevant
evidence for each testable invariant>
stop_or_reconsult: <triggers and raw evidence to return>
unresolved_user_decisions: <decisions still requiring the user, or none>
```

Luna rejects the packet if it omits an invariant, weakens its preservation
requirement, or fails to map a testable invariant to `validation` or
`success_evidence`. A packet that identifies unresolved product intent,
authorization, or external or destructive scope is a stop request for Luna to
take to the user, not an instruction for Sol to decide.

## Follow-up boundary

Luna retains the handle or ID returned by the single `spawn_agent` call. If the
packet is incomplete, Luna may call `collaboration.followup_task` once on that
exact handle or ID, requesting only the missing bounded fields and quoting the
original evidence. If implementation produces the first contradictory raw
evidence, the same one follow-up may instead request a bounded correction.
There is at most one bounded follow-up total per invocation or task. After it
is used, Luna stops if the issue remains unresolved. Luna never creates a
replacement advisor, reviewer, critic, or nested agent.
