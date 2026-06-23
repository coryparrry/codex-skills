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

  test -f "$codex_home/skills/auditing-repository-health/SKILL.md"
  test -f "$codex_home/skills/auditing-repository-health/agents/openai.yaml"
  test -f "$codex_home/skills/auditing-repository-health/references/script-responsibilities.md"
  test -f "$codex_home/skills/auditing-repository-health/scripts/audit_repository_health.py"
  test -f "$codex_home/skills/codex-adversarial-gate/SKILL.md"
  test -f "$codex_home/skills/codex-adversarial-gate/agents/openai.yaml"
  test -f "$codex_home/skills/git-clean-merged-branch/SKILL.md"
  test -f "$codex_home/skills/git-clean-merged-branch/agents/openai.yaml"
  test -f "$codex_home/skills/multi-phase-orchestrator/SKILL.md"
  test -f "$codex_home/skills/multi-phase-orchestrator/agents/openai.yaml"
  test -f "$codex_home/skills/triage-review-comments/SKILL.md"
  test -f "$codex_home/skills/triage-review-comments/agents/openai.yaml"
  test -f "$codex_home/skills/triage-review-comments/references/CLASSIFICATION.md"
  test -f "$codex_home/skills/triage-review-comments/references/EVALUATION.md"
  test -f "$codex_home/skills/triage-review-comments/references/EXAMPLE.md"
  test -f "$codex_home/skills/triage-review-comments/references/INTEGRATION.md"
  test -f "$codex_home/skills/writing-codex-loops/SKILL.md"
  test -f "$codex_home/skills/writing-codex-loops/agents/openai.yaml"
  test -f "$codex_home/skills/writing-codex-loops/references/loop-principles.md"
  test -f "$codex_home/agents/plan-adversarial-reviewer.toml"
  test -f "$codex_home/agents/task-completion-adversarial-reviewer.toml"
  test -f "$codex_home/agents/task-completion-review-critic.toml"
}

LOCAL_HOME="$TMP_DIR/codex-local"
CODEX_HOME="$LOCAL_HOME" bash "$INSTALLER" >/dev/null
assert_installed "$LOCAL_HOME"
CODEX_HOME="$LOCAL_HOME" bash "$LOCAL_HOME/skills/codex-adversarial-gate/scripts/install.sh" >/dev/null
assert_installed "$LOCAL_HOME"

CURL_STYLE_LOG="$TMP_DIR/curl-style.log"
if CODEX_HOME="$TMP_DIR/codex-curl" bash -c "$(cat "$INSTALLER")" >"$CURL_STYLE_LOG" 2>&1; then
  echo "curl-style root installer unexpectedly succeeded" >&2
  exit 1
fi
grep -q "trusted local checkout" "$CURL_STYLE_LOG"
grep -q -- "--global --agent codex" "$CURL_STYLE_LOG"
grep -q '.codex}/skills/codex-adversarial-gate/scripts/install.sh' "$CURL_STYLE_LOG"
test ! -e "$TMP_DIR/codex-curl/skills/codex-adversarial-gate"
test ! -e "$TMP_DIR/codex-curl/skills/writing-codex-loops"

PACKAGE_INSTALLER="$ROOT_DIR/skills/codex-adversarial-gate/scripts/install.sh"
PACKAGE_CURL_STYLE_LOG="$TMP_DIR/package-curl-style.log"
if CODEX_HOME="$TMP_DIR/codex-package-curl" bash -c "$(cat "$PACKAGE_INSTALLER")" >"$PACKAGE_CURL_STYLE_LOG" 2>&1; then
  echo "curl-style package installer unexpectedly succeeded" >&2
  exit 1
fi
grep -q "trusted local skill directory" "$PACKAGE_CURL_STYLE_LOG"
grep -q -- "--global --agent codex" "$PACKAGE_CURL_STYLE_LOG"
grep -q '.codex}/skills/codex-adversarial-gate/scripts/install.sh' "$PACKAGE_CURL_STYLE_LOG"
test ! -e "$TMP_DIR/codex-package-curl/skills/codex-adversarial-gate"

PRESERVE_HOME="$TMP_DIR/codex-preserve"
CODEX_HOME="$PRESERVE_HOME" bash "$INSTALLER" >/dev/null
assert_installed "$PRESERVE_HOME"
before_checksum="$(shasum "$PRESERVE_HOME/skills/codex-adversarial-gate/SKILL.md")"
before_loop_checksum="$(shasum "$PRESERVE_HOME/skills/writing-codex-loops/SKILL.md")"
if CODEX_HOME="$PRESERVE_HOME" bash -c "$(cat "$INSTALLER")" >/dev/null 2>&1; then
  echo "curl-style root installer unexpectedly replaced existing install" >&2
  exit 1
fi
after_checksum="$(shasum "$PRESERVE_HOME/skills/codex-adversarial-gate/SKILL.md")"
after_loop_checksum="$(shasum "$PRESERVE_HOME/skills/writing-codex-loops/SKILL.md")"
test "$before_checksum" = "$after_checksum"
test "$before_loop_checksum" = "$after_loop_checksum"
assert_installed "$PRESERVE_HOME"

echo "Install tests passed"
