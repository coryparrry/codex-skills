# Repository Technology Research

`research-repo-technology` determines which technologies an existing repository should adopt, adapt, build, or reject.

## Use It For

- assessing architecture or product opportunities from a live checkout;
- comparing external projects at source level;
- identifying a narrow dependency, protocol, algorithm, or design pattern worth transferring;
- ranking repo-specific opportunities and defining bounded proofs of concept.

Ask Codex:

```text
Use $research-repo-technology to determine which technologies this repository should adopt, adapt, build, or reject.
```

The skill first establishes repository truth—implementation, tests, constraints, direction, and working-tree state—then derives external research questions from verified gaps.

## Parent Model Requirement

Start the root task with `gpt-5.6-luna` at maximum reasoning. The skill checks the parent model before auditing the repository and stops with restart guidance when the requirement cannot be verified.

Luna Max research subagents cannot compensate for a different parent model because the parent owns baseline verification, integration, contradiction resolution, ranking, and closeout.

## What It Returns

The report leads with a strategic recommendation and includes:

- current strengths, verified limitations, constraints, and unresolved hypotheses;
- ranked opportunities with exact repository integration points;
- adopt, adapt, build, or reject decisions;
- privacy, security, performance, maintenance, platform, and licence risks;
- rejected alternatives and up to three bounded proof-of-concept designs, with fewer when the evidence does not justify them.

Research-only runs do not edit the repository, install dependencies, update tasks, or implement the proposed proofs.

## Related Docs

- [Usage Guide](usage.md)
- [Installation](installation.md)
- [Reference](reference.md)
- [Continue Deep Research](continue-deep-research.md)
