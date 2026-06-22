#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="codex-adversarial-gate"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

SKILLS_DIR="$CODEX_HOME/skills"
AGENTS_DIR="$CODEX_HOME/agents"
SKILL_DIR="$SKILLS_DIR/$SKILL_NAME"

SOURCE_DIR=""
STAGING_DIR=""
BACKUP_DIR=""

cleanup() {
  if [ -n "$STAGING_DIR" ] && [ -d "$STAGING_DIR" ]; then
    rm -rf "$STAGING_DIR"
  fi
  if [ -n "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR" ]; then
    rm -rf "$BACKUP_DIR"
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
  cat >&2 <<EOF
This installer must be run from a trusted local skill directory.

Install the skill first:
  npx skills add coryparrry/codex-skills --global --agent codex --skill $SKILL_NAME

Then run:
  bash "\${CODEX_HOME:-\$HOME/.codex}/skills/$SKILL_NAME/scripts/install.sh"
EOF
  exit 1
fi

mkdir -p "$SKILLS_DIR" "$AGENTS_DIR"

if [ ! -d "$SKILL_DIR" ] || [ "$SOURCE_DIR" != "$(cd "$SKILL_DIR" 2>/dev/null && pwd)" ]; then
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
