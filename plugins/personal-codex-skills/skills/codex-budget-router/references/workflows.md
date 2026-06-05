# Standard Workflows

Load this reference only when a routed task needs the detailed workflow shape.

## A. Unknown Bug In A Medium Or Large Repo

1. Parent on root model restates the symptom and defines the investigation target.
2. Spawn `cheap_mapper` on `gpt-5.4-mini` to find likely files, entry points, recent changes, and relevant tests.
3. Parent chooses the most likely fix path.
4. If the likely fix is routine or mechanical, spawn `spark_worker` first when available.
5. If Spark is unavailable, the likely fix touches product logic, or Spark reports a blocker, spawn `codex_worker` on `gpt-5.3-codex`.
6. Spawn `mid_reviewer` on `gpt-5.4` if the change touches risky logic, auth, payments, persistence, concurrency, migrations, public APIs, or anything user-facing.
7. When validation exposes new failures, run a routing checkpoint and delegate the next bounded fix lane.
8. Parent gives the final integrated answer and validation status.

## B. Small Routine Fix

1. If this skill was not explicitly invoked and the fix is truly tiny, do not spawn subagents.
2. If this skill was explicitly invoked and `spark_worker` is available, give Spark the patch with exact files, acceptance criteria, and validation command. If Spark is unavailable, give the same bounded routine patch to `codex_worker` on `gpt-5.3-codex`.
3. Parent integrates the result, runs or confirms the relevant validation, and stops.

## C. Feature Implementation

1. Parent creates a short plan and identifies separable workstreams.
2. Parent defines feature behavior, architecture boundaries, acceptance criteria, and risk constraints before worker implementation.
3. If file ownership is unclear, spawn `cheap_mapper` first and do not duplicate its map locally.
4. If any low-risk write/test/docs/script lane exists, spawn `spark_worker` for it before assigning product-code lanes. If Spark is unavailable, spawn `codex_worker` on `gpt-5.3-codex` for that routine lane.
5. If the feature spans multiple independent areas, spawn one worker per area up to 4 workers.
6. Use `spark_worker` for low-risk UI polish, tests, scripts, docs, mechanical refactors, and cleanup when available.
7. Use `codex_worker` for bounded product logic, persistence, API, state, integration patches that follow the root plan, or routine lanes when Spark is unavailable.
8. After each worker wave returns, run a routing checkpoint before doing more implementation.
9. Use `mid_reviewer` or parent root for final review depending on risk.
10. Route reviewer findings by risk class instead of root-fixing them all.
11. Do not use workers to produce long alternative designs unless the user explicitly asks.

## D. PR Review

1. Use `cheap_mapper` on `gpt-5.4-mini` to map changed files and ownership.
2. Use `mid_reviewer` on `gpt-5.4` for correctness, security, regression, and missing-test findings.
3. Use `cheap_researcher` on `gpt-5.4-mini` for CI/log/test-output condensation when raw output is large.
4. If the task includes fixing findings, run a Budget reviewer-finding checkpoint and assign routine findings to `spark_worker` when available, routine findings to `codex_worker` when Spark is unavailable, product-code findings to `codex_worker`, and unclear runtime/framework findings to `mid_debugger`.
5. Use parent only to adjudicate disputed findings, assess cross-cutting risk, and produce the final review.
6. Avoid style-only feedback unless it hides a real correctness issue.

## E. Test Failures Or Long Logs

1. Use `cheap_mapper` or `cheap_researcher` on `gpt-5.4-mini` to condense logs.
2. Return only the failing command, key assertion/error, suspected files, and next action.
3. Run a Budget validation-failure checkpoint before editing.
4. Use `spark_worker` first for low-risk fixes in tests, scripts, fixtures, docs, or mechanical compile issues when available.
5. Use `codex_worker` for product-code patches, when Spark reports the task is outside its risk boundary, or when Spark is unavailable.
6. Use `mid_debugger` for unclear concurrency, actor isolation, framework/runtime behavior, or flaky simulator/tooling diagnosis.
7. Use parent if the failure indicates architectural mismatch, security, data corruption, or a migration issue.
8. After each fix, rerun the targeted validation and repeat the routing checkpoint for new failures.

## F. Context Compaction Or Resume

1. Treat compaction/resume as a fresh routing boundary.
2. Restate completed worker lanes, active blockers, and current validation state.
3. Spawn or resume a bounded worker for any new patch/review/log lane before root reads or edits more implementation files.
4. Root may continue directly only for integration bookkeeping, command execution, final judgment, or a tiny documented root-patch exception.
