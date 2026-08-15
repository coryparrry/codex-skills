#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALLER="$ROOT_DIR/scripts/install.sh"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

assert_agent_route() {
  local profile="$1"
  local model="$2"
  local effort="$3"

  grep -Fxq "model = \"$model\"" "$profile"
  grep -Fxq "model_reasoning_effort = \"$effort\"" "$profile"
}

assert_installed() {
  local codex_home="$1"
  local installed_agents
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
  test -f "$codex_home/agents/codex-skills/acceptance-contract-reviewer.toml"
  test -f "$codex_home/agents/codex-skills/artifact-provenance-verifier.toml"
  test -f "$codex_home/agents/codex-skills/delivery-state-reconciler.toml"
  test -f "$codex_home/agents/codex-skills/evidence-ledger-lane-reviewer.toml"
  test ! -e "$codex_home/skills/engineering-advisor"

  installed_skills="$(find "$codex_home/skills" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)"
  test "$installed_skills" = "$(printf '%s\n' appstore-readiness-audit continue-deep-research deep-code-review git-clean-merged-branch research-repo-technology swift-code-review triage-review-comments)"
  installed_agents="$(find "$codex_home/agents/codex-skills" -mindepth 1 -maxdepth 1 -type f -name '*.toml' -exec basename {} \; | sort)"
  test "$installed_agents" = "$(printf '%s\n' acceptance-contract-reviewer.toml artifact-provenance-verifier.toml delivery-state-reconciler.toml evidence-ledger-lane-reviewer.toml)"
  assert_agent_route "$codex_home/agents/codex-skills/acceptance-contract-reviewer.toml" "gpt-5.6-sol" "high"
  assert_agent_route "$codex_home/agents/codex-skills/artifact-provenance-verifier.toml" "gpt-5.6-terra" "high"
  assert_agent_route "$codex_home/agents/codex-skills/delivery-state-reconciler.toml" "gpt-5.6-luna" "max"
  assert_agent_route "$codex_home/agents/codex-skills/evidence-ledger-lane-reviewer.toml" "gpt-5.6-luna" "max"
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
test ! -e "$TMP_DIR/codex-curl/agents"

PRESERVE_HOME="$TMP_DIR/codex-preserve"
CODEX_HOME="$PRESERVE_HOME" bash "$INSTALLER" >/dev/null
assert_installed "$PRESERVE_HOME"
before_cleanup_checksum="$(shasum "$PRESERVE_HOME/skills/git-clean-merged-branch/SKILL.md")"
before_appstore_audit_checksum="$(shasum "$PRESERVE_HOME/skills/appstore-readiness-audit/SKILL.md")"
before_deep_review_checksum="$(shasum "$PRESERVE_HOME/skills/deep-code-review/SKILL.md")"
before_acceptance_agent_checksum="$(shasum "$PRESERVE_HOME/agents/codex-skills/acceptance-contract-reviewer.toml")"
before_provenance_agent_checksum="$(shasum "$PRESERVE_HOME/agents/codex-skills/artifact-provenance-verifier.toml")"
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
after_acceptance_agent_checksum="$(shasum "$PRESERVE_HOME/agents/codex-skills/acceptance-contract-reviewer.toml")"
after_provenance_agent_checksum="$(shasum "$PRESERVE_HOME/agents/codex-skills/artifact-provenance-verifier.toml")"
after_triage_checksum="$(shasum "$PRESERVE_HOME/skills/triage-review-comments/SKILL.md")"
after_continue_research_checksum="$(shasum "$PRESERVE_HOME/skills/continue-deep-research/SKILL.md")"
after_repo_research_checksum="$(shasum "$PRESERVE_HOME/skills/research-repo-technology/SKILL.md")"
after_swift_review_checksum="$(shasum "$PRESERVE_HOME/skills/swift-code-review/SKILL.md")"
test "$before_cleanup_checksum" = "$after_cleanup_checksum"
test "$before_appstore_audit_checksum" = "$after_appstore_audit_checksum"
test "$before_deep_review_checksum" = "$after_deep_review_checksum"
test "$before_acceptance_agent_checksum" = "$after_acceptance_agent_checksum"
test "$before_provenance_agent_checksum" = "$after_provenance_agent_checksum"
test "$before_triage_checksum" = "$after_triage_checksum"
test "$before_continue_research_checksum" = "$after_continue_research_checksum"
test "$before_repo_research_checksum" = "$after_repo_research_checksum"
test "$before_swift_review_checksum" = "$after_swift_review_checksum"
assert_installed "$PRESERVE_HOME"

LEGACY_HOME="$TMP_DIR/codex-legacy"
mkdir -p "$LEGACY_HOME/skills/engineering-advisor"
printf 'legacy\n' >"$LEGACY_HOME/skills/engineering-advisor/SKILL.md"
CODEX_HOME="$LEGACY_HOME" bash "$INSTALLER" >/dev/null
assert_installed "$LEGACY_HOME"

echo "Install tests passed"
