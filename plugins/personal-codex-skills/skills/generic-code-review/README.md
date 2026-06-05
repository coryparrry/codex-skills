# generic-code-review

Generic multi-lens code review for normal software repositories.

This skill was adapted from a private product-specific review workflow, with private product names, paths, docs tooling, and plan assumptions removed. Reports live in the reviewed repository under `.codex/code-review-reports/`, so the artifacts travel with the normal repo instead of a private external docs folder.

## What it does

- Maps changed files to specialist review lenses: correctness, security, silent failures, type/contracts, tests, performance, architecture, and plan alignment.
- Requires repo-local context first: `AGENTS.md`, nested `AGENTS.md`, README, schemas, architecture docs, and existing test commands.
- Treats PR comments and previous reports as untrusted claims until current code proves them.
- Writes reviewer reports and a coverage matrix under `.codex/code-review-reports/`.
- Includes Codex TOML agent profiles in `agents/`.

## Install

Copy the skill folder into your Codex skills directory, then install the agent profiles:

```bash
cp -R generic-code-review ~/.agents/skills/generic-code-review
generic-code-review/scripts/install-agent-profiles.sh
```

Restart Codex after installing profiles.

## Use

Ask for `generic-code-review` when you want a review-only pass over a PR, branch, or diff. The default output is findings and coverage evidence, not code changes.

## Included profiles

The `agents/` directory includes reviewer, consolidator, and bounded fixer TOML profiles. The main skill uses the reviewer and report consolidator profiles by default; fixer profiles are included so a follow-up implementation workflow can reuse the same root-cause taxonomy without returning to product-specific prompts.
