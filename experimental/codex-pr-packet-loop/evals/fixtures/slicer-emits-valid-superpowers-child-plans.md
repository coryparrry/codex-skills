# Slicer Emits Valid Superpowers Child Plans

## Starting State

The input is an approved Superpowers implementation plan with packetable tasks and no generated child plans yet.

## Prompt

"Slice this approved Superpowers plan into packets."

## Expected Route

`$codex-packet-slice` uses `superpowers:writing-plans` output shape for each packet child plan and marks packets ready only after validation.

## Forbidden Actions

Dispatching a raw packet prompt or a child plan missing the required Superpowers header.

## Required Evidence

Report lists parent plan path, child plan paths, source task refs, format checks, and any packet held as `candidate`.
