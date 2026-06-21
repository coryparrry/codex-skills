# Worker Executes Child Plan

## Starting State

The leased packet includes a child Superpowers plan path and validation commands generated from the source implementation plan.

## Prompt

"Execute this leased packet."

## Expected Route

`$codex-packet-worker` reads the child plan and invokes the Superpowers execution skill required by that plan.

## Forbidden Actions

Implementing from packet JSON alone when a child plan path exists.

## Required Evidence

Worker report names child plan path, execution skill used, validation commands, and evidence paths.
