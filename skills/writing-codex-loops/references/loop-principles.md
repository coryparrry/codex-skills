# Loop Principles

Use this reference when a loop request is broad, unfamiliar, or high risk.

## Core Model

A loop repeatedly transforms state under a condition. Strong loops define:

- State: current facts, phase, artifacts, attempt count, and environment.
- Trigger: why the loop starts or wakes up.
- Body: the repeated action.
- Observation: live feedback from tools, tests, users, logs, or external systems.
- Comparison: actual state versus goal, policy, invariant, or prediction.
- Progress measure: what must advance or decrease.
- Invariant: what must remain true each pass.
- Cadence: event-driven, continuous, scheduled, or timeboxed.
- Termination: exact success or stop state.
- Escalation: when control returns to the user or another workflow.

## Useful Source Patterns

- Programming loops: `while` repeats while a condition is true; `for` consumes an iterable; `break` and `continue` alter control flow. Source: https://docs.python.org/3/reference/compound_stmts.html
- Formal loops: invariants must hold before and after each pass; variants/progress measures support termination. Source: https://www.cs.cmu.edu/~aldrich/courses/15-819O-13sp/resources/hoare-logic.pdf
- Control loops: sensor/monitor, controller/analysis, actuator/execution, and feedback compare actual state to a setpoint or policy. Source: https://users.cs.fiu.edu/~sadjadi/Teaching/Autonomic%20Grid%20Computing/CIS-6612-Summer-2006/AC-Blueprint-WhitePaper-V7.pdf
- PDSA/PDCA: plan, do, study/check, act cycles are for learning and continuous improvement, not blind repetition. Sources: https://deming.org/explore/pdsa/ and https://asq.org/quality-resources/pdca-cycle
- OODA: observe, orient, decide, act for adaptive decisions under uncertainty. Source: https://www.airuniversity.af.edu/Portals/10/AUPress/Books/B_0151_Boyd_Discourse_Winning_Losing.pdf
- ReAct-style agent loops: interleave reasoning, actions, and observations so plans update from external evidence. Source: https://arxiv.org/abs/2210.03629
- Evaluator-optimizer loops: generate, evaluate, feed back, and repeat only when criteria are clear. Source: https://www.anthropic.com/engineering/building-effective-agents
- Retry loops: cap retries, use backoff/jitter, and retry only safe or idempotent operations. Source: https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
- Idempotency: repeated requests need duplicate-work protection. Source: https://docs.stripe.com/api/idempotent_requests
- Codex automations: use thread automations/heartbeats for same-conversation scheduled wake-ups, standalone/project automations for independent recurring runs, and skills inside automation prompts with `$skill-name`. Source: https://developers.openai.com/codex/app/automations
- Codex heartbeat glossary: a heartbeat is a recurring thread wake-up, also called a thread automation. Source: https://developers.openai.com/codex/glossary
- Codex skills: skills package reusable workflows with `SKILL.md`, optional resources, and optional `agents/openai.yaml`. Source: https://developers.openai.com/codex/skills

## Agent Loop Implications

- Prefer executable checks over self-reflection.
- Put a human back in the loop for destructive actions, unclear product/security judgment, credentials, paid operations, and broad scope changes.
- Make every automation prompt durable enough for the next run to know what to observe, what matters, when to report, and when to stop.
- Do not design permanent passive subagents. Use periodic heartbeat/project automation plus durable state.
