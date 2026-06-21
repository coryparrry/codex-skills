# Packet Loop State Contract

## Source Of Truth

Structured state lives under `.codex/packet-loop/`.

- `.codex/packet-loop/manifest.json` is the repo loop manifest.
- `.codex/packet-loop/packets/<packet-id>.json` is one packet record.
- `.codex/packet-loop/events.jsonl` records state changes and deterministic repairs.
- `.codex/packet-loop/evidence/<packet-id>/` stores packet-local evidence.
- `docs/codex/packet-loop.md` is generated human-readable dashboard output.

Agents must treat the JSON state as authoritative. Markdown dashboard text is derived output.

## Worker Write Boundary

Workers may update only:

- their leased packet record
- `.codex/packet-loop/evidence/<packet-id>/`
- implementation files inside the packet allowed scope

Workers must not edit the manifest, other packet records, or generated dashboard unless a stage skill explicitly assigns that work.

## Human Gates

Stop for human approval before:

- merge
- branch deletion
- PR closing
- force-push
- default-branch write
- security-sensitive change

## CLI

Use `scripts/packet_loop.py` for deterministic state changes:

```bash
python3 <core-skill>/scripts/packet_loop.py --repo <repo> validate
python3 <core-skill>/scripts/packet_loop.py --repo <repo> maintain --expire-stale-leases
```
