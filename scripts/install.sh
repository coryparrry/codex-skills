#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="codex-adversarial-gate"
PACKAGE_INSTALLER="skills/$SKILL_NAME/scripts/install.sh"

SCRIPT_PATH="${BASH_SOURCE[0]:-}"
if [ -n "$SCRIPT_PATH" ] && [ -f "$SCRIPT_PATH" ]; then
  ROOT_DIR="$(cd "$(dirname "$SCRIPT_PATH")/.." && pwd)"
  if [ -f "$ROOT_DIR/$PACKAGE_INSTALLER" ]; then
    bash "$ROOT_DIR/$PACKAGE_INSTALLER"
    exit $?
  fi
fi

cat >&2 <<EOF
This installer must be run from a trusted local checkout.

Install the skill first:
  npx skills add coryparrry/codex-skills --global --agent codex --skill $SKILL_NAME

Then run the installed skill's agent installer:
  bash ~/.agents/skills/$SKILL_NAME/scripts/install.sh
EOF
exit 1
