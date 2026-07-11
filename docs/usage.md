# Use Codex Skills

This how-to guide explains when and how to invoke the skills in this repository.

## Purpose

Use this guide when the skills are already installed and you want to choose the right one for a task.

## Before You Start

Make sure the relevant skill is installed. See [Install Codex Skills](installation.md).

For `codex-adversarial-gate`, also make sure the custom reviewer agent TOMLs are installed. The skill depends on them for the normal reviewer and critic flow.

## Choose A Skill

| Goal | Skill |
|---|---|
| Create, refresh, or repair a repository context layer | `knowledge-setup` |
| Review a plan before execution | `codex-adversarial-gate` |
| Close an implementation phase or slice | `codex-adversarial-gate` |
| Recover from a skipped completion gate | `codex-adversarial-gate` |
| Design or create a bounded Codex automation loop | `writing-codex-loops` |
| Coordinate multiple related work units through fresh worktree threads | `multi-phase-orchestrator` beta |
| Audit repo readiness before work | `auditing-repository-health` |
| Clean up one merged local Git branch | `git-clean-merged-branch` |
| Classify PR review feedback | `triage-review-comments` |

## Gate Plan Or Implementation Work

Use `codex-adversarial-gate` when Codex should not mark work complete without independent review evidence.

For a plan review, ask:

```text
Use $codex-adversarial-gate to adversarially review this plan before finalization.
```

For implementation closeout, ask:

```text
Use $codex-adversarial-gate to close this implementation slice with archived reviewer and critic evidence.
```

For implementation closeout, Codex should:

1. Build a compact evidence packet.
2. Pre-freeze the final review surface, including staged intended files, ignored evidence logs, manifest/checksum refreshes when used, and current status/whitespace checks.
3. Run `task_completion_adversarial_reviewer`.
4. Archive the exact reviewer output.
5. If archiving changes the staged artifact, stage the archive and rerun current staged status/whitespace checks.
6. Run `task_completion_review_critic` when the reviewer returns `PASS`, passing the reviewer archive path and frozen-state evidence.
7. Archive the exact critic output.
8. Accept completion only when the critic returns `AGREE_PASS`.

Do not use the plan reviewer to close implementation work.

## Write A Codex Loop

Use `writing-codex-loops` when a workflow needs explicit state, cadence, feedback, retry rules, stop conditions, and escalation.

For an actual automation, ask:

```text
Use $writing-codex-loops to create a heartbeat that checks this PR every 10 minutes until CI passes, the same failure repeats three times, or owner input is needed.
```

For a draft-only contract, ask:

```text
Use $writing-codex-loops to draft a bounded loop contract for weekly dependency review, but do not create the automation.
```

The skill should classify the request before acting:

1. Actual loop requests create or update a Codex Automation.
2. Draft-only requests return a loop contract and do not create an automation.
3. Same-thread or sub-hour follow-ups normally use a thread heartbeat.
4. Independent recurring project scans need durable state outside chat context.
5. Immediate repetition in the current turn is an in-thread loop, not an automation.

Every loop should include live observation, progress checks, idempotency, retry limits, success stops, blocked stops, and a concrete escalation question.

## Audit Repository Health

Use `auditing-repository-health` when a repo needs a readiness audit before work starts or when setup, scripts, validation, packaging, generated files, or docs health are unclear.

Ask:

```text
Use $auditing-repository-health to audit this repository before starting work.
```

The skill runs a bundled read-only audit script over live repo state, instructions, existing scripts, validation commands, package surfaces, ignore hygiene, repo size/history risk, and docs link health. It reports a readiness verdict, ranked findings, script responsibilities classified as `present`, `documented`, `missing`, or `not_applicable`, commands run, and anything not checked.

For missing standard scripts, ask:

```text
Use $auditing-repository-health to check whether this repo has the setup, testing, validation, and shipping responsibilities it actually needs.
```

The skill uses script/bootstrap, setup, update, server, test, cibuild, and console as a reference vocabulary, but it should map to the repo's existing conventions rather than forcing those exact names.

## Set Up Repository Context

Use `knowledge-setup` when a repository needs a compact, evidence-backed context layer for repeated agent work.

