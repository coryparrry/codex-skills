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
- plan maps or repo-specific equivalents;
- repo-specific guard, source-owner/proof-tier notes, prevention lanes, risks, and touched user/security/API/schema/docs/runtime surfaces;
- archive path for every reviewer and critic output under `docs/Adversarial Reviews/`.

## PASS Requires

- implementer claims are backed by raw evidence or a safe targeted rerun;
- artifact stayed frozen during review;
- the final staged artifact was frozen before review or critic dispatch: intended ignored evidence files are staged, manifests/checksums are current, and current status/whitespace checks were rerun after the latest archive or evidence change;
- acceptance criteria are met and changed files match task scope;
- validation proves changed behavior and is current to the branch/worktree;
- required owners, proof tiers, auth/exposure modes, runtime/contract surfaces, acceptance traceability, validation environment, docs/types/contracts/generated artifacts, and deferred follow-ups are satisfied or explicitly recorded as owner-accepted gaps;
- selected prevention lanes have no blocker;
- skipped checks are justified;
- no visible secret, personal path, unsafe exposure, privacy/security regression, or unrelated scope creep exists;
- exact reviewer/critic outputs are archived before closeout.

## Non-PASS Triggers

Return non-PASS when validation is missing/weak/stale/wrong-branch, only summaries exist, runtime behavior only compiled/linted, plan criteria were vague, scope drifted, source docs/contracts/tests are stale, static schema parity stands in for runtime proof, accepted follow-ups are unrecorded, prevention lanes block, critic disagrees, artifact changed during review, archive paths are missing, or an owner decision is needed.

## Blocker vs Hygiene Classification

Classify findings before deciding whether to block:

- Product blocker: unmet acceptance criteria, incorrect behavior, unsafe exposure, source-owner drift, stale generated/source-truth artifacts, scope creep, or validation that does not prove the changed behavior.
- Evidence blocker: missing raw logs, stale/wrong-branch validation, unstaged or untracked files that alter the reviewed artifact, ignored evidence files that were not staged, missing manifests/checksums when the packet relies on them, or a live command contradicting the packet.
- Artifact hygiene: archive formatting, evidence-file whitespace, filename polish, or log packaging details that do not change product behavior.

Artifact hygiene blocks only when it fails a required repo check, contradicts the packet's current-state claims, hides or corrupts raw evidence, or would make the archived gate trail unreliable. Otherwise, report it as a nonblocking residual risk or cleanup note.
