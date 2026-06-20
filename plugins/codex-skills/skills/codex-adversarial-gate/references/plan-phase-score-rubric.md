# Plan Phase Score Rubric

Use this rubric when `plan_adversarial_reviewer` reviews a draft plan.

## Scoring

| Category | Points | Pass condition |
|---|---:|---|
| Source grounding, current state, and owner decisions | 15 | The phase is based on current repo/source docs, records resolved questions, and does not assume stale state or owner choices. |
| Plan type, scope, sequencing, and dependencies | 10 | Primary plan type, order, prerequisites, dependency classes, approval gates, and touched surfaces are clear. |
| File/action ownership and prevention guard | 15 | `File Action Map` or repo-specific equivalent, plus any repo-specific prevention guard, names create/modify/test/docs/index actions, canonical owner/source, deliberate non-touches, duplicate representations, and out-of-scope layers. |
| Proof tier and validation quality | 15 | `Proof Tier Map` or repo-specific equivalent names first failing proof, first side effect, exact command, expected failure/pass, required lane, and weak proof not accepted. |
| Runtime emission vs contract parity | 15 | Public DTOs, schemas, enums, generated artifacts, route responses, config values, health/readiness reasons, error taxonomies, migration states, docs/index claims, and equivalent contract surfaces have runtime emitters and parity/drift prevention proof, or a concrete non-applicable reason. |
| Developer-facing surface and deferred follow-ups | 10 | API/CLI/MCP/SDK/docs/setup/auth/error/migration/deployment friction is checked when applicable, and every accepted-but-unbuilt item has owner/source, blocker, and recorded follow-up location. |
| Safety, security, privacy, and scope control | 10 | The phase avoids unsafe exposure, secret leakage, personal paths, scope creep, and hidden implementation decisions. |
| Handoff, self-review, and completion criteria | 10 | Done criteria, stop conditions, closeout evidence, `Plan Quality Self-Review`, completion gates, commit boundaries, and reporting requirements are explicit. |

## Hard Caps

- Owner decision unresolved: max 69.
- Plan records an unasked owner/user decision as a decision, assumption, TBD, or future implementer choice instead of asking the owner: max 69 and return `BLOCKED_OWNER_DECISION`.
- Missing acceptance criteria: max 79.
- Runtime behaviour changed but only compile/lint validation named: max 84.
- Source-of-truth conflict or stale assumption: max 74.
- New dependency without approval path: max 79.
- Security/privacy exposure without mitigation: max 69.
- Phase too broad to validate as one implementation slice: max 89.
- Missing phase/slice-level adversarial completion gates for reviewable implementation slices: max 89. Per-task gates are required only when a task is independently reviewable and risky enough to justify its own gate.
- Missing `docs/Adversarial Reviews/` archive requirement for plan, completion, and critic review outputs: max 89.
- Completion gate lacks the `task_completion_review_critic` PASS audit after `task_completion_adversarial_reviewer` PASS: max 84.
- Completion gate accepts implementer validation summaries, reviewer confidence, or reviewer/critic agreement without raw evidence, artifact paths, or safe rerun proof: max 84.
- Phase lacks source-owner, proof-tier, archive-path, or relevant prevention-lane closeout requirements: max 89.
- Implementation plan lacks `Plan Type`, `File Action Map`, `Proof Tier Map`, `Deferred Follow-Ups`, `Plan Quality Self-Review`, or repo-specific equivalents required by the active planning skill: max 89 for one missing requirement; max 79 for two or more.
- Public contract/runtime surface touched without a `Runtime Emission vs Contract Map` or repo-specific equivalent: max 79.
- API, CLI, MCP, SDK, docs, setup, auth, errors, migration, or deployment surface touched without a `Developer-Facing Surface Check`, repo-specific equivalent, or concrete N/A reason: max 84.
- `File Action Map` or repo-specific equivalent omits canonical owner/source, deliberate non-touches, or why the file owns the change: max 84.
- `Proof Tier Map` or repo-specific equivalent omits first failing proof, expected failure/pass, or weak proof not accepted: max 84.
- `Runtime Emission vs Contract Map` or repo-specific equivalent relies only on static schema parity while runtime behaviour changes: max 74.
- Deferred work is accepted but not recorded in the appropriate todo/doc surface: max 84.
- `Plan Quality Self-Review` is present but rubber-stamps missing sections, placeholder steps, weak proof, or scope creep: max 79.
- Plan contains `TODO`, `TBD`, "handle edge cases", "add validation", "write tests", "similar to above", "implement later", or future-agent decision handoff: max 79.

## 100 Standard

A phase scores 100 only if no concrete, actionable objection remains. The reviewer must not award 100 because the plan is merely plausible.
