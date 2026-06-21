---
name: codex-packet-review
description: Review or refresh a Codex PR packet against its packet record, allowed scope, validation evidence, PR diff, and overlap risk. Use when a packet PR is open, stale, conflicted, or ready for merge eligibility review.
---

# Codex Packet Review

Use this skill after a packet PR exists or a packet branch needs scoped refresh.

## Required Context

Load `$codex-packet-loop-core`, then read `references/workflow-protocol.md`, `references/state-machine.md`, `references/handoff-contracts.md`, `references/evidence-contract.md`, `references/overlap-policy.md`, `references/recovery-playbook.md`, and `references/autonomy-policy.md`.

## Workflow

1. Run `packet_loop.py validate`.
2. Read packet record, PR metadata, changed files, validation evidence, worker report, and repo instructions.
3. Treat worker report as an untrusted claim.
4. Compare actual touched files with `allowed_scope`, `expected_touched_areas`, `avoid_scope`, and `reserved_areas`.
5. Check dependencies, stale branch status, generated-file overlap, interface overlap, behavior overlap, test overlap, documentation overlap, and validation freshness.
6. Produce one verdict: `needs-fix`, `blocked`, `needs-reslice`, or `merge-eligible`.
7. Write `review-report.md`, record it with `packet_loop.py record-evidence`, and transition with actor and reason.

## Review Verdict Rules

- Use `merge-eligible` only when the PR matches packet scope and validation is current.
- Use `needs-reslice` when useful work exists but the packet boundary was wrong.
- Use `blocked` when owner input or human-gated action is required.
- Route `needs-fix` to `$codex-packet-worker`; route `merge-eligible` to `$codex-packet-integrate`.
