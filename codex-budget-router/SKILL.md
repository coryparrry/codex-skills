---
name: codex-budget-router
description: Budget-aware Codex routing for making Codex limits and credits last longer. Use when the user mentions Codex limits, usage, credits, budget, cheaper models, GPT-5.5 orchestration, GPT-5.4-mini, GPT-5.4, GPT-5.3-Codex, model routing, or subagents. Avoid for tiny one-shot questions unless explicitly invoked.
---

# Codex Budget Router

## Purpose

Use this skill to make Codex usage last longer while preserving quality on risky work.

The primary budget metric is model-tier drain, not raw token count. A routed task can use more total tokens and still be a win if it moves substantial work off `gpt-5.5` and onto `gpt-5.4-mini`, `gpt-5.3-codex`, `gpt-5.3-codex-spark`, or `gpt-5.4`.

Default strategy:

1. Keep root on the current high-capability model for orchestration, requirement interpretation, architecture, final integration decisions, and high-risk review.
2. Move broad file-reading, repetitive searching, routine testing, low-risk implementation, log condensation, and bounded review to cheaper workers.
3. Use cheaper workers early when they replace expensive root context or parallelize genuinely independent work.
4. When explicitly invoked for medium or broad work, actively look for 2-4 independent worker lanes.
5. Prefer bounded, non-overlapping workers over unfocused fan-out.
6. Prefer `spark_worker` for low-risk routine patches, mechanical edits, validation wrappers, small tests, docs cleanup, and repetitive repo hygiene when Spark is available. If Spark is unavailable, use `codex_worker` on `gpt-5.3-codex` for those routine implementation lanes.

Do not imply this skill bypasses usage limits, resets limits, creates free usage, or changes OpenAI pricing. It only changes routing behaviour.

## Success Criteria

A budget-routed task is successful when it reduces expensive-model drain:

- root work is limited to orchestration, decisions, integration, and final judgment.
- `gpt-5.4-mini` does broad read-only mapping, docs/reference audits, and long-log condensation.
- `gpt-5.3-codex-spark` does low-risk routine implementation and mechanical edits from precise briefs.
- `gpt-5.3-codex` does bounded non-trivial implementation after ownership is clear.
- `gpt-5.4` does bounded debugging or review when mini is too weak but root is not needed.
- the parent reports whether workers materially displaced root work, not whether total tokens went down.

Do not call a route ineffective just because total child-agent tokens are nonzero. Judge whether those child-agent calls prevented equivalent root-model work.

## Hard Rules

These rules are mandatory when this skill is explicitly invoked. If a rule cannot be followed, stop and state the concrete blocker before continuing.

