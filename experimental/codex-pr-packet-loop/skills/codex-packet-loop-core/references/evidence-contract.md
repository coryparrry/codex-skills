# Packet Loop Evidence Contract

## Worker Evidence

Workers write evidence under `.codex/packet-loop/evidence/<packet-id>/` and record each path with `packet_loop.py record-evidence`.

Required worker evidence: `worker-report.md`, `validation-<timestamp>.txt`, `diffstat-<timestamp>.txt`, and `scope-check.json`.

## Review Evidence

Required review evidence: `review-report.md` and `pr-state.json`.

## Integration Evidence

Required integration evidence: `merge-matrix.md` and `integration-report.md`.

## Maintenance Evidence

Required maintenance evidence: `maintenance-report.md` when maintenance changes packet state.
