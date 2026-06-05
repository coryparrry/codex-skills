# Routing Detail

Load this reference only when the budget route needs expanded activation behavior, duplicate-work examples, checkpoint classification, or recovery detail.

## Explicit Subagent Requests

If the user explicitly invokes this skill or explicitly says to use subagents, workers, delegated agents, cheap agents, the budget router agents, or "the sub agents from the Codex Budget Router skill", do not choose a root-only route by default.

At the first meaningful split point, do one of these:

- Spawn bounded workers that satisfy the breakeven rule. For broad work, this usually means 2-4 workers, not one.
- State the concrete blocker before continuing root-only, such as no subagent tool available, no callable model override, task already narrowed to a one-file edit, or every remaining step is sequential and would increase total usage.

For medium or broad tasks, one worker is not enough by default. Before choosing only one worker, check whether any of these independent lanes exist:

- read-only repo/source map,
- reference/docs/stale-instruction audit,
- validation or long-log summarisation,
- low-risk routine/mechanical patch for `spark_worker`,
- bounded non-trivial implementation patch for `codex_worker`,
- shared contract, persistence, or test implementation,
- platform-specific UI or companion-app surface,
- bounded diff review,
- test-gap or regression-risk review.

If two or more lanes exist, spawn 2-4 workers with disjoint scopes. If only one worker is used, say why the other lanes are not useful or not independent.
If a low-risk write/test/docs/script lane exists and `spark_worker` is available, include it in those workers. If Spark is unavailable, use `codex_worker` on `gpt-5.3-codex` for that routine lane and state `spark unavailable` in the route and scorecard. Treat "no Spark" without that availability reason as an exception that needs a reason.

## No Duplicate Researcher Commands

When root delegates a docs/reference/log/context audit, the worker owns both the read and the retrieval command. Root must not run the same command, query, or broad equivalent while the worker is active.

Examples:

- If `cheap_researcher` is told to run `scripts/docs/find-context`, root must wait for the returned files/ranges.
- If `cheap_mapper` is told to map source ownership, root must not run an equivalent `rg`/file-map sweep over the same source area.
- If a worker is condensing test logs, root must not paste or re-summarise the same raw log.

Allowed root work while those workers run: branch/task setup, reading already-known source-of-truth docs not assigned to a worker, preparing integration constraints, or waiting.

If the user corrects the route mid-task, immediately recover by routing the remaining independent work to workers. Good recovery tasks include active-reference audits, long-log condensation, bounded diff review, targeted test-failure triage, and isolated mechanical patches. Do not wait until all useful independent work is finished.

## Multi-Wave Delegation

Do not treat the first worker batch as the whole route. In long implementation, review, or validation tasks, root must reassess delegation at every new work boundary.

Required checkpoints:

- **After workers return:** root integrates reports, then assigns any new independent patch/test/review lanes instead of keeping all follow-up work.
- **After validation failure:** root classifies each failure before editing:
  - Spark: tests, fixtures, docs, scripts, simple compile fixes, mechanical symbol/API updates.
  - Codex worker fallback: the same routine work when Spark is unavailable.
  - Codex worker: bounded product-code fixes, state/API/persistence logic, non-trivial integration patches.
  - Mid debugger: unclear concurrency/framework/UI/runtime behavior.
  - Root: only tiny one-file integration edits that satisfy every root patch exception condition, or final validation judgment.
- **After reviewer findings:** assign each finding to Spark, Codex worker, or mid debugger by risk class. Use Codex worker for routine findings only when Spark is unavailable. Root should not batch-fix all reviewer findings unless they are truly tiny integration edits.
- **After context compaction/resume:** restate active/completed worker lanes, current validation blocker, and the next delegation choice before reading or editing more code.

Root validation loops should primarily run commands, inspect concise failure summaries, and route fixes. They should not become open-ended root implementation loops.
Root must not describe a validation/reviewer fix as "integration" unless it meets every root patch exception condition. Product behavior, actor/concurrency, persistence, runtime protocol, API shape, test seam, fake-provider behavior, and multi-file fixes are worker-owned by default.
