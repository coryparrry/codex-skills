# Packet Loop Handoff Contracts

## Dispatch Handoff

Required fields: packet id, packet title, packet goal, branch, worktree, owner thread id, allowed scope, avoid scope, expected touched areas, reserved areas, validation commands, evidence directory, stop conditions, and next skill `$codex-packet-worker`.

## Worker Report

Required fields: packet id, summary of changed behavior, files touched, validation commands run, validation result, evidence paths, PR metadata, concerns, and requested next skill `$codex-packet-review`.

## Review Verdict

Required fields: packet id, PR URL or branch, checks performed, scope result, validation result, overlap result, verdict, exact reason, required fix or integration note, and next skill.

## Integration Recommendation

Required fields: candidate packets, PR metadata, stale status, conflict status, overlap categories, recommended serial order, and human-gated action requested.

## Maintenance Report

Required fields: validation status, expired leases, deterministic repairs, invalid records, ready packets, blocked packets, merge-eligible packets, and next safe skill.
