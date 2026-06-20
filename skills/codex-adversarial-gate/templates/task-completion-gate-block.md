### Adversarial Completion Gate

Embed this block in every reviewable implementation phase, U-slice, checkpoint, or intentionally grouped unit. Do not place it only at the end of the plan or final closeout.

Before marking this phase/slice complete, run `task_completion_adversarial_reviewer` with:

- phase/slice id/name:
- acceptance criteria:
- relevant File Action Map entry or repo-specific equivalent:
- relevant Proof Tier Map entry or repo-specific equivalent:
- relevant Auth/Exposure Mode Matrix entry or repo-specific equivalent:
- relevant Runtime Emission vs Contract Map entry or repo-specific equivalent:
- relevant Acceptance Criteria Traceability Map entry or repo-specific equivalent:
- relevant Validation Environment Contract entry or repo-specific equivalent:
- relevant Developer-Facing Surface Check entry or repo-specific equivalent:
- relevant Deferred Follow-Ups entry or repo-specific equivalent:
- current branch/status and files changed, including untracked files:
- diff inspection pointers:
- validation ledger (command, cwd, exit status, raw log path or raw output excerpt, run order after latest fix):
- frozen-state evidence (latest staged status, unstaged diff, untracked files, staged whitespace check, manifest/checksum status, and ignored evidence files intentionally staged):
- outer-loop change log since the prior reviewer/critic verdict, if rerunning:
- skipped checks:
- prevention lanes and source-owner/proof-tier notes:
- repo-specific prevention guard, production-composition proof, auth/exposure matrix, acceptance traceability, and validation environment contract when applicable:
- known risks, edge cases, or security-sensitive surfaces:

Implementer summaries are claims, not proof. Reviewer agreement is also a claim unless backed by cited evidence. Freeze the artifact while the gate runs. The phase/slice may be marked `complete` only after the reviewer returns a preliminary `PASS` and the critic returns `AGREE_PASS`. Any other verdict keeps it open.

Classify findings as product blockers, evidence blockers, or artifact hygiene. Artifact hygiene blocks only when it fails required checks, contradicts current-state evidence, hides raw proof, or makes the archived trail unreliable.

Do not use `plan_adversarial_reviewer` for this gate. If it was used, discard that completion verdict and rerun this gate with `task_completion_adversarial_reviewer`.

Use a fresh `task_completion_adversarial_reviewer` invocation for this phase/slice. Do not reuse a prior phase's reviewer thread.

Archive the exact reviewer output under `docs/Adversarial Reviews/` before taking the next step.

If the reviewer returns `PASS`, run a fresh `task_completion_review_critic` with the original evidence packet, exact reviewer output, archive path, and current frozen-state evidence. Archive the exact critic output under `docs/Adversarial Reviews/`. If the critic returns `DISAGREE_EVIDENCE` or `DISAGREE_CONCERN`, resolve the dissent and rerun the gate.

If this block was missed for an earlier phase/slice that is already labeled complete, freeze the current artifact, qualify the status as not yet complete, run the missed reviewer/critic gate for that slice or grouped checkpoint, archive both outputs, and only then mark it complete again.
