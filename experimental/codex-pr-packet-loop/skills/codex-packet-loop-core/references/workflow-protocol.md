# Packet Loop Workflow Protocol

## Authority Order

1. Direct user instruction for the current turn.
2. Repo and nested `AGENTS.md` instructions.
3. Packet-loop JSON under `.codex/packet-loop/`.
4. Packet-loop evidence paths recorded in packet JSON.
5. Generated dashboard at `docs/codex/packet-loop.md`.

JSON state wins over generated Markdown when the two disagree.

## Stage Routing

| State or request | Next skill |
|---|---|
| No `.codex/packet-loop/manifest.json` exists | `$codex-packet-init` |
| Manifest exists but there are no packet records | `$codex-packet-slice` |
| Invalid packet-loop JSON or expired deterministic lease | `$codex-packet-maintain` |
| Dependency-ready packets fit monitoring and resource-lane capacity | `$codex-packet-dispatch` |
| Packet is leased to the current worker | `$codex-packet-worker` |
| Packet has PR state or status `pr-open` or `reviewing` | `$codex-packet-review` |
| Packet is `merge-eligible` | `$codex-packet-integrate` |
| Packet is `blocked` or `needs-reslice` | `$codex-packet-slice` or user decision |

## Controller Loop

The controller validates state, runs deterministic maintenance, reads status summary, chooses one safe next skill, and stops at human gates. It must supervise active worker lanes by checking thread status, worktree dirt, and diff shape before integration.
