#!/usr/bin/env bash
set -euo pipefail

ADVERSARIAL_GATE="codex-adversarial-gate"
PACKAGE_INSTALLER="skills/$ADVERSARIAL_GATE/scripts/install.sh"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILLS_DIR="$CODEX_HOME/skills"

TEMP_DIRS=()

cleanup() {
  local dir
  for dir in "${TEMP_DIRS[@]}"; do
    if [ -n "$dir" ] && [ -d "$dir" ]; then
      rm -rf "$dir"
    fi
  done
}

validate_skill_dir() {
  local source_dir="$1"

  test -f "$source_dir/SKILL.md"
  test -f "$source_dir/agents/openai.yaml"
}

replace_skill_dir() {
  local skill_name="$1"
  local replacement_dir="$2"
  local skill_dir="$SKILLS_DIR/$skill_name"
  local backup_dir=""

  if [ -e "$skill_dir" ]; then
    backup_dir="$(mktemp -d "$SKILLS_DIR/.${skill_name}.backup.XXXXXX")"
    TEMP_DIRS+=("$backup_dir")
    rmdir "$backup_dir"
    mv "$skill_dir" "$backup_dir"
  fi

  if mv "$replacement_dir" "$skill_dir"; then
    if [ -n "$backup_dir" ]; then
      rm -rf "$backup_dir"
    fi
    return
  fi

  if [ -n "$backup_dir" ] && [ -d "$backup_dir" ]; then
    local restore_dir="$backup_dir"
    if ! mv "$restore_dir" "$skill_dir"; then
      echo "failed to restore existing install from $restore_dir" >&2
      exit 1
    fi
  fi

  echo "failed to install $skill_name" >&2
  exit 1
}

install_skill_dir() {
  local source_dir="$1"
  local skill_name
  local staging_dir

  skill_name="$(basename "$source_dir")"
  staging_dir="$(mktemp -d "$SKILLS_DIR/.${skill_name}.tmp.XXXXXX")"
  TEMP_DIRS+=("$staging_dir")

  cp -R "$source_dir"/. "$staging_dir"/
  rm -rf "$staging_dir/.git" "$staging_dir/docs/solutions"
  validate_skill_dir "$staging_dir"
  replace_skill_dir "$skill_name" "$staging_dir"
}

trap cleanup EXIT

SCRIPT_PATH="${BASH_SOURCE[0]:-}"
if [ -n "$SCRIPT_PATH" ] && [ -f "$SCRIPT_PATH" ]; then
  ROOT_DIR="$(cd "$(dirname "$SCRIPT_PATH")/.." && pwd)"
fi

if [ -z "${ROOT_DIR:-}" ] || [ ! -d "$ROOT_DIR/skills" ] || [ ! -f "$ROOT_DIR/$PACKAGE_INSTALLER" ]; then
  cat >&2 <<EOF
This installer must be run from a trusted local checkout.

Install the repo skills first:
  npx skills add coryparrry/codex-skills --global --agent codex --skill '*'

Then run the installed adversarial gate agent installer when needed:
  bash "\${CODEX_HOME:-\$HOME/.codex}/skills/$ADVERSARIAL_GATE/scripts/install.sh"
EOF
  exit 1
fi

mkdir -p "$SKILLS_DIR"

for source_dir in "$ROOT_DIR"/skills/*; do
  if [ ! -f "$source_dir/SKILL.md" ]; then
    continue
  fi
  if [ "$(basename "$source_dir")" = "$ADVERSARIAL_GATE" ]; then
    continue
  fi
  install_skill_dir "$source_dir"
done

bash "$ROOT_DIR/$PACKAGE_INSTALLER" >/dev/null

cat <<EOF
Installed codex-skills bundle

Skills:
EOF
for source_dir in "$ROOT_DIR"/skills/*; do
  if [ -f "$source_dir/SKILL.md" ]; then
    printf '  %s\n' "$SKILLS_DIR/$(basename "$source_dir")"
  fi
done

cat <<EOF

Adversarial gate agents:
  $CODEX_HOME/agents/plan-adversarial-reviewer.toml
  $CODEX_HOME/agents/task-completion-adversarial-reviewer.toml
  $CODEX_HOME/agents/task-completion-review-critic.toml
EOF
