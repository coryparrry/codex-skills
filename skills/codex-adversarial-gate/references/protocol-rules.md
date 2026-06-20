# Protocol Rules

Read this for any use of `codex-adversarial-gate`.

## Core Model

The implementing Codex thread is the implementer. Reviewer and critic roles are adversarial witnesses.

- The implementer prepares the evidence packet, receives the review, fixes issues, and archives the exact review output.
- The reviewer attempts to falsify the implementer's claim.
- The critic audits a reviewer `PASS` for false consensus, missing evidence, dropped dissent, and scope drift.

Keep the reviewer and critic read-only. Archiving is an implementer responsibility because letting the reviewer mutate the repo during review weakens the frozen-artifact boundary.

For `ce-work`, the protocol applies throughout the implementation flow. A loaded skill, pending checklist item, or final closeout reminder is not enough; every reviewable phase or slice boundary must stop for the reviewer-plus-critic archive cycle before the implementer can mark that unit complete.

## Paper-Derived Process

- Freeze the artifact before review. Any implementation edit, staging change, generated artifact change, or fix command invalidates the active review cycle.
- Freeze once before the decisive review cycle whenever possible: write evidence and archives, stage ignored evidence files intentionally, refresh checksums/manifests, and rerun current staged status and whitespace checks before dispatch.
- Separate review from editing. Reviewers inspect; the implementer fixes only after a non-PASS verdict or after closeout.
- Treat reviewer `PASS` as preliminary. Final acceptance requires critic `AGREE_PASS`.
- Preserve disagreement. `DISAGREE_EVIDENCE` and `DISAGREE_CONCERN` must be resolved through a fresh review cycle or explicit blocker.
- Reject false consensus. Agreement is worthless without raw evidence.
- Filter thin findings. Unsupported speculation does not prove failure, but it should become a concrete missing-evidence request before PASS.
- Separate product and evidence blockers from artifact hygiene. Hygiene blocks only when it fails required checks, contradicts the evidence packet, hides raw proof, or makes the archived trail unreliable.
- Run a scope critic. The critic must compare the diff against the task, plan, implementation unit, and user-requested boundary.
- Keep an archive and disagreement log so humans can audit what happened later.

## Reviewer Routing

- Use `plan_adversarial_reviewer` only for plan quality.
- Use `task_completion_adversarial_reviewer` only for implementation closeout.
- Use `task_completion_review_critic` only after completion reviewer `PASS`.
- Use fresh independent invocations or threads for each reviewable phase/slice and critic audit.
- If no independent reviewer context is available, stop with `BLOCKED_REVIEW_CONTEXT_UNAVAILABLE` instead of self-reviewing.
- If the bundled custom agents are unavailable but an independent reviewer context exists, use `references/reviewer-prompts.md`.

## Hard Guardrails

- Do not let the implementer self-score its own plan as 100.
- Do not let the implementer mark work complete while reviewer or critic verdicts are missing, failed, blocked, disagreed, or unarchived.
- Do not let the implementer continue treating a phase/slice as complete after discovering the gate was skipped. Reopen or qualify the status, freeze the artifact, run the missed gate, and archive the exact outputs.
- Do not accept "looks good" as adversarial review.
- Do not weaken the 100 threshold by averaging phase scores.
- Do not run unbounded plan-review loops.
- Do not fork full implementation context into reviewer roles; send compact review packets.
- Do not hide unasked owner decisions as assumptions, TBDs, or implementation choices.
