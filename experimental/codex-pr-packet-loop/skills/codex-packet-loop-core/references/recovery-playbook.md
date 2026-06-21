# Packet Loop Recovery Playbook

## Stale Lease

If the lease is expired, no PR metadata exists, and no recent evidence indicates useful in-flight work, run `packet_loop.py maintain --expire-stale-leases`.

## Failed Validation Loop

After two failed fix attempts with the same root cause, move the packet to `blocked` or `needs-reslice` with a reason.

## Scope Expansion

If the packet requires edits outside allowed scope, stop implementation and move the packet to `blocked` or `needs-reslice`.

## Bad PR

If a PR contains useful work but the boundary is wrong, review records `needs-reslice` rather than marking the PR merge-eligible.
