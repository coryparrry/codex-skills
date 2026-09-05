---
name: codex-routing
description: Coordinate independent coding work across available agents when delegation improves delivery.
---

# Codex Routing

The root agent owns the task. It decides the approach, delegates useful independent work, integrates the results, validates the combined outcome, and produces the final response.

Keep small or tightly coupled tasks local. Delegate when separate investigation, implementation, testing, or review lanes can make useful progress independently.

## Route By Capability

Choose each agent for the bounded assignment it will perform. Match the lane to available capabilities such as:

- fast codebase exploration and call-path discovery
- implementation in an owned file or module scope
- platform or domain expertise
- security, correctness, maintainability, or acceptance review
- runtime, UI, or integration validation

Use role-specific agents when their contract matches the work. Otherwise use a general worker with the model and reasoning effort appropriate to that lane's ambiguity, risk, and breadth. Do not route by a fixed model identity, minimum effort, or task-wide default when the available agents or assignment needs differ.

Choose from the capabilities available in the current session. Do not assume a particular model, role, or concurrency limit exists.

## Delegate Bounded Lanes

Give each agent a concrete goal, owned files or responsibility, relevant code and evidence anchors, constraints, and observable completion checks. Tell code-writing workers that other agents may be editing the repository and that they must preserve unrelated changes.

Launch ready, non-overlapping lanes in parallel. Keep dependent work sequential, and avoid duplicate investigation unless an independent opinion is the point of the assignment.

The root may continue useful local work while agents run. It should not redo a delegated lane before collecting its result.

## Wait From Evidence

Wait for an agent to finish or report that it needs attention. A wait timeout, elapsed time, silence, or the absence of a patch does not by itself show that the agent has failed or stalled.

Interrupt, replace, or duplicate a lane only when there is concrete evidence: explicit failure, an unrecoverable blocker, termination without completing the assignment, incompatible scope, or user direction. Handle actionable questions or blockers, then continue the original lane when possible.

## Integrate And Review

Treat agent output as input to the root's judgment. Check important findings against the current workspace or external state, resolve overlapping edits, run relevant validation, and confirm that the requested outcome and constraints are satisfied.

Use one focused correction when evidence identifies a defect. Re-review corrected work when the change is material or the prior concern needs fresh proof; do not create review loops without new evidence.

Report delegated results and material blockers when they help the user assess completion. Do not add a model census or coordination log unless the user asks for one.
