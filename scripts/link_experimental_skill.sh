#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
raw_source_dir="${1:-${CODEX_HOME:-$HOME/.codex}/skills/multi-phase-orchestrator}"
target="${repo_root}/experimental/multi-phase-orchestrator"

if [[ ! -d "${raw_source_dir}" ]]; then
  printf 'Missing source skill directory: %s\n' "${raw_source_dir}" >&2
  exit 1
fi

source_dir="$(cd "${raw_source_dir}" && pwd -P)"

if [[ ! -f "${source_dir}/SKILL.md" ]]; then
  printf 'Missing skill entrypoint: %s\n' "${source_dir}/SKILL.md" >&2
  exit 1
fi

if [[ ! -f "${source_dir}/agents/openai.yaml" ]]; then
  printf 'Missing skill metadata: %s\n' "${source_dir}/agents/openai.yaml" >&2
  exit 1
fi

mkdir -p "$(dirname "${target}")"

if [[ -L "${target}" ]]; then
  current_target="$(readlink "${target}")"
  if [[ "${current_target}" == "${source_dir}" ]]; then
    printf 'experimental/multi-phase-orchestrator already links to %s\n' "${source_dir}"
    exit 0
  fi

  rm "${target}"
elif [[ -e "${target}" ]]; then
  printf 'Refusing to replace non-symlink path: %s\n' "${target}" >&2
  exit 1
fi

ln -s "${source_dir}" "${target}"
printf 'Linked experimental/multi-phase-orchestrator -> %s\n' "${source_dir}"
