# Clean Up A Merged Git Branch

This how-to guide explains how to use `git-clean-merged-branch` to clean up one local branch after it has been merged on GitHub.

## Purpose

Use this skill when you are on a local branch that has already been merged and you want to:

- fetch the latest remote branch state;
- switch back to the repository default branch;
- fast-forward pull the default branch;
- delete the old local branch safely.

## Before You Start

You need:

- the `git-clean-merged-branch` skill installed;
- a Git repository with an `origin` remote;
- a clean worktree;
- a current branch, not detached `HEAD`.

The skill stops when the worktree has uncommitted or untracked changes. It will not stash, discard, or reset them for you.

## Install The Skill

Install the skill with the `skills` CLI:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill git-clean-merged-branch
```

Restart Codex if the skill does not appear.

## Run The Skill

From inside the repository whose branch you want to clean up, ask Codex:

```text
git-clean-merged-branch
```

The standard script command is:

```bash
bash "${CODEX_HOME:-$HOME/.codex}/skills/git-clean-merged-branch/scripts/clean_merged_branch.sh"
```

## Understand The Output

The script prints each Git command before it runs it. On success, it reports:

- the branch where cleanup started;
- the default branch it updated;
- whether the old local branch was deleted;
- the final `git status --short --branch` output.

The script resolves the default branch from `origin/HEAD`. If that is unavailable, it falls back to `origin/main` and then `origin/master`.

## Handle Squash Or Rebase Merges

After a squash or rebase merge, Git may not consider the local branch merged because the commit history changed.

If the branch has definitely been merged or is intentionally disposable, rerun with:

```bash
bash "${CODEX_HOME:-$HOME/.codex}/skills/git-clean-merged-branch/scripts/clean_merged_branch.sh" --force-delete-unmerged
```

Use this option only when deletion is intentional. It changes branch deletion from `git branch -d` to `git branch -D` after the safe deletion attempt fails.

## Common Stops

If the repo has local changes, commit, stash, or discard them before rerunning.

If there is no `origin` remote, add or fix the remote before rerunning.

If the repository is in detached `HEAD`, switch to the branch you want to clean up before rerunning.

If the default branch cannot be identified, check `origin/HEAD`, `origin/main`, or `origin/master`.

## What The Skill Will Not Do

The skill will not:

- batch-delete many branches;
- clean up remote branches;
- run `git reset --hard`;
- run `git clean`;
- discard or stash local changes;
- force-delete an unmerged branch unless explicitly requested with `--force-delete-unmerged`.

## File Layout

```text
skills/git-clean-merged-branch/
  SKILL.md
  agents/
    openai.yaml
  scripts/
    clean_merged_branch.sh
```

## Related Docs

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [Reference](reference.md)
- [Triage Review Comments](triage-review-comments.md)
