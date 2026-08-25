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

  test -f "$codex_home/skills/appstore-readiness-audit/SKILL.md"
  test -f "$codex_home/skills/appstore-readiness-audit/agents/openai.yaml"
  test -f "$codex_home/skills/appstore-readiness-audit/references/apple-sources.md"
  test -f "$codex_home/skills/appstore-readiness-audit/references/audit-catalog.md"
  test -f "$codex_home/skills/appstore-readiness-audit/references/report-format.md"
  test -f "$codex_home/skills/appstore-readiness-audit/scripts/check_review_notes.py"
  test -f "$codex_home/skills/appstore-readiness-audit/tests/test_check_review_notes.py"
  test -f "$codex_home/skills/deep-code-review/SKILL.md"
  test -f "$codex_home/skills/deep-code-review/agents/openai.yaml"
  test -f "$codex_home/skills/deep-code-review/references/evidence-and-validation.md"
  test -f "$codex_home/skills/deep-code-review/references/impact-and-negative-space.md"
  test -f "$codex_home/skills/deep-code-review/references/report-format.md"
  test -f "$codex_home/skills/deep-code-review/references/risk-lanes.md"
  test -f "$codex_home/skills/deep-code-review/references/whole-repository-audit.md"
  test -f "$codex_home/skills/git-clean-merged-branch/SKILL.md"
  test -f "$codex_home/skills/git-clean-merged-branch/agents/openai.yaml"
  test -f "$codex_home/skills/git-clean-merged-branch/scripts/clean_merged_branch.sh"
  test -f "$codex_home/skills/codex-routing/SKILL.md"
  test -f "$codex_home/skills/codex-routing/agents/openai.yaml"
  test -f "$codex_home/skills/triage-review-comments/SKILL.md"
  test -f "$codex_home/skills/triage-review-comments/agents/openai.yaml"
  test -f "$codex_home/skills/triage-review-comments/references/CLASSIFICATION.md"
  test -f "$codex_home/skills/triage-review-comments/references/EVALUATION.md"
  test -f "$codex_home/skills/triage-review-comments/references/EXAMPLE.md"
  test -f "$codex_home/skills/triage-review-comments/references/INTEGRATION.md"
  test -f "$codex_home/skills/continue-deep-research/SKILL.md"
  test -f "$codex_home/skills/continue-deep-research/agents/openai.yaml"
  test -f "$codex_home/skills/continue-deep-research/references/research-delta.md"
  test -f "$codex_home/skills/continue-deep-research/references/source-routing.md"
  test -f "$codex_home/skills/research-repo-technology/SKILL.md"
  test -f "$codex_home/skills/research-repo-technology/agents/openai.yaml"
  test -f "$codex_home/skills/research-repo-technology/references/report-contract.md"
  test -f "$codex_home/skills/research-repo-technology/references/research-lanes.md"
  test -f "$codex_home/skills/swift-code-review/SKILL.md"
  test -f "$codex_home/skills/swift-code-review/agents/openai.yaml"
  test -f "$codex_home/skills/swift-code-review/references/concurrency-and-lifetime.md"
  test -f "$codex_home/skills/swift-code-review/references/data-api-and-platform-boundaries.md"
  test -f "$codex_home/skills/swift-code-review/references/evidence-and-ai.md"
  test -f "$codex_home/skills/swift-code-review/references/swiftui-and-appkit.md"

  installed_skills="$(find "$codex_home/skills" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)"
  test "$installed_skills" = "$(printf '%s\n' appstore-readiness-audit codex-routing continue-deep-research deep-code-review git-clean-merged-branch research-repo-technology swift-code-review triage-review-comments)"
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
before_appstore_audit_checksum="$(shasum "$PRESERVE_HOME/skills/appstore-readiness-audit/SKILL.md")"
before_deep_review_checksum="$(shasum "$PRESERVE_HOME/skills/deep-code-review/SKILL.md")"
before_codex_routing_checksum="$(shasum "$PRESERVE_HOME/skills/codex-routing/SKILL.md")"
before_triage_checksum="$(shasum "$PRESERVE_HOME/skills/triage-review-comments/SKILL.md")"
before_continue_research_checksum="$(shasum "$PRESERVE_HOME/skills/continue-deep-research/SKILL.md")"
before_repo_research_checksum="$(shasum "$PRESERVE_HOME/skills/research-repo-technology/SKILL.md")"
before_swift_review_checksum="$(shasum "$PRESERVE_HOME/skills/swift-code-review/SKILL.md")"
if CODEX_HOME="$PRESERVE_HOME" bash -c "$(cat "$INSTALLER")" >/dev/null 2>&1; then
  echo "curl-style root installer unexpectedly replaced existing install" >&2
  exit 1
fi
after_cleanup_checksum="$(shasum "$PRESERVE_HOME/skills/git-clean-merged-branch/SKILL.md")"
after_appstore_audit_checksum="$(shasum "$PRESERVE_HOME/skills/appstore-readiness-audit/SKILL.md")"
after_deep_review_checksum="$(shasum "$PRESERVE_HOME/skills/deep-code-review/SKILL.md")"
after_codex_routing_checksum="$(shasum "$PRESERVE_HOME/skills/codex-routing/SKILL.md")"
after_triage_checksum="$(shasum "$PRESERVE_HOME/skills/triage-review-comments/SKILL.md")"
after_continue_research_checksum="$(shasum "$PRESERVE_HOME/skills/continue-deep-research/SKILL.md")"
after_repo_research_checksum="$(shasum "$PRESERVE_HOME/skills/research-repo-technology/SKILL.md")"
after_swift_review_checksum="$(shasum "$PRESERVE_HOME/skills/swift-code-review/SKILL.md")"
test "$before_cleanup_checksum" = "$after_cleanup_checksum"
test "$before_appstore_audit_checksum" = "$after_appstore_audit_checksum"
test "$before_deep_review_checksum" = "$after_deep_review_checksum"
test "$before_codex_routing_checksum" = "$after_codex_routing_checksum"
test "$before_triage_checksum" = "$after_triage_checksum"
test "$before_continue_research_checksum" = "$after_continue_research_checksum"
test "$before_repo_research_checksum" = "$after_repo_research_checksum"
test "$before_swift_review_checksum" = "$after_swift_review_checksum"
assert_installed "$PRESERVE_HOME"

echo "Install tests passed"
