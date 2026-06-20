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

  test -f "$codex_home/skills/codex-adversarial-gate/SKILL.md"
  test -f "$codex_home/agents/plan-adversarial-reviewer.toml"
  test -f "$codex_home/agents/task-completion-adversarial-reviewer.toml"
  test -f "$codex_home/agents/task-completion-review-critic.toml"
}

make_fixture_repo() {
  local fixture="$1"

  mkdir -p "$fixture"
  cp -R "$ROOT_DIR"/. "$fixture"/
  rm -rf "$fixture/.git" "$fixture/docs/solutions"
  git -C "$fixture" init -q
  git -C "$fixture" add .
  git -C "$fixture" \
    -c user.name="install test" \
    -c user.email="install-test@example.com" \
    commit -q -m "fixture"
}

LOCAL_HOME="$TMP_DIR/codex-local"
CODEX_HOME="$LOCAL_HOME" bash "$INSTALLER" >/dev/null
assert_installed "$LOCAL_HOME"
CODEX_HOME="$LOCAL_HOME" bash "$LOCAL_HOME/skills/codex-adversarial-gate/scripts/install.sh" >/dev/null
assert_installed "$LOCAL_HOME"

FIXTURE_REPO="$TMP_DIR/fixture-repo"
make_fixture_repo "$FIXTURE_REPO"

REMOTE_HOME="$TMP_DIR/codex-remote"
REPO_URL="file://$FIXTURE_REPO" CODEX_HOME="$REMOTE_HOME" bash -c "$(cat "$INSTALLER")" >/dev/null
assert_installed "$REMOTE_HOME"

FAKE_SOURCE="$TMP_DIR/fake-source"
mkdir -p "$FAKE_SOURCE/scripts" "$FAKE_SOURCE/agents"
printf 'fake skill\n' > "$FAKE_SOURCE/SKILL.md"
printf 'fake\n' > "$FAKE_SOURCE/agents/plan-adversarial-reviewer.toml"
printf 'fake\n' > "$FAKE_SOURCE/agents/task-completion-adversarial-reviewer.toml"
printf 'fake\n' > "$FAKE_SOURCE/agents/task-completion-review-critic.toml"
(
  cd "$FAKE_SOURCE/scripts"
  REPO_URL="file://$FIXTURE_REPO" CODEX_HOME="$TMP_DIR/codex-curl" bash -c "$(cat "$INSTALLER")" >/dev/null
)
assert_installed "$TMP_DIR/codex-curl"
if grep -q "fake skill" "$TMP_DIR/codex-curl/skills/codex-adversarial-gate/SKILL.md"; then
  echo "curl-style install used caller-local source" >&2
  exit 1
fi

PRESERVE_HOME="$TMP_DIR/codex-preserve"
REPO_URL="file://$FIXTURE_REPO" CODEX_HOME="$PRESERVE_HOME" bash -c "$(cat "$INSTALLER")" >/dev/null
assert_installed "$PRESERVE_HOME"
before_checksum="$(shasum "$PRESERVE_HOME/skills/codex-adversarial-gate/SKILL.md")"
if REPO_URL="file://$TMP_DIR/missing-repo" CODEX_HOME="$PRESERVE_HOME" bash -c "$(cat "$INSTALLER")" >/dev/null 2>&1; then
  echo "missing remote unexpectedly installed" >&2
  exit 1
fi
after_checksum="$(shasum "$PRESERVE_HOME/skills/codex-adversarial-gate/SKILL.md")"
test "$before_checksum" = "$after_checksum"
assert_installed "$PRESERVE_HOME"

echo "Install tests passed"
