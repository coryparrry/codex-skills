# AI-Generated Code Failure Pattern Reference

Use this as a calibration layer during both review and fix work. The goal is not to assume every AI-generated change is bad; the goal is to look for the predictable failure shapes that AI agents commonly produce when they write plausible-looking code without enough runtime context.

Source anchor supplied by the user: <https://www.augmentcode.com/guides/debugging-ai-generated-code-8-failure-patterns-and-fixes>

## The eight failure patterns

| Pattern | Review signal | TypeScript/Node examples | Python examples | Required proof |
|---|---|---|---|---|
| 1. Hallucinated APIs | Import, method, option, CLI flag, config key, model field, or package looks plausible but is not in current docs or installed deps. | Fake npm package; wrong Node `child_process` option; nonexistent SDK method; old Express/Fastify middleware API; wrong test-runner mock API. | Fake PyPI package; wrong Pydantic v1/v2 method; nonexistent asyncio helper; invalid pytest fixture; wrong subprocess option. | Verify against package docs, installed version, lockfile, type checker, or runtime smoke test. |
| 2. Security vulnerability that looks functional | Happy-path works but adversarial input bypasses auth, leaks data, executes shell, escapes path, or causes SSRF/resource abuse. | Missing object/function/property authorization; string-built SQL/query/filter; unsafe `exec`; unvalidated URL fetch; leaking stack/env/stdout/stderr. | `shell=True` with untrusted input; path traversal; broad exception returning internals; unsafe YAML/pickle; missing auth on route/job/action. | Negative security test or explicit denial-path proof. |
| 3. Performance anti-pattern | Code passes tests but introduces avoidable blocking, O(n²), repeated network/db calls, unbounded buffers, or large memory allocation. | Sync fs/process in request path; N+1 API/DB calls; unbounded `Promise.all`; regex DoS; expensive JSON parse/stringify loops. | Blocking subprocess/IO in async route; repeated model/schema parse; unbounded list accumulation; no streaming; CPU-heavy loop in event loop. | Complexity/limit rationale plus targeted scale/perf guard where practical. |
| 4. Happy-path error handling | `try/catch` logs and continues, callback error ignored, EventEmitter/stream error not handled, cleanup masks primary failure. | Missing `await`; `void promise`; callback `err` ignored; stream no `error`; child process `error`/`close` not handled; false success on failure. | Broad `except`; swallowed `CancelledError`; subprocess return code ignored; `finally` hides error; false success if cleanup fails. | Failure injection test proving caller-visible failure or safe observable fallback. |
| 5. Missing edge cases | Empty/missing/null/undefined/zero/unicode/large inputs, expired data, deleted rows, partial config, cancellation, retry, race. | `arr[0]!`; truthy checks; optional property collapsed; `Map.get` assumed; no abort handling; duplicate job IDs. | `dict[key]` assumed; default mutable args; `None` confused with empty; missing timezone/encoding; concurrent temp path conflict. | Boundary tests for absence, malformed input, and minimum/maximum cases. |
| 6. Outdated library usage | API, package, config, or security pattern is deprecated, v1/v2-incompatible, or learned from old examples. | CJS/ESM mismatch; deprecated request libs; outdated Jest/Vitest/Node test APIs; old SDK methods; stale package install. | Pydantic v1 method used in v2; old asyncio patterns; outdated pytest plugin; unpinned/unsafe package. | Current docs/version check and no opportunistic dependency installs. |
| 7. Data model mismatch | Code assumes schema shape not guaranteed by DB/API/runtime; static types disagree with runtime data. | DTO/domain/persistence drift; `as Type` over JSON; API client response assumed; optional fields returned as required. | Broad `dict[str, Any]`; Pydantic model not used at boundary; dataclass used as validation; TypedDict mismatch. | Runtime validation or explicit parser/narrowing at external boundary. |
| 8. Missing context dependency | Code needs env var, cwd, service, model, file, token, host, tool, or migration not present in all environments. | Env var not validated; depends on local path; package script not in CI; queue worker assumes API key; wrong cwd in child process. | Reads local file from dev machine; assumes PATH tool exists; missing venv dependency; worker assumes env; no startup validation. | Config/startup validation, fallback contract, or documented hard failure. |

## Fast three-gate sanity check

1. **Static first:** run or inspect the repo’s normal lint/type/static checks. For TypeScript this normally means `tsc --noEmit` plus the repo’s lint command. For Python this normally means the repo’s type/lint tools if present, such as `mypy`, `pyright`, `ruff`, or equivalent.
2. **Existing tests next:** run the smallest relevant existing test target before inventing a new one.
3. **Risk-specific proof last:** add or request focused tests for the AI failure pattern, especially denial paths, malformed data, async failure, subprocess failure, and config absence.

## Review rule

A finding is stronger when it names the pattern, proves the trigger, explains why the current code/tests miss it, and proposes the smallest prevention test. Do not file speculative findings that cannot name a concrete trigger or failed invariant.
