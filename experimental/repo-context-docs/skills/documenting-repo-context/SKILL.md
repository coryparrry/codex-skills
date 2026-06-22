---
name: documenting-repo-context
description: Use when classifying repo context into Matt-style agent routing, domain memory, or decision memory docs such as docs/agents/*, CONTEXT.md, CONTEXT-MAP.md, docs/adr/*.md, or docs/decisions/*.md.
---

# Documenting Repo Context

Use this skill to classify durable repo context into exactly three Matt-style document layers: agent routing, domain memory, and decision memory.

The output of this skill is a document ownership map. Superpowers and other invoked skills still own planning, TDD, execution, review, subagents, and verification.

## When to Use

- The user asks for the Matt-style repo document structure.
- A repo needs Matt-style setup docs, context docs, ADRs, or decision maps.
- An agent is unsure whether a fact belongs in `docs/agents/`, `CONTEXT.md`, an ADR, or a decision map.

## Output Contract

When asked what the repo document flow should look like, answer with this three-layer map and no extra taxonomy, no numbered workflow, and no "one note" format:

| Layer | Documents | Owns |
|---|---|---|
| Agent routing | `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, `docs/agents/generated-documents.md` | Where work records live, what labels/states mean, and what generated documents must contain. |
| Domain memory | `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/agents/domain.md` | Project vocabulary, bounded contexts, context relationships, and where domain docs are consumed. |
| Decision memory | `docs/adr/*.md`, `docs/decisions/*.md` | Accepted decisions, tradeoffs, unresolved questions, investigation tickets, and decision-map answers. |

Create these files lazily. Missing context docs are not a problem until the repo has a term, routing rule, or decision worth preserving.

## Classification Rule

Classify each fact by what future agents need it for:

- Routing a work record, label, or generated brief -> agent routing.
- Naming a domain concept or bounded context -> domain memory.
- Preserving a settled tradeoff or unresolved investigation -> decision memory.

If a fact does not fit one of these three needs, this skill has no opinion about it.

## Document Contracts

- `docs/agents/issue-tracker.md`: issue tracker commands or local markdown convention; where PRDs, issues, and comments live.
- `docs/agents/triage-labels.md`: canonical triage roles mapped to this repo's real labels.
- `docs/agents/generated-documents.md`: generated document types, producer skill, consumer skill, required fields, and update rules.
- `docs/agents/domain.md`: how agents find `CONTEXT.md`, `CONTEXT-MAP.md`, and ADRs before work.
- `CONTEXT.md`: glossary only. No implementation plan, status log, or spec.
- `CONTEXT-MAP.md`: index of multiple contexts and relationships between them.
- `docs/adr/*.md`: accepted decisions that are hard to reverse, surprising without context, and based on a real tradeoff.
- `docs/decisions/*.md`: compact decision maps for unresolved multi-session questions, with entries containing `Question`, `Answer`, `Blocked by`, and `Type`.

## Example

If agents keep guessing where issues live, create or repair `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md`. If agents use "packet", "work unit", and "slice" inconsistently, update `CONTEXT.md`. If the repo chooses local-only automation instead of a cloud service, record an ADR. If merge ordering is still unresolved, create `docs/decisions/merge-order.md`.

## Required Response Shape

For "what should the skill/document flow be?" questions, respond in this shape:

1. The skill is `documenting-repo-context`.
2. It owns a three-layer document ownership map.
3. Show the agent routing, domain memory, and decision memory table.
4. State that facts outside those layers are not covered.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Replacing this with generic `architecture.md` or `development.md` advice | Keep the three Matt-style layers: agent routing, domain memory, decision memory. |
| Inventing adjacent docs such as `docs/agent-routing.md`, `docs/domain-model.md`, or `docs/documentation-map.md` | Use the Matt file names in the output contract unless the repo already has an equivalent. |
| Adding source-led audits, README rewrites, onboarding docs, or troubleshooting docs | Return only the document ownership map. |
| Writing a one-off repo note format with problem, invariant, and testing beats | Classify the fact into the three-layer ownership map instead. |
| Turning this into a Superpowers wrapper | Leave planning, TDD, execution, subagents, and verification to the invoked Superpowers skills. |
| Pre-creating empty docs | Create lazily when a real routing rule, term, or decision exists. |
| Copying the same fact into several files | Put each fact in its owning layer and reference it elsewhere. |
| Treating a decision map as an ADR | Promote only accepted, durable decisions that meet the ADR criteria. |
