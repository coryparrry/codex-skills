# Packet Loop State Machine

## Statuses

`candidate`, `ready`, `reserved`, `in-progress`, `pr-open`, `reviewing`, `needs-fix`, `blocked`, `needs-reslice`, `merge-eligible`, `merged`, and `rejected`.

## Autonomous Transitions

| From | To |
|---|---|
| `candidate` | `ready`, `blocked`, `needs-reslice` |
| `ready` | `reserved` |
| `reserved` | `in-progress`, `ready` |
| `in-progress` | `pr-open`, `needs-fix`, `blocked`, `needs-reslice` |
| `pr-open` | `reviewing` |
| `reviewing` | `needs-fix`, `blocked`, `needs-reslice`, `merge-eligible` |
| `needs-fix` | `reserved`, `blocked` |
| `blocked` | `ready`, `needs-reslice` |
| `needs-reslice` | `candidate` |

## Human-Gated Transitions

`merge-eligible` to `merged` requires explicit human approval. Moving any live packet to `rejected` requires explicit human approval when useful work or an open PR would be discarded.

## Transition Event Requirements

Every transition records actor, prior status, new status, reason, timestamp, and evidence path when available. Use `packet_loop.py transition` rather than editing packet JSON directly.
