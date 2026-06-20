# Git Clean Merged Branch

> *"Stop babysitting git. One command, done."*

I built this because I was fed up with the repetitive chore of cleaning up local branches after they'd been merged on GitHub. Fetch, switch, pull, delete — the same four commands every single time, and I'd still occasionally delete the wrong branch or forget to pull before switching. I found it boring, so I automated it.

This skill wraps the entire cleanup into a single command. It inspects before it acts, refuses to run on a dirty worktree, and handles edge cases like squash-merge detection and detached HEAD.

---

## What it does

- Fetches from `origin` with pruning
- Resolves the repo's actual default branch (from `origin/HEAD`, falling back to `main` then `master`)
- Switches to the default branch
- Fast-forward-only pulls to avoid surprise merges
- Safely deletes the old local branch (`git branch -d`)
- Shows the final repo status so you can confirm everything is clean

## What it doesn't do

- Touch uncommitted or untracked changes (it stops and tells you to handle them first)
- Run `git reset --hard`, `git clean`, or any other broad destructive command
- Delete branches that git considers unmerged (unless you explicitly pass `--force-delete-unmerged`)
- Work outside a git repo or without an `origin` remote

## How it works

```
clean_merged_branch.sh
  ├─ Check: inside a git repo?
  ├─ Check: clean worktree?
  ├─ Record current branch
  ├─ git fetch origin --prune
  ├─ Resolve default branch
  ├─ git switch <default>
  ├─ git pull --ff-only origin <default>
  ├─ git branch -d <old-branch>   (or -D with --force-delete-unmerged)
  └─ git status --short --branch
```

The script stops at the first sign of trouble and tells you exactly what's wrong, rather than guessing and making things worse.

## Installation

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills

# Install the skill
mkdir -p ~/.codex/skills
cp -R skills/git-clean-merged-branch ~/.codex/skills/git-clean-merged-branch
```

Then restart Codex. That's it — no agent profiles to install, no dependencies.

---

## Usage

From inside any repo:

```text
clean merged branch
```

Or invoke the skill by name:

```text
git-clean-merged-branch
```

**Good fits:**

- You just merged a PR on GitHub and want the local branch gone
- You've accumulated stale local branches and want to clean up one at a time
- You want a safe, predictable cleanup that won't nuke uncommitted work

**Not a fit:**

- You want to batch-delete many branches at once (this cleans one branch per run)
- You have uncommitted changes you intend to keep (commit or stash them first)

### Force-delete after squash/rebase merge

If GitHub used squash or rebase merge, `git branch -d` will refuse because the commits don't match. When you know the branch has already been merged and is no longer needed:

```bash
bash ~/.codex/skills/git-clean-merged-branch/scripts/clean_merged_branch.sh --force-delete-unmerged
```

---

## Layout

```text
skills/git-clean-merged-branch/
  SKILL.md                    — the skill Codex loads
  agents/                     — agent metadata
  scripts/                    — the cleanup script
```

---

## License

MIT — see [LICENSE](../LICENSE).
