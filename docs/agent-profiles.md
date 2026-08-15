# Codex Agent Profiles

The bundle ships four narrow Codex subagent profiles. They are completion and review lanes, not general implementation agents.

None of the profiles sets `model` or `model_reasoning_effort`. Codex resolves those settings from an explicit spawn, the configured subagent defaults, or the parent task.

The standalone TOML files set `sandbox_mode = "read-only"` for acceptance, delivery-state, and provenance review. The evidence-ledger profile uses `workspace-write` because it must update one assigned checkpoint. Its instructions prohibit every other mutation.

## Acceptance contract reviewer

Use `acceptance-contract-reviewer` after implementation and validation, before claiming the task is complete.

Give it:

- acceptance criteria with stable IDs;
- exact repository, base, head, and dirty state;
- the diff or changed-file inventory;
- test, artifact, runtime, and external-state evidence that applies;
- preserved behavior, exclusions, and known gaps.

Example parent prompt:

```text
Spawn acceptance-contract-reviewer for this completed change. Check contracts AC-1 through AC-5 against HEAD <oid>, the supplied diff, validation log, packaged artifact checksum, and runtime observations. Return the exact verdict contract and do not make changes.
```

Its first output line is `PASS`, `FAIL_NEEDS_FIX`, or `BLOCKED_INSUFFICIENT_EVIDENCE`. A green test suite does not substitute for runtime or artifact proof when the contract concerns those surfaces.

## Delivery state reconciler

Use `delivery-state-reconciler` before merge, during closeout, or when local Git and GitHub appear inconsistent.

Give it:

- the repository and intended terminal state;
- the branch or pull request;
- the latest fetch time or fetch command;
- any branch, worktree, or remote-retention constraints.

Example parent prompt:

```text
Spawn delivery-state-reconciler for this repository and PR. Reconcile the current branch, worktrees, fetched refs, checks, review threads, merge state, and branches that must be retained. Report discrepancies and safe root-owned actions only.
```

The profile does not fetch, resolve threads, merge, delete branches, or remove worktrees. The parent performs those actions and re-checks state afterward.

## Evidence ledger lane reviewer

Use `evidence-ledger-lane-reviewer` for one disjoint lane of a long repository audit. Assign one module, entry point, shared contract, or risk boundary and one Markdown checkpoint that no other lane can edit.

Give it:

- the exact snapshot;
- lane scope, exclusions, and adjacent lanes;
- one checkpoint path;
- the initial evidence slice and stopping budget.

Example parent prompt:

```text
Spawn evidence-ledger-lane-reviewer for the installer-to-runtime provenance lane at HEAD <oid>. You own only review-ledger/installer-runtime.md. Checkpoint after at most eight new files or about 2,000 new lines. Do not modify source or overlap the packaging lane.
```

The profile updates one checkpoint, stops at cross-lane edges, and returns a handoff of at most 300 words. A timed-out or partially traced lane remains uncovered.

## Artifact provenance verifier

Use `artifact-provenance-verifier` when source changes flow through generated files, mirrors, packages, installers, signatures, release assets, or a running process.

Give it:

- the claimed source OID and dirty-state inputs;
- artifact paths, identifiers, checksums, and signatures;
- build or workflow records;
- package, release, installation, and runtime identity;
- downstream consumers that should reflect the source change.

Example parent prompt:

```text
Spawn artifact-provenance-verifier for source HEAD <oid> and the supplied release artifact. Trace dependency pins, generated manifests, checksums, bundled assets, workflow pins, package metadata, installed identity, and uncovered consumers. Do not rebuild or install anything.
```

Its verdict is `MATCH`, `MISMATCH`, or `INSUFFICIENT_EVIDENCE`. Matching filenames, ancestry, timestamps, source tests, and green CI do not establish artifact identity by themselves.

## Orchestration boundary

The parent owns scope, input freshness, fixes, validation, and every state-changing delivery action. Do not send these profiles broad implementation work. Spawn only the profiles that match a real independent lane, and do not add a reviewer chain around a small task that the parent can verify directly.
