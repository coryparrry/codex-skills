# Task Completion Gate Rubric

Use when `task_completion_adversarial_reviewer` reviews a phase/slice before closeout.

## Verdicts

| Verdict | Meaning |
|---|---|
| `PASS` | Preliminary reviewer pass. The phase/slice is not complete until critic `AGREE_PASS`. |
| `FAIL_NEEDS_FIX` | Concrete defect, unmet requirement, or scope problem. |
| `BLOCKED_INSUFFICIENT_EVIDENCE` | Evidence is too weak or unavailable. |
| `BLOCKED_OWNER_DECISION` | Owner decision is required. |

Critic verdicts: `AGREE_PASS`, `DISAGREE_EVIDENCE`, `DISAGREE_CONCERN`.

## Required Evidence

- exact acceptance criteria and relevant plan excerpt;
- current branch/status, staged diff, unstaged diff, and relevant untracked files;
- diff pointers or narrow patch excerpts;
- validation ledger with command, cwd, exit status, raw log/output, and run order after latest fix;
- rerun change log when applicable;
- skipped checks and reasons;
- relevant plan entries, acceptance criteria, or repo-specific equivalents;
- changed contracts, user-facing behavior, security/privacy surfaces, docs, runtime surfaces, risks, and validation environment notes;
- archive path for every reviewer and critic output under `docs/Adversarial Reviews/`.

## PASS Requires

- implementer claims are backed by raw evidence or a safe targeted rerun;
- artifact stayed frozen during review;
- acceptance criteria are met and changed files match task scope;
- validation proves changed behavior and is current to the branch/worktree;
- auth/exposure modes, runtime/contract surfaces, acceptance traceability, validation environment, docs/types/contracts/generated artifacts, and deferred follow-ups are satisfied or explicitly recorded as owner-accepted gaps;
- skipped checks are justified;
- no visible secret, personal path, unsafe exposure, privacy/security regression, or unrelated scope creep exists;
- exact reviewer/critic outputs are archived before closeout.

## Non-PASS Triggers

Return non-PASS when validation is missing/weak/stale/wrong-branch, only summaries exist, runtime behavior only compiled/linted, plan criteria were vague, scope drifted, source docs/contracts/tests are stale, static schema parity stands in for runtime proof, accepted follow-ups are unrecorded, critic disagrees, artifact changed during review, archive paths are missing, or an owner decision is needed.
