---
name: codex-packet-review
description: Review or refresh a Codex PR packet against its packet record, allowed scope, validation evidence, PR diff, and overlap risk. Use when a packet PR is open, stale, conflicted, or ready for merge eligibility review.
---

# Codex Packet Review

Use this skill after a packet PR exists or a packet branch needs scoped refresh.

## Workflow

1. Read repo instructions, packet record, PR metadata, changed files, and validation evidence.
2. Load `$codex-packet-loop-core` and read its state contract.
3. Run packet-loop validation.
4. Compare actual changed files with `allowed_scope` and `expected_touched_areas`.
5. Check dependencies, live leases, generated-file overlap, interface overlap, behavior overlap, test overlap, documentation overlap, and validation freshness.
6. If the branch is stale or conflicted, produce a refresh packet scoped to the original packet only.
7. Move the packet to exactly one status:
   - `needs-fix`
   - `blocked`
   - `needs-reslice`
   - `merge-eligible`
8. Report evidence checked and next valid skill: `$codex-packet-worker` for fixes or `$codex-packet-integrate` for merge candidates.

## Review Verdict Rules

- Use `merge-eligible` only when the PR matches packet scope and validation is current.
- Use `needs-reslice` when useful work exists but the packet boundary was wrong.
- Use `blocked` when owner input or human-gated action is required.
- Treat worker summaries as claims until verified against files, diffs, checks, PR state, and evidence.
