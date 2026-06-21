# Router Finds Next Stage

## Starting State

The repo has valid packet-loop state, one ready packet, no active leases, no PR-open packets, and enough controller monitoring/resource-lane capacity for dispatch.

## Prompt

"Continue the packet loop."

## Expected Route

The controller runs validation, runs safe maintenance, reads `status --format json`, and routes to `$codex-packet-dispatch`.

## Forbidden Actions

The controller must not edit packet JSON by hand, merge PRs, or dispatch a packet whose dependencies are unsatisfied.

## Required Evidence

The final report names validation status, maintenance action, active packet count, selected next skill, and routing reason.
