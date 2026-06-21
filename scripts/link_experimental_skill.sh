#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
raw_source_dir="${repo_root}/experimental/multi-phase-orchestrator"
replace_existing=0

if [[ "${1:-}" == "--replace-existing" ]]; then
  replace_existing=1
  shift
fi

raw_target="${1:-${CODEX_HOME:-$HOME/.codex}/skills/multi-phase-orchestrator}"

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

target_parent="$(dirname "${raw_target}")"
target_name="$(basename "${raw_target}")"
mkdir -p "${target_parent}"
target_parent="$(cd "${target_parent}" && pwd -P)"
target="${target_parent}/${target_name}"

if [[ -z "${target_name}" || "${target_name}" == "." || "${target}" == "/" ]]; then
  printf 'Refusing unsafe target path: %s\n' "${raw_target}" >&2
  exit 1
fi

if [[ "${target}" == "${source_dir}" ]]; then
  printf 'Refusing to replace or link the source skill directory: %s\n' "${target}" >&2
  exit 1
fi

if [[ -L "${target}" ]]; then
  current_target="$(readlink "${target}")"
  if [[ "${current_target}" == "${source_dir}" ]]; then
    printf '%s already links to %s\n' "${target}" "${source_dir}"
    exit 0
  fi

  rm "${target}"
elif [[ -e "${target}" ]]; then
  if [[ "${replace_existing}" -ne 1 ]]; then
    printf 'Refusing to replace non-symlink path: %s\n' "${target}" >&2
    printf 'Re-run with --replace-existing after confirming the repo copy is the source of truth.\n' >&2
    exit 1
  fi

  if [[ ! -d "${target}" || ! -f "${target}/SKILL.md" ]]; then
    printf 'Refusing to replace path that does not look like a skill directory: %s\n' "${target}" >&2
    exit 1
  fi

  rm -rf "${target}"
fi

ln -s "${source_dir}" "${target}"
printf 'Linked %s -> %s\n' "${target}" "${source_dir}"
