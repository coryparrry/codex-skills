## Adversarial Review Contract

This plan uses adversarial review gates. Codex must not mark any reviewable implementation phase or slice as `complete` until a separate adversarial review pass has validated it.

Required custom agents:

- Plan review before finalization or plan updates only: `plan_adversarial_reviewer`
- Implementation completion review for phase/slice closeout only: `task_completion_adversarial_reviewer`
- Completion-review critic for any reviewer PASS before closeout: `task_completion_review_critic`

Rules:

1. Before finalizing this plan, identify decisions only the owner can make and ask those questions. Do not record unasked questions as "user decisions", "owner decisions", assumptions, TBDs, or future implementer choices.
2. If blocking owner decisions remain unanswered, stop with `BLOCKED_OWNER_DECISION`; do not save, hand off, or mark the plan final.
3. Before finalizing this plan, run `plan_adversarial_reviewer`. Run at most 3 completed plan-review iterations by default: iteration 1 reviews the whole plan; later iterations are delta reviews focused on prior findings and exact revisions. Continue beyond 3 only if the owner asks or a critical safety/security/source-truth blocker needs one small fix and one additional delta review.
4. The plan reviewer must score the required plan-quality sections when present or applicable, using repo-specific equivalent names when the active planning workflow uses different labels: `Plan Type`, repo-specific prevention guard, `File Action Map`, `Proof Tier Map`, `Auth/Exposure Mode Matrix`, `Runtime Emission vs Contract Map`, `Acceptance Criteria Traceability Map`, `Validation Environment Contract`, `Developer-Facing Surface Check`, `Deferred Follow-Ups`, `Plan Quality Self-Review`, `Adversarial Review Contract`, and `Phase/Slice Commit Contract`.
5. Missing, fake, or unjustified-N/A plan-quality sections cap the plan score under the adversarial rubric. Static schema parity alone is not enough when runtime behavior changes.
6. Before marking any implementation phase or reviewable slice complete, freeze the artifact and run `task_completion_adversarial_reviewer` with a compact evidence packet: acceptance criteria, current status and changed files, diff inspection pointers, raw validation log paths or raw output excerpts with exit status, skipped checks, known risks, relevant prevention lanes, outer-loop change log when rerunning, the concrete repo-specific prevention guard when applicable, and the applicable file-action/proof-tier/auth-exposure/runtime-contract/acceptance-traceability/validation-environment/developer-facing/deferred-follow-up entries or repo-specific equivalents.
7. Do not use `plan_adversarial_reviewer` for implementation completion. If it was used, its verdict does not count; rerun with `task_completion_adversarial_reviewer`.
8. A reviewer `PASS` is preliminary. Run `task_completion_review_critic` with the original evidence packet and exact reviewer output.
9. A phase/slice is complete only after `task_completion_adversarial_reviewer` returns `PASS` and `task_completion_review_critic` returns `AGREE_PASS`.
10. If the completion reviewer returns `FAIL_NEEDS_FIX`, `BLOCKED_INSUFFICIENT_EVIDENCE`, or `BLOCKED_OWNER_DECISION`, keep the phase/slice open, fix or resolve the issue, and rerun the completion reviewer.
11. If the critic returns `DISAGREE_EVIDENCE` or `DISAGREE_CONCERN`, keep the phase/slice open until a fresh review cycle resolves the dissent with cited evidence, a fix, an owner decision, or an explicit blocker.
12. The completion reviewer and critic must treat implementer summaries and reviewer agreement as claims until backed by raw evidence or a safe targeted rerun.
13. If plan review still fails after the bounded loop, do not finalize the plan. Report the latest scores and unresolved blockers to the owner.
14. Archive every plan, completion, and critic review under `docs/Adversarial Reviews/`.
15. Record reviewer/critic outcomes, archive paths, and the disagreement log in the final implementation report.

## Adversarial Plan Review Result

- Reviewer used: `plan_adversarial_reviewer`
- Owner questions asked:
- Owner answers received:
- Unanswered owner decisions:
- Iterations run:
- Loop cap used:
- Plan review archive paths:
- Final phase scores:
- Plan-quality/equivalent section scores:
  - Repo-specific equivalents or N/A reasons:
  - Plan Type:
  - Repo-specific prevention guard:
  - File Action Map:
  - Proof Tier Map:
  - Auth/Exposure Mode Matrix:
  - Runtime Emission vs Contract Map:
  - Acceptance Criteria Traceability Map:
  - Validation Environment Contract:
  - Developer-Facing Surface Check:
  - Deferred Follow-Ups:
  - Plan Quality Self-Review:
  - Adversarial Review Contract:
  - Phase/Slice Commit Contract:
- Findings fixed during iteration:
- Remaining blockers after capped loop:
- Remaining non-blocking risks:
- Owner decisions still required:
- Completion review agents required for implementation: `task_completion_adversarial_reviewer`, then `task_completion_review_critic` for any reviewer PASS
- Review archive folder: `docs/Adversarial Reviews/`
