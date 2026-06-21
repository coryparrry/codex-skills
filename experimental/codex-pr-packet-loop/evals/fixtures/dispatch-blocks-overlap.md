# Dispatch Blocks Overlap

## Starting State

The repo has valid packet-loop state with one leased packet and one ready packet whose `reserved_areas` collide with the live lease.

## Prompt

"Dispatch the next packet."

## Expected Route

`$codex-packet-dispatch` refuses the colliding ready packet.

## Forbidden Actions

Leasing a packet with `reserved_areas` colliding with a live lease.

## Required Evidence

Refusal names the live packet and colliding reserved area.
