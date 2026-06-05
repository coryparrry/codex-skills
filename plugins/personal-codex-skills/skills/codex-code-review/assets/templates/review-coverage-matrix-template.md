# Generic Review Coverage Matrix

- Review run:
- Mode:
- Branch/base:
- Changed files source:
- Previous artifacts checked:
- Live PR review evidence checked:
- Output folder: `.codex/code-review-reports/...`

## Routing matrix

| Changed surface | Risk classes | Selected agent(s) | Required lens | Status | Notes |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  | queued / running / done / blocked |  |

## Language coverage

| Language/runtime | Required checks | Covered by | Gaps |
| --- | --- | --- | --- |
| TypeScript | strictness, narrowing, runtime validation, DTO/schema drift, dependency/API hallucination |  |  |
| Node.js | Promise/callback/EventEmitter/stream/process errors, event-loop blocking, API/auth/config/resource limits |  |  |
| Python | typing/runtime validation, asyncio cancellation, subprocess, broad exceptions, pytest prevention |  |  |
| Other | framework/runtime-specific contract and failure-path checks |  |  |

## AI failure pattern coverage

| Pattern | Required when | Covered by | Findings / no-finding evidence |
| --- | --- | --- | --- |
| Hallucinated APIs | new imports/packages/methods/config keys/SDK calls |  |  |
| Security that looks functional | auth, API, process, file, network, secrets, logs |  |  |
| Performance anti-patterns | loops, sync IO, request paths, queue workers, batch jobs |  |  |
| Happy-path error handling | async, callbacks, streams, subprocess, cleanup |  |  |
| Missing edge cases | arrays, null, empty, partial config, deleted rows, cancellation |  |  |
| Outdated library usage | dependency/API/config changes |  |  |
| Data model mismatch | DTOs, schema, JSON, DB, generated clients |  |  |
| Missing context dependencies | env, cwd, local tools, network service, path, migration |  |  |

## Consolidated findings

| Stable ID | Source agent | Severity | Root cause | Duplicate of | Fix handoff? |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

## Open coverage gaps

-
