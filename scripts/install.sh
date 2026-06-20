#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="codex-adversarial-gate"
REPO_URL="${REPO_URL:-https://github.com/coryparrry/codex-skills.git}"
PACKAGE_INSTALLER="skills/$SKILL_NAME/scripts/install.sh"
TEMP_REPO=""

cleanup() {
  if [ -n "$TEMP_REPO" ] && [ -d "$TEMP_REPO" ]; then
    rm -rf "$TEMP_REPO"
  fi
}
trap cleanup EXIT

SCRIPT_PATH="${BASH_SOURCE[0]:-}"
if [ -n "$SCRIPT_PATH" ] && [ -f "$SCRIPT_PATH" ]; then
  ROOT_DIR="$(cd "$(dirname "$SCRIPT_PATH")/.." && pwd)"
  if [ -f "$ROOT_DIR/$PACKAGE_INSTALLER" ]; then
    bash "$ROOT_DIR/$PACKAGE_INSTALLER"
    exit $?
  fi
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is required to install from $REPO_URL" >&2
  exit 1
fi

TEMP_REPO="$(mktemp -d)"
git clone --depth 1 "$REPO_URL" "$TEMP_REPO"

if [ ! -f "$TEMP_REPO/$PACKAGE_INSTALLER" ]; then
  echo "missing package installer: $PACKAGE_INSTALLER" >&2
  exit 1
fi

bash "$TEMP_REPO/$PACKAGE_INSTALLER"
