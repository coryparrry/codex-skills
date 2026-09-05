# Triage PR Review Comments

This how-to guide explains how to use `triage-review-comments` to classify PR review feedback and, when explicitly requested, carry valid findings through fixes or review-thread actions.

## Purpose

Use this skill when a PR has review comments from humans or automation and you need a practical triage pass.

The skill treats each comment as a hypothesis. It checks comments against the current code, removes noise, deduplicates repeated findings, and sorts actionable work into buckets.

Triage is read-only by default. A request to triage, review, classify, inspect, or investigate does not authorize patches, commits, pushes, thread replies or resolution, or follow-up creation.

## Before You Start

You need:

- the `triage-review-comments` skill installed;
- access to the PR review context;
- GitHub tooling available if you want fixed inline threads resolved remotely;
- Linear context available if deferred items should be filed in Linear.

The skill is most useful before you start implementing review feedback.

## Install The Skill

Install the skill with the `skills` CLI:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill triage-review-comments
```

Restart Codex if the skill does not appear.

## Run The Skill

Ask Codex from a thread that has access to the PR:

```text
Use $triage-review-comments to triage the review comments on this PR.
```

The skill should load review context before classifying comments. Do not classify comments only from memory or from a PR title.

To authorize changes, say what should happen, for example:

```text
Use $triage-review-comments to verify and fix the valid review comments, then resolve the threads fixed by that work.
```

Once a fix, resolution, or follow-up creation is explicitly authorized, the skill completes that class of action without asking again for each item.

## Understand The Output

The skill reports:

- inventory counts for review comments and threads;
- comments grouped into `Fix now`, `Fix if cheap`, `Defer`, and `Ignore`;
- review fix briefs for every `Fix now` item, with current behavior, desired behavior, key interfaces, acceptance criteria, validation, and out-of-scope boundaries;
- threads already resolved or recommended for resolution;
- remote mutation and refetch evidence when resolution was authorized;
- prevention checks for real issues;
- next steps.

Use `Fix now` for reachable, meaningful issues that should block merge.

Use `Fix if cheap` for likely-valid, low-risk issues that are worth taking now if they stay small.

Use `Defer` for real work that should become follow-up rather than block the current PR.

Use `Ignore` for duplicate, stale, speculative, style-only, or already-fixed comments.

## Handle Common Cases

If a bot leaves a walkthrough or summary with no concrete finding, classify it as non-actionable.

If several comments describe the same underlying issue, keep one representative finding and mark the rest as duplicates.

If code already fixes an inline thread, recommend resolution in read-only mode. Resolve and refetch it when that action was explicitly authorized.

If a real issue is deferred, recommend the right follow-up system in read-only mode. Create or update the record when tracking was explicitly authorized and project context is clear.

If no PR context is available, stop and ask for the PR or review material instead of guessing.

## What The Skill Will Not Do

Without explicit authorization, the skill will not:

- implement fixes;
- reply to or resolve review threads;
- create deferred follow-up records;
- replace owner judgment on whether deferred work is worth tracking;
- resolve general PR conversation comments that GitHub does not expose as resolvable threads;
- invent PR context that is not available.

## File Layout

```text
skills/triage-review-comments/
  SKILL.md
  agents/
    openai.yaml
  references/
    triage-review-comments.md
```

## Related Docs

- [Installation](../installation.md)
- [Usage Guide](../usage.md)
- [Reference](../reference.md)
- [Git Clean Merged Branch](../git-workflow/git-clean-merged-branch.md)
