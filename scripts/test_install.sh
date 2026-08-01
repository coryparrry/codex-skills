#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALLER="$ROOT_DIR/scripts/install.sh"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

assert_installed() {
  local codex_home="$1"
  local installed_skills

  test -f "$codex_home/skills/git-clean-merged-branch/SKILL.md"
  test -f "$codex_home/skills/git-clean-merged-branch/agents/openai.yaml"
  test -f "$codex_home/skills/git-clean-merged-branch/scripts/clean_merged_branch.sh"
  test -f "$codex_home/skills/triage-review-comments/SKILL.md"
  test -f "$codex_home/skills/triage-review-comments/agents/openai.yaml"
  test -f "$codex_home/skills/triage-review-comments/references/CLASSIFICATION.md"
  test -f "$codex_home/skills/triage-review-comments/references/EVALUATION.md"
  test -f "$codex_home/skills/triage-review-comments/references/EXAMPLE.md"
  test -f "$codex_home/skills/triage-review-comments/references/INTEGRATION.md"

  installed_skills="$(find "$codex_home/skills" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)"
  test "$installed_skills" = "$(printf '%s\n' git-clean-merged-branch triage-review-comments)"
}

LOCAL_HOME="$TMP_DIR/codex-local"
CODEX_HOME="$LOCAL_HOME" bash "$INSTALLER" >/dev/null
assert_installed "$LOCAL_HOME"

CURL_STYLE_LOG="$TMP_DIR/curl-style.log"
if CODEX_HOME="$TMP_DIR/codex-curl" bash -c "$(cat "$INSTALLER")" >"$CURL_STYLE_LOG" 2>&1; then
  echo "curl-style root installer unexpectedly succeeded" >&2
  exit 1
fi
grep -q "trusted local checkout" "$CURL_STYLE_LOG"
grep -q -- "--global --agent codex" "$CURL_STYLE_LOG"
test ! -e "$TMP_DIR/codex-curl/skills"

PRESERVE_HOME="$TMP_DIR/codex-preserve"
CODEX_HOME="$PRESERVE_HOME" bash "$INSTALLER" >/dev/null
assert_installed "$PRESERVE_HOME"
before_cleanup_checksum="$(shasum "$PRESERVE_HOME/skills/git-clean-merged-branch/SKILL.md")"
before_triage_checksum="$(shasum "$PRESERVE_HOME/skills/triage-review-comments/SKILL.md")"
if CODEX_HOME="$PRESERVE_HOME" bash -c "$(cat "$INSTALLER")" >/dev/null 2>&1; then
  echo "curl-style root installer unexpectedly replaced existing install" >&2
  exit 1
fi
after_cleanup_checksum="$(shasum "$PRESERVE_HOME/skills/git-clean-merged-branch/SKILL.md")"
after_triage_checksum="$(shasum "$PRESERVE_HOME/skills/triage-review-comments/SKILL.md")"
test "$before_cleanup_checksum" = "$after_cleanup_checksum"
test "$before_triage_checksum" = "$after_triage_checksum"
assert_installed "$PRESERVE_HOME"

echo "Install tests passed"
