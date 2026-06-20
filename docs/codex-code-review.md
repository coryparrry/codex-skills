# Codex Code Review

This how-to guide explains how to use `codex-code-review` for a generic, repository-local review pass.

## Purpose

Use this skill when you want Codex to review a PR, branch, or diff without applying fixes by default.

The skill routes changed files through specialist review lenses, writes review artifacts into the reviewed repository, and keeps private project assumptions out of the workflow.

## Before You Start

You need:

- the `codex-code-review` skill installed;
- the bundled review agent TOMLs installed;
- a Git repository, PR, branch, or diff to review;
- enough repository context for the review, such as `AGENTS.md`, README, schemas, architecture docs, or test commands when they exist.

Install the skill and agent profiles:

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills
mkdir -p ~/.codex/skills
cp -R skills/codex-code-review ~/.codex/skills/codex-code-review
bash ~/.codex/skills/codex-code-review/scripts/install-agent-profiles.sh
```

## Run The Skill

Ask Codex:

```text
Use $codex-code-review to review this PR.
```

The default behavior is review-only. Do not expect it to edit source files unless you explicitly ask Codex to implement fixes after the review.

## Understand The Output

The skill writes reports under the reviewed repository:

```text
.codex/code-review-reports/
```

A broad review may use lenses for correctness, security, silent failures, type contracts, tests, performance, architecture, and plan alignment. Narrow reviews should include only the relevant lanes and record omitted lenses honestly.

## What The Skill Will Not Do

The skill will not:

- apply fixes by default;
- import private project paths or assumptions;
- treat PR comments as true without checking current code;
- write reports outside the reviewed repository;
- claim coverage for omitted review lenses.

## File Layout

```text
skills/codex-code-review/
  SKILL.md
  agents/
  assets/
  references/
  scripts/
```

## Related Docs

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [Reference](reference.md)
