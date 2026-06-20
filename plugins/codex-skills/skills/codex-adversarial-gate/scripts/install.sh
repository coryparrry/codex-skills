#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="codex-adversarial-gate"
REPO_URL="${REPO_URL:-https://github.com/coryparrry/codex-skills.git}"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILL_SOURCE_SUBDIR="skills/$SKILL_NAME"

SKILLS_DIR="$CODEX_HOME/skills"
AGENTS_DIR="$CODEX_HOME/agents"
SKILL_DIR="$SKILLS_DIR/$SKILL_NAME"

SOURCE_DIR=""
REMOTE_INSTALL=0
STAGING_DIR=""
BACKUP_DIR=""
CHECKOUT_DIR=""

cleanup() {
  if [ -n "$STAGING_DIR" ] && [ -d "$STAGING_DIR" ]; then
    rm -rf "$STAGING_DIR"
  fi
  if [ -n "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR" ]; then
    rm -rf "$BACKUP_DIR"
  fi
  if [ -n "$CHECKOUT_DIR" ] && [ -d "$CHECKOUT_DIR" ]; then
    rm -rf "$CHECKOUT_DIR"
  fi
}

validate_skill_dir() {
  local source_dir="$1"

  test -f "$source_dir/SKILL.md"
  test -f "$source_dir/agents/plan-adversarial-reviewer.toml"
  test -f "$source_dir/agents/task-completion-adversarial-reviewer.toml"
  test -f "$source_dir/agents/task-completion-review-critic.toml"
}

replace_skill_dir() {
  local replacement_dir="$1"

  if [ -e "$SKILL_DIR" ]; then
    BACKUP_DIR="$(mktemp -d "$SKILLS_DIR/.${SKILL_NAME}.backup.XXXXXX")"
    rmdir "$BACKUP_DIR"
    mv "$SKILL_DIR" "$BACKUP_DIR"
  fi

  if mv "$replacement_dir" "$SKILL_DIR"; then
    STAGING_DIR=""
    if [ -n "$BACKUP_DIR" ]; then
      rm -rf "$BACKUP_DIR"
      BACKUP_DIR=""
    fi
    return
  fi

  if [ -n "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR" ]; then
    local restore_dir="$BACKUP_DIR"
    BACKUP_DIR=""
    if ! mv "$restore_dir" "$SKILL_DIR"; then
      echo "failed to restore existing install from $restore_dir" >&2
      exit 1
    fi
  fi
  echo "failed to install $SKILL_NAME" >&2
  exit 1
}

trap cleanup EXIT

SCRIPT_PATH="${BASH_SOURCE[0]:-}"
if [ -n "$SCRIPT_PATH" ] && [ -f "$SCRIPT_PATH" ]; then
  SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
  CANDIDATE_SOURCE="$(cd "$SCRIPT_DIR/.." && pwd)"
  if [ -f "$CANDIDATE_SOURCE/SKILL.md" ] && [ -d "$CANDIDATE_SOURCE/agents" ]; then
    SOURCE_DIR="$CANDIDATE_SOURCE"
  fi
fi

if [ -z "$SOURCE_DIR" ]; then
  if ! command -v git >/dev/null 2>&1; then
    echo "git is required to install from $REPO_URL" >&2
    exit 1
  fi

  REMOTE_INSTALL=1
fi

mkdir -p "$SKILLS_DIR" "$AGENTS_DIR"

if [ "$REMOTE_INSTALL" -eq 1 ]; then
  CHECKOUT_DIR="$(mktemp -d "$SKILLS_DIR/.${SKILL_NAME}.repo.XXXXXX")"
  git clone --depth 1 "$REPO_URL" "$CHECKOUT_DIR"
  if [ -d "$CHECKOUT_DIR/$SKILL_SOURCE_SUBDIR" ]; then
    SOURCE_DIR="$CHECKOUT_DIR/$SKILL_SOURCE_SUBDIR"
  else
    SOURCE_DIR="$CHECKOUT_DIR"
  fi

  STAGING_DIR="$(mktemp -d "$SKILLS_DIR/.${SKILL_NAME}.tmp.XXXXXX")"
  rmdir "$STAGING_DIR"
  cp -R "$SOURCE_DIR"/. "$STAGING_DIR"/
  rm -rf "$STAGING_DIR/.git" "$STAGING_DIR/docs/solutions"
  validate_skill_dir "$STAGING_DIR"
  replace_skill_dir "$STAGING_DIR"
  SOURCE_DIR="$SKILL_DIR"
elif [ ! -d "$SKILL_DIR" ] || [ "$SOURCE_DIR" != "$(cd "$SKILL_DIR" 2>/dev/null && pwd)" ]; then
  STAGING_DIR="$(mktemp -d "$SKILLS_DIR/.${SKILL_NAME}.tmp.XXXXXX")"
  cp -R "$SOURCE_DIR"/. "$STAGING_DIR"/
  rm -rf "$STAGING_DIR/.git" "$STAGING_DIR/docs/solutions"
  validate_skill_dir "$STAGING_DIR"
  replace_skill_dir "$STAGING_DIR"
  SOURCE_DIR="$SKILL_DIR"
fi

validate_skill_dir "$SKILL_DIR"
cp "$SKILL_DIR"/agents/*.toml "$AGENTS_DIR"/

test -f "$SKILL_DIR/SKILL.md"
test -f "$AGENTS_DIR/plan-adversarial-reviewer.toml"
test -f "$AGENTS_DIR/task-completion-adversarial-reviewer.toml"
test -f "$AGENTS_DIR/task-completion-review-critic.toml"

cat <<EOF
Installed $SKILL_NAME

Skill:
  $SKILL_DIR

Agents:
  $AGENTS_DIR/plan-adversarial-reviewer.toml
  $AGENTS_DIR/task-completion-adversarial-reviewer.toml
  $AGENTS_DIR/task-completion-review-critic.toml
EOF
