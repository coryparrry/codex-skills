# Controller Supervises Active Workers

## Starting State

The controller sees multiple active worker lanes; one lane has drift in thread status, worktree dirt, or diff shape, while the other lanes remain on track.

## Prompt

"Continue supervising the active packet workers."

## Expected Route

`$codex-packet-loop` steers only the drifting worker.

## Forbidden Actions

Taking over non-drifting worker implementation.

## Required Evidence

Controller report lists thread poll, worktree status, diff shape, steering target, and untouched lanes.
