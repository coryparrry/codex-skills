# Packet Loop Overlap Policy

## Overlap Categories

Classify overlap as file, area, interface, behavior, test, generated-file, dependency, documentation, or state-file overlap.

## Dispatch Rule

Dispatch refuses a packet when its `reserved_areas` collide with a live leased packet. Dispatch may proceed with documented caution when overlap is documentation-only and neither packet is live.

## Review Rule

Review verifies actual touched files against allowed scope, expected touched areas, reserved areas, and avoid scope. Unexpected overlap cannot be waved through by worker summary.
