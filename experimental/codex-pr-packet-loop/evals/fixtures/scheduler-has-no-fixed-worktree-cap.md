# Scheduler Has No Fixed Worktree Cap

## Starting State

Packet-loop state has more than three dependency-ready packets and no owner cap or monitoring constraint that requires holding them.

## Prompt

"Schedule ready packet work."

## Expected Route

`$codex-packet-loop` dispatches every dependency-ready packet it can actively monitor.

## Forbidden Actions

Stopping at a hidden count such as three active workers when no owner cap exists.

## Required Evidence

Controller report names dependency-ready packets, active monitoring basis, review capacity, and any packet deliberately held back.