1. **No root-only broad work.** For medium or broad tasks, root must spawn budget workers at the first meaningful split point. Root-only is allowed only for trivial/small tasks or when there is a concrete blocker.
2. **No duplicate worker work.** Once a worker owns a map, audit, review, log summary, or patch, root must not perform the same search/read/review locally. If a worker prompt names a command such as `scripts/docs/find-context`, `rg`, `git diff`, test-log parsing, or a docs/reference query, that command belongs to the worker; root must wait for the worker's result instead of running it too.
3. **Root read cap.** For explicitly routed broad work, root may read at most 2 implementation files before splitting the task into worker lanes. For medium work, the cap is 3. Source-of-truth docs, task tracking, and config checks do not count against this cap.
4. **No broad root ownership.** Root must not own shared contracts, app processing, persistence, tests, project integration, and platform UI in the same route. Split at least one high-value implementation lane to a cheaper worker.
5. **Root owns feature judgment.** For feature-building tasks, root/orchestrator keeps ownership of feature judgment, architecture, acceptance criteria, integration decisions, and final risk review. Do not delegate those decisions to cheaper workers.
6. **Workers execute bounded slices.** Workers may implement, test, map, debug, or review only bounded slices from root's plan. Worker prompts must include relevant constraints, owned files/symbols, acceptance criteria, and validation expectations.
7. **No delegated feature design.** Do not delegate feature design, architecture, product behavior, persistence/session/runtime contract decisions, or final go/no-go review to cheaper workers.
8. **Use 2-4 workers for broad work.** If two or more independent lanes exist, spawn 2-4 workers with disjoint scopes. If only one worker is used, state why no second lane is useful or independent.
9. **Valid spawn shape only.** Typed/model-specific workers must use self-contained prompts. Do not set `fork_context=true` with `agent_type`, `model`, or `reasoning_effort`.
10. **Wait instead of racing.** If root's next decision depends on a worker's answer, wait for that worker. Do not race it with duplicate root exploration.
11. **Close worker slots.** Close completed workers after integrating their report. If a useful worker spawn fails due to thread limits, close completed workers and retry once.
12. **Pre-edit gate required.** Before the first code edit on medium or broad work, print a short gate with root implementation files read `N/2` for broad or `N/3` for medium, active/complete worker lanes, root-owned files, worker-owned files, and pass/fail. If it fails, stop and reroute before editing.
13. **Default broad-task route.** For medium or broad implementation, default to these lanes when they exist: `cheap_mapper` for file ownership, `cheap_researcher` or `cheap_mapper` for docs/reference audit, `spark_worker` for routine/mechanical patch lanes, `codex_worker` for one non-trivial bounded implementation lane, and `mid_reviewer` for bounded review before closeout.
14. **Spark-first routine work.** If an explicit routed task has any low-risk write lane such as tests, fixtures, scripts, docs, mechanical refactors, simple compile fixes, small UI polish, or repetitive cleanup, spawn `spark_worker` before the first edit, not merely as a planned future lane. If exact files are not known yet, wait for the mapper and then spawn Spark before root or `codex_worker` edits. If Spark is unavailable, use `codex_worker` on `gpt-5.3-codex` for the routine lane and state `spark unavailable` in the budget route and scorecard.
15. **Codex worker is not the routine default when Spark is available.** Use `codex_worker` for non-trivial product logic, persistence, API/state integration, patches where Spark hit a blocker, or routine implementation lanes when Spark is unavailable. Do not use `codex_worker` for routine low-risk work merely because it feels safer when Spark is available.
16. **Multi-wave delegation.** Delegation is not one wave. After workers return, after validation exposes new failures, after a reviewer returns findings, and after context compaction/resume, root must run a routing checkpoint and either spawn the next bounded worker wave or state why root is the right owner.
17. **Validation failures are not root-owned.** After any compile/test/lint/runtime validation failure, root must run a validation-failure checkpoint before editing. Root must delegate the fix unless it qualifies for the root patch exception.
18. **Reviewer findings are not root-owned.** After a reviewer returns findings, root must classify and delegate each finding unless it qualifies for the root patch exception.
19. **Root patch exception.** Root may directly patch only when all are true: the fix is a tiny integration correction, no product behavior decision is involved, no new file or API surface is needed, only one file is edited, and no additional implementation-file reading beyond the root cap is needed. Root-patched fixes must be listed in the checkpoint and scorecard with the reason they were not delegated.
20. **Violation recovery.** If the user says root is reading too much, duplicating workers, not using workers, not using Spark, delegating feature judgment, or keeping too much work, immediately stop root exploration, summarize the violation, assign remaining independent lanes to workers, and continue only after the route passes the gate.
21. **Budget scorecard required.** Final output must include a compact scorecard with root model, workers used, Spark usage yes/no with reason, model-tier displacement, worker waves/checkpoints, validation/reviewer failures routed yes/no, root implementation files read before worker results, duplicate-work status, hard-rule pass/fail, and any remaining root-only work with the reason.

## Activation Behaviour

Keep chat output terse. The router should improve model usage, not produce long process narration.

Use these compact lines:

```text
Budget route: root=<orchestration/integration>; workers=<mapper/researcher/spark/codex/reviewer>; target=<30%+ if broad>; risk=<short control>.
Budget gate: root_reads=N/<2|3>; workers=<active/complete>; spark=<spawned|n/a>; root=<integration/tiny exception>; gate=<pass|fail>.
Budget checkpoint: trigger=<event>; delegate=<workers or none>; root=<integration/tiny exception>; gate=<pass|fail>.
Budget failure checkpoint: failure=<short>; route=<spark/codex/mid/root-exception>; delegated=<yes/no>; gate=<pass|fail>.
Budget review checkpoint: findings=<count/short>; route=<spark/codex/mid/root-exception>; delegated=<yes/no>; gate=<pass|fail>.
```

Only expand these lines when something fails, root claims an exception, or the user asks for routing detail.

Activation only means the skill loaded. It does not prove custom subagent profiles are callable. Before promising a named worker, check the available `spawn_agent` schema. If named workers are not callable, use built-in subagents with matching model overrides when available; otherwise use the model-switch fallback in `references/model-switch-fallback.md`.

Automatic activation from nearby words such as "limits", "usage", or "budget" should save usage by keeping root focused, searching before reading, and avoiding broad logs. It should not silently fan out agents unless the user also invoked this skill or asked for subagents/delegation.

Explicit invocation means the user wants budget-router subagents used. Treat prompts such as "use codex-budget-router", "use the Codex Budget Router skill", or "route this with the budget router" as permission to spawn bounded workers when the breakeven rule is met.

For the expanded activation rules, duplicate-work examples, and checkpoint classifications, use `references/routing-detail.md`.

## Model Routing Policy

Use this routing table when the matching agent route is available. If a named custom agent is installed but not callable in the current runtime, say so and use the fallback route instead of pretending the custom name exists.

