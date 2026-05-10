#!/usr/bin/env bash
set -euo pipefail

force_delete_unmerged=false

for arg in "$@"; do
  case "$arg" in
    --force-delete-unmerged)
      force_delete_unmerged=true
      ;;
    -h|--help)
      cat <<'USAGE'
Usage: clean_merged_branch.sh [--force-delete-unmerged]

Safely switch a Git repo back to its default branch, pull latest changes,
and delete the branch that was active when the script started.

Use --force-delete-unmerged only when the user has clearly said the branch
has already been merged or is no longer needed.
USAGE
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 2
      ;;
  esac
done

run() {
  printf '+ %s\n' "$*"
  "$@"
}

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "This folder is not inside a Git repo." >&2
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Stopped: this repo has local changes." >&2
  echo "Commit, stash, or discard them before cleaning up a merged branch." >&2
  git status --short
  exit 1
fi

start_branch="$(git branch --show-current)"
if [[ -z "$start_branch" ]]; then
  echo "Stopped: Git is in detached HEAD state, so there is no current branch to clean up." >&2
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "Stopped: this repo has no 'origin' remote." >&2
  exit 1
fi

run git fetch origin --prune

default_ref="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)"
if [[ -n "$default_ref" ]]; then
  default_branch="${default_ref#origin/}"
elif git show-ref --verify --quiet refs/remotes/origin/main; then
  default_branch="main"
elif git show-ref --verify --quiet refs/remotes/origin/master; then
  default_branch="master"
else
  echo "Stopped: could not identify the default branch from origin/HEAD, origin/main, or origin/master." >&2
  exit 1
fi

if [[ "$start_branch" != "$default_branch" ]]; then
  run git switch "$default_branch"
fi

run git pull --ff-only origin "$default_branch"

deleted_branch=false
if [[ "$start_branch" != "$default_branch" ]]; then
  if git show-ref --verify --quiet "refs/heads/$start_branch"; then
    if run git branch -d "$start_branch"; then
      deleted_branch=true
    elif [[ "$force_delete_unmerged" == true ]]; then
      echo "Safe deletion failed, but forced deletion was explicitly enabled."
      run git branch -D "$start_branch"
      deleted_branch=true
    else
      echo "The old branch was not deleted because Git does not consider it fully merged." >&2
      echo "If GitHub used squash or rebase merge and the branch is definitely no longer needed, rerun with --force-delete-unmerged." >&2
      exit 1
    fi
  fi
fi

echo
echo "Cleanup complete."
echo "Started on: $start_branch"
echo "Default branch updated: $default_branch"
if [[ "$start_branch" == "$default_branch" ]]; then
  echo "No old branch deleted because you were already on the default branch."
elif [[ "$deleted_branch" == true ]]; then
  echo "Deleted old local branch: $start_branch"
else
  echo "Old local branch was already absent: $start_branch"
fi
echo
git status --short --branch
