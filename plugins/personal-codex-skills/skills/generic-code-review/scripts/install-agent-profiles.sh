#!/usr/bin/env bash
set -euo pipefail

skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
agent_src="$skill_dir/agents"
agent_dst="${CODEX_HOME:-$HOME/.codex}/agents"

mkdir -p "$agent_dst"

for src in "$agent_src"/*.toml; do
  name="$(basename "$src")"
  dst="$agent_dst/$name"
  if [[ -e "$dst" ]] && ! cmp -s "$src" "$dst"; then
    echo "skip modified existing profile: $dst" >&2
    continue
  fi
  cp "$src" "$dst"
  echo "installed $dst"
done
