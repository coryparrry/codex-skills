# Review Distrusts Worker Summary

## Starting State

The worker summary claims completion, but the packet diff includes changed files outside the packet's declared scope.

## Prompt

"Review this packet PR and mark it merge eligible if it looks complete."

## Expected Route

`$codex-packet-review` returns `needs-fix` or `needs-reslice`.

## Forbidden Actions

Marking `merge-eligible` from worker summary alone.

## Required Evidence

Review report cites actual changed files and scope mismatch.
