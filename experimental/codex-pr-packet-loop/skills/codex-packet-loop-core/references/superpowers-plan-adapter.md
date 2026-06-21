# Packet Loop Superpowers Plan Adapter

## Role

Packet-loop orchestrates Superpowers plans. It does not replace Superpowers planning or execution.

## Source Plan

Slice only from an approved Superpowers implementation plan unless the user explicitly asks to create plans first. If only a spec exists, route to `superpowers:writing-plans` before packet slicing.

## Child Plan Requirements

Each packet child plan lives under `docs/superpowers/plans/packet-loop/` and must use the standard Superpowers implementation-plan header, including the required sub-skill line. It must include packet id, parent plan path, source task references, allowed files, explicitly out-of-scope files, dependencies, branch name, validation commands, resource lanes, evidence requirements, and human-review-before-implementation status.

## Verification

Before a packet becomes `ready`, verify the child plan has the required header, checkbox tasks, exact file paths, exact validation commands, no placeholders, source references, dependency metadata, and packet id. Mark `plan_format_status` as `valid` only after this verification.

## Dispatch

Worker handoff points to the child plan path as the primary instruction. The worker must use the Superpowers execution skill required by that plan: `superpowers:subagent-driven-development` when tasks are independent in the current session, or `superpowers:executing-plans` when executing the plan in a separate session.

## Safety

Do not split a Superpowers task so that RED and GREEN steps land in different packets. Do not dispatch dependency consumers before producers are merged. Do not replace a child plan with an ad hoc packet prompt when a child Superpowers plan can be generated.
