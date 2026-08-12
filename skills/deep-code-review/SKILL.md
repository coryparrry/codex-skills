---
name: deep-code-review
description: Perform deep, language-agnostic, repository-wide code review of a pull request, branch, commit, diff, working tree, or AI-generated change. Trace affected behavior beyond changed lines, reconstruct intent and invariants, route specialist review by risk, use deterministic and behavioral evidence, inspect missing companion changes, and report only validated defects, material unresolved risks, merge blockers, and explicit coverage gaps. Use for deep, exhaustive, repo-wide, adversarial, or AI-code review and for deciding whether a change is safe, complete, appropriate, and mergeable.
---

# Deep code review

Review the proposed change as a behavioral change to a repository, not as isolated edited lines. Establish what was intended, what is affected, which invariants must survive, what evidence proves or disproves each concern, and what remains unknown.

Treat review as read-only. Do not edit, stage, commit, push, post comments, or resolve threads unless the user separately asks for changes. If the request includes fixes, finish and report the review before starting a clearly separated repair phase.

## 1. Bind the review to an exact state

Resolve the requested scope before judging it:

- For a pull request or branch, record the authoritative base, head, merge base, and comparison mode.
- For a non-merge commit, compare it with its parent. For a merge commit, state which parent or combined view is in scope.
- For a working tree, inventory staged, unstaged, and untracked paths and state exclusions.
- For files, pasted patches, or paths, keep findings inside that scope while reading repository context needed to validate them.
- Record repository, remote, branch, `HEAD`, dirty state, submodules, generated artifacts, relevant toolchain versions, and available CI evidence.

Inventory every changed path before partitioning the work. If the checkout or remote head changes, re-resolve the state and do not combine evidence from different snapshots silently.

If the supplied material cannot establish the complete change, mark the review partial. Do not approve a complete change from a partial inventory.

## 2. Resolve repository policy

Discover root and path-specific instructions before semantic review. Inspect applicable `AGENTS.md` files or equivalents, contribution guidance, security policy, ownership rules, pull-request templates, architecture records, generated-file rules, and repository-defined build, test, lint, type, release, and validation commands.

Resolve precedence and applicability. Load only rules relevant to the changed and affected paths, but record unresolved conflicts and material rules that could not be loaded.

## 3. Reconstruct intent and invariants

Use the user's request, linked issue or specification, observable base behavior, existing contracts, callers, tests, documentation, history, reverts, and accepted repository conventions. Do not use the new implementation or its new tests as sole proof of intent.

Write a compact ledger of:

- requested before/after behavior;
- preserved and new invariants;
- failure, retry, cancellation, ordering, idempotency, and recovery expectations;
- security, compatibility, migration, rollback, and operational requirements;
- unresolved interpretation questions.

If intent remains ambiguous, report the ambiguity instead of inventing a defect.

## 4. Map changed and affected behavior

Read [impact-and-negative-space.md](references/impact-and-negative-space.md). Build a compact repository map and typed impact model from each changed symbol or artifact through the relevant callers, consumers, configuration, data, generated outputs, tests, deployment surfaces, and historical rationale.

Label every relationship by provenance: verified static, verified runtime, verified configuration, verified history, inferred semantic, or unresolved. Stop expansion only when a boundary is demonstrated safe. Do not flatten the entire repository into context merely because it fits.

Maintain a coverage ledger of changed paths, classified symbols, affected paths, critical flows, and unresolved edges.

## 5. Route review depth by risk

Run the core correctness and integration lane for every change. Read [risk-lanes.md](references/risk-lanes.md) and activate specialist lanes only when their triggers are present. Route by semantics, criticality, coupling, reversibility, and strength of available verification, not by one universal line-count threshold.

Inspect every changed slice deeply, then perform an integration pass across shared contracts and cross-cutting state. A file-by-file checklist without path reconstruction is not a complete review.

When independent subagents are available, use them only for genuinely non-overlapping, read-only lanes after the primary reviewer has inventoried the full change and identified shared contracts. Give them raw scope and artifacts, not suspected answers. Recheck every candidate against the complete exact-head change before reporting it.

## 6. Collect deterministic and behavioral evidence

Read [evidence-and-validation.md](references/evidence-and-validation.md). Use deterministic tools for claims they can answer directly: parsers, compilers, type checkers, linters, schema validators, dependency resolvers, static analysis, tests, runtime traces, sanitizers, and repository-defined checks.

Treat tool failure, timeout, unavailable credentials, missing runtime, and environment mismatch as evidence gaps, never as passes.

Treat tests as necessary evidence where applicable, not as the complete specification. Audit changed tests, fixtures, mocks, snapshots, skips, and assertions. Establish whether a new regression test fails on the base state, derives its oracle independently of the implementation, exercises the production path, and rejects realistic wrong implementations.

Escalate behavioral challenge in proportion to risk: focused regression, broader suite, before/after comparison, mutation, property or metamorphic checks, fuzzing, differential execution, race/stress testing, or migration/rollback compatibility.

## 7. Inspect negative space and reuse

Ask what companion change or evidence should normally exist but is absent. Check migrations, registrations, generated outputs, clients, lockfiles, permissions, production configuration, observability, rollback, compatibility, and tests when the intended change implies them.

Ask what an established maintainer would reuse instead of each new helper, parser, retry loop, cache, authorization check, serializer, transaction wrapper, or process launcher. Prove that an existing abstraction applies before reporting bypass or duplication as a defect.

Absence, unusual structure, broad exception handling, scaffolding, mocks, or AI authorship are investigation signals only. Report them only after proving a violated property.

## 8. Falsify and validate candidates

Treat every candidate finding as unproven. Try to disprove it against the exact head by checking reachability, preconditions, alternative explanations, language and framework guarantees, existing safeguards, history, and whether a proposed correction would create a regression.

For material candidates, use a neutral validation pass when available. Supply the exact state, requirement evidence, factual path, and reproduction without persuasive framing. Allow `no defect established` as a first-class result.

Classify candidates as `validated`, `unresolved`, `observation only`, `disproved`, or `stale at current head`. Report only validated defects and material unresolved risks. Do not promote a concern because it sounds severe or came from another model or scanner.

## 9. Report findings and coverage

Read [report-format.md](references/report-format.md). Lead with validated findings, ordered by priority. Keep severity, confidence, and validation status separate. Give each finding a concrete trigger, affected execution or data path, violated invariant, impact, exact evidence, false-positive check, and smallest fix direction.

Then report material unresolved risks, process or merge blockers, validation performed, coverage, exclusions, unavailable evidence, and disposition. A coverage ledger proves what was investigated, not that the conclusions are correct.

If no material finding survives, say so directly. Do not invent a comment to make the review look useful.

## Non-negotiables

- Bind every conclusion to the exact reviewed state.
- Review affected behavior and required missing changes, not only the diff.
- Prefer selected, provenance-backed context over indiscriminate context volume.
- Use deterministic evidence before model speculation.
- Separate a scanner match from a reachable defect or exploitable vulnerability.
- Separate non-merge, policy, duplication, and coordination issues from technical defects.
- Prefer a few reproducible findings over speculative volume.
- State every unreviewed surface and withheld verdict.
