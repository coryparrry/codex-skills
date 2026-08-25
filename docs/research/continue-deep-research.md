# Continue Deep Research

`continue-deep-research` extends an existing research evidence base without restarting the topic or flattening prior work into another summary.

## Use It For

- continuing a ChatGPT Pro Deep Research report with live repository context;
- verifying or updating findings from notes, files, URLs, papers, or prior tasks;
- investigating open questions and contradictory evidence;
- producing a primary-source-cited delta from an accepted baseline.

Ask Codex:

```text
Use $continue-deep-research to continue this Deep Research report against the live repository. Verify the unresolved claims and return the research delta.
```

Provide the existing report, notes, links, local paths, or task IDs and state the decision the research should support when it is not already clear.

## Runtime Availability

The skill starts from the supplied evidence with the current root agent. When the runtime supports useful independent lanes, it uses them for bounded verification gaps; otherwise it completes a root-only audit and discloses the reduced coverage. It never refuses a well-scoped research request merely because a preferred model is unavailable.

## What It Returns

The skill leads with the current answer, recovers the prior baseline, and reports only material changes under the relevant categories: retained, confirmed, corrected, new, contradicted, and unresolved. It maps evidence to claims and separates verified facts from inference.

Research-only runs remain read-only. Supplied material is preserved, current or disputed claims are checked against primary sources, and inaccessible evidence is disclosed rather than guessed.

## Related Docs

- [Usage Guide](../usage.md)
- [Installation](../installation.md)
- [Reference](../reference.md)
- [Repository Technology Research](research-repo-technology.md)
