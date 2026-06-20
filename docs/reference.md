# Reference

This reference describes the moving parts in `codex-adversarial-gate`.

## Custom Agents

| Agent | Purpose | Output |
|---|---|---|
| `plan_adversarial_reviewer` | Reviews plans before finalization or updates | `PASS_100`, `FAIL_NEEDS_REVISION`, `BLOCKED_OWNER_DECISION` |
| `task_completion_adversarial_reviewer` | Reviews implementation phase/slice closeout | `PASS`, `FAIL_NEEDS_FIX`, `BLOCKED_INSUFFICIENT_EVIDENCE`, `BLOCKED_OWNER_DECISION` |
| `task_completion_review_critic` | Audits reviewer `PASS` verdicts | `AGREE_PASS`, `DISAGREE_EVIDENCE`, `DISAGREE_CONCERN` |

All three agents are read-only.

## Install Paths

Default Codex install paths:

| Component | Destination |
|---|---|
| Skill | `${CODEX_HOME:-$HOME/.codex}/skills/codex-adversarial-gate/` |
| Plan reviewer | `${CODEX_HOME:-$HOME/.codex}/agents/plan-adversarial-reviewer.toml` |
| Completion reviewer | `${CODEX_HOME:-$HOME/.codex}/agents/task-completion-adversarial-reviewer.toml` |
| Completion critic | `${CODEX_HOME:-$HOME/.codex}/agents/task-completion-review-critic.toml` |

The installer copies the skill and agent TOMLs separately because Codex may not install custom agents when installing a skill folder.

## Verdicts

### Plan Review

| Verdict | Meaning |
|---|---|
| `PASS_100` | The plan has no actionable objection under the rubric |
| `FAIL_NEEDS_REVISION` | The plan needs concrete changes |
| `BLOCKED_OWNER_DECISION` | The plan depends on a decision the implementer cannot make |

### Completion Review

| Verdict | Meaning |
|---|---|
| `PASS` | Preliminary pass; critic review is still required |
| `FAIL_NEEDS_FIX` | Concrete defect or unmet requirement |
| `BLOCKED_INSUFFICIENT_EVIDENCE` | Evidence is too weak or unavailable |
| `BLOCKED_OWNER_DECISION` | Completion depends on an owner decision |

### Completion Critic

| Verdict | Meaning |
|---|---|
| `AGREE_PASS` | Reviewer `PASS` is evidence-backed and safe to accept |
| `DISAGREE_EVIDENCE` | Evidence contradicts the reviewer |
| `DISAGREE_CONCERN` | Missing evidence or unresolved uncertainty remains |

## Archive Helper

Script:

```text
scripts/archive_adversarial_review.py
```

Arguments:

| Argument | Required | Description |
|---|---:|---|
| `--repo` | yes | Target repository root |
| `--kind` | yes | `plan`, `completion`, or `critic` |
| `--phase` | yes | Plan, phase, or slice name |
| `--reviewer` | yes | Reviewer role or custom agent name |
| `--verdict` | yes | Review disposition |
| `--resolution` | no | Implementer resolution when known |
| `--review-file` | one source required | File containing exact review output |
| `--stdin` | one source required | Read exact review output from standard input |

`--agent` is accepted as a hidden compatibility alias for `--reviewer`.

## Archive Location

Review outputs are saved under:

```text
<repo>/docs/Adversarial Reviews/
```

Each archive contains:

- review kind;
- phase or slice;
- reviewer label;
- verdict;
- timestamp;
- repo-relative archive path;
- exact review body.

## Fallback Prompt Reference

`references/reviewer-prompts.md` contains fallback prompts for environments without custom-agent support.

Fallback prompts still require an independent reviewer context. Same-thread self-review is blocked.

## Templates

| Template | Purpose |
|---|---|
| `templates/plan-adversarial-review-section.md` | Plan contract section |
| `templates/task-completion-gate-block.md` | Per-phase or per-slice completion gate |

## Validation Commands

```bash
bash -n scripts/install.sh
bash -n skills/codex-adversarial-gate/scripts/install.sh
bash scripts/test_install.sh
python3 skills/codex-adversarial-gate/scripts/test_archive_adversarial_review.py
python3 -m py_compile \
  skills/codex-adversarial-gate/scripts/archive_adversarial_review.py \
  skills/codex-adversarial-gate/scripts/test_archive_adversarial_review.py
git diff --check
```