Ask:

```text
Use $knowledge-setup in this repo.
```

The skill reconciles `AGENTS.md`, `.repo/context.md`, and `.repo/graph.json` from live source, tests, manifests, CI, and documentation. Future agents read a compact context kernel and route catalog, then load only `general` plus the selected route's evolved context and graph nodes before verifying the listed source files. Run the same trigger again to refresh or repair drift without replacing verified entries wholesale.

## Coordinate Multiple Work Units

Use `multi-phase-orchestrator` beta only when you explicitly want Codex to coordinate multiple related units through fresh worktree threads.

Ask:

```text
Use $multi-phase-orchestrator to coordinate these work units with fresh worktree threads.
```

The skill should bind the work source, route required skills into each child thread, track unit status, verify child outputs against live files and validation, then integrate completed units deliberately.

## Archive Review Output

Archive a review from a file:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/codex-adversarial-gate/scripts/archive_adversarial_review.py" \
  --repo "$PWD" \
  --kind completion \
  --phase "parser cleanup" \
  --reviewer task_completion_adversarial_reviewer \
  --verdict PASS \
  --review-file ./review.md
```

Archive a review from standard input:

```bash
printf '%s\n' "$REVIEW_TEXT" | python3 "${CODEX_HOME:-$HOME/.codex}/skills/codex-adversarial-gate/scripts/archive_adversarial_review.py" \
  --repo "$PWD" \
  --kind critic \
  --phase "parser cleanup" \
  --reviewer task_completion_review_critic \
  --verdict AGREE_PASS \
  --stdin
```

The helper writes review records under:

```text
<repo>/docs/Adversarial Reviews/
```

## Clean Up A Merged Branch

Use `git-clean-merged-branch` after a PR has been merged and you want the local branch removed safely.

From inside the target Git repository, ask:

```text
git-clean-merged-branch
```

The skill should run its cleanup script from the installed skill folder:

```bash
bash "${CODEX_HOME:-$HOME/.codex}/skills/git-clean-merged-branch/scripts/clean_merged_branch.sh"
```

If GitHub used squash or rebase merge and the branch is definitely no longer needed, use the force-delete option:

```bash
bash "${CODEX_HOME:-$HOME/.codex}/skills/git-clean-merged-branch/scripts/clean_merged_branch.sh" --force-delete-unmerged
```

Do not use the force-delete option unless the branch is known to be merged or intentionally disposable.

## Triage PR Review Comments

Use `triage-review-comments` when a PR has review comments that need sorting before implementation.

Ask:

```text
Use $triage-review-comments to triage the review comments on this PR.
```

The skill should:

1. Load the current PR review context.
2. Inventory open and resolved inline threads, general comments, and standalone review findings.
3. Remove boilerplate and non-actionable comments.
4. Deduplicate repeated findings.
5. Classify actionable items into `Fix now`, `Fix if cheap`, `Defer`, or `Ignore`.
6. Resolve clearly fixed inline threads when GitHub tooling is available.
7. Recommend prevention checks for real issues.

The skill classifies review work. It does not implement fixes by itself.

## Common Cases

If a completion gate was skipped, use `codex-adversarial-gate` to freeze the current artifact, reopen the status, run reviewer and critic, archive both outputs, and only then restore completion.

If a loop request says only "keep going until done", use `writing-codex-loops` to replace it with observable continue, success, blocked, and no-progress predicates.

If agents repeatedly rediscover repository structure or load a large graph, use `knowledge-setup` to reconcile a routes-first context layer. Do not use it as a substitute for live source verification.

If branch cleanup stops on local changes, commit, stash, or discard those changes before rerunning the skill.

If review triage has no PR context, load the PR or provide enough review context before invoking the skill.

## Related Docs

- [Installation](installation.md)
- [Reference](reference.md)
- [Knowledge Setup](knowledge-setup.md)
- [Audit Repository Health](auditing-repository-health.md)
- [Codex Adversarial Review Gate](codex-adversarial-gate.md)
- [Writing Codex Loops](writing-codex-loops.md)
- [Multi-Phase Orchestrator](multi-phase-orchestrator.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
- [Triage Review Comments](triage-review-comments.md)
