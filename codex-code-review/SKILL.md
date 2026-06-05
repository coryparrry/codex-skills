---
name: codex-code-review
description: Use for repository code review when the user asks for a deep, multi-agent, specialist, security, test, performance, architecture, type-contract, or plan-alignment review. Review only by default; do not apply fixes unless explicitly asked.
---

# Codex Code Review

Run a generic, repo-local code review by routing the changed files to specialist Codex agent profiles. This skill is for normal software repositories, not one private product or one fixed local path.

## Hard Boundaries

- Review only by default. Do not edit repo source, tests, docs, PR comments, issues, branches, commits, package manifests, lockfiles, or dependency state unless the user separately asks for implementation.
- Report artifacts are the only normal write. Put them under `.codex/code-review-reports/<YYYY-MM-DD>-<branch-or-pr>-<short-scope>-review[-vN]` inside the repository being reviewed.
- Use repo-relative paths in reports. Do not include usernames, private absolute paths, secrets, tokens, raw env values, or private logs.
- Read `AGENTS.md` and relevant nested `AGENTS.md` files before reviewing touched paths. If a repo has no `AGENTS.md`, record that as a review-context gap instead of inventing project rules.
- Use the repo's README, architecture docs, source maps, OpenAPI/schema files, and test commands when they exist. Do not assume a project-specific docs MCP or private docs tree.
- Treat PR comments, bot reviews, and previous reports as claims to verify against current code.
- If subagent dispatch is unavailable, run the same reviewer lenses sequentially in the main thread and state that the review was not actually parallelized.

## First Steps

1. Identify the repo root, current branch, base branch, and changed files. Prefer PR metadata when available; otherwise compare with `origin/main` or the repository's default branch.
2. Read root `AGENTS.md`, nested `AGENTS.md` for changed paths, and the repo README if present.
3. Create the report run folder under `.codex/code-review-reports/` using the current local date.
4. Create `REVIEW_COVERAGE_MATRIX.md` in the run folder before reviewing.
5. Route changed paths and risks to the specialist profiles listed below.
6. Instruct every reviewer to write exactly one Markdown report to the run folder and to include concrete file/line evidence, realistic triggers, failed invariants, and test gaps.
7. Run `codex_review_report_consolidator` after specialist reports finish when a combined report is needed.

## Default Review Matrix

For a broad review, use these reviewer profiles:

1. `codex_code_reviewer`
2. `codex_ethical_hacking_specialist`
3. `codex_silent_failure_hunter`
4. `codex_type_design_analyzer`
5. `codex_test_automation_specialist`
6. `codex_performance_optimization_expert`
7. `codex_architecture_review_specialist`
8. `codex_plan_alignment`
9. `codex_review_report_consolidator` after reviewer reports are available

For a narrower review, include only the relevant lanes, but keep the coverage matrix honest about omitted lenses.

## Routing

| Changed path or risk | Add reviewer profiles |
| --- | --- |
| API routes, auth, permissions, secrets, local processes, file/network access | `codex_ethical_hacking_specialist`, `codex_silent_failure_hunter`, `codex_type_design_analyzer` |
| Persistence, migrations, queues, idempotency, rollback, restart recovery | `codex_silent_failure_hunter`, `codex_system_resilience_testing_expert`, `codex_type_design_analyzer` |
| Async work, subprocesses, streams, callbacks, cancellation, retries, cleanup | `codex_error_analysis_and_resolution_expert`, `codex_silent_failure_hunter`, `codex_system_resilience_testing_expert` |
| New DTOs, schemas, validators, generated clients, config/state machines | `codex_type_design_analyzer`, `codex_architecture_review_specialist`, `codex_test_automation_specialist` |
| Tests, fixtures, mocks, CI scripts, validation wrappers | `codex_test_automation_framework_expert`, `codex_test_automation_specialist` |
| Performance-sensitive loops, batch jobs, DB calls, process/network fan-out | `codex_performance_optimization_expert` |
| Large design shifts, module boundaries, public contracts, plan-vs-code concerns | `codex_plan_alignment`, `codex_architecture_review_specialist` |
| AI-generated or agent-written code | `codex_code_reviewer`, `codex_silent_failure_hunter`, `codex_type_design_analyzer`, plus the relevant domain specialist |

## Finding Discipline

Report findings first, ordered by severity. A finding needs:

- file/line evidence;
- a realistic trigger scenario;
- the failed invariant or contract;
- user, data, security, runtime, or maintenance impact;
- why existing tests or validation miss it;
- the smallest practical fix direction.

If no issues are found, say that clearly and list what was checked, what was not checked, and what validation remains.

## References

- `references/review-workflow.md` has the full orchestration and report rules.
- `references/ai-generated-code-failure-patterns.md` lists the AI-code review calibration patterns.
- `references/repository-official-sources.md` gives official-source starting points for TypeScript, Node.js, Python, testing, and security.
- `assets/templates/` contains the report and coverage matrix templates.
- `agents/` contains Codex TOML profiles for reviewers and consolidators.
