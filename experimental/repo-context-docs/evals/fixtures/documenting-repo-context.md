# documenting-repo-context pressure fixture

## Scenario

The user wants a new experimental skill that captures the Matt Pocock-style repo documentation structure, but it must not conflict with Superpowers. The user specifically cares about:

- agent routing: `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, `docs/agents/generated-documents.md`
- domain memory: `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/agents/domain.md`
- decision memory: `docs/adr/*.md`, `docs/decisions/*.md`

## Baseline failures observed

Without this skill, pressure-scenario agents drifted into:

- generic doc-audit skills such as README or architecture planning
- workflow-shaped skills that inspect, plan, draft, pressure-test, or close docs
- alternate taxonomies such as `docs/domain-model.md`, `docs/agent-routing.md`, or `docs/documentation-map.md`
- Superpowers-adjacent routing language that risks owning planning, TDD, subagent dispatch, or verification

The first with-skill wording still allowed:

- five-layer taxonomies such as orientation, concept, workflow, contract, and maintenance
- source-led documentation flows with audience/doc-type selection
- new routing docs such as `docs/agents/routing.md`
- generic practical documentation skills for README, onboarding, architecture, troubleshooting, and usage examples
- one-off repo note flows with problem/invariant/testing beats

## Passing behavior

An agent using the skill should:

- preserve the three selected layers by name
- use the Matt-style file names where given
- describe document ownership, not a full workflow
- keep Superpowers responsibilities out of scope
- create docs lazily, only when facts exist
- classify new information into exactly one owning layer
