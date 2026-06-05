#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${CODEX_BUDGET_ROUTER_AGENT_SOURCE:-$ROOT/agents}"
DEST_DIR="${CODEX_AGENT_HOME:-$HOME/.codex/agents}"
STAMP="$(date +%Y%m%d%H%M%S)"
installed=0
skipped=0

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Missing agent profile directory: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"

for profile in "$SOURCE_DIR"/*.toml; do
  [[ -e "$profile" ]] || continue
  name="$(basename "$profile")"
  dest="$DEST_DIR/$name"
  if [[ -e "$dest" ]]; then
    if cmp -s "$profile" "$dest"; then
      echo "Already installed: $name"
      skipped=$((skipped + 1))
      continue
    fi
    echo "Exists with local changes, leaving unchanged: $name"
    echo "  To replace it, move or delete $dest and rerun this script."
    skipped=$((skipped + 1))
    continue
  fi
  cp "$profile" "$dest"
  echo "Installed: $name"
  installed=$((installed + 1))
done

if [[ "$installed" -eq 0 ]]; then
  echo "No missing codex-budget-router agent profiles were installed."
else
  echo "Installed $installed codex-budget-router agent profile(s) to $DEST_DIR"
  echo "Restart Codex to pick up new agent profiles."
fi

if [[ "$skipped" -gt 0 ]]; then
  echo "Skipped $skipped existing profile(s)."
fi
