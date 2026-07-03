# Script Responsibilities

Use this reference when the audit output around scripts looks ambiguous.

The scripts-to-rule-them-all names are a vocabulary, not a naming mandate. A healthy repo can use `make`, `just`, package scripts, shell helpers, custom tools, or documented commands instead of `script/*`.

## Statuses

| Status | Meaning |
|---|---|
| `present` | A repo file, package script, Make target, or recognizable custom command covers the responsibility. |
| `documented` | Public docs name an equivalent command, even if its filename is not semantically recognizable. |
| `missing` | The repo appears to need the responsibility, but no file, target, package script, or documented equivalent was found. |
| `not_applicable` | The repo shape does not show a need for that responsibility. |

## Responsibility Judgment

| Responsibility | Usually applicable when | Often not applicable when |
|---|---|---|
| `bootstrap` / `setup` | Dependency manifests, package managers, generated toolchains, or install instructions exist. | Static docs or standalone stdlib scripts need no dependency setup. |
| `update` | Dependency or generated-state refresh is part of normal work. | There is no dependency/update surface beyond pulling Git. |
| `server` | The repo runs an app, service, dev server, container stack, or local runtime. | Library, docs, skill, script-only, or package metadata repos have no long-running process. |
| `test` | Executable code, package behavior, shipped scripts, tests, or installable skills exist. | Static docs or pure metadata repos have no executable behavior to test. |
| `cibuild` | A repo has code, package surfaces, generated artifacts, installable skills, or release gates. | Static docs with no render/lint/test requirement may not need a full gate. |
| `console` | The repo documents or exposes a REPL, shell, console, or framework console. | Most docs, skills, libraries, and CLIs do not need one. |

## Interpretation Rules

- Treat custom names as valid when docs explain their purpose, for example `./tools/doit --all` as a full gate.
- Prefer the repo's own command spelling over adding standard names.
- Report missing responsibilities as findings only when the repo shape shows the responsibility is needed.
- Do not turn `not_applicable` into a fix request.
- If a documented command points at a missing file, report the documentation mismatch separately only after confirming it is not an external tool.
