# Codex Skill and Plugin

## Detection Artifacts

- `SKILL.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`
- `tests/`
- plugin mirror paths under `plugins/codex-skills/skills/<skill>/`

## Common Repo Shapes

- source skill with a mirrored plugin copy
- skill bundle with references and validation tests
- repo-maintained helper script surface

## Required Lifecycle Gates

- setup/bootstrap: no external package setup unless the skill script explicitly needs it
- focused test: skill-specific validation command such as `quick_validate` or repo test command
- full validation/CI: source and mirror parity checks plus the repo's audit or install validation

## Native Commands

- `quick_validate`
- repo-specific test command for the skill
- parity or diff check between source and mirror

## CI Expectations

CI should validate source and mirror together, and it should run the skill's own tests from both copies when the repo ships them.

## Package Boundary Rules

Treat the source skill and plugin mirror as separate paths that must stay in lockstep. Keep relative paths correct in both trees.

## Common False Positives

- Do not report source-only reference paths as healthy if the mirror is missing them.
- Do not ignore mirror-only drift when a skill ships in two locations.

## Severity Guidance

Mirror drift is usually P2 because it breaks shipped behavior. Missing skill tests can rise to P1 when the skill is user-facing or installable.

## Good Finding Examples

- P2 scoped to `skills/auditing-repository-health`: a new reference file exists in the source tree but not in the plugin mirror.

## Bad Finding Examples

- P2 at root: repo lacks `npm test` even though the skill is validated by `python3 tests/test_audit_repository_health.py`.
