# Recovery Reslices Bad Packet

## Starting State

A packet repeatedly fails review because its scope boundary does not match the actual implementation dependency boundary.

## Prompt

"Recover this blocked packet."

## Expected Route

`$codex-packet-review` or `$codex-packet-maintain` routes to `$codex-packet-slice`.

## Forbidden Actions

Repeatedly fixing the same boundary mismatch.

## Required Evidence

Report records `needs_reslice_reason`.
