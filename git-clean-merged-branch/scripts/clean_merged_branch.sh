#!/usr/bin/env bash
set -euo pipefail

force_delete_unmerged=false
verify_squash_merge=true
delete_remote=true

for arg in "$@"; do
  case "$arg" in
    --force-delete-unmerged)
      force_delete_unmerged=true
      ;;
    --no-verify-squash-merge)
      verify_squash_merge=false
      ;;
    --delete-remote)
      delete_remote=true
      ;;
    --keep-remote)
      delete_remote=false
      ;;
    -h|--help)
      cat <<'USAGE'
Usage: clean_merged_branch.sh [--force-delete-unmerged] [--no-verify-squash-merge] [--keep-remote]

Safely switch a Git repo back to its default branch, pull latest changes,
and delete the branch that was active when the script started.

By default, if safe deletion fails, the script checks GitHub for a merged PR
from the starting branch and verifies the branch diff equals the merged PR diff
before deleting the local branch with git branch -D.

Use --force-delete-unmerged only when the user has clearly said the branch has
already been merged or is no longer needed, even if squash-merge verification is
unavailable.

By default, the old origin branch is deleted after local cleanup succeeds. Use
--keep-remote only when the remote branch should remain.
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

verify_squash_merged_branch() {
  local branch="$1"

  if ! command -v gh >/dev/null 2>&1; then
    echo "Squash-merge verification skipped: gh is not installed." >&2
    return 1
  fi

  local pr_info
  pr_info="$(
    gh pr list \
      --state merged \
      --head "$branch" \
      --limit 1 \
      --json number,url,mergedAt,mergeCommit,commits \
      --jq '.[] | [.number, .url, .mergedAt, (.mergeCommit.oid // ""), ((.commits // []) | length)] | @tsv' 2>/dev/null || true
  )"

  if [[ -z "$pr_info" ]]; then
    echo "Squash-merge verification failed: no merged GitHub PR found for '$branch'." >&2
    return 1
  fi

  local pr_number pr_url merged_at merge_oid commit_count
  IFS=$'\t' read -r pr_number pr_url merged_at merge_oid commit_count <<< "$pr_info"

  if [[ -z "$merge_oid" ]]; then
    echo "Squash-merge verification failed: merged PR #$pr_number has no merge commit OID." >&2
    return 1
  fi

  if [[ ! "$commit_count" =~ ^[0-9]+$ || "$commit_count" -lt 1 ]]; then
    echo "Squash-merge verification failed: merged PR #$pr_number has no commit count." >&2
    return 1
  fi

  local merge_parent
  if ! merge_parent="$(git rev-parse "$merge_oid^" 2>/dev/null)"; then
    echo "Squash-merge verification failed: could not resolve parent for merge commit '$merge_oid'." >&2
    return 1
  fi

  local branch_patch_id merge_patch_id
  local matched_shape=""
  local candidates=("$merge_parent:squash")

  if [[ "$commit_count" -gt 1 ]]; then
    local rebase_base
    if rebase_base="$(git rev-parse "$merge_oid~$commit_count" 2>/dev/null)"; then
      candidates+=("$rebase_base:rebase")
    fi
  fi

  local candidate candidate_base candidate_shape
  for candidate in "${candidates[@]}"; do
    candidate_base="${candidate%%:*}"
    candidate_shape="${candidate##*:}"

    if ! branch_patch_id="$(git diff --full-index "$candidate_base...$branch" | git patch-id --stable | awk '{print $1}')"; then
      continue
    fi

    if ! merge_patch_id="$(git diff --full-index "$candidate_base" "$merge_oid" | git patch-id --stable | awk '{print $1}')"; then
      continue
    fi

    if [[ -n "$branch_patch_id" && "$branch_patch_id" == "$merge_patch_id" ]]; then
      matched_shape="$candidate_shape"
      break
    fi
  done

  if [[ -z "$matched_shape" ]]; then
    echo "Squash-merge verification failed: branch diff does not match merged PR #$pr_number." >&2
    echo "PR: $pr_url" >&2
    return 1
  fi

  echo "Verified ${matched_shape}-merged branch: '$branch' diff matches merged PR #$pr_number from $merged_at."
  echo "PR: $pr_url"
  return 0
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

start_upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"

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
verified_squash_merge=false
if [[ "$start_branch" != "$default_branch" ]]; then
  if git show-ref --verify --quiet "refs/heads/$start_branch"; then
    if run git branch -d "$start_branch"; then
      deleted_branch=true
    elif [[ "$verify_squash_merge" == true ]] && verify_squash_merged_branch "$start_branch"; then
      verified_squash_merge=true
      echo "Safe deletion failed because Git ancestry does not include the branch, but merge diff verification passed."
      run git branch -D "$start_branch"
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

deleted_remote=false
if [[ "$delete_remote" == true && "$start_branch" != "$default_branch" ]]; then
  remote_branch="$start_branch"
  if [[ "$start_upstream" == origin/* ]]; then
    remote_branch="${start_upstream#origin/}"
  fi

  if git show-ref --verify --quiet "refs/remotes/origin/$remote_branch"; then
    if [[ "$deleted_branch" == true || "$force_delete_unmerged" == true || "$verified_squash_merge" == true ]]; then
      run git push origin --delete "$remote_branch"
      deleted_remote=true
    else
      echo "Remote branch was not deleted because local cleanup did not prove the branch safe to remove." >&2
    fi
  else
    echo "Remote branch was already absent: origin/$remote_branch"
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
  if [[ "$verified_squash_merge" == true ]]; then
    echo "Deletion used verified merge diff equality."
  fi
else
  echo "Old local branch was already absent: $start_branch"
fi
if [[ "$delete_remote" == true ]]; then
  if [[ "$deleted_remote" == true ]]; then
    echo "Deleted old remote branch: origin/$remote_branch"
  else
    echo "Old remote branch was not deleted."
  fi
fi
echo
git status --short --branch
