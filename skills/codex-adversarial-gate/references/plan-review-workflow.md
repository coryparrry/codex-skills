# Plan Review Workflow

Read this only when drafting, updating, or finalizing a plan.

## Owner Decision Gate

Before finalizing a plan, identify decisions only the owner can make. Ask before writing the final plan when the decision affects scope, architecture, dependency adoption, validation environment, security/privacy posture, deployment, schedule, data retention, user-facing behavior, or irreversible side effects.

Return `BLOCKED_OWNER_DECISION` if the plan records an unresolved owner choice as a user decision, assumption, TBD, non-blocker, or future implementer choice.

## Required Flow

1. Draft the plan with the active planning skill and current repo instructions.
2. Add the contract from `templates/plan-adversarial-review-section.md`.
3. Run `plan_adversarial_reviewer` with the plan path, source docs checked, owner questions/answers, assumptions, phase list, validation strategy, dependency choices, plan-quality sections or repo-specific equivalents, and out-of-scope boundaries.
4. Require every reviewable phase to score 100.
5. Revise and rerun only inside the bounded loop.
6. Archive each reviewer output under `<repo>/docs/Adversarial Reviews/`.
7. Finalize only after PASS_100 or a recorded owner blocker.

## Loop Control

- Default cap: 3 completed plan-review iterations.
- Iteration 1 reviews the whole plan.
- Iterations 2 and 3 are delta reviews focused on prior findings and exact revisions.
- Later iterations may introduce new blockers only when they are critical, caused by the revision, or clearly missed safety/security/source-truth defects.
- After the cap, stop and report unresolved findings instead of continuing to patch and rerun.
- Continue beyond the cap only if the owner asks, or for one small critical blocker fix needed to avoid unsafe work.

## Plan Packet Must Include

- user request and source docs checked;
- owner questions asked and answers received;
- assumptions and locked decisions;
- unresolved risks or non-blockers;
- phase list and acceptance criteria;
- dependency and validation choices;
- file/action ownership map or equivalent;
- proof-tier map or equivalent;
- production-composition proof expectations when relevant;
- auth/exposure mode matrix when relevant;
- runtime/generated-artifact contract map when relevant;
- acceptance traceability;
- validation environment contract;
- developer-facing surface check;
- deferred follow-ups;
- plan quality self-review;
- out-of-scope boundaries.

## Stop Conditions

Stop and ask the owner instead of fabricating certainty when the score cannot reach 100 because of unresolved product/architecture decisions, missing source-truth docs, dependency approval, unknown validation environment, conflicting instructions, or scope too broad to validate honestly.

Use `references/plan-phase-score-rubric.md` for scoring details and caps.