| Work type | Preferred custom route | Built-in fallback route | Model | Notes |
|---|---:|---:|---:|---|
| Ambiguous requirements, feature judgment, architecture, product behavior, persistence/session/runtime contracts, cross-cutting design, security-sensitive changes, acceptance criteria, final integration review, final go/no-go review | Parent/root orchestrator | Parent/root orchestrator | current root model | Do not delegate these decisions. User controls root model/effort. Do not make root scan the whole repo unless necessary. |
| Repo mapping, symbol search, dependency tracing, log/test-output summarisation, docs lookup, simple low-risk analysis | `cheap_mapper` / `cheap_researcher` | `explorer` with model override | `gpt-5.4-mini` | Best default for read-heavy bounded work. Return concise evidence with file paths and symbols. |
| Routine small implementation, mechanical refactors, test additions, docs/scripts cleanup, simple targeted bug fixes after files are known | `spark_worker`, or `codex_worker` if Spark is unavailable | `worker` with model override | `gpt-5.3-codex-spark` when available, else `gpt-5.3-codex` | First-choice implementation worker for low-risk work. Give precise ownership and acceptance criteria. |
| Non-trivial bounded implementation after files/approach are known | `codex_worker` | `worker` with model override | `gpt-5.3-codex` | Use when Spark is unavailable, Spark is too weak, or the patch touches product logic. Keep scope narrow. |
| Medium-risk debugging, tricky framework behaviour, review of a bounded diff, browser/UI diagnosis | `mid_debugger` / `mid_reviewer` | `explorer` or `worker` with model override, depending on edit scope | `gpt-5.4` | Use when mini is likely too weak but root is not needed. |

If the user explicitly asks to conserve limits, default to the cheapest model that can plausibly complete the current subtask safely. If `spark_worker` is available, prefer it for low-risk implementation. If Spark is unavailable, use `codex_worker` on `gpt-5.3-codex` for routine implementation lanes. Before using `codex_worker` while Spark is available, check whether the task is actually too risky for Spark.

## Breakeven And Fan-Out

Before spawning any subagent, answer internally: **What expensive root-model work is this subagent replacing?**

Spawn only if the answer is concrete: mapping a large area, condensing logs, implementing an isolated patch from a root decision, or reviewing a bounded diff. Do not spawn when the task is a one-file/two-file change, the worker would read the same broad context as root, the work is sequential, constant parent judgment is required, or no meaningful root work moves off the expensive model.

Fan-out defaults:

- `0` subagents for trivial answers, one-file fixes, and small edits.
- `1` subagent only when exactly one independent lane exists or the user did not explicitly invoke this skill.
- `2-4` subagents for explicitly invoked medium/broad work with genuinely independent lanes.
- `4+` subagents only when the user explicitly asks for high parallelism and the task is large enough.

Do not allow recursive delegation unless the user explicitly requests it. Close completed workers after integrating their report. If a spawn fails because the worker pool is full, close completed workers and retry once.

## Context Discipline

Apply these rules aggressively:

1. Search before reading; prefer targeted symbol/file searches.
2. Read snippets, not whole files, unless full-file context is necessary.
3. Do not paste large logs into root context; summarise decisive errors only.
4. Ask workers for file paths, line ranges, symbols, commands run, evidence, validation results, risks, and concise conclusions.
5. Ask workers for compact reports by default, but do not impose hard length caps.
6. Do not duplicate worker-owned map/audit/log/review/patch work in root.
7. While workers run, root may only do non-overlapping work such as branch/task setup, known source-of-truth docs, integration constraints, or waiting.
8. If root's next step depends on a worker's answer, wait instead of duplicating.
9. After a worker returns, trust its bounded report unless there is a contradiction, high-risk claim, or missing evidence. Re-read only exact files/ranges needed for integration, edits, or validation.
10. After a worker returns, run a routing checkpoint and delegate any new bounded follow-up lane.
11. If root needs to read more than 2 implementation files for broad work or 3 for medium work, stop and split into worker lanes.
12. Do not let root keep all high-value implementation domains; split at least one to `spark_worker`, `codex_worker`, or `cheap_mapper`.
13. Prefer targeted tests first. Run the full suite only at the end of risky/broad changes or when asked.
14. Validation failures and reviewer findings are new routing inputs; classify and delegate unless the root patch exception applies.
15. Keep progress updates short: state only what changed, what is blocked, or which worker owns the next lane.

## Workflows And Prompts

For standard workflows, use `references/workflows.md`:

- unknown bug in a medium/large repo
- small routine fix
- feature implementation
- PR review
- test failures or long logs
- context compaction or resume

For worker prompt templates, use `references/worker-prompts.md`.

## Budget Scorecard

End every explicitly routed medium or broad task with this compact scorecard:

```text
Budget scorecard: workers=<count/roles>; spark=<yes/no/n-a>; waves=<n>; failures_routed=<yes/no/n-a>; root_patches=<none|tiny list>; result=<pass/fail>.
```

If the result is `fail`, add only the failing rule and recovery. Do not include token counts, audit summaries, or detailed displacement math unless the user explicitly asks.

Use `scripts/budget_router_audit.py` only when the user asks whether the router saved model-tier usage in recent threads.

## Final Response Requirements

At the end of a routed task, include:

- What was done.
- Which route was used.
- Validation performed.
- Remaining risks or files not checked.
- Whether additional subagents would likely help or would likely waste usage.

Keep the final answer compact. The goal is to save usage, not generate long commentary.
