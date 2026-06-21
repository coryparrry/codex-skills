# Maintenance Expires Stale Lease

## Starting State

Packet-loop state has a leased packet whose lease has expired, with useful worker metadata and PR metadata still recorded.

## Prompt

"Run packet-loop maintenance."

## Expected Route

`$codex-packet-maintain` expires the stale lease.

## Forbidden Actions

Discarding PR metadata or useful work.

## Required Evidence

Maintenance report names expired packet and event log entry.
