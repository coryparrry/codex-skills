# Packet Loop Autonomy Policy

## Safe Autonomous Actions

- Validate packet-loop state.
- Expire stale leases when the lease TTL has passed and no PR metadata exists.
- Regenerate generated dashboards through the CLI.
- Reserve ready packets when dependencies, monitoring capacity, serialized resource-lane constraints, and reserved-area checks pass.
- Record evidence paths and PR metadata through the CLI.
- Recommend merge order without performing the merge.

## Recommend-Only Actions

- Merge packet PRs.
- Close PRs.
- Delete branches or worktrees.
- Force-push packet branches.
- Change packet scope after useful work exists.

## Hard Stops

Stop for user input before destructive Git operations, default-branch writes, security-sensitive tradeoffs, external submissions not already authorized, or repeated failures with the same root cause.
