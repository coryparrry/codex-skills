---
name: triage-review-comments
description: Verify and classify PR review feedback; apply fixes or remote updates only when authorized.
---

# Triage Review Comments

Treat every review comment as a hypothesis until current-code evidence proves the issue exists on the PR head. Protect the PR from real bugs while rejecting stale, duplicate, speculative, preference-only, and false-positive feedback.

## Scope And Authorization

A request to triage, review, classify, inspect, or investigate comments authorizes read-only collection and analysis. Produce the report without changing code, committing, pushing, replying to or resolving threads, or creating follow-up issues.

Mutation verbs authorize the corresponding work. Requests such as `fix the review comments`, `implement the valid findings`, `resolve the fixed threads`, or `create issues for deferred items` authorize those named actions within the established PR scope. Triage first, then carry the authorized work through validation and the requested delivery boundary. Do not ask for separate approval for each item or repeat an approval request after the user has already authorized that class of action.

Do not infer one mutation from another when it is outside the normal requested workflow. For example, permission to resolve threads does not authorize code changes, and permission to triage does not authorize issue creation.

## Read-Only Triage

1. Identify the current PR and review surface.
   - Prefer live GitHub review data when the repository and PR are known.
   - If the PR cannot be identified, use supplied comments and mark inventory completeness honestly.

2. Build the inventory before classifying.
   - Count open and resolved inline threads, general PR comments, and review submissions with standalone findings.
   - Treat truncated output, browser snippets, or a single incomplete source as incomplete inventory.

3. Filter and deduplicate.
   - Exclude walkthroughs, banners, status boilerplate, and formatting summaries without findings.
   - Deduplicate by root cause.

4. Verify against the PR head.
   - Try to falsify each claim by checking the current path, trigger, guards, later commits, surrounding invariants, and existing tests.
   - Only treat a claim as real when it is reachable and survives the false-positive checks.
   - Use [EVALUATION.md](references/EVALUATION.md) for the evidence checklist.

5. Classify each unique finding into exactly one bucket.
   - `Fix now`: verified, meaningful, and should block merge.
   - `Fix if cheap`: verified and limited enough to take only if the patch stays small and low-risk.
   - `Defer`: verified work that should survive as follow-up rather than block this PR.
   - `Ignore`: false positive, stale, duplicate, preference-only, already fixed, or unverified.
   - Use [CLASSIFICATION.md](references/CLASSIFICATION.md) for edge cases.

6. Recommend the smallest useful prevention check for every real finding. Do not recommend tests for noise unless it reveals a missing broader guard.

Read-only triage may identify threads that are safe to resolve or deferred items worth tracking, but report them as recommendations unless those mutations were authorized.

## Authorized Execution

When the user explicitly requests fixes:

- implement every verified `Fix now` item within scope
- implement `Fix if cheap` items only while they remain small, low-risk, and in scope; otherwise reclassify them as `Defer` with a reason
- add focused prevention coverage when it provides meaningful behavioral proof
- validate every touched surface with relevant repository commands
- preserve unrelated work and follow the repository's delivery rules

When replies or thread resolution are authorized, act only after the fix is implemented, validated, and visible in the current PR state. Refetch the remote thread and count it as resolved only when GitHub reports `isResolved: true`. Report exact blockers for any authorized thread that could not be resolved.

When deferred tracking is authorized, search for an existing item before creating one and use the correct project. Record only verified real issues. Use [INTEGRATION.md](references/INTEGRATION.md) for GitHub, Linear, and Binder patterns.

## Report Contract

Lead with inventory completeness and bucket counts. For each real finding include:

- confidence and current-head evidence
- a concrete reachable trigger
- the main false-positive explanation checked and ruled out
- consequence if unchanged
- the smallest prevention test or check

For every `Fix now` item, include a fix brief with current and desired behavior, stable interfaces, acceptance criteria, validation, scope boundary, and adjacent risk.

For `Ignore`, state the disproof or missing proof. If inventory is incomplete, label all totals accordingly.

Include execution status only for actions the user authorized: fixes applied, validation run, replies or resolutions refetched, follow-ups created, and blockers. Do not imply that read-only recommendations were executed.

See [triage-review-comments.md](references/triage-review-comments.md) for the compact report shape and [EXAMPLE.md](references/EXAMPLE.md) for a worked claim.

## Operating Rules

- Prefer structured GitHub tools when available; use `gh` as a fallback.
- Do not preserve reviewer severity when current evidence disagrees.
- Do not patch merely to satisfy an unproven comment.
- Security boundary, authorization, privacy, data loss, and cross-workspace isolation bugs default to `Fix now` when reachable.
- Keep ordinary triage read-only. Once fixes or external mutations are explicitly authorized, complete them without repeated approval requests.
