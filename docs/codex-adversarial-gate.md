# Codex Adversarial Review Gate

This how-to guide explains how to use `codex-adversarial-gate` to keep implementation work open until independent reviewer and critic evidence is archived.

## Purpose

Use this skill when Codex is reviewing a plan, closing an implementation phase, or recovering from work that was marked complete without the required gate.

The skill treats completion as a claim that must be falsified before it is accepted. The implementing thread prepares evidence, a reviewer attempts to break the claim, and a critic audits any reviewer `PASS`.

## Before You Start

You need:

- the `codex-adversarial-gate` skill installed;
- the custom reviewer agent TOMLs installed;
- Python 3 if you want to use the archive helper;
- a clear plan, phase, slice, checkpoint, or grouped implementation boundary.

Install with the skill script because the marketplace install does not copy the custom reviewer agent TOMLs:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill codex-adversarial-gate
bash ~/.agents/skills/codex-adversarial-gate/scripts/install.sh
```

## Use The Gate For Implementation Closeout

Ask Codex:

```text
Use $codex-adversarial-gate to close this implementation slice with archived reviewer and critic evidence.
```

At each reviewable implementation boundary, Codex should:

1. Freeze the artifact and stop editing.
2. Build a compact evidence packet.
3. Run `task_completion_adversarial_reviewer`.
4. Archive the exact reviewer output.
5. Keep the work open if the reviewer does not return `PASS`.
6. Run `task_completion_review_critic` only after reviewer `PASS`.
7. Archive the exact critic output.
8. Accept completion only when the critic returns `AGREE_PASS`.

A loaded skill, reminder, checklist item, or promise to review later is not enough. The review cycle must finish before the phase or slice is marked complete.

## Build The Evidence Packet

The evidence packet should be compact and pointer-heavy. Include:

- phase or slice name and acceptance criteria;
- current branch and worktree status;
- changed files, including staged, unstaged, and untracked files;
- diff pointers;
- validation commands with cwd, exit status, and whether they ran after the latest fix;
- skipped checks and reasons;
- relevant plan entries and known risks;
- changed contracts, security or privacy surfaces, and user-facing behavior when relevant.

Reviewer agreement is not evidence by itself. The reviewer and critic should be able to trace claims back to raw code, diffs, logs, screenshots, or owner decisions.

## Use The Gate For Plan Review

Use plan review when drafting, updating, or finalizing a plan:

```text
Use $codex-adversarial-gate to adversarially review this plan before finalization.
```

Plan review uses `plan_adversarial_reviewer`, not the completion reviewer. A plan is ready only when each reviewable phase reaches `PASS_100` or the plan is explicitly blocked for an owner decision.

Do not use `plan_adversarial_reviewer` to close implementation work.

## Archive Review Output

Archive every plan review, completion review, critic review, and rerun output under:

```text
<repo>/docs/Adversarial Reviews/
```

Use the helper when Python 3 is available:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/codex-adversarial-gate/scripts/archive_adversarial_review.py" \
  --repo "$PWD" \
  --kind completion \
  --phase "parser cleanup" \
  --reviewer task_completion_adversarial_reviewer \
  --verdict PASS \
  --review-file ./review.md
```

If the review output contains a secret or credential, stop and report it instead of archiving silently.

## Report Results

Final implementation reports should include an `Adversarial Completion Review Results` table with:

- phase or slice;
- reviewer verdict and archive path;
- critic verdict and archive path;
- disagreement class;
- raw evidence checked;
- fixes or evidence required;
- final status.

Skipped, blocked, failed, disagreed, or unarchived gates must stay open. Do not report them as complete.

## Common Stops

If no independent reviewer context is available, stop with `BLOCKED_REVIEW_CONTEXT_UNAVAILABLE` instead of self-reviewing.

If a critic returns `DISAGREE_EVIDENCE` or `DISAGREE_CONCERN`, keep the work open, fix or gather evidence, then rerun a fresh reviewer and critic cycle.

If work was already marked complete without the gate, freeze the current artifact, reopen or qualify the status, run the missed gate, archive both outputs, and only then restore completion.

## File Layout

```text
skills/codex-adversarial-gate/
  SKILL.md
  agents/
    plan-adversarial-reviewer.toml
    task-completion-adversarial-reviewer.toml
    task-completion-review-critic.toml
  references/
  scripts/
    archive_adversarial_review.py
    install.sh
  templates/
```

## Related Docs

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [Reference](reference.md)
